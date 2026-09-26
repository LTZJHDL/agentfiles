"""Build anonymous pairs and descriptive counts; no model calls or scoring."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


cases = {item["id"]: item for item in read("cases.json")}
runs = {}
for name in ("chat-control-1", "chat-guide-1", "chat-control-2", "chat-guide-2", "doc-original", "doc-split"):
    run = read(name + ".json")
    answers = {item["id"]: item["answer"] for item in run["answers"]}
    expected = {f"C{i}" for i in range(1, 7)} if name.startswith("chat") else {"D1", "D2"}
    assert set(answers) == expected and len(run["answers"]) == len(expected), name
    assert all(isinstance(answer, str) and answer.strip() for answer in answers.values()), name
    runs[name] = answers

specs = [(f"C{i}", f"chat-control-{rep}", f"chat-guide-{rep}", rep) for rep in (1, 2) for i in range(1, 7)]
specs += [(f"D{i}", "doc-original", "doc-split", 1) for i in (1, 2)]
rng = random.Random(20260925)
rng.shuffle(specs)
guide_on_x = [True] * 7 + [False] * 7
rng.shuffle(guide_on_x)
pairs, mapping, counts = [], [], []
markdown = ["# 匿名回复对照", "", "X/Y 位置按题交换；本文件不标明使用了哪份规范。每题背景是回答时已知的材料。", ""]
for index, ((case_id, baseline, treatment, replicate), on_x) in enumerate(zip(specs, guide_on_x), start=1):
    pair_id = f"P{index:02d}"
    x, y = (treatment, baseline) if on_x else (baseline, treatment)
    case = cases[case_id]
    pairs.append({"pair_id": pair_id, "case_id": case_id, "user": case["user"], "context": case["context"], "X": runs[x][case_id], "Y": runs[y][case_id]})
    mapping.append({"pair_id": pair_id, "case_id": case_id, "replicate": replicate, "X": x, "Y": y})
    for label, run_name in (("X", x), ("Y", y)):
        answer = runs[run_name][case_id]
        counts.append({"pair_id": pair_id, "case_id": case_id, "replicate": replicate, "label": label, "run": run_name, "non_whitespace_characters": sum(not c.isspace() for c in answer)})
    markdown += [f"## {pair_id} · {case_id}", "", case["user"], "", "已知背景：" + case["context"], "", "### X", "", runs[x][case_id], "", "### Y", "", runs[y][case_id], ""]

write("blind-pairs.json", pairs)
write("blind-pairs-reversed.json", [{**pair, "X": pair["Y"], "Y": pair["X"]} for pair in reversed(pairs)])
write("condition-map.json", mapping)
write("character-counts.json", counts)
(ROOT / "blind-comparison.md").write_text("\n".join(markdown), encoding="utf-8")
print(f"Built {len(pairs)} anonymous pairs from {len(runs)} runs; treatment appears on each side seven times.")
