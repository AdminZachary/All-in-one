# All-in-one

一个“即开即用”的本地整合包原型：
- 前端：`1.html`（沉浸式控制台 UI）
- 后端：`FastAPI`（声音克隆、任务创建、进度查询）
- 启动脚本：`start.sh` / `start.bat`

## 设计策略（关于 Wan2GP vs InfiniteTalk）
当前版本采用**双引擎抽象**：
- 默认引擎：`Wan2GP`（稳定优先，适合整合包首发）
- 可选引擎：`InfiniteTalk`（质量优先，可作为增强模式）

后端通过 `preferred_engine` 字段路由，前端不需要直接耦合底层实现。

## 快速启动
### Linux / macOS
```bash
./start.sh
```

### Windows
```bat
start.bat
```

启动后访问：
- `http://127.0.0.1:8000`

## API（当前原型）
- `GET /health`
- `POST /api/voice/clone`
- `POST /api/jobs`
- `GET /api/jobs/{job_id}`

## 说明
本仓库目前先完成了“前后端贯通 + 可启动”的整合包骨架。
真实模型推理可在后续将 `choose_engine` 路由到具体的 Wan2GP / InfiniteTalk 调用器。
