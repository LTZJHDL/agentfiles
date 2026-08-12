# Coding Standards

These standards provide default engineering principles for human-authored production code, tests, scripts, and migrations.

They guide judgment rather than prescribe every situation. Each principle states a desired property and the conditions that make it useful; prohibitions are reserved for boundaries where ambiguity would compromise correctness or safety. When principles compete, prefer the design that makes correctness easiest to understand, verify, and change.

## Directness and clarity

Prefer straightforward code whose behavior is evident from its names, signatures, data shapes, and control flow. Use familiar language and standard-library features when they fit the problem.

Make correctness-relevant dependencies, assumptions, and side effects explicit. Express critical constraints in code and interfaces. Use documentation to preserve rationale and tradeoffs that code cannot express.

Choose the simplest mechanism that satisfies the current requirement. Add an abstraction, dependency, framework, or configuration layer when it directly serves that requirement and its benefit outweighs the added indirection and maintenance cost.

Reuse or extend existing code when it already owns the same rule and remains the natural place for the behavior. Similar-looking code with different reasons to change may be better kept separate.

Treat large files or functions, deep nesting, high branch complexity, and long parameter lists as review signals, not automatic violations. Refactor when it improves clarity, locality, testability, or responsibility boundaries rather than merely satisfying a number.

Name a value when it expresses a domain rule or a non-obvious constraint that a literal cannot communicate.

Use comments to preserve non-obvious intent, invariants, constraints, or tradeoffs. Let clear code explain what it does.

## Change discipline

Let the agreed requirement define the behavior to add. Make the smallest coherent change that corrects the root cause at its source of truth, measuring scope by conceptual focus rather than file count.

Leave unrelated refactors, renames, formatting, dependency updates, and features outside the change. Preserve the surrounding style and architecture unless they cause the problem or prevent a clear root-cause correction. When the intended design is unclear, clarify it before restructuring the code.

When the source can be changed directly, prefer one correction there over outer wrappers, special cases, compatibility adapters, or duplicated logic.

Before adding or preserving compatibility behavior, identify the agreed requirement, versioning policy, or established external contract it serves. Without one, replace the obsolete path rather than extending it with adapters or branches.

## Failure behavior

Make failures explicit, local, and diagnosable. Fail where an invalid state first becomes knowable.

Represent expected boundary failures in terms callers can handle. Fail fast when an internal invariant is violated.

Require an agreed product or architecture requirement before adding fallbacks, retries, recovery, or resilience behavior. Define and test their failure semantics.

Never conceal failure with swallowed errors, silent defaults, or mock success paths.

## Dependencies and effects

Make time, randomness, I/O, and external-service dependencies explicit when behavior depends on them. Keep decision logic understandable and testable without requiring the real external system.

Keep mutable state local and make its ownership clear. Prefer immutable value flow when it makes state transitions easier to follow.

## Trust boundaries

Parse and validate untrusted input at trust boundaries before relying on it.

Obtain secrets through the system's designated secret channel. Never place secrets in source code or logs.

Use structured APIs that keep untrusted data separate from executable code, queries, and commands. Never interpolate untrusted data into executable text.

## Verification

Match verification to risk. Start with the narrowest reproducible check that could falsify the changed behavior, then broaden when the change crosses module or system boundaries.

Test observable behavior through stable interfaces. Prefer tests that survive internal refactoring and derive expected results from an independent source of truth.

Choose unit, integration, and end-to-end tests, type checks, static analysis, and formatting according to the failure modes each can detect. Passing a weaker check is not evidence for behavior it cannot exercise.

For a bug fix, preserve a regression test when the defect can be reproduced through a stable observable interface. If no such interface exists, treat that absence as design information rather than forcing a brittle test.
