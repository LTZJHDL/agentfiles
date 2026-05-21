---
name: rigorous-discussion
description: Use when the user wants exploratory technical discussion, design analysis, tradeoff evaluation, or problem clarification before implementation. Trigger on phrases like "先讨论", "不要实现", "分析方案", "有哪些问题", "是否可行", or "需要澄清".
---

# Rigorous Discussion

## Goal

Explore the problem space without committing to implementation too early.

## Required Flow

1. Read source files, docs, logs, or task records when the question depends on
   local project truth.
2. Separate facts, assumptions, inferences, uncertainties, and decisions.
3. Identify viable routes and compare them by correctness, complexity, risk,
   reversibility, performance, and validation cost.
4. Distinguish blocking questions from non-blocking questions where a safe
   default can be chosen.
5. State recommended defaults when available, but keep them labeled as defaults
   until accepted by the user or confirmed from files.
6. Preserve exploration freedom by defining constraints and decision boundaries
   instead of over-specifying incidental implementation details.

## Boundaries

- Do not implement or edit files.
- Do not produce a final spec or handoff unless the user asks to transition to
  planning.
- Do not turn assumptions into confirmed decisions.
