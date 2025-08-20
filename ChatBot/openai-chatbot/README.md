# OpenAI Chatbot

一个基于 OpenAI API 和 Gradio 的简单聊天机器人应用，支持自定义模型配置和对话交互。

## 功能介绍

- 通过 Gradio 提供友好的 Web 交互界面。
- 支持与 AI 模型进行连续对话。
- 可通过配置文件自定义模型参数。
- 支持流式输出响应内容。

## 环境要求

- Python 3.12+。
- 依赖包：`gradio`、`openai`、`pyyaml`。

## 安装步骤

1. 克隆或下载项目代码到本地。
2. 安装依赖包：

```bash
pip install gradio
pip install openai
pip install pyyaml
```

## 配置说明

1. 复制或修改项目根目录下的 `config.yaml` 文件，配置以下参数：

- `base_url`：API 服务地址（默认使用 SiliconFlow 服务）。
- `api_key`：你的 API 密钥（需替换 `<your_api_key>`）。
- `model`：要使用的模型名称（默认：`Qwen/Qwen3-8B`）。
- `system_content`：系统提示词，定义 AI 助手的行为。
- `max_tokens`：最大生成令牌数。
- `temperature`：温度参数，控制输出随机性（0-1 之间，值越高越随机）。
- `top_p`：核采样参数，控制输出多样性。

2. 配置示例：

```yaml
base_url: https://api.siliconflow.cn/v1
api_key: your_actual_api_key_here
model: Qwen/Qwen3-8B
system_content: You are a helpful assistant.
max_tokens: 8192
temperature: 0.7
top_p: 0.95
```

## 使用方法

1. 确保配置文件已正确设置。
2. 运行主程序：

```bash
python main.py
```

3. 程序启动后，会自动在浏览器打开 Gradio 界面（默认地址：`http://localhost:7860`）。
4. 在输入框中输入你的问题，即可与 AI 助手进行对话。

## 项目结构

- `main.py`：主程序文件，包含聊天逻辑和 Gradio 界面配置。
- `config.yaml`：配置文件，存储 API 和模型相关参数。

## 注意事项

- 请妥善保管你的 `api_key`，不要泄露给他人。
- 不同的 `base_url` 可能对应不同的 API 服务，需根据实际服务提供商的要求进行配置。
- 模型参数（`temperature`，`top_p` 等）可以根据需要调整，以获得不同的对话效果。
- 若对话响应缓慢，可能与网络状况或 API 服务负载有关。
