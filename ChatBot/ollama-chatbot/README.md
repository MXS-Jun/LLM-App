# Ollama Chatbot

## 介绍

利用 Gradio + Ollama 实现的【聊天机器人】Web 应用。

## 使用方法

### 配置 Ollama 服务

按照 Ollama 官方教程安装并运行 Ollama 服务。

本程序默认使用：

- HOST：`http://localhost:11434`
- MODEL：`qwen3:4b-instruct`

更多配置，请参考 `config.yaml` 中的条目。

### 配置虚拟环境

本程序基于 `Python 3.12` 开发。

安装依赖：

```bash
pip install gradio
pip install ollama
```

### 本地运行程序

执行命令：

```bash
cd /the/path/to/ollama-chatbot
python main.py
```

然后在浏览器访问 `http://127.0.0.1:7860/` 即可使用。

> 暂未适配思考模型：因为无法渲染<think>标签，所以思考过程不可见
