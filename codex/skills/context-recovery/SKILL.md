---
name: context-recovery
description: Use when the user asks to recover context, continue prior work, inspect current project state, or take over from another agent. Trigger on phrases like "恢复上下文", "接着上次", "先了解现状", "handoff 接手", or when task state must be reconstructed from files before acting.
---

# Context Recovery

## Goal

Restore the current task state from truth sources before reasoning or acting.

## Required Flow

1. Locate the working directory, project root, relevant task directories, and applicable instruction files, including
   `~/.codex/AGENTS.md` when present and any `AGENTS.md` from the workspace/project root down to the relevant task paths.
2. Read those instruction files before drawing conclusions, then read local truth sources:
   project docs, task records, git state, code, tests, logs, and artifacts.
3. If taskmaster or another task tracker is present, treat its task-state file as the execution-state source of truth.
4. Cross-check docs against code, tests, and artifacts. Mark stale or conflicting docs explicitly.
5. Separate facts, inferences, assumptions, unknowns, risks, and next actions.
6. Report the recovered state concisely:
   current goal, completed work, remaining work, blockers, evidence read, and next executable step.

## Boundaries

- Do not implement, refactor, or modify files unless the user explicitly asks.
- Do not infer task state from conversation memory when local files can answer.
- Do not silently repair inconsistent records. Surface the mismatch and identify which source should win.
