import json
import socket

import httpx
import pytest

from mathlottery.config import ToolConfig
from mathlottery.execution import python_exec
from mathlottery.formal import lean_check
from mathlottery.models import OpenStatus, Phase, Problem, ToolCall, now
from mathlottery.sources import WebTools, conservative_status, parse_arxiv, parse_page, public_url
from mathlottery.storage import safe_path
from mathlottery.tools import ToolRegistry


def test_python_runs_real_sympy_in_isolation(tmp_path):
    result = python_exec(
        "import sympy as s\nprint(s.factor(s.Symbol('x')**2-1))", tmp_path, ToolConfig()
    )
    assert result["status"] == "OK", result
    assert "(x - 1)*(x + 1)" in result["stdout"]


@pytest.mark.parametrize("operation", ["read", "write", "truncate", "chmod"])
def test_python_cannot_access_or_damage_outside_files(tmp_path, operation):
    secret = tmp_path / "private.txt"
    secret.write_text("private test fixture")
    code = {
        "read": f"print(open({str(secret)!r}).read())",
        "write": f"open({str(secret)!r},'w').write('changed')",
        "truncate": f"import os\nos.truncate({str(secret)!r},0)",
        "chmod": f"import os\nos.chmod({str(secret)!r},0)",
    }[operation]
    result = python_exec(code, tmp_path / "sandbox", ToolConfig())
    assert result["status"] == "ERROR"
    assert "PermissionError" in result["stderr"]
    assert secret.read_text() == "private test fixture"


@pytest.mark.parametrize(
    "code",
    [
        "import socket\nsocket.socket()",
        "import subprocess\nsubprocess.run(['/usr/bin/true'])",
    ],
)
def test_network_and_process_creation_are_blocked(tmp_path, code):
    result = python_exec(code, tmp_path, ToolConfig())
    assert result["status"] == "ERROR"
    assert "PermissionError" in result["stderr"]


def test_worker_has_no_parent_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_TEST_SECRET", "do-not-inherit")
    result = python_exec(
        "import os\nprint(os.environ.get('MATHLOTTERY_TEST_SECRET'))", tmp_path, ToolConfig()
    )
    assert result["status"] == "OK"
    assert result["stdout"].strip() == "None"


def test_experiment_cannot_rewrite_its_source_record(tmp_path):
    result = python_exec(
        "open('../experiment.py','w').write('fake source')", tmp_path, ToolConfig()
    )
    assert result["status"] == "ERROR"
    assert "fake source" in (tmp_path / "experiment.py").read_text()
    assert (tmp_path / "experiment.py").read_text().startswith("open(")


def test_timeout_and_output_limits(tmp_path):
    result = python_exec("while True: pass", tmp_path / "timeout", ToolConfig(timeout_seconds=0.2))
    assert result["status"] == "TIMEOUT"
    assert result["elapsed_seconds"] < 3
    result = python_exec(
        "while True: print('x'*1000)", tmp_path / "output", ToolConfig(max_output_chars=1000)
    )
    assert result["status"] != "OK"
    assert len(result["stdout"]) <= 1000


def test_file_tool_paths_and_symlinks_cannot_escape(tmp_path):
    root = tmp_path / "artifacts"
    root.mkdir()
    (root / "escape").symlink_to(tmp_path)
    for relative in ("../private.txt", "/etc/passwd", "escape/private.txt"):
        with pytest.raises(ValueError):
            safe_path(root, relative)


def test_tool_arguments_and_review_context_boundary(waiting, store):
    _, run = waiting
    registry = ToolRegistry(store.run_dir(run.id), ToolConfig())
    result = registry.execute(
        ToolCall(name="python_exec", arguments_json='{"code":"print(1)","shell":true}'), run, 0
    )
    assert result["result"]["status"] == "ERROR"
    run.phase = Phase.VERIFY
    for name, arguments in (
        ("search_memory", {"query": "secret"}),
        ("read_artifact", {"path": "notes.txt"}),
    ):
        result = registry.execute(ToolCall(name=name, arguments_json=json.dumps(arguments)), run, 1)
        assert result["result"]["status"] == "ERROR"
        assert "Independent review" in result["result"]["error"]


def test_erdos_parser_extracts_statement_without_promoting_status():
    html = '<title>9 | Erdős Problems</title><div class="problem-text" id="open"><div id="content">Is $P(n)$ true?</div><div id="tags">number theory</div></div><script>malicious text</script>'
    result = parse_page(html, "https://www.erdosproblems.com/9")
    problem = Problem.model_validate(result["problem"])
    assert problem.id == "erdos-9"
    assert problem.statement == "Is $P(n)$ true?"
    assert problem.status == OpenStatus.UNKNOWN
    assert "malicious text" not in result["text"]


def test_aim_links_are_resolved_without_treating_list_as_a_proof():
    result = parse_page(
        '<title>Problems</title><main><a href="/lists/a">Algebra</a></main>',
        "https://aimath.org/problemlists/",
    )
    assert result["links"][0]["url"] == "https://aimath.org/lists/a"
    assert result["problem"] is None


def test_arxiv_parses_authors_and_dates():
    xml = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/1234.5678</id><title>A theorem</title><author><name>A. Researcher</name></author><published>2025-01-01</published><summary>Partial result.</summary></entry></feed>'
    result = parse_arxiv(xml)[0]
    assert result["authors"] == ["A. Researcher"]
    assert result["published_at"] == "2025-01-01"
    assert result["url"].startswith("https://")
    assert result["retrieved_at"]


def test_open_status_is_not_established_by_two_fresh_urls():
    source, paper = "https://www.erdosproblems.com/9", "https://arxiv.org/abs/1234.5678"
    problem = Problem(
        id="test",
        title="Test",
        statement="P",
        source_url=source,
        status=OpenStatus.OPEN,
        status_evidence=[source, paper],
    )
    assert conservative_status(problem, []).status == OpenStatus.UNKNOWN
    first = {"status": "OK", "url": source, "retrieved_at": now()}
    assert conservative_status(problem, [first]).status == OpenStatus.UNKNOWN
    second = {"status": "OK", "results": [{"url": paper, "retrieved_at": now()}]}
    checked = conservative_status(problem, [first, second])
    assert checked.status == OpenStatus.UNKNOWN
    assert checked.evidence_assessment.reasons
    assert checked.status_checked_at
    first["retrieved_at"] = "2020-01-01T00:00:00+00:00"
    assert conservative_status(problem, [first, second]).status == OpenStatus.UNKNOWN


def test_problem_source_deduplication(store):
    a = Problem(id="one", title="One", statement="P", source_url="https://example.org/problem")
    b = a.model_copy(update={"id": "two"})
    store.save_problem(a)
    b = store.save_problem(b)
    assert b.id == a.id
    assert len(store.list_problems()) == 1


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://127.0.0.1/",
        "https://u:p@example.org/",
        "http://example.org:8080/",
    ],
)
def test_public_url_validation(url):
    with pytest.raises(ValueError):
        public_url(url)


def test_private_dns_result_is_blocked(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **kw: [(2, 1, 6, "", ("10.0.0.1", 443))])
    with pytest.raises(ValueError, match="Private"):
        public_url("https://example.org/")


def test_network_failure_is_a_recorded_tool_error(waiting, store, monkeypatch):
    _, run = waiting

    def unavailable(*args, **kwargs):
        raise httpx.ConnectError("Offline")

    monkeypatch.setattr(WebTools, "_request", unavailable)
    registry = ToolRegistry(store.run_dir(run.id), ToolConfig())
    result = registry.execute(
        ToolCall(name="web_search", arguments_json='{"query":"number theory"}'), run, 0
    )
    assert result["result"]["status"] == "ERROR"
    assert (store.run_dir(run.id) / result["artifact"]).exists()


@pytest.mark.parametrize(
    "proof", ["by sorry", "by admit", "by exact sorryAx _ true", "by\n axiom fake : False"]
)
def test_lean_placeholders_never_pass(tmp_path, proof):
    result = lean_check(proof, "True", tmp_path, ToolConfig())
    assert result["status"] in {"REJECTED", "UNAVAILABLE"}
    assert result["status"] != "KERNEL_CHECKED"


def test_lean_unavailable_or_unpinned_is_not_success(tmp_path):
    config = ToolConfig(lean_command="/nonexistent/lean")
    assert lean_check("by trivial", "True", tmp_path, config)["status"] == "UNAVAILABLE"
    assert lean_check("by trivial", None, tmp_path, config)["status"] == "UNAVAILABLE"
