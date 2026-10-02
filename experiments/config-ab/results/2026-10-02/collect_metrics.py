"""Reconstruct this pilot's initial task turns from local, per-request usage logs.

Only aggregate metadata is exported. Conversation text and account identifiers stay
in the original local logs. Standard-rate credits are a comparison proxy, not a bill.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile


BENCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BENCH))
from benchlib import digest_files

RUNS = [
    ("run-01", "feature", "A", "01a0f7ea-981b-7370-8eae-b2fe1c13c258"),
    ("run-02", "bug", "A", "01a0f80b-43b0-76c1-9adc-d51d425ed45b"),
    ("run-03", "feature", "B", "01a0fa81-85b2-7070-916b-df503eb8166d"),
    ("run-04", "bug", "B", "01a0fa82-ee0a-7db2-b990-6783013d7157"),
]
TOKEN_KEYS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
              "output_tokens", "reasoning_output_tokens", "total_tokens")
# Credits / million tokens: uncached input, cached input, output.
# https://learn.chatgpt.com/docs/pricing, inspected 2026-10-02.
RATES = {"gpt-6-astra": (250, 25, 1250), "gpt-6.1-sol": (50, 2.5, 250),
         "gpt-6-luna": (2.5, .25, 12.5), "gpt-5.6-luna": (5, .5, 30)}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def sum_usage(values):
    return {key: sum(value[key] for value in values) for key in TOKEN_KEYS}


def credits(usage, model):
    uncached, cached, output = RATES[model]
    return ((usage["input_tokens"] - usage["cached_input_tokens"]) * uncached
            + usage["cached_input_tokens"] * cached
            + usage["output_tokens"] * output) / 1_000_000


def git(project, *args):
    return subprocess.run(["git", "-c", f"safe.directory={project.as_posix()}",
                           "-C", str(project), *args], check=True,
                          capture_output=True).stdout


def summarize_thread(ident, root_turn, exports, session_paths, seen_responses):
    paths = [p for p in session_paths if p.name.endswith(ident + ".jsonl")]
    assert len(paths) == 1, (ident, paths)
    rows = [json.loads(line) for line in paths[0].read_text(encoding="utf-8").splitlines()]
    meta = next(r["payload"] for r in rows if r["type"] == "session_meta")
    contexts = [r["payload"] for r in rows if r["type"] == "turn_context"
                and r["payload"]["root_turn_id"] == root_turn]
    turns = {c["turn_id"] for c in contexts}
    assert len({(c["model"], c["effort"]) for c in contexts}) == 1
    context = contexts[0]
    records = [r["payload"] for r in rows if r["type"] == "token_usage_record"
               and r["payload"]["root_turn_id"] == root_turn]
    unique = []
    for record in records:
        assert record["thread_id"] == ident
        assert record["turn_id"] in turns
        key = record["response_id"]
        if key in seen_responses:
            assert seen_responses[key] == record["usage"]
            continue
        seen_responses[key] = record["usage"]
        unique.append(record)
    usage = sum_usage([r["usage"] for r in unique])
    for turn in turns:
        local = [r for r in unique if r["turn_id"] == turn]
        assert sum_usage([r["usage"] for r in local]) == local[-1]["turn_token_usage"]
    assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]
    assert usage["cache_write_input_tokens"] == 0
    completions = [r["payload"] for r in rows if r["type"] == "event_msg"
                   and r["payload"].get("type") == "task_complete"
                   and r["payload"].get("turn_id") in turns]
    assert len(completions) == len(turns)
    calls = []
    current_turn = None
    rates = []
    for row in rows:
        p = row["payload"]
        if row["type"] == "event_msg" and p.get("type") == "task_started":
            current_turn = p.get("turn_id")
        if current_turn not in turns:
            continue
        if row["type"] == "response_item" and p.get("type") in ("function_call", "custom_tool_call"):
            call = {"timestamp": row["timestamp"], "name": p["name"]}
            if p.get("namespace") == "collaboration":
                args = json.loads(p["arguments"])
                call["arguments"] = {k: v for k, v in args.items() if k != "message"}
            calls.append(call)
        if row["type"] == "event_msg" and p.get("type") == "token_count" and p.get("rate_limits"):
            rate = p["rate_limits"]
            rates.append({"timestamp": row["timestamp"], "primary": rate.get("primary"),
                          "secondary": rate.get("secondary")})
    source = meta.get("source")
    spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
    if spawn:
        assert not any(c["name"] == "spawn_agent" for c in calls), "Unaccounted nested descendants"
    state = next(r["payload"]["state"] for r in rows if r["type"] == "world_state")
    ui = read_json(exports / ((ident if spawn else next(r[0] for r in RUNS if r[3] == ident)) + "-thread.json"))
    task_items = [item for t in ui["turns"] if t["id"] in turns for item in t["items"]]
    return {
        "thread_id": ident, "agent_path": spawn.get("agent_path", "/root"),
        "role": spawn.get("agent_role", "main"), "parent_thread_id": spawn.get("parent_thread_id"),
        "model": context["model"], "effort": context["effort"], "cli_version": meta["cli_version"],
        "duration_ms": sum(c["duration_ms"] for c in completions),
        "started_at_utc": datetime.fromtimestamp(min(c["started_at"] for c in completions), timezone.utc).isoformat(),
        "completed_at_utc": datetime.fromtimestamp(max(c["completed_at"] for c in completions), timezone.utc).isoformat(),
        "time_to_first_token_ms": completions[0].get("time_to_first_token_ms"),
        "request_count": len(unique), "usage": usage,
        "standard_credit_proxy": round(credits(usage, context["model"]), 6),
        "tool_calls": dict(Counter(c["name"] for c in calls)),
        "collaboration_calls": [c for c in calls if "arguments" in c],
        "ui_command_execution_count": sum(i["type"] == "commandExecution" for i in task_items),
        "usage_limit_first_observed": rates[0] if rates else None,
        "usage_limit_last_observed": rates[-1] if rates else None,
        "agents_md_text": state.get("agents_md", {}).get("text", ""),
        "base_instructions_sha256": hashlib.sha256(meta.get("base_instructions", {}).get("text", "").encode()).hexdigest()
            if isinstance(meta.get("base_instructions"), dict) else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--exports", type=Path, required=True)
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = list(args.sessions.rglob("*.jsonl"))
    freeze = read_json(BENCH / "freeze.json")
    result = {"analysis_date": "2026-10-02", "scope": "Initial development turn plus all its descendants; later commit turns excluded",
              "rates_source": "https://learn.chatgpt.com/docs/pricing", "rates_checked_date": "2026-10-02",
              "standard_credit_rates_per_million": RATES,
              "proxy_limitations": "Assumes Standard speed; historical speed unverified. Not observed credit charges or subscription allowance usage.",
              "runs": []}
    seen_responses = {}
    for name, task, condition, ident in RUNS:
        ui = read_json(args.exports / (name + "-thread.json"))
        turn = min(ui["turns"], key=lambda t: t["startedAt"])
        children = [item for item in turn["items"] if item["type"] == "subAgentActivity" and item["kind"] == "started"]
        ids = [ident] + [child["agentThreadId"] for child in children]
        threads = [summarize_thread(i, turn["id"], args.exports, paths, seen_responses) for i in ids]
        snapshot = (BENCH / "configs" / condition / "AGENTS.md").read_text(encoding="utf8")
        agents_match = normalized(threads[0].pop("agents_md_text")) == normalized(snapshot)
        for thread in threads[1:]:
            thread.pop("agents_md_text")
        prompt = "\n".join(c["text"] for item in turn["items"] if item["type"] == "userMessage"
                           for c in item["content"] if c["type"] == "text")
        expected_prompt = (BENCH / "tasks" / (task + ".md")).read_text(encoding="utf8")
        project = args.projects / name
        baseline = git(project, "rev-list", "--max-parents=0", "HEAD").decode().strip()
        with tarfile.open(fileobj=io.BytesIO(git(project, "archive", baseline))) as archive:
            files = {f.name: archive.extractfile(f).read() for f in archive.getmembers() if f.isfile()}
        source_digest = digest_files(files)
        evaluation = read_json(args.exports / (name + "-evaluation.json"))
        usage = sum_usage([t["usage"] for t in threads])
        result["runs"].append({
            "run": name, "task": task, "condition": condition, "thread_id": ident, "root_turn_id": turn["id"],
            "baseline_commit": baseline, "baseline_tree": git(project, "rev-parse", baseline + "^{tree}").decode().strip(),
            "source_matches_freeze": source_digest == freeze["tasks"][task]["source_sha256"],
            "prompt_matches_after_whitespace_normalization": normalized(prompt) == normalized(expected_prompt),
            "agents_md_matches_snapshot_after_whitespace_normalization": agents_match,
            "head_commit": evaluation["head_commit"], "final_status": git(project, "status", "--porcelain").decode(),
            "diff_numstat": git(project, "diff", "--numstat", baseline, "HEAD").decode().strip(),
            "automated_pass": evaluation["automated_pass"],
            "root_duration_ms": turn["durationMs"], "request_count_all_threads": sum(t["request_count"] for t in threads),
            "usage_all_threads": usage, "standard_credit_proxy_all_threads": round(sum(t["standard_credit_proxy"] for t in threads), 6),
            "standard_credit_proxy_children": round(sum(t["standard_credit_proxy"] for t in threads[1:]), 6),
            "threads": threads,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for run in result["runs"]:
        print(json.dumps({k: v for k, v in run.items() if k not in ["threads", "diff_numstat"]}, ensure_ascii=False))
        for t in run["threads"]:
            print(json.dumps({k: t[k] for k in ["agent_path", "model", "effort", "request_count", "usage", "standard_credit_proxy", "tool_calls"]}))


if __name__ == "__main__":
    main()
