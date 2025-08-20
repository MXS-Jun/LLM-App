# OpenAI Chatbot

基于 Gradio 和兼容 OpenAI 接口的大模型云服务平台构建的轻量型聊天机器人 Web 应用。

## 核心特性

- 广泛兼容：可使用各种兼容 OpenAI 接口的大模型云服务平台。
- 快速启动：极简配置，3 分钟内完成部署。
- Web 界面：基于 Gradio 的直观交互界面，支持上下文对话。
- 灵活配置：通过配置文件轻松修改应用参数。

## 环境准备

### 配置云服务（以“硅基流动”为例）

在[硅基流动官网](https://account.siliconflow.cn/)注册账号，并申请 `api_key`。

阅读你想调用的模型的文档，获取 `base_url`、`model` 等参数。

将参数填入 `config.yaml` 的指定位置。

> 请参考 `config.yaml` 中的条目，了解需要设置的参数。

### 安装 Python 及相关依赖

本程序基于 `Python 3.12` 开发。

安装好 `Python` 后，执行下列命令安装依赖：

```bash
pip install gradio
pip install openai
```

### 本地运行程序

执行命令：

```bash
cd /the/path/to/openai-chatbot
python main.py
```

然后在浏览器访问 `http://127.0.0.1:7860/` 即可使用。

> 暂未适配思考模型：因为无法渲染 `<think>` 标签，所以思考过程不可见。
