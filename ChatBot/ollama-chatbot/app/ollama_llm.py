import json
import requests
from typing import Generator, List, Dict, Optional


class OllamaLLM:
    """
    与Ollama聊天API交互的客户端类，支持流式响应和思考模式
    """

    def __init__(
        self, model: str, chat_api_url: str = "http://localhost:11434/api/chat"
    ):
        """
        初始化OllamaLLM实例

        参数:
            model: 使用的模型名称
            chat_api_url: Ollama聊天API的URL地址
        """
        self.chat_api_url = chat_api_url
        self.model = model

        # 初始化系统消息和对话历史
        self.system_message: Dict[str, str] = {
            "role": "system",
            "content": "你是能干的AI助手，让我们一步一步思考。",
        }
        self.messages: List[Dict[str, str]] = [self.system_message]

        # 思考模式开关
        self.think: bool = False

        # 模型参数配置
        self.options: Dict[str, float] = {"temperature": 0.7, "num_ctx": 8192}

    def set_chat_api_url(self, chat_api_url: str) -> None:
        """设置Ollama聊天API的URL地址"""
        self.chat_api_url = chat_api_url

    def set_model(self, model: str) -> None:
        """设置要使用的模型名称"""
        self.model = model

    def set_system_message(self, content: str) -> None:
        """设置系统提示消息内容"""
        self.system_message["content"] = content
        self.messages[0] = self.system_message

    def add_user_message(self, content: str) -> None:
        """添加用户消息到对话历史"""
        self.messages.append({"role": "user", "content": content})

    def clear_chat_history(self) -> None:
        """清空对话历史，仅保留系统消息"""
        self.messages = [self.system_message]

    def set_think(self, think: bool) -> None:
        """设置是否启用思考模式"""
        self.think = think

    def set_temperature(self, temperature: float) -> None:
        """设置模型的温度参数（控制输出随机性）"""
        self.options["temperature"] = temperature

    def set_num_ctx(self, num_ctx: int) -> None:
        """设置模型的上下文窗口大小"""
        self.options["num_ctx"] = num_ctx

    def get_response_stream(self) -> Generator[str, None, None]:
        """
        获取模型的流式响应

        返回:
            生成器，流式返回模型的响应内容，包括可能的思考过程（如果启用）
        """
        # 构建正确的API请求 payload（还原为Ollama API要求的格式）
        payload: Dict[str, any] = {
            "model": self.model,
            "messages": self.messages,  # 发送完整对话历史
            "think": self.think,
            "options": self.options,
            "stream": True,
        }

        try:
            # 发送POST请求并处理流式响应
            with requests.post(
                self.chat_api_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=30,  # 设置超时时间
            ) as response:
                response.raise_for_status()  # 检查HTTP错误状态

                full_response: str = ""
                start_thinking: bool = not self.think
                end_thinking: bool = not self.think

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        data = json.loads(line.decode("utf-8"))

                        # 处理思考模式输出
                        if not start_thinking:
                            start_thinking = True
                            yield "<blockquote>\n"

                        if not end_thinking:
                            if "thinking" in data.get("message", {}):
                                yield data["message"]["thinking"]
                            else:
                                end_thinking = True
                                yield "</blockquote>\n\n"

                        # 处理实际响应内容
                        if end_thinking:
                            if not data.get("done", False):
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    full_response += content
                                    yield content
                            else:
                                # 保存完整响应到对话历史
                                self.messages.append(
                                    {"role": "assistant", "content": full_response}
                                )

                    except json.JSONDecodeError:
                        yield f"[ERROR] 无法解析服务器响应: {line.decode('utf-8')}"
                    except KeyError as e:
                        yield f"[ERROR] 响应格式错误: 缺少 {str(e)}"

        except requests.exceptions.RequestException as e:
            yield f"[ERROR] 请求失败：{str(e)}"
        except Exception as e:
            yield f"[ERROR] 发生意外错误：{str(e)}"


if __name__ == "__main__":
    # 大模型实例化
    model = "deepseek-r1:8b"
    print(f"[INFO] model: {model}\n")
    llm = OllamaLLM(model)

    # Ollama Chat API URL
    print(f"[INFO] ollama chat api url: {llm.chat_api_url}\n")

    # 测试非思考模式
    test_user_content = "你好"
    think = False
    llm.set_think(think)
    llm.add_user_message(test_user_content)
    print("[INFO] no think mode testing...")
    print(f"# user message:\n{test_user_content}\n")
    print(f"# assistant response:")
    for token in llm.get_response_stream():
        print(token, end="", flush=True)
    print("\n")

    # 测试思考模式
    test_user_content = "用一句话介绍一下Ollama"
    think = True
    llm.set_think(think)
    llm.add_user_message(test_user_content)
    print("[INFO] think mode testing...")
    print(f"# user message:\n{test_user_content}\n")
    print(f"# assistant response:")
    for token in llm.get_response_stream():
        print(token, end="", flush=True)
    print("\n")

    # 对话历史
    print("[INFO] chat history")
    print(f"# messages:\n{llm.messages}\n")

    # 清空对话历史
    llm.clear_chat_history()
    print("[INFO] clear chat history...")
    print(f"# messages:\n{llm.messages}\n")

    # 修改系统提示词
    test_system_content = "你是一个能干的AI助手。"
    llm.set_system_message(test_system_content)
    print("[INFO] set system message...")
    print(f"# messages:\n{llm.messages}\n")

    # 修改温度
    llm.set_temperature(0.3)
    print("[INFO] set temperature 0.3")
    print(f"# options:\n{llm.options}\n")

    # 修改上下文窗口
    llm.set_num_ctx(4096)
    print("[INFO] set num_ctx 4096")
    print(f"# options:\n{llm.options}\n")
