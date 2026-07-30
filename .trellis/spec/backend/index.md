# Python Worker Specs

This directory documents the current `testing-agent-api-ui-worker` codebase. It is a single Python 3.12 package that polls a Go control plane, executes UI Playwright tasks and API HTTP tasks, and reports worker results back to internal endpoints.

## Source Layout

- `src/test_worker/__main__.py` owns process startup and `poll` / `once` mode routing.
- `src/test_worker/core/` owns TOML configuration and stdout logging.
- `src/test_worker/contracts/types.py` owns typed dataclass contracts for UI worker snapshots and result payloads.
- `src/test_worker/control_plane/client.py` owns HTTP calls to the Go control plane.
- `src/test_worker/poller/task_poller.py` owns claim, heartbeat, execution dispatch, and error reporting loops.
- `src/test_worker/ui/` owns Playwright UI case and suite execution.
- `src/test_worker/api/` owns API case and collection execution, request rendering, extraction, and assertion rules.
- `tests/` contains focused pytest and unittest coverage for config, API runner behavior, and control-plane response unwrapping.

Generated files such as `src/testing_agent_api_ui_worker.egg-info/`, `__pycache__/`, `.pytest_cache/`, and virtual environment content are not project architecture.

## Guides

- [Directory Structure](./directory-structure.md): package boundaries and where new code belongs.
- [Configuration And Contracts](./configuration-and-contracts.md): TOML config, dataclasses, JSON naming, and control-plane payload rules.
- [Runner Flows](./runner-flows.md): poll loop, once mode, UI runner, API runner, and artifact conventions.
- [Error Handling And Logging](./error-handling.md): local failure classification, reporting, heartbeat handling, and stdout logs.
- [Quality Guidelines](./quality-guidelines.md): tests, verification commands, and local anti-patterns.

## Quick Rules

- Keep control-plane endpoint strings and payload shape changes centered in `ControlPlaneClient`.
- Add typed UI snapshot/result fields in `contracts/types.py` before wiring them into UI runners.
- Keep API runner payloads as dicts that match the Go worker contract; tests should assert the exact returned keys when adding fields.
- Use `config.toml` as the only local configuration source. Environment variables intentionally do not override it.
- Preserve `once` mode compatibility when changing snapshot parsing or runner contracts.
