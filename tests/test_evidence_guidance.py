"""Prompt/schema guidance separates proof obligations from validation limits."""

import pytest

from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.models import CandidateInput, Review, Workflow
from mathlottery.native_prompts import build_native_prompt
from mathlottery.orchestrator import Orchestrator
from mathlottery.prompts import build_prompt


@pytest.mark.parametrize("native", [True, False])
def test_verify_prompt_explains_obligation_fields_without_relaxing_evidence_rules(store, native):
    config = Config()
    run = Orchestrator(store).create(config, demo_problem(), workflow=Workflow.VERIFY, proof="A proof.")
    prompt = build_native_prompt(run, 120) if native else build_prompt(run, config)
    assert "remaining_obligations only for unresolved mathematical proof" in prompt
    assert "use an empty list []" in prompt
    assert "pending or failed compilation in FORMAL checks" in prompt
    assert "blocking=true when" in prompt and "essential to accepting the proof" in prompt
    assert "gaps in literature_search.unresolved" in prompt
    assert "Never reclassify an" in prompt and "unproved mathematical step" in prompt


@pytest.mark.parametrize("native", [True, False])
def test_verify_verdict_separates_novelty_but_retains_source_dependent_math_gaps(store, native):
    config = Config()
    run = Orchestrator(store).create(config, demo_problem(), workflow=Workflow.VERIFY, proof="A proof.")
    prompt = build_native_prompt(run, 120) if native else build_prompt(run, config)
    text = " ".join(prompt.split())
    assert "verdict assesses the candidate's mathematical claim and proof" in text
    assert "used only for a novelty comparison does not by itself require INCONCLUSIVE" in text
    assert "literature_search.unresolved/obstacles and novelty_notes, not as mathematical issues" in text
    assert "This does not justify a positive proof verdict" in text
    assert "every essential step and claimed statement-alignment obligation checked" in text
    assert "original problem's meaning, a mathematical assumption or an essential proof dependency" in text
    assert "appropriate blocking check, retain unresolved statement alignment/coverage, and use INCONCLUSIVE" in text
    assert "Do not relabel a mathematical uncertainty as a novelty-only gap" in text
    assert "Old gaps otherwise continue blocking supported novelty/open-status assessments" in text
    assert "Use INCONCLUSIVE if you cannot decide." not in prompt


@pytest.mark.parametrize("model", [CandidateInput, Review])
def test_obligation_field_schema_discloses_mathematical_scope_and_empty_list(model):
    description = model.model_json_schema()["properties"]["remaining_obligations"]["description"]
    assert "mathematical proof or original-statement coverage obligations only" in description
    assert "Use [] when none remain" in description
    assert "not a sentence saying none remain" in description
