# Review And Verification Checklist

## Code Review

- Scope matches the current task record.
- No unrelated refactor, formatting churn, or dependency change.
- Data flow and ownership boundaries are clear.
- Errors surface near the root cause.
- Inputs, outputs, and edge cases are explicit.
- Tests cover changed behavior and known failure modes.

## Verification

- Run the step validation command from the task record.
- Run targeted tests for changed modules.
- Run broader tests when shared behavior changed.
- Run static or formatting checks when available.
- Record exact commands and outcomes in durable task evidence.

## Completion

- Task state matches validation evidence.
- Docs and handoff reflect the final behavior.
- Git status is understood before final response or commit.
