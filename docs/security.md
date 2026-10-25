# Security notes

- Keep credentials in `.env`, which is excluded by `.gitignore`.
- Model output is untrusted input. Do not execute generated code or shell commands automatically.
- SQLite queries use read-only URI mode and a SQLite authorizer; a progress handler limits execution time and fetched results are capped. The pre-validator is only an additional guardrail, not a full SQL parser.
- SQLite read-only mode prevents database writes through this connection, but does not prevent reading sensitive rows. Only select database files you are authorized to access.
- History is stored locally in `data/history.json` and may contain sensitive prompts/answers. Clear it when no longer needed.
- The Streamlit app has no authentication layer. Keep it on a trusted machine/network unless protected by suitable access controls.
