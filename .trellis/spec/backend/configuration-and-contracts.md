# Configuration And Contracts

## TOML Configuration

Local runtime configuration is loaded from `config.toml` only. `load_config()` checks the current working directory first and the project root second. Environment variables are intentionally ignored.

Reference files:
- `src/test_worker/core/config.py`
- `config.example.toml`
- `tests/test_config.py`

Rules:
- Add new local settings to `WorkerConfig` in `contracts/types.py`, then parse them in `core/config.py`.
- Keep defaults inside `core/config.py` helper calls so absent or invalid TOML fields degrade predictably.
- Use the existing helpers `_config_string`, `_config_int`, and `_config_bool` instead of direct dict reads in new config parsing.
- Keep `artifacts_root_dir` resolved to an absolute path, matching the current `Path(artifacts_dir).resolve()` behavior.

Avoid:
- Do not make environment variables override `config.toml`; `tests/test_config.py::test_environment_variables_do_not_override_config_toml` protects this behavior.
- Do not read `.env` files. The README explicitly says the worker does not read `.env` or environment variables for local startup configuration.

## Worker Contracts

UI worker payloads are represented by dataclasses and Literal unions in `src/test_worker/contracts/types.py`. This keeps UI runner code explicit and gives future changes one contract file to inspect.

Rules:
- Add UI task types, statuses, snapshot fields, and result fields in `contracts/types.py` before consuming them elsewhere.
- Prefer optional fields with `None` defaults for snapshot fields that may be absent from the Go control plane.
- Use `field(default_factory=list)` for result lists so each result has its own list.
- Keep status strings aligned with existing unions such as `UiStepStatus`, `UiCaseRunStatus`, `UiSuiteItemRunStatus`, and `UiSuiteRunStatus`.

## JSON Naming Boundary

The Python code uses snake_case dataclass fields. The Go control plane expects camelCase JSON payloads.

Reference files:
- `src/test_worker/control_plane/client.py`
- `tests/test_control_plane_client.py`

Rules:
- Serialize UI dataclass result payloads through `ControlPlaneClient._serialize_task_result()` or `_serialize_suite_item_result()` so nested fields become camelCase.
- Parse incoming UI snapshots explicitly from camelCase dict keys in `ControlPlaneClient._parse_case_run_snapshot()` and `_parse_suite_run_snapshot()`.
- When the control plane keeps `taskId` or `runId` at the outer snapshot layer, inject those values before parsing `caseRun` or `suiteRun` so runner-level item reports never build URLs with blank task IDs.
- Keep API runner completion payloads as camelCase dicts because `ApiCaseRunner` and `ApiCollectionRunner` already mirror the Go API worker contract directly.
- When the Go service wraps responses as `{code, message, data}`, read through `_unwrap_response_data()`. Tests currently cover standard envelope support for API claim responses.

Avoid:
- Do not return raw dataclass `asdict()` output directly to control-plane methods; it uses snake_case.
- Do not duplicate endpoint path strings in runners or tests when a `ControlPlaneClient` method is the correct boundary.

