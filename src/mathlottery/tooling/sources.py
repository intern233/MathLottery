from __future__ import annotations

import ipaddress
import re
import socket
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from mathlottery.config import ToolConfig
from mathlottery.models import Problem, Reference, digest, now
from mathlottery.storage.core import atomic_write, json_text

USER_AGENT = "MathLottery/0.1 (+local mathematical research; Python httpx)"


def public_url(url: str) -> None:
    parts = urlsplit(url)
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or parts.username
        or parts.password
    ):
        raise ValueError("Only public HTTP(S) URLs without credentials are allowed")
    if parts.port not in (None, 80, 443):
        raise ValueError("Only HTTP(S) default ports are allowed")
    addresses = socket.getaddrinfo(parts.hostname, parts.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError("Private/local network destinations are not allowed")


def parse_page(html: str, url: str, retrieved_at: str | None = None) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "nav", "header", "footer"]):
        node.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    content = soup.select_one(".problem-text #content")
    problem = None
    if "erdosproblems.com" == (urlsplit(url).hostname or "").removeprefix("www.") and content:
        match = re.search(r"/(\d+)(?:[/?#]|$)", url)
        tags = soup.select_one("#tags")
        if match:
            problem = Problem(
                id=f"erdos-{match[1]}",
                title=f"Erdős problem #{match[1]}",
                statement=content.get_text(" ", strip=True),
                source_url=url,
                field=tags.get_text(" ", strip=True) if tags else "unknown",
            )
    text = (soup.select_one("main") or soup.body or soup).get_text("\n", strip=True)
    links = []
    seen = set()
    for anchor in soup.select("a[href]"):
        target = urljoin(url, anchor["href"])
        if target.startswith(("https://", "http://")) and target not in seen:
            links.append({"url": target, "title": anchor.get_text(" ", strip=True)})
            seen.add(target)
    return {
        "url": url,
        "title": title,
        "text": text,
        "links": links[:80],
        "retrieved_at": retrieved_at or now(),
        "problem": problem.model_dump(mode="json") if problem else None,
    }


def parse_arxiv(xml: str) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml)
    result = []
    for entry in root.findall("a:entry", ns):
        url = entry.findtext("a:id", default="", namespaces=ns)
        if "api/errors" in url:
            raise ValueError(entry.findtext("a:summary", default="arXiv API error", namespaces=ns))
        result.append(
            Reference(
                url=url.replace("http://", "https://", 1),
                title=" ".join(entry.findtext("a:title", default="", namespaces=ns).split()),
                authors=[
                    a.findtext("a:name", default="", namespaces=ns)
                    for a in entry.findall("a:author", ns)
                ],
                published_at=entry.findtext("a:published", namespaces=ns),
                retrieved_at=now(),
                summary=" ".join(entry.findtext("a:summary", default="", namespaces=ns).split()),
                source="arxiv_api",
            ).model_dump(mode="json")
        )
    return result


class WebTools:
    def __init__(self, directory: Path, config: ToolConfig, cancelled=lambda: False):
        self.directory = directory
        self.config = config
        self.cancelled = cancelled
        self.robots: dict[str, RobotFileParser] = {}
        self.last_request: dict[str, float] = {}

    def _wait(self, host: str):
        delay = max(self.config.web_interval_seconds, 3 if "arxiv.org" in host else 0)
        end = self.last_request.get(host, 0) + delay
        while time.monotonic() < end:
            if self.cancelled():
                raise ValueError("Run interrupted during web request")
            time.sleep(min(0.1, end - time.monotonic()))
        self.last_request[host] = time.monotonic()

    def _request(self, url: str, *, check_robots=True) -> tuple[str, str]:
        data, final_url, _ = self.download(url, check_robots=check_robots)
        return data.decode("utf-8", errors="replace"), final_url

    def download(self, url: str, *, check_robots=True, allow_pdf=False) -> tuple[bytes, str, str]:
        for _ in range(5):
            if self.cancelled():
                raise ValueError("Run interrupted before web request")
            public_url(url)
            parts = urlsplit(url)
            origin = f"{parts.scheme}://{parts.netloc}"
            if check_robots and origin not in self.robots:
                robot = RobotFileParser()
                try:
                    robots_text, _ = self._request(origin + "/robots.txt", check_robots=False)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in (404, 410):
                        robots_text = "User-agent: *\nAllow: /"
                    else:
                        raise ValueError(f"Unable to verify robots policy for {origin}") from exc
                robot.parse(robots_text.splitlines())
                self.robots[origin] = robot
            if check_robots and not self.robots[origin].can_fetch(USER_AGENT, url):
                raise ValueError(f"robots.txt disallows fetching {url}")
            self._wait(parts.hostname)
            with httpx.Client(
                timeout=self.config.web_timeout_seconds,
                follow_redirects=False,
                headers={"User-Agent": USER_AGENT},
            ) as client:
                with client.stream("GET", url) as response:
                    if response.is_redirect:
                        url = urljoin(url, response.headers["location"])
                        continue
                    response.raise_for_status()
                    kind = response.headers.get("content-type", "")
                    if kind and not any(x in kind for x in ("text", "xml", "json")) and not (
                        allow_pdf and "application/pdf" in kind
                    ):
                        raise ValueError(f"Unsupported content type {kind}; provide text/Markdown")
                    chunks = []
                    size = 0
                    for chunk in response.iter_bytes():
                        if self.cancelled():
                            raise ValueError("Run interrupted during download")
                        size += len(chunk)
                        if size > self.config.max_download_bytes:
                            raise ValueError("Download exceeds configured size limit")
                        chunks.append(chunk)
                    return b"".join(chunks), url, kind
        raise ValueError("Too many HTTP redirects")

    def fetch(self, url: str) -> dict:
        html, final_url = self._request(url)
        result = parse_page(html, final_url)
        key = digest(url + result["retrieved_at"])[:16]
        relative = f"literature/{key}.txt"
        atomic_write(self.directory / relative, html)
        result.update({"status": "OK", "artifact": relative, "sha256": digest(html)})
        atomic_write(self.directory / "literature" / f"{key}.json", json_text(result))
        result["text"] = result["text"][: self.config.max_output_chars]
        return result

    def search(self, query: str, limit: int = 5) -> dict:
        limit = min(max(limit, 1), 10)
        terms = re.findall(r"[\w-]+", query, flags=re.UNICODE)
        if not terms:
            raise ValueError("Search query must contain at least one word")
        search_query = " AND ".join(f"all:{term}" for term in terms[:15])
        params = {
            "search_query": search_query,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = "https://export.arxiv.org/api/query?" + urlencode(params)
        # This is the documented public API, governed by its API Terms of Use, not
        # the web crawler policy. _wait enforces >=3 seconds between API requests.
        xml, _ = self._request(url, check_robots=False)
        key = digest(url + now())[:16]
        artifact = f"literature/{key}.xml"
        atomic_write(self.directory / artifact, xml)
        results = parse_arxiv(xml)
        for record in results:
            record.update(artifact=artifact, sha256=digest(xml))
        output = {
            "status": "OK",
            "query": query,
            "results": results,
            "retrieved_at": now(),
            "scope": "arXiv metadata only; not an exhaustive novelty check",
            "artifact": artifact,
        }
        atomic_write(self.directory / "literature" / f"{key}.json", json_text(output))
        return output


def conservative_status(problem: Problem, retrieved: list[dict], *, previous_assessments=()) -> Problem:
    from mathlottery.verify.policy import assess_problem

    return assess_problem(problem, retrieved, previous_assessments=previous_assessments)
