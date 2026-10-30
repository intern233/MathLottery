import pytest

from mathlottery.telemetry.search import queries_from_call


def test_mcp_search_queries_come_from_completed_inputs_not_output():
    item = {"type": "mcp_tool_call", "tool": "literature_search", "status": "completed",
            "arguments": {"query": "exact conjecture later solution"},
            "result": {"content": [{"text": "I searched for fabricated-query"}]}}
    assert queries_from_call(item) == {"exact conjecture later solution"}


def test_chat_mcp_and_batched_queries():
    assert queries_from_call({"type": "mcp_call", "name": "search", "status": "completed",
                              "arguments": '{"search_query":[{"q":"conjecture erratum"},{"q":"equivalent theorem"}]}'}) == {"conjecture erratum", "equivalent theorem"}


@pytest.mark.parametrize("changes", [
    {"status": "failed"}, {"status": "in_progress"}, {"error": "failed"},
    {"result": {"isError": True}}, {"tool": "write_note"}, {"arguments": "malformed"},
    {"type": "agent_message"},
])
def test_nonsearch_or_failed_calls_do_not_establish_search(changes):
    item = {"type": "mcp_tool_call", "tool": "search", "status": "completed", "arguments": {"query": "q"}}
    assert queries_from_call(item | changes) == set()
