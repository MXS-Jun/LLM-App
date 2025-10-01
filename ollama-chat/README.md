# 🤖 Ollama Chat — 基于 Ollama 的本地大模型聊天界面

**Ollama Chat** 是一个轻量级、可配置的 Web 聊天界面，基于 [Ollama](https://ollama.com/) 本地大模型服务构建，使用 [Gradio](https://www.gradio.app/) 实现交互式前端。它支持自定义系统提示词、上下文窗口大小、温度等参数，并具备对话记忆与流式响应功能。

> 💡 本项目旨在提供一个开箱即用、易于部署和定制的本地 LLM 聊天客户端。

---

## 📦 功能特性

- ✅ **本地部署**：完全运行在本地，无需联网（前提是 Ollama 服务已本地部署）
- ✅ **流式响应**：支持逐字输出，提升交互体验
- ✅ **对话记忆**：自动维护对话历史，支持清空
- ✅ **灵活配置**：
  - 自定义系统提示词（`system_prompt.md`）
  - 调整上下文窗口（`num_ctx`）
  - 控制生成温度（`temperature`）
- ✅ **多会话隔离**：每个浏览器会话拥有独立的对话状态
- ✅ **美观简洁的 UI**：基于 Gradio 构建，支持深色/浅色主题

---

## 🛠️ 快速开始

### 1. 环境要求

- Python 3.9+
- 已安装并运行 [Ollama](https://ollama.com/)
- 推荐在 Linux / macOS / Windows (WSL) 上运行

### 2. 安装依赖

```bash
cd ollama-chat
pip install -r requirements.txt
```

### 3. 配置 Ollama 服务地址

编辑 `config.yaml` 文件，设置 Ollama 服务的 IP （默认为 `127.0.0.1`）和端口（默认为 `11434`）：

```yaml
ip: 127.0.0.1
port: 11434
model:
  name: qwen3:4b-instruct   # 确保该模型已在 Ollama 中 pull
  options:
    num_ctx: 8192
    temperature: 0.7
```

> 💡 若 Ollama 服务运行在服务器，请将 `ip` 改为服务器 IP。

### 4. 启动应用

```bash
python app.py
```

启动成功后，终端将显示类似：

```
[INFO] config.yaml read successfully
[INFO] system_prompt.md read successfully
[INFO] Ollama service is available
Running on local URL:  http://127.0.0.1:7860
```

打开浏览器访问 `http://127.0.0.1:7860` 即可开始聊天！

---

## ⚙️ 自定义系统提示词

系统提示词定义在 `system_prompt.md` 中，用于指导模型行为。默认内容如下：

```markdown
# Role
You are a helpful, honest, and harmless AI assistant.

# Behavior Guidelines
Please answer users' questions in a clear and concise style.

# Scope & Limitations
If you don't know the answer, please say 'I don't know'.

# Output Format
If it is necessary to answer user questions step by step, present the steps in a list form.
```

你可以在 **Settings** 标签页中实时修改提示词，或直接编辑该文件后重启应用。

---

## 📁 项目结构

```
ollama-chat/
├── app.py                # 主程序入口（Gradio 应用）
├── config.yaml           # Ollama 服务地址与模型配置
├── system_prompt.md      # 默认系统提示词
├── ollama-logo.png       # 网页 favicon
├── requirements.txt      # Python 依赖
└── README.md             # 本说明文件
```

---

## 🔒 注意事项

- 本项目**不包含模型本身**，需提前通过 `ollama pull <model>` 下载模型（如 `qwen3:4b-instruct`）。
- 确保 Ollama 服务正在运行且可通过配置的 `ip:port` 访问。
- 若修改 `config.yaml` 中的模型名，请确认该模型已安装。

---

## 🧩 依赖说明

- [`ollama`](https://github.com/ollama/ollama)：Python 客户端，用于与 Ollama 服务通信
- [`gradio`](https://gradio.app/)：快速构建机器学习/Web UI
- [`pyyaml`](https://pyyaml.org/)：解析 YAML 配置文件

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)（如有），欢迎自由使用、修改与分发。

---

## 🙌 致谢

- [Ollama](https://ollama.com/) — 让本地运行大模型变得简单
- [Gradio](https://gradio.app/) — 快速构建交互式 AI 应用
