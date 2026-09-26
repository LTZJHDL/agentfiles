"""Reveal conditions after review; retain both reviewers' judgments separately."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


mapping = {item["pair_id"]: item for item in read("condition-map.json")}
normalized = []
for reviewer in (1, 2):
    rows = read(f"blind-review-{reviewer}.json")
    assert len(rows) == len(mapping) and {r["pair_id"] for r in rows} == set(mapping)
    for row in rows:
        info = mapping[row["pair_id"]]
        run_for_label = {"X": info["X"], "Y": info["Y"]}
        if reviewer == 2:
            run_for_label = {"X": info["Y"], "Y": info["X"]}
        normalized_row = {**row, "reviewer": reviewer, "case_id": info["case_id"], "replicate": info["replicate"]}
        for metric in ("readability_preference", "overall_preference"):
            choice = row[metric]
            assert choice in ("X", "Y", "tie")
            normalized_row[metric + "_run"] = "tie" if choice == "tie" else run_for_label[choice]
        normalized_row["run_for_label"] = run_for_label
        normalized.append(normalized_row)

totals = {}
for reviewer in (1, 2):
    totals[reviewer] = {}
    for kind in ("C", "D"):
        totals[reviewer][kind] = {}
        subset = [row for row in normalized if row["reviewer"] == reviewer and row["case_id"].startswith(kind)]
        for metric in ("readability_preference", "overall_preference"):
            winners = []
            for row in subset:
                run_name = row[metric + "_run"]
                winners.append("tie" if run_name == "tie" else "additional-guide-or-split" if "guide" in run_name or "split" in run_name else "control-or-original")
            totals[reviewer][kind][metric] = dict(Counter(winners))

result = {"totals": totals, "reviews": normalized}
(ROOT / "review-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(totals, ensure_ascii=False, indent=2))
for row in sorted(normalized, key=lambda row: (row["case_id"], row["replicate"], row["reviewer"])):
    print(row["pair_id"], row["case_id"], f'rep={row["replicate"]}', f'reviewer={row["reviewer"]}', row["overall_preference_run"], row["materiality"], row["reason"])
