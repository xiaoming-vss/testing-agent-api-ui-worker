# Directory Structure

## Package Boundary

The installable package is `test_worker` under `src/`. New runtime code should stay inside this package and follow the current layer boundaries instead of adding top-level scripts.

Reference files:
- `pyproject.toml`
- `src/test_worker/__main__.py`
- `src/test_worker/core/config.py`

## Layer Ownership

`core/` owns process-level utilities:
- `config.py` loads `config.toml`, resolves defaults, and produces `WorkerConfig`.
- `logger.py` writes UTC timestamped stdout logs with optional JSON metadata.

`contracts/` owns typed UI worker contracts:
- Add or rename UI snapshot/result fields in `contracts/types.py` first.
- Keep Literal status and task-type unions near their dataclasses.
- Do not scatter UI dataclass definitions into runners.

`control_plane/` owns Go control-plane communication:
- Endpoint paths, `X-Worker-Token`, request timeouts, response envelope unwrapping, and snake_case-to-camelCase result serialization belong in `ControlPlaneClient`.
- Runners should receive snapshots and return results; they should not construct internal endpoint paths.

`poller/` owns orchestration:
- `TaskPoller.start()` claims UI tasks first, then API tasks, then sleeps by `poll_interval_ms`.
- Task-specific heartbeat loops and error-reporting payloads belong in `task_poller.py`.

`ui/` owns Playwright execution:
- `case_runner.py` handles one UI case with its own browser context.
- `suite_runner.py` handles multiple suite items in order and reports item-level progress when a control-plane client is present.
- `step_executor.py`, `locator.py`, and `templates.py` contain reusable step primitives.

`api/` owns HTTP API execution:
- `case_runner.py` builds requests, executes them, runs extract/assert rules, and returns completion dicts.
- `collection_runner.py` runs API cases sequentially and carries `runtime_vars` between items.
- `http_client.py`, `rule_runtime.py`, and `template_runtime.py` should stay small and reusable.

## Where To Add New Work

- New UI step keyword: add handling in `ui/step_executor.py`, any locator support in `ui/locator.py`, and tests around the runner or executor behavior.
- New API body type or request rendering behavior: add it to `api/case_runner.py` and shared rendering helpers in `api/template_runtime.py`.
- New extract/assert comparator or source: add it to `api/rule_runtime.py` and cover it in `tests/test_api_runner.py` or a new focused test file.
- New control-plane endpoint: add a public method to `ControlPlaneClient`, keep the endpoint path there, and update `log_planned_contract()` when it is part of the planned worker contract.

## Avoid

- Do not add database guidance or persistence code to this worker; current persistence lives in the Go control plane.
- Do not put generated artifacts, `egg-info`, `__pycache__`, or local virtual environment files into specs or source patterns.
- Do not bypass the existing package entry point `testing-agent-api-ui-worker = "test_worker.__main__:main"` when adding startup behavior.
