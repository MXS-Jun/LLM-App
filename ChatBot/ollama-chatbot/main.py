import gradio as gr
import json
import requests
import yaml


def load_config(file_path: str):
    # 打开配置文件，以只读模式读取
    with open(file_path, "r") as config_file:
        # 尝试安全地加载 YAML 配置文件
        try:
            config = yaml.safe_load(config_file)
        except yaml.YAMLError:
            # 如果 YAML 解析失败，打印错误信息
            print(f"[ERROR] Failed to load configuration file: {config_file}")
        else:
            # 如果成功加载配置，返回配置内容
            return config


class LLM:
    def __init__(self, config: dict):
        self.config = config

    def generate(self, message: str, history: list):
        # 设置 API
        url = self.config["base_url"].rstrip("/") + "/api/chat"
        # 设置模型
        model = self.config["model"]
        # 构造消息
        system_message = {"role": "system", "content": self.config["system_prompt"]}
        messages = [system_message]
        messages.extend(history)
        messages.append(message)
        # 构造选项
        options = {
            "num_ctx": self.config["parameters"]["num_ctx"],
            "temperature": self.config["parameters"]["temperature"],
            "num_predict": self.config["parameters"]["num_predict"],
            "top_k": self.config["parameters"]["top_k"],
            "top_p": self.config["parameters"]["top_p"],
            "min_p": self.config["parameters"]["min_p"],
        }
        # 构造请求
        payload = {
            "model": model,
            "stream": True,
            "messages": messages,
            "options": options,
        }
        # 发送请求
        response = requests.post(url, json=payload, stream=True)
        # 处理流式输出
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "content" in data["message"]:
                    yield data["message"]["content"]
                if data["done"]:
                    break


def generate_chat_completion(message: str, history: list):
    global llm
    # 将用户输入消息格式化为标准的对话消息结构
    message = {"role": "user", "content": message}
    # 将历史对话列表中的每条消息重新格式化为标准结构
    history = [
        {"role": message["role"], "content": message["content"]} for message in history
    ]
    # 初始化响应字符串，用于拼接流式输出
    response = ""
    # 遍历LLM生成的每一条内容，逐步拼接并返回
    for completion in llm.generate(message, history):
        response += completion
        yield response


if __name__ == "__main__":
    config = load_config("config.yaml")
    llm = LLM(config)
    demo = gr.ChatInterface(
        fn=generate_chat_completion,
        type="messages",
        save_history=True,
        title="ChatBot"
    )
    demo.launch()
