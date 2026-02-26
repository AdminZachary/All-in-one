# InfiniteTalk & Wan2GP All-in-one

> 一款「即开即用」的本地数字人视频生成整合包。支持声音克隆 + 数字人形象驱动，无需手工配置复杂 GPU 环境即可体验高质量视频合成。

---

## 📑 目录

- [功能概览](#功能概览)
- [系统要求](#系统要求)
- [快速启动](#快速启动)
- [安装 Wan2GP 推理引擎](#安装-wan2gp-推理引擎)
- [配置说明](#配置说明)
- [目录结构](#目录结构)
- [API 参考](#api-参考)
- [双引擎架构](#双引擎架构)
- [常见问题排查](#常见问题排查)
- [开发者指引](#开发者指引)

---

## 功能概览

| 功能 | 说明 |
|------|------|
| 🎙️ 声音克隆 | 上传音频样本，系统提取声纹特征用于视频合成 |
| 🧑‍💻 数字人生成 | 支持 Wan2GP（t2v 1.3B/14B）、Hunyuan Avatar、Wan Multitalk |
| 🔄 引擎回退 | InfiniteTalk → Wan2GP 自动降级，任务永不静默失败 |
| 📦 任务持久化 | SQLite 存储任务状态，重启后任务不丢失 |
| 🌐 REST API | 完整 HTTP API，支持浏览器/curl 访问 |

---

## 系统要求

| 组件 | 最低要求 |
|------|---------|
| OS | Windows 10/11 64-bit（推荐）；Linux/macOS 亦可 |
| Python | **3.10 或 3.11**（源码启动模式） |
| GPU | NVIDIA GPU，VRAM ≥ 8GB（运行 Wan2GP 推理引擎） |
| CUDA | 12.4（配合 PyTorch 2.5.1 使用） |
| 磁盘空间 | 至少 **30 GB** 可用空间（含模型权重） |

> **仅运行后端 API（无推理）**：任意主流 PC 均可，不需要 GPU。

---

## 快速启动

### 方式一：源码启动（推荐开发/调试）

**1. 克隆仓库**
```bash
git clone https://github.com/AdminZachary/All-in-one.git
cd All-in-one
```

**2. 复制并编辑环境变量**
```bash
cp .env.example .env
# 使用文本编辑器打开 .env，根据实际情况修改端口和缓存目录
```

**3a. Windows 一键启动**
```bat
start.bat
```

**3b. Linux / macOS**
```bash
bash ./start.sh
```

启动脚本将自动完成：
- 检测端口 `8000` 是否被占用
- 创建 Python 虚拟环境 `.venv/`
- 安装 `requirements.txt` 中的依赖
- 创建 `data/` 和 `logs/` 目录
- 启动 FastAPI 后端（uvicorn）

**4. 访问 WebUI**

浏览器打开：[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 方式二：手动安装

```bash
# 创建虚拟环境
py -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

---

## 安装 Wan2GP 推理引擎

> Wan2GP 是本地 GPU 推理引擎，需要**额外安装**。后端 API 可在不安装引擎的情况下正常运行（任务会以错误状态结束）。

### 步骤

1. 确保 `wan2gp_core/` 目录已存在于项目根目录（其中包含 Wan2GP 源码）。
2. 在项目根目录执行（Windows）：
   ```bat
   install_wan2gp.bat
   ```
3. 脚本将自动：
   - 下载**可携带版 Python 3.10**（独立沙盒，不污染系统环境）
   - 安装 **PyTorch 2.5.1 + CUDA 12.4**（约 3GB 下载）
   - 安装 Wan2GP 所有依赖

4. 安装完成后，重启后端即可在 UI 中选择本地 GPU 进行推理。

> **注意**：首次运行某模型时，系统会从 HuggingFace 自动拉取对应权重文件（可能需要额外 5-20GB 空间）。建议通过 `.env` 将 HF 缓存目录设置到空间充裕的磁盘。

---

## 配置说明

所有配置通过项目根目录的 `.env` 文件管理。复制 `.env.example` 后按需修改：

```ini
# 后端监听地址与端口
HOST=127.0.0.1
PORT=8000

# HuggingFace 模型缓存目录
# 默认会写入 C 盘用户目录，建议改到空间充裕的磁盘
HF_HOME=D:\hf_cache
TRANSFORMERS_CACHE=D:\hf_cache\hub
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | `127.0.0.1` | 服务监听地址，`0.0.0.0` 可局域网访问 |
| `PORT` | `8000` | 服务监听端口 |
| `HF_HOME` | 系统默认 | HuggingFace 模型权重存储路径 |
| `TRANSFORMERS_CACHE` | 系统默认 | Transformers 模型缓存路径 |

---

## 目录结构

```
All-in-one/
├── backend/
│   ├── api/
│   │   └── routes.py          # FastAPI 路由（声音克隆、任务管理）
│   ├── engines/
│   │   ├── base.py            # 引擎抽象基类
│   │   ├── wan2gp_adapter.py  # Wan2GP 引擎适配器
│   │   └── infinitetalk_adapter.py  # InfiniteTalk 引擎适配器
│   ├── models/                # Pydantic 数据模型
│   ├── services/              # 业务逻辑层（任务队列、引擎路由）
│   ├── storage/
│   │   ├── setup.py           # 目录与数据库初始化
│   │   └── db.py              # SQLite 数据访问层
│   ├── utils/
│   │   ├── config.py          # 环境变量读取与路径配置
│   │   ├── logger.py          # 日志配置（app + worker）
│   │   ├── downloader.py      # 模型下载辅助
│   │   └── wan2gp_runner.py   # Wan2GP 原生子进程执行器
│   └── main.py                # FastAPI 应用入口
│
├── wan2gp_core/               # Wan2GP 原生仓库（需自行放置）
│   └── python_env/            # 由 install_wan2gp.bat 创建（不提交 git）
│
├── data/                      # 运行时数据（不提交 git）
│   ├── uploads/               # 用户上传的音频/图片
│   ├── outputs/               # 生成的视频文件
│   ├── hf_cache/              # HuggingFace 模型缓存
│   └── sqlite.db              # SQLite 任务数据库
│
├── logs/                      # 日志文件（不提交 git）
│   ├── app.log                # API 服务日志
│   └── worker.log             # 推理引擎及回退详细日志
│
├── .env                       # 本地环境变量（不提交 git）
├── .env.example               # 环境变量模板（提交 git）
├── requirements.txt           # Python 依赖
├── start.bat                  # Windows 一键启动脚本
├── start.sh                   # Linux/macOS 启动脚本
├── install_wan2gp.bat         # Wan2GP GPU 引擎一键安装脚本
├── All-in-one.spec            # PyInstaller 打包配置
└── build.py                   # 自动化打包脚本
```

---

## API 参考

基础 URL：`http://127.0.0.1:8000/api`

### 1. 声音克隆

```
POST /api/voice/clone
Content-Type: multipart/form-data

# 表单字段
audio_file: <音频文件>
```

响应：
```json
{
  "voice_id": "voice_1234abcd",
  "status": "ready",
  "engine": "wan2gp"
}
```

### 2. 创建视频生成任务

```
POST /api/jobs
Content-Type: application/json
```

请求体：
```json
{
  "voice_id": "voice_1234abcd",
  "avatar_url": "https://example.com/avatar.jpg",
  "script_mode": "manual",
  "script_input": "你好，欢迎使用数字人生成系统。",
  "preferred_engine": "auto",
  "wangp_model": "Wan t2v 1.3B"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `voice_id` | string | 克隆声音 ID |
| `avatar_url` | string | 数字人参考图片 URL 或本地路径 |
| `script_mode` | `manual` / `auto` | 手动输入台词 / 自动生成 |
| `script_input` | string | 台词内容（`manual` 模式必填） |
| `preferred_engine` | `auto` / `wan2gp` / `infinitetalk` | 引擎选择，`auto` 系统自动路由 |
| `wangp_model` | string | 模型选择，见下表 |

**可用模型（`wangp_model`）**：

| 值 | 说明 |
|----|------|
| `Wan t2v 1.3B` | 轻量文生视频，低 VRAM 友好 |
| `Wan t2v 14B` | 高质量文生视频 |
| `Hunyuan Avatar` | 混元数字人（需图片 + 音频） |
| `Wan Multitalk` | 多人对话数字人 |
| `Fantasy` | 幻想风格视频 |

响应：
```json
{
  "job_id": "job_9876efgh",
  "selected_engine": "wan2gp",
  "status": "queued"
}
```

### 3. 查询任务状态

```
GET /api/jobs/{job_id}
```

响应：
```json
{
  "job_id": "job_9876efgh",
  "status": "processing",
  "progress": 45,
  "message": "Generating frames...",
  "fallback_reason": null
}
```

| `status` 值 | 说明 |
|-------------|------|
| `queued` | 等待处理 |
| `processing` | 推理进行中 |
| `completed` | 生成成功 |
| `failed` | 生成失败，查看 `message` 字段 |
| `fallback` | 已从 InfiniteTalk 回退至 Wan2GP |

### 4. 下载生成结果

```
GET /api/jobs/{job_id}/result
```

返回视频文件（`video/mp4`）。

### 5. 健康检查

```
GET /health
```

响应：`{"ok": true}`

---

## 双引擎架构

```
用户请求
    │
    ▼
引擎路由层（preferred_engine）
    │
    ├─ auto / infinitetalk ──► InfiniteTalk Adapter
    │                               │
    │                          失败/OOM
    │                               │
    │                               ▼
    └─ wan2gp ──────────────► Wan2GP Adapter
                                    │
                               run_native_wan2gp_job()
                                    │
                               wan2gp_core/python_env/python.exe
                               （独立进程 + 独立 CUDA 环境）
```

- **InfiniteTalk**：高质量稀疏帧驱动，长视频能力优秀，但 VRAM 需求较高。
- **Wan2GP**：基于 deepbeepmeep/Wan2GP，低 VRAM 兼容，支持多种模型类型，作为兜底引擎。
- **回退逻辑**：系统在 OOM 或引擎错误时自动降级，`fallback_reason` 字段记录原因，前端 UI 会以橙色警告展示。

---

## 常见问题排查

### ❌ 端口 8000 被占用

```
[Error] Port 8000 is already in use.
```

**解决**：关闭已运行的旧版本，或在 `.env` 中修改 `PORT=8001`。

### ❌ Wan2GP Process exited with code 1

**排查步骤**：
1. 确认已运行 `install_wan2gp.bat`，且安装成功。
2. 查看 `logs/worker.log` 中的详细 Python 报错栈。
3. 确认 `wan2gp_core/python_env/python.exe` 文件存在。
4. CUDA 版本须与 PyTorch 对应（当前要求 CUDA 12.4）。

### ❌ 模型下载失败 / HuggingFace 超时

1. 检查网络代理设置（部分地区需要代理访问 HF）。
2. 在 `.env` 中设置 `HF_HOME` 到磁盘空间充裕的目录。
3. 也可手动从 [huggingface.co](https://huggingface.co) 下载对应模型，放入 `HF_HOME` 指定目录。

### ❌ InfiniteTalk 回退到 Wan2GP

这是**预期行为**。前端 UI 会亮起橙色提示并展示回退原因，任务会由兼容引擎继续完成，视频仍会正常生成。

### ❌ 日志查阅

| 日志文件 | 内容 |
|---------|------|
| `logs/app.log` | API 请求、路由、启动信息 |
| `logs/worker.log` | 推理引擎执行、回退、错误 CallStack |

---

## 开发者指引

### 环境搭建

```bash
git clone https://github.com/AdminZachary/All-in-one.git
cd All-in-one
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 开发模式启动

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

`--reload` 开启热重载，代码修改后自动生效。

### 打包为可执行文件（PyInstaller）

```bash
python build.py
```

或手动：
```bash
pyinstaller All-in-one.spec
```

生成的 `dist/All-in-one.exe` 即为单文件便携版，用户无需安装 Python。

### 新增引擎适配器

1. 在 `backend/engines/` 下创建新适配器，继承 `BaseEngineAdapter`。
2. 实现 `name` 属性和 `process_job()` 方法。
3. 在 `backend/services/` 的路由逻辑中注册新引擎。

```python
# backend/engines/my_engine.py
from backend.engines.base import BaseEngineAdapter

class MyEngineAdapter(BaseEngineAdapter):
    @property
    def name(self) -> str:
        return "my_engine"

    async def process_job(self, job_id, voice_id, avatar_url, script_text, **kwargs) -> str:
        # 实现推理逻辑
        ...
        return f"/api/jobs/{job_id}/result"
```

### 代码结构约定

- **日志**：使用 `backend/utils/logger.py` 中的 `app_logger` 或 `worker_logger`，不要使用 `print()`。
- **路径**：使用 `backend/utils/config.py` 中定义的 `DATA_DIR`、`OUTPUTS_DIR` 等常量，保证 PyInstaller 打包兼容性。
- **异步**：引擎的 `process_job` 为 `async` 方法，CPU 密集操作用 `asyncio.to_thread()` 包裹。

---

## License

MIT License. See [LICENSE](LICENSE) for details.
