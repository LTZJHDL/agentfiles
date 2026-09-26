"""Check experimental bookkeeping and quotations without scoring quality."""
import ast
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8-sig"))
for path in ROOT.rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8-sig"))
for path in ROOT.glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"))
runs=read("generation-manifest.json")
assert len(runs)==12 and len({r["id"] for r in runs})==12
provenance=[]
for run in runs:
    result=read(f'answers/{run["id"]}.json')
    assert result["id"]==run["id"] and result["task"]==run["task"]
    paths=result["loaded_instruction_files"]
    applied=any("human-facing-expression.md" in p for p in paths)
    assert applied==(run["condition"]=="G"), run["id"]
    provenance.append({"run":run["id"],"recorded_guide_read":applied})
mapping=read("answer-map.json")
raw={a["answer_id"]:read(f'answers/{a["run"]}.json')["answer"] for a in mapping}
for item in mapping:
    assert hashlib.sha256(raw[item["answer_id"]].encode()).hexdigest()==item["sha256"]
    assert sum(not c.isspace() for c in raw[item["answer_id"]])==item["non_whitespace_characters"]
run_text={item["run"]:raw[item["answer_id"]] for item in mapping}
pairs=read("blind-pairs.json")
pair_map={item["pair_id"]:item for item in read("pair-map.json")}
assert len(pairs)==6 and len(pair_map)==6
for pair in pairs:
    for side in ("X","Y"):
        assert pair[side]==run_text[pair_map[pair["pair_id"]][side]]
assert read("blind-pairs-reversed.json")==[{**p,"X":p["Y"],"Y":p["X"]} for p in reversed(pairs)]
for task in ("T1","T2","T3"):
    sources=read(f"materials/{task}.sources.json")
    packet=(ROOT/f"materials/{task}.md").read_text(encoding="utf-8")
    assert all(s["excerpt"] in packet for s in sources)
quote_issues=[]
question_count=0
for index in range(1,5):
    for result in read(f"reader-results-{index}.json"):
        source=raw[result["answer_id"]]
        for q in result["questions"]:
            question_count+=1
            quotes=q["support_quote"]
            if isinstance(quotes,str): quotes=[quotes] if quotes else []
            for quote in quotes:
                if quote not in source:
                    quote_issues.append({"answer_id":result["answer_id"],"question_id":q["question_id"],"quote":quote})
assert question_count==48
assert not quote_issues,quote_issues
trailing=[]
for path in ROOT.rglob("*"):
    # Frozen evidence preserves numbered blank source lines verbatim.
    if path.parent == ROOT / "materials":
        continue
    if path.is_file() and path.suffix in (".md",".py",".json",".txt"):
        for i,line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(),1):
            if line.rstrip(" \t")!=line: trailing.append(f"{path.name}:{i}")
assert not trailing,trailing
links=[]
for name in ("report.md",):
    path=ROOT/name
    if path.exists():
        for target in re.findall(r"\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
            if not re.match(r"(https?://|[A-Za-z]:)",target):
                assert (path.parent/target.split("#")[0]).exists(),target
                links.append(target)
result={"generations":12,"blind_pairs_checked":6,"reversed_pairs_checked":6,"reader_questions":question_count,"source_packets":3,"recorded_provenance":provenance,"reader_quote_issues":quote_issues,"report_links_checked":links}
(ROOT/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"generations":12,"reader_questions":question_count,"quote_issues":len(quote_issues),"links":len(links)}))
