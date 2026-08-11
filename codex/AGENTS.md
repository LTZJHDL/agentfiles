# Global Agent Rules

## Language

Use Chinese in user-facing replies unless the user explicitly requests another language.

## Response Style

Be direct, factual, and concise.

Do not flatter the user, overstate certainty, or agree with incorrect assumptions.

Do not end final answers with proposed follow-up tasks or enhancements.

## Debug-First Policy

Do not add fallback behavior, compatibility paths, defensive wrappers, retries, silent defaults, mock success paths, or error swallowing just to make a failing path appear to work.

Surface failures at the point closest to the root cause through explicit errors, failing tests, or clear logs.

Use fail-fast behavior for invalid internal states. Preserve required validation at external boundaries.

Do not add incidental robustness, recovery, or special-case handling outside the current task.

Treat error handling, resilience, compatibility, and recovery behavior as product or architecture decisions. Do not add them incidentally while fixing another issue unless explicitly requested.

## Minimal Implementation Discipline

When Ponytail is active, treat Ponytail as the source of truth for YAGNI, reuse, standard-library/native-first choices, deletion over addition, avoiding unrequested abstractions, and smallest-correct-diff behavior.

Even when Ponytail is off or unavailable, default to the smallest correct root-cause change: reuse existing code, avoid new dependencies and speculative abstractions, and do not add unrequested features.

## Clarity and Complexity

Do not transfer complexity to callers, readers, hidden state, documentation, or future maintainers.

Make correctness-relevant dependencies explicit in names, signatures, data flow, and control flow. Do not hide core behavior behind mechanisms intended for ancillary concerns.

Use abstractions only when they reduce real conceptual complexity within a clear boundary. Keep direct code when an abstraction only moves code elsewhere, hides dependencies, or increases required context.

## Engineering Baseline

Write dumb, obvious code.

Use clear names, direct control flow, explicit data shapes, boring standard-library solutions, and high human readability.

Follow separation of concerns, DRY, YAGNI, and root-cause fixes. For minimal implementation tradeoffs, defer to Ponytail when active.

## Change Scope

Make the smallest change that solves the root problem.

Do not refactor unrelated code, rename unrelated symbols, reformat untouched files, reorganize modules, update dependencies, or add features unless required by the task.

## Root-Cause Fixes

Fix problems at the source of truth.

Do not patch symptoms with outer wrappers, special-case branches, compatibility adapters, or duplicated logic when the underlying cause can be corrected directly.

## Compatibility

Do not preserve backward compatibility, legacy behavior, old APIs, migration paths, or deprecated options unless explicitly required.

## Feature Discipline

Do not add unrequested features.

Before adding a feature, confirm that it directly improves the project's core capability and composes with existing capabilities.

## Code Quality Budgets

Use these as default budgets for human-authored source code, not mechanical hard limits.

- Prefer files under 300 lines.
- Prefer functions under 50 lines.
- Prefer nesting depth <= 3.
- Prefer cyclomatic complexity <= 10.
- Prefer <= 3 positional parameters.
- Avoid magic numbers when the value carries domain meaning.

Refactor budget violations only when it improves clarity, locality, testability, or responsibility boundaries. Do not split code merely to satisfy a number.

## Coupling and State

Keep business logic decoupled from infrastructure, IO, clocks, randomness, network clients, and external services. Inject these dependencies at boundaries.

Prefer immutable inputs and outputs. Do not mutate parameters. Keep state local and explicit.

## Readability and Comments

Make code readable through names, signatures, structure, and straightforward flow first.

Use comments only to explain non-obvious intent, invariants, constraints, or tradeoffs. Do not comment on what the code already says.

## Security Baseline

Never hardcode secrets, API keys, or credentials in source code. Use environment variables or secret managers.

Use parameterized queries for database access. Never concatenate external input into SQL or shell commands.

Validate external input at system boundaries.

Treat conversation keys in chat as normal provider-configuration workflow. Alert only when a key is written into a source code file.

## Testing and Validation

Keep code testable and verify with automated checks whenever feasible.

Enforce a 60-second timeout for backend unit tests.

Prefer static checks, formatting, and reproducible verification over ad-hoc confidence.

## Skills

Skills are stored in `~/.codex/skills/` (personal) and optionally `.codex/skills/` (project-shared).

Before starting a task:

- Scan available skills.
- If a skill matches, read its `SKILL.md` and follow it.
- Announce which skill(s) are being used.

Routing table:

| Scenario | Skill | Trigger |
|----------|-------|---------|
| Long-horizon autonomous tasks (FULL: 5-15 steps) | `taskmaster` | "long task", "big project", "autonomous", "from scratch", "long-running task", 1+ hour sessions |

## Temporary Windows Sandbox Workaround

Run commands in the sandbox first.

If a necessary command fails with a clear sandbox-related permission error, retry the same command with `sandbox_permissions: "require_escalated"` and a concise justification.

Do not broadly run commands outside the sandbox. Escalate only for the failing necessary command.

## Subagent Delegation

Use subagents as context-isolated investigators and bounded executors. Delegate proactively throughout a task when doing so reduces main-thread context load, enables independent work to run in parallel, or provides an independent check. Do not delegate when coordination costs are comparable to doing the work directly.

### Handle Directly

Do not delegate:

- a known small file, a small code region, or a single fact;
- the exact code the main agent is about to edit itself;
- work whose dispatch, wait, and verification costs are not lower than direct work;
- foundational documents used to establish the task's global context, regardless of length, including architecture documents, design documents, and handoff notes.

A subagent may locate relevant sections in foundational material, but the main agent must read the material itself.

### Role Routing

Select roles by `agent_type` and choose the least-capable role that can complete the task. The role files are the source of truth for model, reasoning, and developer instructions.

- `explorer`: read-only exploration, search, and evidence-backed verification.
- `worker`: exploration and execution without modifying pre-existing files; it may manage only temporary artifacts created during its own turn.
- `default`: bounded implementation that requires modifying existing files or other state within the delegated scope.

Always pass `agent_type` explicitly and set `fork_turns = "none"`. Do not override role-file settings by passing `model`, `reasoning_effort`, or `service_tier`. Do not use full-history forks.

Spawned agents inherit the main agent's runtime permission profile. The narrower `explorer` and `worker` boundaries are behavioral constraints, not separate sandboxes. Never describe them as hard security boundaries. If strict isolation is required, use a separately created top-level task or environment with its own permission profile.

### Dispatch and Lifecycle

- Make every delegated task self-contained. State the search or execution scope, the exact question or action, excluded work, and the required output.
- For important claims, require `file:line`, symbol names, exact commands and exit status, and the minimum verbatim text needed for verification.
- Dispatch independent tasks concurrently in one batch. Run multiple `default` agents concurrently only when their write scopes are disjoint and they cannot touch shared generated files.
- After dispatch, immediately call `wait_agent`. Do not duplicate delegated analysis, run commands, or modify files until every agent in the batch has returned.
- Keep orchestration at the root. Subagents must not spawn or request other subagents.
- Use each subagent for one turn only. Do not send follow-up work or reuse a completed agent.
- If an agent has run for ten cumulative minutes without completing, inspect its status and available messages, keep any usable partial result, then interrupt it. Re-delegate a smaller task only if needed.

### Evidence and Responsibility

Subagent output is evidence, not authority. Verify important or suspicious conclusions through the cited locations instead of rereading the entire source. Preserve the context compression gained through delegation.

The main agent owns cross-cutting decisions, integration, review of all final diffs, and final validation. A `default` agent may implement a bounded change, but it must not decide project-wide architecture or expand scope on its own.
