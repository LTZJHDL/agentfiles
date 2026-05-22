---
name: spec-handoff-planning
description: Use when the user wants to turn discussion into a durable spec, design, task plan, execution record, or handoff for another agent. Trigger on phrases like "形成 spec", "任务计划", "创建 handoff", "持久化", "交付给另一个 agent", or "为后续执行做准备".
---

# Spec Handoff Planning

## Goal

Convert confirmed decisions into durable execution material that another agent can recover from a cold start.

## Required Flow

1. Recover context first: read relevant instructions, docs, task records, code, tests, git state, and artifacts.
2. Extract goals, non-goals, confirmed decisions, assumptions, open questions, risks, deliverables, validation gates, and acceptance criteria.
3. Determine whether any blocking question remains. Ask only for decisions that cannot be derived from files and would materially change scope or behavior.
4. If planning is sufficiently clear, update long-lived project docs for stable design decisions.
5. Create or update task handoff records for execution state, such as taskmaster `SPEC.md`, `TODO.csv`, and `PROGRESS.md` when appropriate.
6. Keep project docs and task records separate: durable design belongs in docs;
   execution state belongs in task records.
7. Verify the handoff is cold-start recoverable and points to exact files, commands, acceptance criteria, and next action.

## Boundaries

- Do not implement feature code by default.
- Do not hide unresolved questions inside the spec.
- Do not store the only copy of task state in chat.
- Do not over-constrain implementation details unless they are confirmed decisions or required validation boundaries.

## Optional Templates

- For a compact spec shape, use `assets/spec_template.md`.
- For an agent handoff shape, use `assets/handoff_template.md`.
