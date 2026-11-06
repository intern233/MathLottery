"""Per-researcher coordination views: voluntary invitations and advisory overlap hints."""

from mathlottery.solve.bulletin import events, navigation


def view(board, actor, *, run=None):
    ledger = events.rows(board)
    agents = events.registry(board, run, ledger)
    invitations, unread = [], []
    channels = events.channels(ledger)
    for channel in channels:
        if channel["closed"]:
            continue
        response = channel["responses"].get(actor, "pending")
        if actor in channel["invitees"] and response in {"pending", "deferred"}:
            invitations.append({"channel": channel["key"], "from": channel["creator"],
                                "purpose": channel["purpose"], "status": response})
        if actor not in {*channel["members"], *channel["invitees"]} or response in {"declined", "left"}:
            continue
        keys = [e["key"] for e in channel["events"]]
        seen = channel["read_through"].get(actor)
        start = keys.index(seen) + 1 if seen in keys else 0
        messages = [e for e in channel["events"][start:]
                    if e["actor"] != actor and e["action"] in {"channel_open", "channel_message"}]
        if messages:
            unread.append({"channel": channel["key"], "purpose": channel["purpose"],
                           "count": len(messages), "last_event": messages[-1]["key"]})
    current = next((a["report"] for a in agents if a["actor"] == actor and a["report_current"]), None)
    own_terms = navigation.terms(" ".join(current.get(k, "") for k in ("topic", "summary"))) if current else set()
    overlaps = []
    for peer in agents:
        if peer["actor"] == actor or not peer["report_current"]:
            continue
        report = peer["report"]
        if report["status"] not in {"working", "seeking_help"}:
            continue
        shared = sorted(own_terms & navigation.terms(" ".join(report.get(k, "") for k in ("topic", "summary"))))
        same_focus = sorted(set((current or {}).get("focus", [])) & set(report["focus"]))
        topic = (current or {}).get("topic", "").strip().casefold()
        same_topic = len(topic) >= 2 and topic == report.get("topic", "").strip().casefold()
        if len(shared) >= 2 or same_focus or same_topic:
            overlaps.append({"actor": peer["actor"], "topic": report.get("topic"),
                             "summary": report["summary"], "approach": report.get("approach"),
                             "intent": report.get("intent"), "shared_terms": shared,
                             "shared_focus": same_focus, "same_topic": same_topic, "time": report["time"]})
    query = " ".join((current or {}).get(k, "") for k in ("topic", "summary"))
    related = navigation.search(board.cards(), query, include_archived=True)["messages"] if query else []
    related_channels = [
        {"channel": c["key"], "purpose": c["purpose"], "members": c["members"]}
        for c in channels if not c["closed"] and (
            len(own_terms & navigation.terms(c["purpose"])) >= 2
            or set((current or {}).get("focus", [])) & set(c["focus"]))
    ]
    return {
        "actor": actor, "invitations": invitations[:30], "unread_channels": unread[:30],
        "invitation_count": len(invitations), "unread_channel_count": len(unread),
        "possible_overlaps": overlaps[:30], "overlap_count": len(overlaps),
        "related_results": [c for c in related if c["author"] != actor][:5],
        "related_channels": related_channels[:10],
        "note": "Hints only, not mathematical equivalence or exclusive task ownership. "
                "Choose your own route; collaborate, extend a result, or record why independent checking helps. "
                "Reading this inbox does not accept invitations or acknowledge channel messages.",
    }
