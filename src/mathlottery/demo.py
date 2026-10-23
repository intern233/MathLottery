import json

from mathlottery.backends import AgentBackend, BackendResult, BackendStatus
from mathlottery.models import Problem


def demo_problem(case="correct") -> Problem:
    examples = {
        "correct": (
            "Sum of the first n odd integers",
            "For every integer n ≥ 0, ∑_{k=1}^n (2k−1) = n².",
        ),
        "incorrect": ("Invalid cancellation", "For real numbers a = b = 1, is 2 = 1?"),
        "hidden-assumption": ("Square root and sign", "Is sqrt(x²) = x for every real number x?"),
        "finite-only": (
            "Finite testing is not a proof",
            "For every integer n ≥ 0, ∑_{k=1}^n (2k−1) = n².",
        ),
    }
    if case not in examples:
        raise ValueError("Demo case must be correct, incorrect, hidden-assumption or finite-only")
    title, statement = examples[case]
    return Problem(
        id=f"demo-{case}",
        title=title,
        statement=statement,
        educational=True,
        field="elementary mathematics",
        selection_reason="Known educational fixture",
    )


class DemoBackend(AgentBackend):
    """Scripted visible responses; actual tools are executed by the same real harness."""

    def __init__(self, case="correct"):
        self.case = case

    def capabilities(self):
        return {"automatic": True, "usage": False, "billing": "none; scripted demo"}

    def invoke(self, prompt, schema, directory, timeout, cancelled=lambda: False):
        fields = dict(
            line.split(": ", 1)
            for line in prompt.splitlines()
            if line.startswith(("run_id: ", "task_id: ", "phase: "))
        )
        context = json.loads(
            prompt.split("CONTEXT (JSON DATA):\n", 1)[1].split("\n\nRESPONSE SCHEMA:")[0]
        )
        response = {**fields, "summary": "Scripted educational demo response.", "action": "REASON"}
        phase = fields["phase"]
        problem = context.get("problem") or demo_problem(self.case).model_dump(mode="json")
        if phase == "FIND":
            response.update(action="SELECT_PROBLEM", problem=problem)
        elif phase == "SOLVE" and context.get("last_review", {}).get("verdict") == "ISSUES_FOUND":
            response.update(
                action="STOP",
                summary="The reviewer found an error; preserve the rejected candidate.",
            )
        elif not any(
            o["phase"] == phase and o["tool"] == "python_exec"
            for o in context.get("observations", [])
        ):
            code = {
                "correct": "for n in range(1001):\n    assert sum(2*k-1 for k in range(1,n+1)) == n*n\nprint('1001 finite cases passed; not a universal proof')",
                "finite-only": "for n in range(101):\n    assert sum(2*k-1 for k in range(1,n+1)) == n*n\nprint('101 finite cases passed; not a universal proof')",
                "incorrect": "a=b=1\nprint({'a_minus_b': a-b, 'two_equals_one': 2==1})",
                "hidden-assumption": "import sympy as s\nx=-1\nprint({'x': x, 'sqrt_x_squared': str(s.sqrt(x*x)), 'equal': s.sqrt(x*x)==x})",
            }[self.case]
            response.update(
                action="TEST_CASES",
                tools=[{"name": "python_exec", "arguments_json": json.dumps({"code": code})}],
            )
        elif phase == "SOLVE":
            proof = {
                "correct": "Induct on n. At n=0 the empty sum is 0. If the sum through n equals n², then adding 2(n+1)−1 gives n²+2n+1=(n+1)². Induction proves the statement for every integer n≥0.",
                "incorrect": "Let a=b=1. From a²=ab, subtract b² and factor: (a−b)(a+b)=b(a−b). Cancel a−b to obtain a+b=b, hence 2=1.",
                "hidden-assumption": "Squaring sqrt(x²) and x gives the same result x², so they must be equal.",
                "finite-only": "I checked n=0,…,100 and each case passed, so the identity holds for every n.",
            }[self.case]
            response.update(
                action="SUBMIT_CANDIDATE",
                candidate={"claim": problem["statement"], "proof": proof, "scope": "COMPLETE"},
                memory=[
                    {
                        "kind": "strategy",
                        "content": "Test small cases, then audit a precise candidate.",
                    }
                ],
            )
        else:
            good = self.case == "correct"
            issue = {
                "correct": "",
                "incorrect": "The cancellation divides by a−b=0.",
                "hidden-assumption": "Equality of squares does not determine sign; x=-1 is a counterexample.",
                "finite-only": "Testing a finite range cannot justify the universal quantifier over n.",
            }[self.case]
            response.update(
                action="REVIEW",
                review={
                    "verdict": "NO_ISSUES_FOUND" if good else "ISSUES_FOUND",
                    "truth_assessment": "Known elementary identity."
                    if good
                    else "See counterexample or proof gap.",
                    "proof_assessment": "Base case and induction step are valid."
                    if good
                    else issue,
                    "issues": [] if good else [issue],
                    "evidence": ["Explicit candidate text and recorded Python experiment."],
                    "novelty": "UNKNOWN",
                    "novelty_notes": "Educational demo, no online novelty search.",
                    "original_problem_coverage": "FULL" if good else "UNKNOWN",
                    "coverage_explanation": "The candidate has exactly the original n≥0 quantifier." if good else "",
                    "checks": [{
                        "claim": problem["statement"], "method": "DERIVATION",
                        "result": "SUPPORTED" if good else "CONTRADICTED",
                        "reasoning": "S(0)=0; S(n+1)=S(n)+2n+1=n²+2n+1=(n+1)²." if good else issue,
                        "evidence": ["Candidate proof and independently recorded calculation"],
                    }],
                },
            )
        return BackendResult(BackendStatus.COMPLETED, text=json.dumps(response, ensure_ascii=False))
