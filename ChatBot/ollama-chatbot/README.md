# Ollama Chatbot

基于 Gradio 和 Ollama 构建的轻量型聊天机器人 Web 应用。

## 核心特性

- 本地部署：无需依赖云端服务，数据隐私可控。
- 快速启动：极简配置，3 分钟内完成部署。
- Web 界面：基于 Gradio 的直观交互界面，支持上下文对话。
- 灵活配置：通过配置文件轻松修改应用参数。

## 环境准备

### 准备 Ollama

在 [Ollama 官网](https://ollama.com/) 根据指示来安装 Ollama，并启动 Ollama 服务。

拉取大模型：

```bash
ollama pull <model>
```

> 更多 Ollama 相关的配置，请参考 `config.yaml` 中的条目。

### 安装 Python 及相关依赖

本程序基于 `Python 3.12` 开发。

安装 `Python` 后，执行下列命令安装依赖：

```bash
pip install gradio
pip install ollama
```

## 运行程序

执行命令：

```bash
cd /the/path/to/ollama-chatbot
python main.py
```

然后在浏览器访问 `http://127.0.0.1:7860/` 即可使用。

> 暂未适配思考模型：因为无法渲染 `<think>` 标签，所以思考过程不可见。
