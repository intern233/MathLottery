"""Independent limits on active groups and their combined researcher count."""

import pytest
from test_solve_team import TeamBackend, problem
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.config import Config, SolveConfig
from mathlottery.models import State, Workflow
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.service import Overrides, ResumeRequest, StartRequest, WebService


def group_config(parallel=4, groups=2, calls=3):
    config = Config()
    config.solve = SolveConfig(coordination="allocation", parallel_agents=parallel, max_groups=groups)
    config.budget.max_iterations = calls
    config.budget.finalize_minutes = 0
    return config


@pytest.mark.parametrize("value", [0, -1, 33, True, 2.5, "2"])
def test_group_limits_reject_noninteger_and_out_of_range_values(value):
    with pytest.raises(ValueError):
        SolveConfig(parallel_agents=4, max_groups=value)
    with pytest.raises(ValueError):
        Overrides(solve_max_groups=value)
    with pytest.raises(ValueError):
        ResumeRequest(solve_max_groups=value)


def test_group_limit_requires_managed_researcher_parallelism():
    original = Config()
    with pytest.raises(ValueError, match="solve.parallel_agents"):
        Config.model_validate({"solve": {"max_groups": 2}})
    with pytest.raises(ValueError, match="solve.parallel_agents"):
        Overrides(solve_max_groups=2).apply(original)
    assert original.solve.max_groups is None and original.solve.parallel_agents is None
    # Older configurations have no extra group cap; groups still need an agent each.
    legacy = Config.model_validate({"solve": {"parallel_agents": 4}})
    assert legacy.solve.max_groups is None and legacy.solve.group_limit == 4
    assert SolveConfig(parallel_agents=2, max_groups=8).group_limit == 2


def test_one_group_can_use_multiple_researcher_slots(store):
    backend = TeamBackend(synchronize=True)
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(group_config(parallel=2, groups=1), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.peak == 2 and len(run.native.solve_team.groups) == 1
    assert run.native.solve_team.groups[0].agents == 2
    assert len(run.candidates) == 2
    prompt = backend.calls[0]["prompt"]
    assert "Maximum simultaneous Solve researchers: 2" in prompt
    assert "Maximum simultaneous research groups: 1" in prompt
    detail = WebService(store.root).detail(run.id)["solve_team"]
    assert detail["max_groups"] == detail["effective_max_groups"] == 1


def test_supervisor_cannot_exceed_group_limit_even_below_agent_limit(store):
    backend = TeamBackend(plans=[[
        {"id": f"route-{i}", "agents": 1, "objective": f"Route {i}"} for i in range(3)
    ]])
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(group_config(parallel=4, groups=2), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED, run.last_error
    assert "maximum research groups" in run.native.solve_team.decision
    assert len(run.native.solve_team.groups) == 1 and len(backend.calls) == 2


@pytest.mark.parametrize("planning_failure", ["oversized", "timeout"])
def test_lower_group_cap_on_resume_clamps_old_plan_and_retains_inactive_sessions(store, planning_failure):
    groups = [{"id": name, "agents": 1, "objective": name} for name in ["route-a", "route-b"]]

    class ResumeBackend(TeamBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if planning_failure == "timeout" and self.planning and "resource supervision" in prompt:
                self.planning += 1
                return BackendResult(BackendStatus.INTERRUPTED, invoked=True,
                                     usage={"input_tokens": 1, "output_tokens": 1}, error="Planning timed out")
            return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)

    backend = ResumeBackend(complete=False, plans=[groups, groups])
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(group_config(), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.PAUSED and len(run.native.solve_team.groups) == 2
    peer = run.native.solve_team.workers["route-b-1"]
    saved_session, saved_turns = peer.session_id, peer.turns
    config = Config.model_validate(run.config)
    config.solve.max_groups = 1
    config.budget.max_iterations = 5
    resumed = engine.resume(run.id, config=config)
    assert resumed.state == State.PAUSED and resumed.iteration == 5
    assert len(resumed.native.solve_team.groups) == 1
    inactive = resumed.native.solve_team.workers["route-b-1"]
    assert (inactive.session_id, inactive.turns) == (saved_session, saved_turns)
    researchers = [c for c in backend.calls if not c["supervisor"]]
    assert len(researchers) == 3
    assert researchers[-1]["workspace"].name == "workspace"
    assert researchers[-1]["session"] == "session-workspace"


def test_web_start_and_resume_preserve_or_override_group_limit_per_task(store, monkeypatch):
    web = WebService(store.root)
    monkeypatch.setattr(web, "config", Config)
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launches.append((args, kwargs)))
    created = web.start(StartRequest(workflow="solve", statement=problem().statement,
                                    options=Overrides(solve_parallel_agents=6, solve_max_groups=2)))
    assert created["settings"]["solve_max_groups"] == 2
    web.resume(created["id"], ResumeRequest())
    assert launches[-1][1]["config"]["solve"]["max_groups"] == 2
    web.resume(created["id"], ResumeRequest(solve_max_groups=1))
    assert launches[-1][1]["config"]["solve"]["max_groups"] == 1
    assert launches[-1][1]["config"]["solve"]["parallel_agents"] == 6
    assert store.load(created["id"]).config["solve"]["max_groups"] == 2
    with pytest.raises(ValueError, match="only to Solve"):
        web.start(StartRequest(workflow="find", options=Overrides(solve_max_groups=2)))
    found = Orchestrator(store).create(Config(), workflow=Workflow.FIND)
    with pytest.raises(ValueError, match="only to Solve"):
        web.resume(found.id, ResumeRequest(solve_max_groups=1))


def test_cli_start_and_resume_pass_both_limits_to_execution(store, monkeypatch):
    backend = TeamBackend(complete=False)
    (store.root / "config.yaml").write_text("solve:\n  coordination: allocation\n")

    def factory(*args):
        return Orchestrator(store, backend)

    monkeypatch.setattr("mathlottery.cli.common.Orchestrator", factory)
    monkeypatch.setattr("mathlottery.cli.tasks.Orchestrator", factory)
    cli = CliRunner()
    prefix = ["--root", str(store.root)]
    started = cli.invoke(app, prefix + ["solve", "--prompt", problem().statement,
                        "--parallel-agents", "4", "--max-groups", "2", "--max-iterations", "3"])
    assert started.exit_code == 0, started.output
    run = store.list_runs()[0]
    assert run.config["solve"]["max_groups"] == 2
    resumed = cli.invoke(app, prefix + ["resume", run.id, "--parallel-agents", "2",
                                       "--max-groups", "1", "--max-iterations", "6"])
    assert resumed.exit_code == 0, resumed.output
    saved = store.load(run.id)
    assert saved.config["solve"]["parallel_agents"] == 2
    assert saved.config["solve"]["max_groups"] == 1 and saved.iteration == 6
    rejected = cli.invoke(app, prefix + ["solve", "--prompt", problem().statement, "--max-groups", "2"])
    assert rejected.exit_code == 2 and "solve.parallel_agents" in rejected.output
    assert len(store.list_runs()) == 1
