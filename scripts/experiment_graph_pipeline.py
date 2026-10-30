"""Bounded real-model reproduction; uses configured credentials and model allowance."""

import argparse
from pathlib import Path

from mathlottery.config import load_config
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import Store

SOURCE = "https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357"
REQUEST = (
    "This is a bounded reproducibility experiment on published graph conjectures. "
    "Read Some properties of stepwise irregular graphs by Bera, Paul and Subramanian. "
    "Select one precise conjecture suitable for a short, elementary proof or counterexample, "
    "preferably the degree-sequence sufficiency question. Check the primary statement and "
    "any later resolution you can find; use UNKNOWN for current open status when not established. "
    "Do not read MathLottery showcases, prior experiments, or files outside this workspace. "
    "The subsequent solver should give a self-contained proof/counterexample with a small "
    "reproducible certificate when possible. This is an integration test, not a novelty claim. "
    "Keep discovery concise so the solve and independent review stages have time remaining."
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--root", type=Path, default=Path(".mathlottery/experiments/graph-pipeline"))
    parser.add_argument("--minutes", type=float, default=12)
    args = parser.parse_args()
    config = load_config(Path.cwd(), args.config)
    config.budget.max_wall_time_minutes = args.minutes
    config.budget.max_iterations = 8
    engine = Orchestrator(Store(args.root))
    run = engine.create(config, source=SOURCE, discovery_request=REQUEST, discovery_count=1)
    print(f"Run: {run.id}\nRoot: {args.root}\nBudget: {args.minutes} minutes", flush=True)
    run = engine.drive(run.id)
    print(f"State: {run.state}\nReason: {run.stop_reason}")
    print(f"Report: {engine.store.run_dir(run.id) / 'report.md'}")


if __name__ == "__main__":
    main()
