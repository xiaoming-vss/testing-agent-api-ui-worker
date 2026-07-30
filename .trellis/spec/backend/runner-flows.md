# Runner Flows

## Startup Modes

`src/test_worker/__main__.py` is the process boundary. It loads config, constructs runners, then routes to either `once` or `poll`.

Rules:
- Preserve both modes when changing snapshot parsing or runner constructor signatures.
- `poll` mode requires `[control_plane].base_url`; missing base URL should fail fast.
- `once` mode reads `[once].snapshot_file` and supports these snapshot shapes:
  - UI envelope with `taskType`, `caseRun`, or `suiteRun`.
  - API envelope with `api_case_debug` plus `caseRun`.
  - API envelope with `api_collection_run` plus `collectionRun`.
  - Direct suite snapshots with `items`.
  - Direct API case snapshots with `request` and `caseId`.

Avoid:
- Do not make `once` mode depend on a live control plane. API collection once mode uses `_NoopControlPlaneClient` for item reports.

## Poll Loop

`TaskPoller` owns long-running orchestration in `src/test_worker/poller/task_poller.py`.

Current flow:
- Log worker startup.
- Claim a UI task with `claim_task()`.
- If no UI task exists, claim an API task with `claim_api_task()`.
- If no task exists, sleep by `poll_interval_ms`.
- For claimed tasks, report started, start heartbeat, fetch snapshot, run the correct runner, report completed, then cancel heartbeat.

Rules:
- Keep heartbeat loops cancellable and swallow `asyncio.CancelledError` in the cleanup path.
- Preserve error-reporting fallbacks so the control plane receives an `error` completion even when execution fails before normal result creation.
- Use `heartbeat_interval_ms` for heartbeat loops and `poll_interval_ms` for idle/error loop delays.

## UI Execution

UI case and suite runners use Playwright Chromium with browser launch and context options resolved from the server-provided `suite` snapshot. Local `config.toml` must not decide UI `headless` or `slowMoMs`.

Reference files:
- `src/test_worker/ui/case_runner.py`
- `src/test_worker/ui/suite_runner.py`
- `src/test_worker/ui/step_executor.py`
- `src/test_worker/ui/locator.py`

Rules:
- Normalize steps from `case.steps` first; fall back to `case.steps_json`.
- Skip disabled steps with `enabled is False`.
- Sort steps by `order_no` and use `index + 1` as fallback order.
- Resolve `headless`, `slowMoMs`, viewport settings, `defaultStepTimeoutMs`, and `screenshotPolicy` from `caseRun.suite` or `suiteRun.suite`.
- Do not fall back to local config for UI browser mode, screenshot policy, or default step timeout.
- Use a default step timeout of 5000 ms only when the server-provided suite omits `defaultStepTimeoutMs`.
- Apply screenshot policy as: `on_failure` captures failed steps, `after_each_step` captures successful and failed steps, and `never` captures no automatic screenshots.
- Store UI artifacts under `artifacts_root_dir / run_id`; suite item artifacts go under `run_id / item_id`.
- When trace is enabled, write `trace.zip` under the run artifact directory and stop tracing during cleanup if execution exits early.
- Keep explicit `screenshot` keyword behavior independent of automatic screenshot policy.

Step keywords currently supported by `StepExecutor`:
- `open`, `reload`, `click`, `dblclick`, `input`, `clear`, `press`
- `wait_visible`, `wait_hidden`, `wait_text`
- `assert_text`, `assert_visible`, `assert_url`
- `screenshot`, `sleep`

Locator types currently supported:
- `css`, `xpath`, `text`, `placeholder`, `label`, `test_id` / `testid`, `role`

## API Execution

API runners use dict snapshots that already match the Go API worker contract.

Reference files:
- `src/test_worker/api/case_runner.py`
- `src/test_worker/api/collection_runner.py`
- `src/test_worker/api/http_client.py`
- `src/test_worker/api/rule_runtime.py`
- `src/test_worker/api/template_runtime.py`
- `tests/test_api_runner.py`

Rules:
- Render runtime variables with `{{ varName }}` syntax before sending requests or evaluating expected values.
- Preserve unknown template variables as their original `{{...}}` text.
- Support request body types `none`, `json`, `form`, and `raw` through `build_request()`.
- Carry collection runtime variables from one API case to later cases by updating `runtime_vars` after each item.
- Sort enabled extract and assert rules by `orderNo`.
- Treat extract/assert rule failures as case `failed`; unexpected exceptions are case `error`.
- In collections, disabled items or halted downstream items report `skipped`.

Avoid:
- Do not make API execution depend on UI dataclasses; the API worker path intentionally uses dict payloads.
- Do not add broad JSONPath support casually. Current JSON path support is simple `$.field.nested` and list index traversal.


