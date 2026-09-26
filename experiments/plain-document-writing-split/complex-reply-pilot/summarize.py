"""Normalize blinded labels and retain separate factual, reading and extraction results."""
import json
import sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8-sig"))
runs={x["id"]:x for x in read("generation-manifest.json")}
answers={x["answer_id"]:x for x in read("answer-map.json")}
pairs={x["pair_id"]:x for x in read("pair-map.json")}
normalized=[]
for reviewer in (1,2):
    rows=read(f"readability-review-{reviewer}.json")
    assert len(rows)==6 and {x["pair_id"] for x in rows}==set(pairs)
    for row in rows:
        pair=pairs[row["pair_id"]]
        mapping={"X":pair["X"],"Y":pair["Y"]}
        if reviewer==2: mapping={"X":pair["Y"],"Y":pair["X"]}
        def resolve(choice):
            assert choice in ("X","Y","tie"), choice
            return "tie" if choice=="tie" else runs[mapping[choice]]["condition"]
        normalized.append({**row,"reviewer":reviewer,"task":pair["task"],"replicate":pair["replicate"],"run_for_label":mapping,"winner_condition":resolve(row["overall_preference"]),"dimension_conditions":{name:resolve(value["preference"]) for name,value in row["dimensions"].items()}})
facts=[]
for task in ("T1","T2","T3"):
    rows=read(f"fact-review-{task}.json")
    assert len(rows)==4 and len({x["answer_id"] for x in rows})==4
    for row in rows:
        info=answers[row["answer_id"]]
        assert info["task"]==task
        facts.append({**row,"run":info["run"],"task":task,"condition":info["condition"],"replicate":info["replicate"]})
readers=[]
for index in range(1,5):
    rows=read(f"reader-results-{index}.json")
    assert len(rows)==3
    for row in rows:
        info=answers[row["answer_id"]]
        assert row["task"]==info["task"] and len(row["questions"])==4
        readers.append({**row,"reader":index,"run":info["run"],"condition":info["condition"],"replicate":info["replicate"]})
assert len({r["answer_id"] for r in readers})==12
totals={str(i):dict(Counter(r["winner_condition"] for r in normalized if r["reviewer"]==i)) for i in (1,2)}
characters={c:sum(a["non_whitespace_characters"] for a in answers.values() if a["condition"]==c) for c in ("C","G")}
result={"overall_preferences":totals,"characters":characters,"readability":normalized,"facts":facts,"readers":readers}
(ROOT/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"overall_preferences":totals,"characters":characters},ensure_ascii=False,indent=2))
for row in sorted(normalized,key=lambda x:(x["task"],x["replicate"],x["reviewer"])):
    print(row["pair_id"],row["task"],row["replicate"],"judge",row["reviewer"],row["winner_condition"],row["materiality"],row["reason"])
for row in facts:
    issues=[f for f in row["facts"] if f["impact"]!="none"]+row["other_issues"]
    if issues: print("FACT",row["run"],row["condition"],json.dumps(issues,ensure_ascii=False))
for condition in ("C","G"):
    questions=[q for r in readers if r["condition"]==condition for q in r["questions"]]
    print("EXTRACTION",condition,dict(Counter(q["status"] for q in questions)),dict(Counter(q["navigation"] for q in questions)))
