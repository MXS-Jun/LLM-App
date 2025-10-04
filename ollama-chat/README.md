# Ollama Chat

基于 Ollama 和 Gradio 的聊天机器人 Web 应用，支持思考模式，可实时调整系统提示词、上下文窗口大小和温度，具备会话隔离功能。

可以利用本项目快速地调试自定义的 Ollama 模型。

## 1 安装

### 1.1 安装 Python 环境

```bash
cd /the/path/to/ollama-chat
conda create -n llm-app python=3.12
conda activate llm-app
pip install -r requirements.txt
```

### 1.2 安装 Ollama 服务

参考 [Ollama 官网](https://ollama.com/) 的教程。

### 1.3 拉取 Ollama 模型

```bash
ollama pull qwen3:4b-instruct
ollama pull qwen3:4b-thinking
```

## 2 快速开始

### 2.1 启动程序

```bash
python app.py
```

### 2.2 使用应用

浏览器访问链接 [127.0.0.1:7860](127.0.0.1:7860) 即可使用。

## 3 配置文件

### 3.1 config.yaml

```yaml
ip: 127.0.0.1                  # Ollama 服务端的 IP
port: 11434                    # Ollama 服务端的端口
model:
  instruct: qwen3:4b-instruct  # 非思考模型
  thinking: qwen3:4b-thinking  # 思考模型
  options:
    num_ctx: 8192              # 上下文窗口大小
    temperature: 0.7           # 温度
```

### 3.2 system_prompt.md

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

## 4 许可证

[MIT License](../LICENSE)