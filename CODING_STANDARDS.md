# Coding Standards

These standards provide default engineering principles for human-authored production code, tests, scripts, and migrations.

They guide judgment rather than prescribe every situation. When principles compete, prefer the design that makes correctness easiest to understand, verify, and change.

## Directness and clarity

Prefer straightforward code whose behavior is evident from its names, signatures, data shapes, and control flow. Use familiar language and standard-library features when they fit the problem.

Make correctness-relevant dependencies, assumptions, and side effects explicit. Express critical constraints in code and interfaces. Use documentation to preserve rationale and tradeoffs that code cannot express.

A useful abstraction, dependency, framework, or configuration layer serves a concrete current need or clearly reduces total conceptual complexity. Keep the direct form when indirection merely relocates logic or increases the context required to understand it.

Reuse existing code when it already represents the same rule. Similar-looking code with different reasons to change may be better kept separate.

Treat large files or functions, deep nesting, high branch complexity, and long parameter lists as review signals, not automatic violations. Refactor when it improves clarity, locality, testability, or responsibility boundaries rather than merely satisfying a number.

Give domain-significant values meaningful names.

Use comments to preserve non-obvious intent, invariants, constraints, or tradeoffs. Let clear code explain what it does.

## Change discipline

Make the smallest coherent change that corrects the root cause at its source of truth. Measure scope by conceptual focus, not by file count.

Keep the change conceptually focused: leave unrelated refactors, renames, formatting, dependency updates, and features outside it. Preserve the surrounding style and architecture unless they obscure or cause the problem.

Prefer one direct correction over outer wrappers, special cases, compatibility adapters, or duplicated logic.

Let the current change define the behavior to add. Extend existing primitives when they naturally own that behavior.

Treat compatibility for public APIs, persisted data, and external protocols as a product decision. Preserve an established contract unless the current change explicitly replaces it; when no contract exists, prefer removing obsolete paths to layering adapters.

## Failure behavior

Make failures explicit, local, and diagnosable. In code, fail where an invalid state first becomes knowable; in verification, use targeted assertions or logs that identify the violated condition.

Validate external input at system boundaries and fail fast when an internal invariant is violated.

Treat fallbacks, retries, recovery, and resilience as deliberate product or architecture choices with defined failure semantics and tests.

Never conceal failure with swallowed errors, silent defaults, or mock success paths.

## Coupling and state

Separate business rules from infrastructure and I/O so their behavior can be understood and tested without external systems. Make clocks, randomness, network clients, and other external effects explicit at the boundary that owns them.

Prefer immutable input and output flow. When mutation is the clearer choice, make ownership explicit and keep mutable state local.

## Security boundaries

Load secrets through the environment or a secret store. Never hardcode secrets or expose them in logs.

Use parameterized queries and process APIs that keep arguments separate from command text. Never concatenate untrusted input into SQL or shell commands.

## Verification

Match verification to risk. Start with the narrowest reproducible check that could falsify the changed behavior, then broaden when the change crosses module or system boundaries.

Test observable behavior through stable interfaces. Prefer tests that survive internal refactoring and derive expected results from an independent source of truth.

Choose unit, integration, and end-to-end tests, type checks, static analysis, and formatting according to the failure modes each can detect. Passing a weaker check is not evidence for behavior it cannot exercise.

For a bug fix, preserve a regression test when a stable seam can reproduce the defect. If no such seam exists, treat that as design information rather than forcing a brittle test.
