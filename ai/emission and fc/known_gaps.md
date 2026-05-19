## Test Harness Semantics

Current limitation:
`expect_end_call` at scenario level is semantically ambiguous for multi-turn scenarios.

Current meaning:
Whether the call has ended by completion of all turns.

Future options:

- `expect_final_end_call`
- per-turn `expect_end_call`

Deferred because:
Current scenario volume does not justify added harness complexity.
