# OpenAI Chatbot

## 介绍

利用 Gradio + 兼容 OpenAI 接口的云服务（如“硅基流动”）实现的【聊天机器人】Web 应用。

## 使用方法

### 配置云服务

在云服务平台注册账号，申请 API_KEY。

本程序默认使用：

- BASE_URL：`https://api.siliconflow.cn/v1`
- MODEL：`Qwen/Qwen3-8B`

请手动填入 API_KEY 到 `config.yaml` 的指定位置。

更多配置，请参考 `config.yaml` 中的条目。

### 配置虚拟环境

本程序基于 `Python 3.12` 开发。

安装依赖：

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

> 暂未适配思考模型：因为无法渲染 `<think>` 标签，所以思考过程不可见
