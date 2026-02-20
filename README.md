# InfiniteTalk & Wan2GP All-in-one

一个“即开即用”的本地整合包，旨在让普通用户无需手工配置即可运行并体验先进的空间计算与视频生成模型。

## 🎯 设计策略（双引擎架构）

当前架构采用了**双引擎抽象适配层**：
- **默认引擎**：`Wan2GP`（作为 [deepbeepmeep/Wan2GP](https://github.com/deepbeepmeep/Wan2GP) 的适配器，注重稳定性和低 VRAM 支持，适合整合包兜底首发）。
- **质量引擎**：`InfiniteTalk`（作为 [MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) 的适配器，提供高质量、稀疏帧驱动的长视频语音克隆合成）。

系统具备**智能路由与回退策略**（Fallback机制）：当尝试调用高质量引擎（InfiniteTalk）发生 OOM 或错误时，系统能自动回退至兼容模式（Wan2GP），从而保证任务的稳定完成，杜绝“静默失败”。

## 🚀 快速启动 (Quick Start)

为确保开箱即用，我们在工程中内置了完整的运行脚本、自检流程和 SQLite 任务持久化。

### 前提条件
- 已安装 Python 3.10+。

### 启动命令
**Linux / macOS**
```bash
bash ./start.sh
```

**Windows**
```bat
start.bat
```

启动脚本将自动检测端口冲突、创建虚拟环境、安装依赖、并初始化 `data/` 和 `logs/` 目录结构。
启动成功后，浏览器访问：[http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📁 存储结构设计
- `data/sqlite.db`: 存储所有的任务与声音模型记录，重启后状态不丢失。
- `data/uploads/`: 用户上传的音频、图片文件。
- `data/outputs/`: 最终生成的视频结果存放地。
- `logs/app.log`: API 服务的主日志。
- `logs/worker.log`: 引擎后台处理与降级的详细日志。

## 🔧 API 契约示例

你可以通过 `curl` 调用核心 API（目前引擎层处于模拟执行状态）：

**1. 声音克隆 (Clone Voice)**
```bash
curl -X POST http://127.0.0.1:8000/api/voice/clone -H "Content-Type: application/json"
# 返回: {"voice_id": "voice_1234abcd", "status": "ready", "engine": "wan2gp"}
```

**2. 创建生成任务 (Create Job)**
```bash
curl -X POST http://127.0.0.1:8000/api/jobs \
     -H "Content-Type: application/json" \
     -d '{"voice_id": "voice_1234abcd", "avatar_url": "url", "script_mode": "manual", "script_input": "测试", "preferred_engine": "auto"}'
# 返回: {"job_id": "job_9876efgh", "selected_engine": "wan2gp"}
```
> `preferred_engine` 可选 `auto`, `wan2gp`, `infinitetalk`。

**3. 查询任务状态 (Check Status)**
```bash
curl http://127.0.0.1:8000/api/jobs/job_9876efgh
# 包含 progress, status, message, fallback_reason 等信息。
```

## 🛠️ 常见错误与排查

1. **端口 `:8000` 被占用**
   脚本会拦截并提示。请关闭其他占用该端口的服务（例如正在运行的旧版）。
2. **InfiniteTalk 回退到 Wan2GP**
   这是预期内的设计。前端 UI 会自动亮起橙色警告并展示出回退原因，任务会由兼容引擎继续完成。
3. **查阅失败原因**
   请直接查阅整合包目录下的 `logs/worker.log`，内含详细的 Python CallStack 与错误信息。
