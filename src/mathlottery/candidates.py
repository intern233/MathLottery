"""Immutable candidate content and review projections, shared by both runners."""

from mathlottery.auditor import audit
from mathlottery.literature import collect_sources
from mathlottery.models import Candidate, CandidateInput, Review, Run, digest, uid
from mathlottery.native_formal import record_formal_check
from mathlottery.storage import Store, atomic_write, json_text, safe_path


def review_input(candidate: Candidate) -> dict:
    """A reviewer receives evidence to assess, without previous verdicts or solver history."""
    return candidate.model_dump(
        mode="json", include=set(CandidateInput.model_fields) | {"id", "sha256"}
    )


class CandidateStore:
    def __init__(self, store: Store):
        self.store = store

    def path(self, run: Run, candidate: Candidate):
        return safe_path(self.store.run_dir(run.id), f"candidates/{candidate.id}.json")

    def add(self, run: Run, content: CandidateInput) -> Candidate:
        candidate = Candidate(
            **content.model_dump(),
            id=uid("candidate"),
            # Preserve the historical checksum format for old checkpoints and imports.
            sha256=digest(content.claim + "\n" + content.proof),
            source_iteration=run.iteration,
        )
        path = self.path(run, candidate)
        if path.exists():
            raise ValueError("Candidate versions are immutable")
        atomic_write(path, json_text(candidate))
        run.candidates.append(candidate)
        return candidate

    def check(self, run: Run) -> Candidate:
        candidate = run.candidates[-1]
        original = Candidate.model_validate_json(self.path(run, candidate).read_text())
        immutable = set(CandidateInput.model_fields) | {"id", "sha256", "source_iteration"}
        if (
            original.model_dump(include=immutable) != candidate.model_dump(include=immutable)
            or digest(candidate.claim + "\n" + candidate.proof) != candidate.sha256
        ):
            raise ValueError("Candidate artifact was modified; refusing verification")
        return candidate

    @staticmethod
    def observations(run: Run) -> list[dict]:
        return [o for o in run.observations if o["iteration"] > run.candidates[-1].source_iteration]

    def prepare_review(self, run: Run, review: Review) -> None:
        self.check(run)
        collect_sources(self.store, run, review.citations)
        record_formal_check(self.store, run, review.formal_check)

    def review(self, run: Run, review: Review, extra_observations=(), *, prepared=False) -> Candidate:
        if not prepared:
            self.prepare_review(run, review)
        candidate = audit(
            self.check(run), review, self.observations(run) + list(extra_observations),
            prior_literature=([run.problem.literature_search] if run.problem else []) + run.review_literature,
            prior_assessments=[run.problem.evidence_assessment] if run.problem else [],
            original_statement=run.problem.statement if run.problem else None,
        )
        run.candidates[-1] = candidate
        atomic_write(
            safe_path(self.store.run_dir(run.id), f"verification/{candidate.id}.json"),
            json_text(candidate),
        )
        return candidate
