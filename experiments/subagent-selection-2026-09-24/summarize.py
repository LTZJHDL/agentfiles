"""Validate and summarize the six recorded role-selection simulations."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN_IDS = ("a1", "a2", "b1", "b2", "c1", "c2")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundary", action="store_true", help="Summarize the boundary follow-up.")
    args = parser.parse_args()
    suffix = "-boundary" if args.boundary else ""
    prefix = "boundary-" if args.boundary else ""
    run_ids = tuple(run_id + suffix for run_id in RUN_IDS)
    scenarios = read_json(ROOT / "inputs" / f"{prefix}scenarios.json")
    scenario_ids = [scenario["id"] for scenario in scenarios]
    roles = {entry["name"] for entry in read_json(ROOT / "inputs" / "catalog-a.json")}
    runs = {}
    counts = {}

    for run_id in run_ids:
        result = read_json(ROOT / "runs" / f"{run_id}.json")
        assert result["run_id"] == run_id, run_id
        decisions = result["decisions"]
        assert len(decisions) == len(scenario_ids), run_id
        assert {decision["id"] for decision in decisions} == set(scenario_ids), run_id
        for decision in decisions:
            assert decision["choice"] in roles, (run_id, decision)
            assert decision["runner_up"] in roles, (run_id, decision)
            assert decision["runner_up"] != decision["choice"], (run_id, decision)
            assert decision["confidence"] in {"high", "medium", "low"}, (run_id, decision)
            assert isinstance(decision["reason"], str) and decision["reason"].strip(), run_id
        runs[run_id] = {decision["id"]: decision for decision in decisions}
        counts[run_id] = dict(Counter(decision["choice"] for decision in decisions))

    plan = read_json(ROOT / "plan.json")
    preferred = {} if args.boundary else {
        scenario_id: role
        for role, ids in plan["preferred_roles_before_results"].items()
        for scenario_id in ids
    }
    alignment = {
        run_id: sum(runs[run_id][sid]["choice"] == preferred[sid] for sid in scenario_ids)
        for run_id in run_ids
    } if preferred else None
    changes = {}
    for alternative in ("b", "c"):
        for replicate in (1, 2):
            base_id = f"a{replicate}{suffix}"
            alternative_id = f"{alternative}{replicate}{suffix}"
            changes[f"{base_id}_to_{alternative_id}"] = [
                {
                    "id": sid,
                    "before": runs[base_id][sid]["choice"],
                    "after": runs[alternative_id][sid]["choice"],
                }
                for sid in scenario_ids
                if runs[base_id][sid]["choice"] != runs[alternative_id][sid]["choice"]
            ]
    summary = {
        "scenario_count": len(scenarios),
        "run_count": len(run_ids),
        "selection_counts": counts,
        "agreement_with_parent_preferences": alignment,
        "paired_changes": changes,
        "within_condition_disagreements": {
            condition: [
                sid
                for sid in scenario_ids
                if runs[f"{condition}1{suffix}"][sid]["choice"] != runs[f"{condition}2{suffix}"][sid]["choice"]
            ]
            for condition in ("a", "b", "c")
        },
    }
    (ROOT / f"{prefix}summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (ROOT / f"{prefix}choices.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["id", "task", "parent_preference", *run_ids])
        for scenario in scenarios:
            sid = scenario["id"]
            writer.writerow([sid, scenario["task"], preferred.get(sid, ""), *[runs[run_id][sid]["choice"] for run_id in run_ids]])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
