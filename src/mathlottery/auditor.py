from mathlottery.models import Candidate, Level, Review, digest


def audit(candidate: Candidate, review: Review, observations: list[dict]) -> Candidate:
    if candidate.sha256 != digest(candidate.claim + "\n" + candidate.proof):
        raise ValueError("Candidate integrity check failed; proof or claim was modified")
    candidate = candidate.model_copy(deep=True)
    current = [o for o in observations if o.get("phase") == "VERIFY"]
    retrieved = {
        r["url"]
        for o in current
        if o.get("result", {}).get("status") == "OK"
        for r in [o["result"], *o["result"].get("results", [])]
        if r.get("url")
    }
    if not any(ref.url in retrieved for ref in review.novelty_references):
        review = review.model_copy(update={"novelty": "UNKNOWN"})
    candidate.reviews.append(review)
    candidate.evidence.extend(o["artifact"] for o in current if o.get("artifact"))
    if review.verdict == "ISSUES_FOUND" and review.issues and review.evidence:
        candidate.level = Level.REJECTED
    elif review.verdict == "NO_ISSUES_FOUND":
        candidate.level = Level.SELF_CHECKED
        if any(
            o.get("tool") == "lean_check" and o.get("result", {}).get("status") == "KERNEL_CHECKED"
            for o in current
        ):
            # Kernel-only checks are not the full formal verification trust policy.
            candidate.level = Level.PARTIALLY_VERIFIED
    return candidate
