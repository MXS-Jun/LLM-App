# Ollama Chatbot

一个基于 Ollama 和 Gradio 的简单聊天机器人应用，支持与本地 Ollama 模型进行交互式对话。

## 项目简介

本项目通过 Gradio 构建 Web 交互界面，连接本地运行的 Ollama 服务，实现与指定大语言模型的实时聊天功能。支持流式输出响应，配置灵活，可根据需求调整模型参数。

## 功能特点

- 基于 Gradio 的直观聊天界面，支持消息式交互。
- 连接本地 Ollama 服务，支持自定义模型。
- 可配置模型参数（上下文长度、温度值等）。
- 流式输出响应，提升聊天体验。

## 依赖安装

1. 确保已安装 Python 3.12+。
2. 安装依赖包：

```bash
pip install gradio
pip install ollama
pip install pyyaml
```

## 环境准备

1. 安装并启动 Ollama 服务：

   - 参考官方文档安装 Ollama：[https://ollama.com/download](https://ollama.com/download)。
   - 启动 Ollama 服务（默认端口为 11434）。

2. 拉取所需模型（以配置文件中的模型为例）：

```bash
ollama pull qwen3:4b-instruct
```

## 配置说明

项目配置文件为 `config.yaml`，可根据需求修改以下参数：

| 参数                  | 说明                           | 默认值                         |
| --------------------- | ------------------------------ | ------------------------------ |
| `host`                | Ollama 服务地址                | `http://localhost:11434`       |
| `model`               | 使用的 Ollama 模型名称         | `qwen3:4b-instruct`            |
| `system_content`      | 系统提示词（模型角色定义）     | `You are a helpful assistant.` |
| `options.num_ctx`     | 上下文窗口大小                 | `8192`                         |
| `options.temperature` | 温度值（控制输出随机性，0-1）  | `0.7`                          |
| `options.num_predict` | 最大生成 token 数（-1 为无限） | `-1`                           |
| `options.top_k`       | 采样候选词数量                 | `20`                           |
| `options.top_p`       | 核采样概率阈值                 | `0.95`                         |
| `options.min_p`       | 最小概率阈值                   | `0.05`                         |

## 运行步骤

1. 克隆或下载项目代码。
2. 根据需求修改 `config.yaml` 配置。
3. 启动应用：

```bash
cd /the/path/to/ollama-chatbot
python main.py
```

4. 打开终端输出中的本地 URL（通常为 `http://127.0.0.1:7860`），即可在浏览器中使用聊天机器人。

## 使用说明

- 在聊天输入框中输入问题，点击发送或按回车。
- 系统会实时流式返回模型的响应。
- 聊天历史会自动保存在界面中，支持连续对话。

## 注意事项

- 确保 Ollama 服务已启动且地址与 `config.yaml` 中的 `host` 一致。
- 使用的模型需已通过 `ollama pull` 命令下载到本地。
- 调整 `num_ctx` 等参数可能影响模型性能和响应速度，建议根据硬件配置合理设置。
