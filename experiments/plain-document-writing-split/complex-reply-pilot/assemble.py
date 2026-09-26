"""Make anonymous assessment packets after every generation has finished."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))
def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

runs = read("generation-manifest.json")
cases = {x["id"]:x for x in read("cases.json")}
questions = {x["id"]:x["questions"] for x in read("reader-questions.json")}
keys = {x["id"]:x["facts"] for x in read("fact-key.json")}
answers = {}
for run in runs:
    obj = read(f'answers/{run["id"]}.json')
    assert obj["id"] == run["id"] and obj["task"] == run["task"] and obj["answer"].strip()
    answers[run["id"]] = obj["answer"]
rng = random.Random(2026092502)
shuffled = runs.copy()
rng.shuffle(shuffled)
anon_map = {run["id"]:f"E{i:02d}" for i,run in enumerate(shuffled,1)}
counts = [{"run":r["id"],"answer_id":anon_map[r["id"]],"task":r["task"],"condition":r["condition"],"replicate":r["replicate"],"non_whitespace_characters":sum(not c.isspace() for c in answers[r["id"]]),"sha256":hashlib.sha256(answers[r["id"]].encode()).hexdigest()} for r in runs]
write("answer-map.json",counts)
grouped = {(t,rep):{r["condition"]:r for r in runs if r["task"] == t and r["replicate"] == rep} for t in cases for rep in (1,2)}
groups = list(grouped.items())
rng.shuffle(groups)
sides = [True]*3 + [False]*3
rng.shuffle(sides)
pairs, mapping, md = [], [], ["# 复杂回复匿名对照", "", "X/Y 按题交换；这里不显示哪份答案使用了规范。", ""]
for i, (((task, rep), group), guide_x) in enumerate(zip(groups,sides),1):
    x,y = (group["G"],group["C"]) if guide_x else (group["C"],group["G"])
    pid = f"P{i:02d}"
    pairs.append({"pair_id":pid,"task":task,"user":cases[task]["user"],"questions":questions[task],"X":answers[x["id"]],"Y":answers[y["id"]]})
    mapping.append({"pair_id":pid,"task":task,"replicate":rep,"X":x["id"],"Y":y["id"]})
    md += [f"## {pid} · {cases[task]['title']}", "", cases[task]["user"], "", "### X", "", answers[x["id"]], "", "### Y", "", answers[y["id"]], ""]
write("blind-pairs.json",pairs)
write("blind-pairs-reversed.json",[{**p,"X":p["Y"],"Y":p["X"]} for p in reversed(pairs)])
write("pair-map.json",mapping)
(ROOT/"blind-comparison.md").write_text("\n".join(md),encoding="utf-8")
for task in cases:
    selected = [r for r in shuffled if r["task"]==task]
    write(f"facts-{task}.json",{"task":task,"user":cases[task]["user"],"material":(ROOT/cases[task]["material"]).read_text(encoding="utf-8"),"facts":keys[task],"answers":[{"answer_id":anon_map[r["id"]],"answer":answers[r["id"]]} for r in selected]})
reader_groups = [[] for _ in range(4)]
for task_index, task in enumerate(cases):
    selected = [next(r for r in runs if r["task"]==task and r["condition"]==condition and r["replicate"]==replicate) for condition,replicate in (("C",1),("G",1),("C",2),("G",2))]
    selected = selected[task_index:] + selected[:task_index]
    for index,run in enumerate(selected):
        reader_groups[index].append({"answer_id":anon_map[run["id"]],"task":task,"user":cases[task]["user"],"answer":answers[run["id"]],"questions":questions[task]})
for i,group in enumerate(reader_groups,1):
    write(f"reader-packet-{i}.json",group)
print("12 answers validated; 6 balanced pairs; 3 fact packets; 4 disjoint reader packets.")
