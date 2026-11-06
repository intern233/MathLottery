"""Bounded autonomous continuation while another session reviews frozen evidence."""

from mathlottery.solve.allocation import selected_workers


def pending_signals(run):
    state = run.native.solve_team.campaign
    acknowledged = set(state.acknowledged_signals)
    return [s for s in state.signals if s["task_id"] not in acknowledged]


def complete_claim_pending(run):
    return any(s["status"] == "claimed_complete" for s in pending_signals(run))


def queue_continuations(run, config):
    """Allow one extra attempt per worker ahead of review, never an unbounded retry loop.

    The current plan determines capacity/identity only. A worker chooses its own
    mathematical route and declares it on the board. No additional slots/accounts.
    """
    team, state = run.native.solve_team, run.native.solve_team.campaign
    if not state.decisions or state.closed or complete_claim_pending(run):
        return
    busy = {a["worker_id"] for a in team.active_attempts}
    pending = pending_signals(run)
    eligible = {w.id for w in team.workers.values() if w.state == "completed"
                and w.id not in busy and w.id not in state.dispatch
                and sum(s["worker_id"] == w.id for s in pending) == 1}
    if not eligible:
        return
    planned = selected_workers(run.model_copy(deep=True), config, config.solve.parallel_agents)
    for planned_worker in planned:
        identifier = planned_worker.id
        worker = team.workers.get(identifier)
        if worker is None or identifier not in eligible:
            continue
        # Preserve the active plan's capacity and the worker's pinned conversation.
        worker.group, worker.mode, worker.objective = (
            planned_worker.group, planned_worker.mode, planned_worker.objective,
        )
        state.dispatch.append(identifier)


def continuation_reason(run, worker):
    if any(s["worker_id"] == worker.id for s in pending_signals(run)):
        return "autonomous_continuation_while_review_pending"
    return "supervisor_capacity_plan"
