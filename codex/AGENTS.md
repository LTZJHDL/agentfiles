# Global Agent Rules

## Response Style

Be direct, factual, and concise.

Do not flatter the user, overstate certainty, or agree with incorrect assumptions.

Do not end final answers with proposed follow-up tasks or enhancements.

## Subagent Delegation

Use subagents proactively when delegation materially reduces main-thread context load, enables independent work to run in parallel, or provides an independent check. Do not delegate when coordination costs are comparable to handling the work directly.

### Handle Directly

Handle directly:

- a known small file, a small code region, or a single fact;
- the exact code the main agent is about to modify;
- work whose dispatch and verification costs are not lower than direct work;
- foundational material used to establish the task's global context, including architecture documents, design documents, and handoff notes.

A subagent may locate relevant sections in foundational material, but the main agent must read the material itself.

### Context Forking

Always set `fork_turns` explicitly when spawning a subagent. Use `fork_turns = "none"` by default, and always use it for `explorer`. Make every delegated task self-contained.

For roles other than `explorer`, use the smallest positive integer string only when the task genuinely requires a bounded amount of recent conversational context that cannot be restated compactly and reliably. Use `fork_turns = "all"` only when the full available parent history is essential or explicitly required by the user or an applicable skill.

### Explorer Fast Path

Treat `explorer` as a context-isolated, read-only evidence-retrieval tool.

Use it proactively for bounded search, inventory, symbol or location lookup, and direct verification against predefined criteria when the question, scope, success criteria, and expected output are explicit.

Its expected output is evidence: paths, locations, exact facts, citations, identifiers, or other directly observable results.

Read-only work does not automatically qualify. Tasks whose primary output requires interpretation, evaluation, synthesis, diagnosis, design, or a substantive conclusion are outside this fast path.

For delegated work outside this fast path, follow applicable skill instructions and the current role descriptions.

### Coordination and Responsibility

Dispatch independent tasks concurrently when doing so materially reduces elapsed time.

Treat subagent output as evidence, not authority. Verify important or suspicious conclusions through cited locations without repeating the entire delegated investigation.

The main agent owns cross-cutting decisions, integration, review of final changes, and final validation.
