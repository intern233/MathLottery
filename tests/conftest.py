import json

import pytest

from mathlottery.config import Config
from mathlottery.providers.demo import demo_problem
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path)


@pytest.fixture
def config():
    value = Config()
    value.backend.mode = "manual"
    value.backend.execution = "structured"
    value.budget.max_wall_time_minutes = 1
    value.budget.max_iterations = 10
    value.backend.max_retries = 0
    return value


@pytest.fixture
def waiting(store, config):
    engine = Orchestrator(store)
    run = engine.create(config, demo_problem())
    return engine, engine.drive(run.id)


def response(run, **kwargs):
    return json.dumps(
        {
            "run_id": run.id,
            "task_id": run.task_id,
            "phase": run.phase,
            "action": "REASON",
            "summary": "Visible mathematical progress.",
            **kwargs,
        }
    )
