"""Opt-in lifecycle and soft admission deadline for supervised standalone Solve."""

from mathlottery.models import Phase, Workflow


def supervised(run, config):
    return (
        run.workflow == Workflow.SOLVE and run.phase == Phase.SOLVE
        and run.execution == "native" and run.mode in {"codex", "work", "chat"}
        and config.solve.parallel_agents is not None
        and config.solve.coordination == "supervised"
    )
