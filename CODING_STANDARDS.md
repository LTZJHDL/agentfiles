# Coding Standards

These standards define how human-authored production code, tests, scripts, and migrations should be changed and reviewed.

## Debug-First Failure Handling

Do not add fallback behavior, compatibility paths, defensive wrappers, retries, silent defaults, mock success paths, or error swallowing just to make a failing path appear to work.

Surface failures at the point closest to the root cause through explicit errors, failing tests, or clear logs.

Use fail-fast behavior for invalid internal states. Preserve required validation at external boundaries.

Do not add incidental robustness, recovery, or special-case handling outside the current task.

Treat error handling, resilience, compatibility, and recovery behavior as product or architecture decisions. Do not add them incidentally while fixing another issue unless explicitly requested.

## Clarity And Complexity

Do not transfer complexity to callers, readers, hidden state, documentation, or future maintainers.

Make correctness-relevant dependencies explicit in names, signatures, data flow, and control flow. Do not hide core behavior behind mechanisms intended for ancillary concerns.

Use abstractions only within clear problem boundaries. Add indirection only when it reduces real conceptual complexity.

Keep the direct form when an abstraction only moves code elsewhere, hides dependencies, or increases required context.

Do not refactor unclear designs before clarifying the problem. Refactor only when the intended design is clear but poorly expressed.

After changing code, remove avoidable hidden assumptions through clearer structure, names, signatures, or tests.

## Implementation Baseline

Write dumb, obvious code.

Use clear names, direct control flow, explicit data shapes, boring standard-library solutions, and high human readability.

Follow separation of concerns, DRY, YAGNI, and root-cause fixes.

Reuse existing code before adding new code. Do not introduce new dependencies or speculative abstractions unless the current task requires them.

Do not introduce frameworks, patterns, configuration layers, or generic helpers unless they are required by the current task or reduce real conceptual complexity.

## Change Scope

Make the smallest change that solves the root problem.

Do not refactor unrelated code, rename unrelated symbols, reformat untouched files, reorganize modules, update dependencies, or add features unless required by the task.

Preserve the surrounding style and architecture unless they are the root cause of the issue.

## Root-Cause Fixes

Fix problems at the source of truth.

Do not patch symptoms with outer wrappers, special-case branches, compatibility adapters, or duplicated logic when the underlying cause can be corrected directly.

Prefer deleting obsolete paths over preserving them with additional branching, unless compatibility is explicitly required.

## Compatibility

Do not preserve backward compatibility, legacy behavior, old APIs, migration paths, or deprecated options unless explicitly required.

## Feature Discipline

Do not add unrequested features.

Before adding a feature, confirm that it directly improves the project's core capability and composes with existing capabilities.

Prefer strengthening existing primitives over adding isolated one-off behavior.

## Code Quality Budgets

Use these as default budgets for human-authored source code, not mechanical hard limits:

- Prefer files under 300 lines.
- Prefer functions under 50 lines.
- Prefer nesting depth <= 3.
- Prefer cyclomatic complexity <= 10.
- Prefer <= 3 positional parameters.
- Avoid magic numbers when the value carries domain meaning.

Refactor budget violations only when it improves clarity, locality, testability, or responsibility boundaries. Do not split code merely to satisfy a number.

<!-- ## Coupling And State

Keep business logic decoupled from infrastructure, IO, clocks, randomness, network clients, and external services. Inject these dependencies at boundaries.

Prefer immutable inputs and outputs. Do not mutate parameters. Keep state local and explicit. -->

## Readability And Comments

Make code readable through names, signatures, structure, and straightforward flow first.

Use comments only to explain non-obvious intent, invariants, constraints, or tradeoffs. Do not comment on what the code already says.

<!-- ## Security Baseline

Never hardcode secrets, API keys, or credentials in source code. Use environment variables or secret managers.

Use parameterized queries for database access. Never concatenate external input into SQL or shell commands.

Validate external input at system boundaries. -->

<!-- ## Testing And Validation

Keep code testable and verify with automated checks whenever feasible.

Enforce a 60-second timeout for backend unit tests.

Prefer static checks, formatting, and reproducible verification over ad-hoc confidence. -->

<!-- ## Review Checklist

When reviewing a change against these standards, check whether the diff:

- hides a failure, fabricates success, or adds a silent fallback;
- adds recovery, retry, compatibility, or migration behavior without an explicit requirement;
- moves complexity into callers, hidden state, documentation, or future maintainers;
- hides correctness-relevant dependencies outside names, signatures, data flow, or control flow;
- introduces a framework, pattern, configuration layer, generic helper, or abstraction that the task does not require;
- patches symptoms instead of fixing the source of truth;
- adds unrequested features or isolated one-off behavior;
- couples business logic directly to IO, clocks, randomness, network clients, or external services;
- concatenates external input into SQL or shell commands;
- lacks feasible automated validation for non-trivial behavior. -->
