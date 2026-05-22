---
name: execute-handoff-taskmaster
description: Use when the user asks to execute a documented plan, handoff, or long-running task using taskmaster. Trigger on phrases like "根据文档执行", "按照 handoff 完成", "使用 taskmaster", "自主完成", "完成所有阶段", or "执行任务计划".
---

# Execute Handoff With Taskmaster

## Goal

Complete a documented task end to end with persistent task state and evidence.

## Required Flow

1. Read applicable instructions, handoff, taskmaster `SPEC.md`, `TODO.csv`, `PROGRESS.md`, project docs, code, tests, and git state.
2. Read `~/.codex/AGENTS.md` and cwd `AGENTS.md` at task start and after context recovery, handoff takeover, scope changes, cwd changes, or long-running context transitions.
   During normal phase execution, rely on the already-read rules unless they may be stale or unclear.
3. Re-read the task-state file before each step. The task record is the execution-state source of truth.
4. For each phase, follow this loop:
   - read phase docs, code, tests, task records, git state, and applicable rules
   - expand the phase design, refine the task plan, and converge the implementation route
   - implement the scoped changes step by step
   - review changed code for correctness, conflicts, scope drift, and missing tests
   - verify from multiple angles: targeted tests, broader tests when needed, static checks, artifact inspection, and acceptance criteria
   - update docs, evidence, and task state before moving to the next phase
5. Mark a step done only after its validation gate passes.
6. If validation fails, record the failure, fix the root cause, and re-run the same gate before moving on.
7. Keep conversation updates concise; put durable details in task records.
8. Run final integration gates before reporting completion. Commit only when the user requested it or the handoff explicitly requires it.

## Uncertainty And Subagents

- Work through unclear points by reading files, code, tests, logs, artifacts, and task records first.
- If the active user request or handoff explicitly authorizes subagents, create one reviewer subagent for difficult unresolved design or correctness questions.
- Prefer `gpt-5.5` with `xhigh` reasoning when available and appropriate.
- Use the subagent for independent review, critique, and alternatives, not for replacing the main execution loop.
- Stop for user confirmation only when the decision materially changes scope, behavior, risk, dependency policy, or cannot be determined from local truth sources.

## Boundaries

- Do not drift from handoff scope.
- Do not skip review, verification, or evidence updates.
- Do not add fallback behavior to make a failing path appear successful.
- Do not mark task state complete based on confidence without a passing check.
- Do not implement code that violates the latest-read `~/.codex/AGENTS.md` or cwd `AGENTS.md`, even if it would make the current validation pass.

## Optional Reference

Use `references/review_verify_checklist.md` when a phase needs a structured review and verification pass.
