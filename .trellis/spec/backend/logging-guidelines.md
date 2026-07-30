# Logging Guidelines

Logging behavior for this project is documented in [Error Handling And Logging](./error-handling.md). Keep this file as a short redirect because older Trellis workflows may look for `logging-guidelines.md`.

Local rules:
- Use `src/test_worker/core/logger.py`.
- Log UTC ISO timestamps to stdout.
- Pass structured metadata as a dict.
- Prefer stable English log messages and include task metadata keys that match control-plane payload names, such as `taskId`, `runId`, and `taskType`.
