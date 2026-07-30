# testing-agent-api-ui-worker

`testing-agent-api-ui-worker` 是 `testing-agent` 的独立 API/UI 测试执行器项目。它在一个 worker 进程内支持：

- UI Playwright 用例和测试集任务
- API HTTP 单用例和集合任务
- poll 模式轮询 Go 控制面领取任务
- once 模式基于本地 snapshot 调试 UI 或 API

## 项目结构

```text
testing-agent-api-ui-worker/
├── config.toml
├── config.example.toml
├── pyproject.toml
├── README.md
├── src/
│   └── test_worker/
│       ├── __main__.py
│       ├── api/             # API HTTP runner、规则和模板运行时
│       ├── contracts/       # worker 内部数据类型
│       ├── control_plane/   # Go 控制面客户端
│       ├── core/            # 配置和日志
│       ├── poller/          # poll 模式任务调度
│       └── ui/              # Playwright UI runner
└── tests/
```

## 安装

```powershell
uv sync
uv run playwright install chromium
```

开发依赖：

```powershell
uv sync --extra dev
```

## 配置

默认读取当前工作目录或项目根目录下的 `config.toml`。Worker 不读取 `.env` 或环境变量，所有本地启动配置都放在 TOML 中。

常用配置：

```toml
mode = "poll"

[control_plane]
base_url = "http://127.0.0.1:8000"
worker_token = "replace-with-worker-token"

[worker]
id = ""
poll_interval_ms = 3000
request_timeout_ms = 15000
heartbeat_interval_ms = 10000

[ui]
artifacts_dir = "./artifacts"
headless = true
slow_mo_ms = 0
trace_enabled = true
screenshot_on_failure = true

[once]
snapshot_file = ""
```

`worker_token` 要和 Go 后端配置里的 `security.worker.key` 一致。

## 启动

poll 模式：

```powershell
cd D:\GoProjects\testing-agent-api-ui-worker
uv run python -m test_worker
```

once 模式：把 `config.toml` 改成：

```toml
mode = "once"

[once]
snapshot_file = "./snapshot.json"
```

然后启动：

```powershell
uv run python -m test_worker
```

`snapshot.json` 可以是 `/internal/ui-worker/*/snapshot` 或 `/internal/api-worker/*/snapshot` 返回内容，也可以直接是其中的 `caseRun`、`suiteRun` 或 `collectionRun`。

安装后也可以使用脚本入口：

```powershell
uv run testing-agent-api-ui-worker
```

## 验证

```powershell
uv run python -m compileall src/test_worker
uv run python -m unittest tests.test_config -v
uv run pytest
```
