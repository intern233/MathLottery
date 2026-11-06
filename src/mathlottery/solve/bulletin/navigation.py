"""Small, stdlib-only graph queries, shared with the isolated native board client."""

import hashlib
import re
import unicodedata


def terms(text):
    """Normalize spelling/punctuation only; never claim mathematical canonicalization."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    tokens = set(re.findall(r"[^\W_]+", normalized))
    stop = {"the", "a", "an", "and", "or", "of", "for", "to", "in", "is", "on", "with", "by"}
    return {t for t in tokens if len(t) > 1 and t not in stop}


def archive_path(key):
    return f"bulletin/archive/messages/{hashlib.sha256(key.encode()).hexdigest()}.json"


def card(value):
    theorem = value.get("theorem") or {}
    return {
        **{key: value[key] for key in (
            "key", "title", "author", "group", "kind", "time", "standing", "check_status",
            "content_sha256", "depends_on", "assumptions", "archived", "usage",
        )},
        "statement": theorem.get("statement"),
        "remaining_obligations": theorem.get("remaining_obligations", []),
        "proof_step_count": len(theorem.get("proof_steps", [])),
        "review_id": (value.get("supervisor_review") or {}).get("id"),
        "curation_id": (value.get("curation") or {}).get("id"),
        "target": value.get("target"),
        "tags": value.get("tags", []), "aliases": value.get("aliases", []),
        "path": archive_path(value["key"]),
    }


def graph(cards, include_archived=False):
    visible = {c["key"] for c in cards if include_archived or not c["archived"]}
    # If later work reuses an archived premise, retain an explicit archived stub.
    by_key = {c["key"]: c for c in cards}
    pending = list(visible)
    while pending:
        value = by_key[pending.pop()]
        related = value["depends_on"] + ([value["target"]] if value.get("target") else [])
        for key in related:
            if key not in visible:
                visible.add(key)
                pending.append(key)
    nodes = [c for c in cards if c["key"] in visible]
    return {
        "nodes": nodes,
        "edges": [{"from": dep, "to": c["key"], "kind": "premise", "proof_path": c["path"]}
                  for c in nodes for dep in c["depends_on"]],
        "annotations": [{"from": c["key"], "to": c["target"], "kind": c["kind"], "path": c["path"]}
                        for c in nodes if c.get("target")],
        "archived_count": sum(c["archived"] for c in cards),
        "note": "Prerequisites → conclusions. Edges are declared dependencies, not certified deductions. "
                "Open path for full proof steps and materials; archive state never changes proof standing.",
    }


def search(cards, query, offset=0, include_archived=False):
    if type(offset) is not int or offset < 0:
        raise ValueError("Offset must be a nonnegative integer")
    words = terms(str(query))
    phrase = unicodedata.normalize("NFKC", str(query)).casefold().strip()
    ranked = []
    for value in cards:
        if value["archived"] and not include_archived:
            continue
        haystack = " ".join([value["key"], value["title"], value.get("statement") or "",
                             *value.get("assumptions", []), *value.get("tags", []),
                             *value.get("aliases", [])])
        normalized = unicodedata.normalize("NFKC", haystack).casefold()
        score = len(words & terms(haystack)) + (3 if phrase and phrase in normalized else 0)
        if not phrase or score:
            ranked.append((score, value))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("standing") != "supervisor_accepted"))
    return {"total": len(ranked), "next_offset": offset + 20 if offset + 20 < len(ranked) else None,
            "messages": [v for _, v in ranked[offset:offset + 20]],
            "search_scope": "titles, exact statements, assumptions, tags and aliases; "
                            "normalized lexical retrieval, not mathematical equivalence"}


def explore(cards, key, direction="both", depth=1):
    if direction not in {"premises", "consequences", "both"}:
        raise ValueError("Direction must be premises, consequences or both")
    if type(depth) is not int or not 0 <= depth <= 8:
        raise ValueError("Depth must be an integer between 0 and 8")
    if key not in {c["key"] for c in cards}:
        raise ValueError("No such message in this run")
    full = graph(cards, include_archived=True)
    chosen, frontier = {key}, {key}
    for _ in range(depth):
        found = set()
        for edge in full["edges"]:
            if direction in {"premises", "both"} and edge["to"] in frontier:
                found.add(edge["from"])
            if direction in {"consequences", "both"} and edge["from"] in frontier:
                found.add(edge["to"])
        frontier = found - chosen
        chosen |= found
    truncated = len(chosen) > 200
    if truncated:
        chosen = {key, *sorted(chosen - {key})[:199]}
    return {"nodes": [c for c in cards if c["key"] in chosen],
            "edges": [e for e in full["edges"] if {e["from"], e["to"]} <= chosen],
            "annotations": [e for e in full["annotations"] if e["to"] in chosen or e["from"] in chosen],
            "truncated": truncated, "depth": depth, "direction": direction}
