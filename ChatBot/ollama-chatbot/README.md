# Ollama Chatbot

## 介绍

利用 Gradio + Ollama 实现的【聊天机器人】Web 应用。

## 使用方法

### 配置 Ollama 服务

按照 Ollama 官方教程安装并运行 Ollama 服务。

本程序默认使用：
- API 接口：`http://localhost:11434/api/chat`
- 模型：`deepseek-r1:8b`

> 进入 Web UI 后可自定义 API 接口和模型。

### 配置虚拟环境

本程序基于 `Python 3.12` 开发，可利用 `conda` 或 `venv` 等工具创建虚拟环境。

创建并激活虚拟环境后，安装依赖：

```bash
pip install -r ./requirements.txt
```

### 运行程序

在同一个虚拟环境内，进入 `app` 文件夹：

```bash
cd ./app
```

执行命令：

```bash
python ./main.py
```

然后在浏览器访问 `http://127.0.0.1:7860/` 即可使用。