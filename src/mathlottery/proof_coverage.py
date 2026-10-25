"""Check declared proof dependencies and evidence bindings, not mathematical truth."""

from collections import Counter

from mathlottery.models import Candidate, ProofCoverage, Review, now

FACETS = {"DEFINITIONS", "ASSUMPTIONS", "QUANTIFIERS", "DOMAIN", "BOUNDARY_CASES", "CONCLUSION"}


def assess_proof_coverage(candidate: Candidate, review: Review, original_statement: str | None = None) -> ProofCoverage:
    result = ProofCoverage(policy_version="proof-coverage-v1", assessed_at=now(), total_steps=len(review.proof_steps))
    steps = {step.id: step for step in review.proof_steps}
    checks = {check.id: check for check in review.checks if check.id}
    proof_reasons = []
    if not steps:
        proof_reasons.append("No declared proof steps; legacy reviews need a step-by-step reassessment")
    if len(steps) != len(review.proof_steps):
        proof_reasons.append("Duplicate proof-step IDs")
    if any(count > 1 for count in Counter(check.id for check in review.checks if check.id).values()):
        proof_reasons.append("Duplicate proof-check IDs")
    conclusions = [s for s in review.proof_steps if s.kind == "CONCLUSION" and s.essential]
    def canonical(text):
        return " ".join(text.split())

    if not any(canonical(s.statement) == canonical(candidate.claim) for s in conclusions):
        proof_reasons.append("An essential CONCLUSION step must state the exact submitted candidate claim")

    receipt = review.formal_receipt or {}
    declarations = {
        item.get("name") for item in receipt.get("declarations", []) if isinstance(item, dict)
    } if receipt.get("status") == "KERNEL_REPLAYED" and receipt.get("candidate_sha256") == candidate.sha256 else set()

    def supported_check(check_id: str) -> bool:
        check = checks.get(check_id)
        if not check or check.result != "SUPPORTED" or not check.reasoning.strip() or not check.claim.strip():
            return False
        if check.method in {"DERIVATION", "COUNTEREXAMPLE"}:
            return True
        return (check.method == "FORMAL" and bool(check.formal_declarations)
                and set(check.formal_declarations).issubset(declarations))

    def supported_bindings(check_ids: list[str]) -> bool:
        # Finite experiments can corroborate a derivation but cannot replace it.
        return any(supported_check(check_id) for check_id in check_ids) and all(
            check_id in checks and checks[check_id].result != "CONTRADICTED"
            and (not checks[check_id].blocking or (
                checks[check_id].result == "SUPPORTED"
                and (checks[check_id].method != "FORMAL" or supported_check(check_id))
            )) for check_id in check_ids
        )

    needed = {s.id for s in steps.values() if s.essential}
    pending = list(needed)
    while pending:
        node = pending.pop()
        for dependency in steps[node].dependencies:
            if dependency in steps and dependency not in needed:
                needed.add(dependency)
                pending.append(dependency)
    result.essential_steps = len(needed)
    state: dict[str, str] = {}
    cycle_nodes: set[str] = set()

    def visit(node: str, trail: list[str]) -> bool:
        if state.get(node) == "visiting":
            cycle_nodes.update(trail[trail.index(node):])
            return False
        if node in state:
            return state[node] == "supported"
        state[node] = "visiting"
        step = steps[node]
        valid = bool(step.statement.strip()) and supported_bindings(step.check_ids)
        if not any(supported_check(check_id) and canonical(checks[check_id].claim) == canonical(step.statement)
                   for check_id in step.check_ids):
            valid = False
        for check_id in step.check_ids:
            if check_id not in checks:
                proof_reasons.append(f"Step {node} references missing check {check_id}")
                valid = False
        for dependency in step.dependencies:
            if dependency not in steps:
                proof_reasons.append(f"Step {node} references missing dependency {dependency}")
                valid = False
            elif not visit(dependency, [*trail, node]):
                valid = False
        state[node] = "supported" if valid else "unresolved"
        return valid

    for node in steps:
        visit(node, [])
    if cycle_nodes:
        proof_reasons.append("Circular proof dependencies: " + ", ".join(sorted(cycle_nodes)))
    result.supported_steps = [node for node in steps if state[node] == "supported"]
    result.unresolved_steps = [node for node in steps if node in needed and state[node] != "supported"]
    if result.unresolved_steps:
        proof_reasons.append("Essential steps lack supported checks or dependencies: " + ", ".join(result.unresolved_steps))
    result.proof_complete = bool(needed) and not proof_reasons
    result.reasons = list(dict.fromkeys(proof_reasons))

    facets = [alignment.facet for alignment in review.statement_alignment]
    alignment_reasons = []
    if set(facets) != FACETS or len(facets) != len(FACETS):
        alignment_reasons.append("Statement alignment must cover definitions, assumptions, quantifiers, domain, boundary cases and conclusion exactly once")
    for alignment in review.statement_alignment:
        if (alignment.assessment != "MATCHED"
                or not all(text.strip() for text in (alignment.original, alignment.candidate, alignment.reasoning))
                or not supported_bindings(alignment.check_ids)):
            alignment_reasons.append(f"Statement facet {alignment.facet} lacks a supported matching check")
        if alignment.facet == "CONCLUSION" and (
            canonical(alignment.candidate) != canonical(candidate.claim)
            or not original_statement or canonical(alignment.original) != canonical(original_statement)
        ):
            alignment_reasons.append("CONCLUSION alignment must quote the exact original problem and submitted candidate claim")
    result.statement_aligned = not alignment_reasons
    result.reasons.extend(alignment_reasons)
    return result
