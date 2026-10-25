"""Scripted CLI integration fixtures, not model-quality or sandbox evaluations."""

import json
import os
import subprocess
import sys
import threading
import time
from uuid import UUID

import pytest
from typer.testing import CliRunner

from mathlottery.backends import BackendStatus
from mathlottery.cli import app
from mathlottery.config import BackendConfig, Config
from mathlottery.demo import demo_problem
from mathlottery.models import Level, Phase, Run, State, Workflow
from mathlottery.native import NativeRunner
from mathlottery.native_backend import NativeWorkBackend
from mathlottery.orchestrator import Orchestrator
from mathlottery.storage import json_text

FAKE_NATIVE = r"""
import json, os, sys, time, uuid
from pathlib import Path
args = sys.argv[1:]
if os.environ.get('MATHLOTTERY_FAKE_ENV_LOG'):
    with Path(os.environ['MATHLOTTERY_FAKE_ENV_LOG']).open('a') as stream:
        stream.write(json.dumps({'args':args, 'home':os.environ.get('CODEX_HOME'),
            'sqlite':os.environ.get('CODEX_SQLITE_HOME'),
            'api_key_present':'OPENAI_API_KEY' in os.environ}) + '\n')
if args == ['--version']:
    print('codex-cli fake-native-tests')
elif args[-2:] == ['login', 'status']:
    print('Logged in using ChatGPT')
elif '--help' in args:
    print('--json --output-last-message --sandbox resume')
else:
    behavior = os.environ.get('MATHLOTTERY_NATIVE_FAKE', 'progress')
    prompt = sys.stdin.read()
    fields = dict(line.split(': ', 1) for line in prompt.splitlines()
                  if line.startswith(('run_id: ', 'task_id: ')))
    session = args[-2] if 'resume' in args else str(uuid.uuid4())
    if behavior == 'wrong_session':
        session = str(uuid.uuid4())
    sessions = Path(os.environ['CODEX_HOME']) / 'sessions'
    sessions.mkdir(parents=True, exist_ok=True)
    record = sessions / (session + '.jsonl')
    if not record.exists():
        record.write_text(json.dumps({'type':'event_msg','payload':{'type':'token_count',
            'info':{'total_token_usage':{'input_tokens':0,'output_tokens':0,'cached_input_tokens':0}}}}) + '\n')
    if behavior != 'missing_session':
        print(json.dumps({'type':'thread.started', 'thread_id':session}), flush=True)
    if behavior == 'slow':
        time.sleep(20)
    if behavior == 'visible_then_slow':
        for message in ('First complete lemma.', 'Second complete derivation.'):
            print(json.dumps({'type':'item.completed','item':{
                'type':'agent_message','text':message}}), flush=True)
        time.sleep(20)
    if behavior == 'rate':
        print(json.dumps({'type':'turn.failed','error':{'message':'429 usage limit'}}), flush=True)
        sys.exit(1)
    work = Path.cwd()
    count_file = work / 'fake-call-count'
    count = int(count_file.read_text()) + 1 if count_file.exists() else 1
    count_file.write_text(str(count))
    checkpoint = dict(fields, kind='progress', summary='Recorded mathematical progress')
    if behavior == 'three_tasks':
        if 'Task: FIND' in prompt:
            problem = {'id':'fixture-problem', 'title':'Fixture discovery',
                       'statement':'A scripted test question', 'selection_reason':'Test ranking'}
            checkpoint.update(kind='selection', problem=problem, shortlist=[problem])
        elif 'Task: VERIFY' in prompt:
            checkpoint.update(kind='review', review={'verdict':'INCONCLUSIVE',
                              'truth_assessment':'Unknown', 'proof_assessment':'Need more evidence'})
        else:
            checkpoint.update(kind='candidate', conclude=True,
                              candidate={'claim':'Fixture claim', 'proof':'Fixture proof'})
    elif behavior in ('lifecycle', 'partial'):
        if 'Independently review the following' in prompt:
            candidate = json.loads((work/'candidate.json').read_text())
            verdict = 'INCONCLUSIVE' if candidate['proof'] == 'candidate-1' else 'NO_ISSUES_FOUND'
            checkpoint.update(kind='review', review={
                'verdict':verdict, 'truth_assessment':'A precise claim',
                'proof_assessment':'Need another step' if verdict == 'INCONCLUSIVE' else 'No gap found',
                'issues':['Missing step'] if verdict == 'INCONCLUSIVE' else [],
                'evidence':['Independent algebra check'],
                'checks':[{'id':'algebra', 'claim':candidate['claim'], 'method':'DERIVATION',
                           'result':'SUPPORTED', 'reasoning':'Scripted algebra check, not a model evaluation'}],
                'proof_steps':[{'id':'conclusion', 'kind':'CONCLUSION', 'statement':candidate['claim'],
                                'check_ids':['algebra']}]})
        else:
            checkpoint.update(kind='candidate', conclude=behavior != 'partial',
                              candidate={'claim':'Sum of odd numbers', 'proof':f'candidate-{count}'})
    elif behavior == 'stop':
        checkpoint['kind'] = 'stop'
    elif behavior == 'malformed':
        checkpoint['task_id'] = 'stale-task'
    path = work / 'submissions' / (fields['task_id'] + '.json')
    path.parent.mkdir(exist_ok=True)
    if behavior not in ('no_milestone', 'answer_milestone'):
        path.write_text(json.dumps(checkpoint))
    answer = Path(args[args.index('--output-last-message')+1])
    answer.write_text('Full ordinary Markdown answer with mathematical derivations.\n')
    if behavior == 'answer_milestone':
        checkpoint.update(kind='candidate', conclude=True,
                          candidate={'claim':'A precise claim', 'proof':'A self-contained proof'})
        answer.write_text('Full proof\n```mathlottery\n' + json.dumps(checkpoint) + '\n```\n')
    print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':'python research.py','exit_code':0}}))
    if behavior == 'search_trace':
        print(json.dumps({'type':'item.completed','item':{'type':'web_search','action':{
            'query':'exact conjecture solution erratum'}, 'results':[{'url':'https://example.org/paper'}]}}))
    event = {'type':'turn.completed'}
    if behavior != 'no_usage':
        sessions = Path(os.environ['CODEX_HOME']) / 'sessions'
        sessions.mkdir(parents=True, exist_ok=True)
        record = sessions / (session + '.jsonl')
        previous = json.loads(record.read_text().splitlines()[-1])['payload']['info']['total_token_usage'] if record.exists() else {}
        event['usage'] = {key: previous.get(key, 0) + value for key, value in
                          {'input_tokens':19,'output_tokens':7,'cached_input_tokens':3}.items()}
        with record.open('a') as stream:
            stream.write(json.dumps({'type':'event_msg','payload':{'type':'token_count',
                         'info':{'total_token_usage':event['usage']}}}) + '\n')
    print(json.dumps(event), flush=True)
"""


@pytest.fixture
def native_config(tmp_path, monkeypatch):
    executable = tmp_path / "native-codex"
    executable.write_text(f"#!{sys.executable}\n" + FAKE_NATIVE)
    executable.chmod(0o755)
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "progress")
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "fake-codex-home"))
    config = Config()
    config.backend.mode = "work"
    config.backend.codex_command = str(executable)
    config.budget.max_wall_time_minutes = 1
    config.budget.max_iterations = 2
    return config


def commands(store, run):
    # Wall-clock file timestamps can move backwards; saved turn order is authoritative.
    root = store.run_dir(run.id)
    paths = [(root / entry["answer"]).with_name("command.json") for entry in run.native.history]
    if run.native.active_attempt:
        paths.append(root / run.native.active_attempt / "command.json")
    return [json.loads(path.read_text()) for path in dict.fromkeys(paths) if path.is_file()]


def test_native_defaults_inherit_model_and_remove_microstep_restrictions(tmp_path):
    config = BackendConfig()
    assert config.execution == "native"
    assert config.model is config.reasoning_effort is config.native_turn_timeout_seconds is None
    backend = NativeWorkBackend(config, root=tmp_path)
    backend.executable = "codex"
    cmd = backend.native_command(tmp_path, tmp_path / "workspace", None)
    assert "--model" not in cmd
    assert not any(value.startswith("model_reasoning_effort=") for value in cmd)
    assert "--ephemeral" not in cmd and "--ignore-user-config" not in cmd
    assert "--output-schema" not in cmd and "mcp_servers={}" not in cmd
    assert "features.shell_tool=true" in cmd and 'web_search="live"' in cmd
    assert 'sandbox_mode="workspace-write"' in cmd
    assert "--dangerously-bypass-approvals-and-sandbox" not in cmd
    assert "features.apps=false" not in cmd and "features.plugins=false" not in cmd
    assert not any(c.startswith(("features.multi_agent=", "features.memories=")) for c in cmd)


@pytest.mark.parametrize("enabled", [True, False])
def test_configured_capabilities_and_reviewer_memory_isolation(tmp_path, enabled):
    backend = NativeWorkBackend(BackendConfig(native_multi_agent=enabled, native_memories=enabled), root=tmp_path)
    backend.executable = "codex"
    command = backend.native_command(tmp_path, tmp_path / "workspace", None)
    assert f"features.multi_agent={str(enabled).lower()}" in command
    assert f"features.memories={str(enabled).lower()}" in command
    review = backend.native_command(tmp_path, tmp_path / "review", None, reviewer=True)
    assert "features.memories=false" in review and "features.memories=true" not in review


def test_native_search_trace_is_recorded_without_certifying_the_source(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "search_trace")
    native_config.budget.max_iterations = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    runtime = run.native.history[0]["runtime"]
    assert runtime["search_queries"] == ["exact conjecture solution erratum"]
    assert runtime["source_urls"] == ["https://example.org/paper"]
    assert any(o["tool"] == "native_search" for o in run.observations)
    assert not any(o.get("result", {}).get("record_kind") == "source_snapshot" for o in run.observations)


def test_native_resume_keeps_session_files_tools_and_usage(store, native_config):
    native_config.backend.model = "gpt-6-astra"
    native_config.backend.reasoning_effort = "max"
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and run.iteration == 2
    assert run.phase == Phase.SOLVE
    UUID(run.native.solver_session_id)
    first, second = commands(store, run)
    for command in (first, second):
        assert command[command.index("--model") + 1] == "gpt-6-astra"
        assert 'model_reasoning_effort="max"' in command
    assert "resume" not in first
    assert "resume" in second and second[-2] == run.native.solver_session_id
    assert "--last" not in second
    assert (store.run_dir(run.id) / "workspace/fake-call-count").read_text() == "2"
    assert run.usage.input_tokens == 38 and run.usage.output_tokens == 14
    assert run.native.history[-1]["runtime"]["tools_observed"] == ["command_execution"]
    assert len(list((store.run_dir(run.id) / "workspace/research-history").glob("*.md"))) == 1


def test_cumulative_codex_usage_does_not_exhaust_budget_one_turn_early(store, native_config):
    native_config.budget.max_iterations = 5
    native_config.budget.max_input_tokens = 45
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.iteration == 3 and run.usage.input_tokens == 57
    assert run.usage.output_tokens == 21 and run.usage.cached_input_tokens == 9
    assert run.native.history[-1]["runtime"]["reported_usage"]["input_tokens"] == 57
    assert run.native.history[-1]["usage"]["input_tokens"] == 19
    assert run.native.history[-1]["runtime"]["usage_scope"] == "session_cumulative_delta"
    assert "Measured input_tokens budget reached" in run.stop_reason


def test_inconclusive_review_returns_to_same_solver_then_uses_fresh_reviewer(
    store,
    native_config,
    monkeypatch,
):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "lifecycle")
    native_config.budget.max_iterations = 8
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.COMPLETED and run.iteration == 4
    assert len(run.candidates) == 2
    assert run.candidates[0].reviews[0].verdict == "INCONCLUSIVE"
    assert run.candidates[0].level == Level.CANDIDATE
    assert run.candidates[-1].level == Level.SELF_CHECKED
    history = run.native.history
    assert history[0]["session_id"] == history[2]["session_id"]
    assert len({entry["session_id"] for entry in history}) == 3
    for entry in (history[1], history[3]):
        prompt = (store.run_dir(run.id) / entry["answer"]).with_name("prompt.md").read_text()
        assert "Full ordinary Markdown" not in prompt
        assert "Independently review" in prompt


def test_interrupted_independent_checks_do_not_repeat_a_model_turn(store, native_config, monkeypatch):
    from mathlottery.candidates import CandidateStore

    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "lifecycle")
    native_config.budget.max_iterations = 8
    engine = Orchestrator(store)
    original = CandidateStore.prepare_review

    def interrupt_checks(*args):
        raise KeyboardInterrupt

    monkeypatch.setattr(CandidateStore, "prepare_review", interrupt_checks)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED
    assert run.iteration == 2 and len(run.native.history) == 1
    assert run.native.pending_result is not None
    monkeypatch.setattr(CandidateStore, "prepare_review", original)
    resumed = engine.resume(run.id)
    assert resumed.state == State.COMPLETED
    assert resumed.iteration == 4 and len(resumed.native.history) == 4
    assert len({item["task_id"] for item in resumed.native.history}) == 4


def test_passing_partial_candidate_does_not_end_research(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "partial")
    native_config.budget.max_iterations = 4
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and run.phase == Phase.SOLVE
    assert run.candidates[-1].reviews[-1].verdict == "NO_ISSUES_FOUND"


@pytest.mark.parametrize("behavior", ["malformed", "no_milestone"])
def test_incomplete_milestone_keeps_full_answer_and_continues(
    store, native_config, monkeypatch, behavior
):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", behavior)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and run.iteration == 2
    assert run.native.solver_session_id
    for entry in run.native.history:
        assert "mathematical derivations" in (store.run_dir(run.id) / entry["answer"]).read_text()
    if behavior == "malformed":
        assert "Stale" in run.native.checkpoint_error
    else:
        assert "Missing milestone" in run.native.checkpoint_error
        second = store.run_dir(run.id) / run.native.history[1]["answer"]
        assert "do not repeat completed research" in second.with_name("prompt.md").read_text()


def test_codex_explicit_answer_milestone_avoids_repeating_research(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "answer_milestone")
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED and run.iteration == 1
    assert run.candidates[0].proof == "A self-contained proof"
    assert run.native.checkpoint_error is None


def test_interrupted_turn_preserves_all_visible_work_without_accepting_a_proof(
    store, native_config, monkeypatch,
):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "visible_then_slow")
    native_config.backend.native_turn_timeout_seconds = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and not run.candidates
    entry = run.native.history[-1]
    assert entry["status"] == "INTERRUPTED" and "milestone" not in entry
    saved = (store.run_dir(run.id) / entry["answer"]).read_text()
    assert "First complete lemma." in saved and "Second complete derivation." in saved
    # Switching to another transport imports the full saved visible work, even after a timeout.
    resumed = engine.resume(run.id, mode="manual", message="Continue the two saved derivations")
    prompt = (store.run_dir(resumed.id) / resumed.prompt_path).read_text()
    assert "First complete lemma." in prompt and "Second complete derivation." in prompt


def test_manual_accepts_markdown_without_json_and_supports_steering(store):
    engine = Orchestrator(store)
    run = engine.drive(engine.create(Config(), demo_problem(), mode="manual").id)
    assert run.execution == "native" and run.state == State.WAITING_FOR_USER
    run = engine.submit(run.id, "## 引理\n\n先证明归纳步骤。$n^2 + 2n + 1 = (n+1)^2$。")
    assert run.iteration == 1 and run.usage.unknown_calls == 1
    assert run.state == State.WAITING_FOR_USER
    run = engine.resume(run.id, message="接下来检查边界情况")
    assert "接下来检查边界情况" in (store.run_dir(run.id) / run.prompt_path).read_text()


def test_invalid_manual_milestone_is_transactional(store):
    engine = Orchestrator(store)
    run = engine.drive(engine.create(Config(), demo_problem(), mode="manual").id)
    before = store.load(run.id).model_dump()
    with pytest.raises(ValueError, match="Stale"):
        engine.submit(run.id, 'An answer\n```mathlottery\n{"run_id":"other","task_id":"x"}\n```')
    assert store.load(run.id).model_dump() == before


def test_completed_native_research_can_be_extended_in_same_session(
    store, native_config, monkeypatch
):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "stop")
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.COMPLETED
    session = run.native.solver_session_id
    resumed = engine.resume(run.id, message="Investigate a generalization")
    assert resumed.state == State.COMPLETED and resumed.iteration == 2
    assert resumed.native.solver_session_id == session
    assert "resume" in commands(store, resumed)[-1]


def test_native_rate_limit_is_not_retried_or_switched(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "rate")
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.RATE_LIMITED and run.iteration == 1
    assert run.native.solver_session_id and run.usage.unknown_calls == 1
    assert run.mode == "work" and len(commands(store, run)) == 1


def test_native_unknown_usage_stops_token_limited_run(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "no_usage")
    native_config.budget.max_input_tokens = 100
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and run.iteration == 1
    assert "unknown" in run.stop_reason


def test_stop_records_native_session_before_completion(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "slow")
    engine = Orchestrator(store)
    run = engine.create(native_config, demo_problem())
    thread = threading.Thread(target=engine.drive, args=(run.id,))
    thread.start()
    deadline = time.monotonic() + 4
    while not store.load(run.id).native.solver_session_id:
        assert time.monotonic() < deadline
        time.sleep(0.02)
    engine.stop(run.id)
    thread.join(timeout=4)
    assert not thread.is_alive()
    stopped = store.load(run.id)
    assert stopped.state == State.CANCELLED and stopped.native.solver_session_id
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "stop")
    resumed = engine.resume(run.id)
    assert resumed.state == State.COMPLETED
    assert resumed.native.solver_session_id == stopped.native.solver_session_id


def test_receipt_recovery_does_not_repeat_native_model_call(store, native_config, monkeypatch):
    native_config.budget.max_iterations = 1
    original = NativeRunner.queue
    interrupted = []

    def crash_once(self, run, receipt):
        if not interrupted:
            interrupted.append(True)
            raise KeyboardInterrupt
        return original(self, run, receipt)

    monkeypatch.setattr(NativeRunner, "queue", crash_once)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.state == State.PAUSED and run.native.active_attempt
    run = engine.resume(run.id)
    assert run.iteration == 1 and len(run.native.history) == 1
    assert len(commands(store, run)) == 1
    assert run.usage.input_tokens == 19


@pytest.mark.parametrize("behavior", ["missing_session", "wrong_session"])
def test_no_silent_replacement_of_native_sessions(tmp_path, native_config, monkeypatch, behavior):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", behavior)
    backend = NativeWorkBackend(native_config.backend, root=tmp_path)
    session = "11111111-1111-4111-8111-111111111111" if behavior == "wrong_session" else None
    if session:
        folder = backend.identity.home / "sessions"
        folder.mkdir(parents=True)
        (folder / f"rollout-{session}.jsonl").write_text("{}\n")
    result = backend.invoke_native(
        "run_id: run-123456789012\ntask_id: task-example\n",
        tmp_path / "attempt",
        tmp_path / "work",
        3,
        session_id=session,
    )
    assert result.status in (BackendStatus.FAILED, BackendStatus.INTERRUPTED)
    assert "session" in result.error.lower()


def test_workspace_symlink_cannot_redirect_harness_writes(store):
    engine = Orchestrator(store)
    run = engine.create(Config(), demo_problem())
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir()
    outside = store.root / "untouched.json"
    outside.write_text("keep")
    (workspace / "problem.json").symlink_to(outside)
    run = engine.drive(run.id)
    assert run.state == State.FAILED
    assert outside.read_text() == "keep"


def test_direct_prompt_cli_and_old_checkpoint_compatibility(tmp_path):
    result = CliRunner().invoke(
        app,
        ["--root", str(tmp_path), "run", "--backend", "manual", "--prompt", "请研究一个数学问题"],
    )
    assert result.exit_code == 0, result.output
    assert "Execution: native" in result.output and "response.md" in result.output
    old = Run(id="run-123456789012", mode="work").model_dump(mode="json")
    old.pop("execution")
    old.pop("native")
    assert Run.model_validate_json(json_text(old)).execution == "structured"


def test_runtime_metadata_reports_actual_settings_only_from_matching_session(tmp_path, monkeypatch):
    backend = NativeWorkBackend(BackendConfig(), root=tmp_path)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "unrelated-home"))
    folder = backend.identity.home / "sessions"
    folder.mkdir(parents=True)
    session = "11111111-1111-4111-8111-111111111111"
    (folder / f"rollout-{session}.jsonl").write_text(
        json.dumps(
            {
                "type": "turn_context",
                "payload": {
                    "model": "actually-selected-model",
                    "effort": "high",
                    "sandbox_policy": {"type": "workspace-write"},
                    "private": "Do not copy unrelated payload fields",
                },
            }
        )
        + "\n"
    )
    runtime = backend.session_runtime(session)
    assert runtime["model"] == "actually-selected-model"
    assert runtime["reasoning_effort"] == "high"
    assert "private" not in runtime
    assert backend.session_runtime("22222222-2222-4222-8222-222222222222") == {}


def test_chat_feedback_is_imported_when_returning_to_work(store, native_config):
    native_config.budget.max_iterations = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    session = run.native.solver_session_id
    native_config.budget.max_iterations = 3
    run = engine.resume(run.id, mode="manual", config=native_config)
    assert "Full ordinary Markdown" in (store.run_dir(run.id) / run.prompt_path).read_text()
    run = engine.submit(run.id, "CHAT_ONLY_NEW_LEMMA: the boundary n=0 requires the empty sum.")
    run = engine.resume(run.id, mode="work")
    assert run.iteration == 3 and run.native.solver_session_id == session
    last = run.native.history[-1]
    prompt = (store.run_dir(run.id) / last["answer"]).with_name("prompt.md").read_text()
    assert "CHAT_ONLY_NEW_LEMMA" in prompt


def test_native_turn_limit_preserves_a_resumable_session(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "slow")
    native_config.backend.native_turn_timeout_seconds = 0.4
    engine = Orchestrator(store)
    started = time.monotonic()
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert time.monotonic() - started < 3
    assert run.state == State.PAUSED and run.native.solver_session_id
    assert run.usage.unknown_calls == 1


def test_recovery_stops_only_its_identified_orphan_process(tmp_path):
    directory = tmp_path / "attempt"
    directory.mkdir()
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(20)", str(directory / "answer.md")],
        start_new_session=True,
    )
    try:
        started = NativeWorkBackend.process_start(child.pid)
        assert started
        # A stale identity must never kill a newly reused PID.
        (directory / "process.json").write_text(json_text({"pid": child.pid, "start": "wrong"}))
        NativeWorkBackend.stop_orphan(directory)
        assert child.poll() is None
        (directory / "process.json").write_text(json_text({"pid": child.pid, "start": started}))
        NativeWorkBackend.stop_orphan(directory)
        child.wait(timeout=3)
        assert child.returncode != 0
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()


def test_new_direction_survives_recovery_of_older_completion(store, native_config, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "stop")
    original = NativeRunner.queue
    interrupted = []

    def crash_once(self, run, receipt):
        if not interrupted:
            interrupted.append(True)
            raise KeyboardInterrupt
        return original(self, run, receipt)

    monkeypatch.setattr(NativeRunner, "queue", crash_once)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, demo_problem()).id)
    assert run.native.active_attempt
    run = engine.resume(run.id, message="NEW_DIRECTION_AFTER_CRASH")
    assert run.state == State.COMPLETED and run.iteration == 2
    assert len(commands(store, run)) == 2  # Old receipt replayed; only the new direction invoked.
    path = store.run_dir(run.id) / run.native.history[-1]["answer"]
    assert "NEW_DIRECTION_AFTER_CRASH" in path.with_name("prompt.md").read_text()


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.SOLVE, Workflow.VERIFY])
def test_three_standalone_tasks_use_codex(store, native_config, monkeypatch, workflow):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "three_tasks")
    local_home = store.root / "local-codex"
    local_home.mkdir()
    credential = local_home / "auth.json"
    credential.write_text('{"fixture":"separate account"}')
    before = credential.read_bytes()
    log = store.root / "child-environments.jsonl"
    monkeypatch.setenv("CODEX_HOME", str(local_home))
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-forward")
    monkeypatch.setenv("MATHLOTTERY_FAKE_ENV_LOG", str(log))
    native_config.backend.mode = "codex"
    engine = Orchestrator(store)
    kwargs = {"workflow": workflow}
    if workflow != Workflow.FIND:
        kwargs["problem"] = demo_problem()
    if workflow == Workflow.VERIFY:
        kwargs["proof"] = "A test proof"
    run = engine.drive(engine.create(native_config, **kwargs).id)
    assert run.state == State.COMPLETED and run.iteration == 1
    assert len(commands(store, run)) == 1
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    isolated_home = store.root / ".mathlottery" / "codex-home"
    assert len(entries) == 4
    assert all(entry["home"] == str(isolated_home) for entry in entries)
    assert all(not entry["api_key_present"] for entry in entries)
    assert list((isolated_home / "sessions").glob("*.jsonl"))
    assert not (local_home / "sessions").exists()
    assert credential.read_bytes() == before
    assert os.environ["CODEX_HOME"] == str(local_home)
    assert 'cli_auth_credentials_store="file"' in commands(store, run)[0]
    if workflow == Workflow.FIND:
        assert run.shortlist[0].id == "fixture-problem"
        assert store.load_problem("fixture-problem") == run.problem
        assert not run.candidates
    elif workflow == Workflow.SOLVE:
        assert run.candidates[0].level == Level.CANDIDATE
        assert not run.candidates[0].reviews
    else:
        assert run.candidates[0].reviews[0].verdict == "INCONCLUSIVE"
        assert run.native.solver_session_id is None


def test_old_shared_session_is_not_resumed_or_copied(tmp_path, native_config, monkeypatch):
    session = "11111111-1111-4111-8111-111111111111"
    local_home = tmp_path / "local-codex"
    sessions = local_home / "sessions"
    sessions.mkdir(parents=True)
    record = sessions / f"rollout-{session}.jsonl"
    record.write_text('{"fixture":"shared session stays separate"}\n')
    before = record.read_bytes()
    monkeypatch.setenv("CODEX_HOME", str(local_home))
    backend = NativeWorkBackend(native_config.backend, root=tmp_path)
    result = backend.invoke_native(
        "Saved research", tmp_path / "attempt", tmp_path / "research", 3, session_id=session,
    )
    assert result.status == BackendStatus.UNSUPPORTED
    assert not result.invoked
    assert "isolated account" in result.error
    assert not (backend.identity.home / "sessions").exists()
    assert not (tmp_path / "attempt").exists()
    assert record.read_bytes() == before
