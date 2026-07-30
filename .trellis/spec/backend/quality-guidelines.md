# Quality Guidelines

## Test Style

The project currently uses pytest for API/control-plane behavior and unittest for config behavior.

Reference files:
- `tests/test_config.py`
- `tests/test_api_runner.py`
- `tests/test_control_plane_client.py`

Rules:
- Keep tests focused on behavior at stable boundaries: config loading, runner output payloads, control-plane response handling, and runtime variable flow.
- Use monkeypatching for external HTTP execution, as in `tests/test_api_runner.py`.
- Use fake clients for control-plane item reporting rather than starting a real Go service.
- When changing config behavior, preserve tests that temporarily change cwd and restore environment/module state.
- When adding API runner behavior, assert both final status and exact request/result fields affected by the change.

## Verification Commands

Use the commands documented by the README:

```powershell
uv run python -m compileall src/test_worker
uv run python -m unittest tests.test_config -v
uv run pytest
```

Current environment note: if `uv run` fails because the local `.venv` is malformed or locked, use the installed uv-managed Python directly for read-only validation, or repair the environment before treating test failure as product failure.

## Dependency And Runtime Constraints

Project runtime dependencies are intentionally small:
- Python `>=3.12`
- `playwright>=1.52.0`
- `httpx>=0.28.0`

Reference files:
- `pyproject.toml`
- `requirements.txt`

Rules:
- Do not add new dependencies for simple JSON/TOML/path logic already handled by the standard library.
- Keep async boundaries clear: Playwright and API request execution are async, while `ControlPlaneClient` currently uses synchronous `httpx.Client`.
- Install Chromium for UI execution with `uv run playwright install chromium` when validating browser behavior.

## Common Anti-Patterns

- Do not update only API or only UI task handling when a change affects both poll and once modes.
- Do not skip control-plane serialization tests when adding nested UI result fields; nested fields must become camelCase.
- Do not reuse the same mutable list across dataclass results; use `field(default_factory=list)`.
- Do not store artifacts outside `artifacts_root_dir / run_id` unless the control-plane contract changes too.
- Do not confuse a rule failure (`failed`) with runner infrastructure failure (`error`).
