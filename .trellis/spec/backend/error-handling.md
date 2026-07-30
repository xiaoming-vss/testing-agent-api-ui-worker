# Error Handling And Logging

## Failure Categories

The worker distinguishes normal assertion failures from unexpected execution errors.

UI runner pattern:
- A step exception becomes a failed `UiStepRunResult`.
- If `continue_on_failure` is false or absent, the case stops after the failed step.
- A runner-level exception becomes case or suite status `error`.
- Suite item failures set the suite status to `failed`; suite item errors set the suite status to `error`.

API runner pattern:
- Extract/assert rule mismatch or failed extraction makes the API case status `failed`.
- Request rendering, HTTP execution, JSON parsing, unsupported source/comparator, or other unexpected exceptions make the API case status `error`.
- API collection status is `error` if any item errors, `failed` if any item fails, otherwise `success`.

Reference files:
- `src/test_worker/ui/case_runner.py`
- `src/test_worker/ui/suite_runner.py`
- `src/test_worker/api/case_runner.py`
- `src/test_worker/api/collection_runner.py`
- `src/test_worker/api/rule_runtime.py`

## Reporting Errors

`TaskPoller` should always try to report task completion even when execution fails.

Rules:
- For UI task errors, build `UiCaseRunResult` or `UiSuiteRunResult` with status `error` in `_report_task_error()`.
- For API task errors, report a completion dict with `status: "error"`, a blank request, a zero-status response, empty rule results, and the original `startedAt`.
- Keep heartbeat cancellation in `finally` blocks so task cleanup does not leave background tasks running.
- Log failures to report errors, but do not let report-failure exceptions crash the poller loop.

Reference file:
- `src/test_worker/poller/task_poller.py`

## Control-Plane HTTP Errors

`ControlPlaneClient._request()` wraps HTTP and JSON problems with endpoint context.

Rules:
- Include method, pathname, HTTP status code, and response text for `httpx.HTTPStatusError`.
- Treat HTTP 204 and empty response bodies as `None`.
- Use `_unwrap_response_data()` to accept both standard `{code, data}` envelopes and bare worker responses.

Reference files:
- `src/test_worker/control_plane/client.py`
- `tests/test_control_plane_client.py`

## Logging

The local logger is intentionally simple stdout logging.

Reference file:
- `src/test_worker/core/logger.py`

Rules:
- Use `logger.info`, `logger.warn`, or `logger.error` with a short stable message and metadata dict.
- Keep timestamps UTC ISO strings.
- Keep metadata JSON serialized with `ensure_ascii=False` so Chinese error messages remain readable.
- Include task identifiers such as `taskId`, `runId`, `taskType`, `itemId`, or `stepOrderNo` when available.

Avoid:
- Do not introduce a separate logging framework without updating all call sites and tests.
- Do not print raw exceptions directly from runners; use the logger boundary or return `errorMessage` in the worker result payload.
