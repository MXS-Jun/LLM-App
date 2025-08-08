# Ollama Chatbot

## 介绍

利用 Gradio + Ollama 实现的【聊天机器人】Web 应用。

<img width="1507" height="954" alt="image" src="https://github.com/user-attachments/assets/783e7f27-8c8b-4eb2-839b-139499d22a73" />

## 使用方法

### 配置 Ollama 服务

按照 Ollama 官方教程安装并运行 Ollama 服务。

本程序默认使用：
- API 接口：`http://localhost:11434/api/chat`
- 模型：`qwen3:4b-instruct`

> 暂未适配思考模型：因为无法渲染<think>标签，所以思考过程不可见

### 配置虚拟环境

本程序基于 `Python 3.12` 开发，可利用 `conda` 或 `venv` 等工具创建虚拟环境。

创建并激活虚拟环境后，安装依赖：

```bash
pip install gradio
pip install json
pip install requests
pip install yaml
```

### 运行程序

在同一个虚拟环境内，执行命令：

```bash
cd /the/path/to/ollama-chatbot
python ./main.py
```

然后在浏览器访问 `http://127.0.0.1:7860/` 即可使用。
