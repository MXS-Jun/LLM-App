import gradio as gr
import ollama
import re
import sys
import yaml

from pathlib import Path
from typing import Iterator


# 读取 config.yaml 文件内容，并据此初始化默认配置（DEFAULT_CONFIG）
CONFIG_PATH: str = (Path(__file__).parent / "config.yaml").as_posix()

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        DEFAULT_CONFIG: dict = yaml.safe_load(f)
        print("[INFO] config.yaml read successfully")
except Exception as e:
    print("[ERROR] Failed to read config.yaml")
    sys.exit(1)


# 读取 system_prompt.md 文件内容，并据此初始化默认系统提示词（DEFAULT_SYSTEM_PROMPT）
SYSTEM_PROMPT_PATH: str = (Path(__file__).parent / "system_prompt.md").as_posix()

try:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        DEFAULT_SYSTEM_PROMPT: str = f.read()
        print("[INFO] system_prompt.md read successfully")
except Exception as e:
    print("[ERROR] Failed to read system_prompt.md")
    sys.exit(1)


# 创建 Ollama 客户端，并检查 Ollama 服务端是否可访问
OLLAMA_CLIENT: ollama.Client = ollama.Client(
    host=f"http://{str(DEFAULT_CONFIG["ip"])}:{int(DEFAULT_CONFIG["port"])}",
    headers={"x-some-header": "some-value"},
)

try:
    OLLAMA_CLIENT.list()  # 如果 Ollama 服务端可以访问，则不会抛出异常
    print(f"[INFO] Ollama service is available")
except Exception as e:
    print(f"[ERROR] Ollama service is unavailable: {e}")
    sys.exit(1)


# 隐藏 Chatbot 组件右上角的“垃圾桶”图标（适配中文界面和英文界面）
CSS = """
button.icon-button[title="清空对话"],
button.icon-button[title="Clear"] {
    display: none !important;
}
"""


class Memory:
    """记忆模块

    用于管理对话历史，针对 ollama 和 gradio.Chatbot 组件设计
    """

    def __init__(self) -> None:
        # Ollama 消息格式的系统提示词，用于生成 AI 响应
        self._system_prompt: dict = {
            "role": "system",
            "content": "",
        }

        # Ollama 消息格式的消息列表，用于生成 AI 响应，不包括思考过程
        self._messages: list[dict[str, str]] = []

        # gradio.Chatbot 组件需要的对话历史列表，用于前端渲染，包括思考过程
        self._history: list[dict[str, str]] = []

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词

        :param  prompt: 系统提示词
        :type prompt: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 prompt 为 None 或空白字符串
        """
        if prompt is None or not prompt.strip():
            raise ValueError("[ERROR] system prompt is empty")

        self._system_prompt["content"] = prompt

    def add_user_message(self, message: str) -> None:
        """添加用户消息

        :param message: 用户消息
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 message 为 None 或空白字符串
        """
        if message is None or not message.strip():
            raise ValueError("[ERROR] user message is empty")

        self._messages.append({"role": "user", "content": message})
        self._history.append({"role": "user", "content": message})

    def add_ai_message(self, message: str) -> None:
        """添加 AI 消息

        :param message: AI 消息，不包括思考过程
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 message 为 None 或空白字符串
        """
        if message is None or not message.strip():
            raise ValueError("[ERROR] ai message is empty")

        self._messages.append({"role": "assistant", "content": message})

    def add_ai_response(self, response: str) -> None:
        """添加 AI 响应

        :param message: AI 响应，包括思考过程
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 response 为 None 或空白字符串
        """
        if response is None or not response.strip():
            raise ValueError("[ERROR] ai response is empty")

        self._history.append({"role": "assistant", "content": response})

    def get_system_prompt(self) -> dict[str, str]:
        """获取系统提示词

        :returns: Ollama 消息格式的系统提示词
        :rtype: dict[str, str]
        """
        return self._system_prompt.copy()

    def get_history(self) -> list[dict[str, str]]:
        """获取 gradio.Chatbot 组件需要的对话历史列表

        完整的对话历史，用于前端渲染，包括思考过程

        :returns: 适配 gradio.Chatbot 组件输入要求的对话历史列表，包括思考过程
        :rtype: list[dict[str, str]]
        """
        return self._history.copy()

    def get_context(self, num_ctx: int) -> list[dict[str, str]]:
        """获取 Ollama 消息格式的消息列表

        系统提示词加上倒数 n 条消息，不包括思考过程，用于生成 AI 响应，
        系统提示词和倒数 n 条消息的字符总数不大于 num_ctx

        :param num_ctx: 上下文窗口大小
        :type num_ctx: int
        :returns: 系统提示词加上倒数 n 条消息
        :rtype: list[dict[str, str]]
        :raises ValueError: 如果 num_ctx 太小，以至于无法容纳系统提示词或无法容纳一条用户消息
        """
        n: int = 0
        count: int = len(self._system_prompt["content"])

        if count > num_ctx:
            raise ValueError(f"[ERROR] num_ctx={num_ctx} is too small")

        for message in reversed(self._messages):
            count += len(message["content"])
            if count >= num_ctx:
                break
            else:
                n += 1

        if n > 0 and n % 2 == 0:
            n -= 1

        if n == 0:
            raise ValueError(f"[ERROR] num_ctx={num_ctx} is too small")

        return self._messages[-n:]

    def clear(self) -> None:
        """清空消息列表和对话历史列表

        不重置系统提示词

        :returns: 无
        :rtype: None
        """
        self._messages.clear()
        self._history.clear()

    def __len__(self) -> int:
        """返回消息列表（对话历史列表）的长度

        消息列表的长度等于对话历史列表的长度，
        计算长度时，不包括系统提示词

        :return: 等于 AI 消息加上用户消息的数量
        :rtype: int
        """
        return len(self._messages)


class OllamaLLM:
    """Ollama LLM 模块

    对 ollama 库的再次封装
    """

    def __init__(self, client: ollama.Client) -> None:
        self._client: ollama.Client = client
        self._model: str = ""
        self._num_ctx: int = 2048
        self._temperature: float = 0.7

    def set_model(self, model: str) -> None:
        """设置模型

        :param model: ollama 模型 id
        :type model: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 model 不在 Ollama 服务端已拉取的模型列表中
        """
        model_list: list[str | None] = [
            elem.model for elem in self._client.list().models
        ]

        if model not in model_list or not model.strip():
            raise ValueError(f"[ERROR] model={model} not found")

        self._model: str = model

    def set_num_ctx(self, num_ctx: int) -> None:
        """设置上下文窗口大小

        :param num_ctx: 上下文窗口大小
        :type num_ctx: int
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 num_ctx 小于 2048
        """
        if num_ctx < 2048:
            raise ValueError(f"[ERROR] num_ctx={num_ctx} is too small")

        self._num_ctx: int = num_ctx

    def set_temperature(self, temperature: float) -> None:
        """设置温度

        温度范围 0.0 ~ 1.0

        :param temperature: 温度大小
        :type temperature: float
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 temperature 不在温度范围内
        """
        if temperature < 0.0 or temperature > 1.0:
            raise ValueError(
                f"[ERROR] temperature={temperature} is not between 0.0 and 1.0"
            )

        self._temperature: float = temperature

    def get_num_ctx(self) -> int:
        """获取上下文窗口大小

        :return: 上下文窗口大小
        :rtype: int
        """
        return self._num_ctx

    def chat(
        self, messages: list[dict[str, str]], think: bool
    ) -> Iterator[tuple[str, str]]:
        """生成 AI 回复

        AI 响应流包括思考流和内容流，如果一个流不为空，则另一个流必为空

        :param messages: Ollama 格式的消息列表
        :type messages: list[dict[str, str]]
        :param think: 思考模式开关
        :type think: bool
        :return: AI 响应流元组的迭代器，元组结构：(思考流, 内容流)
        :rtype: Iterator[tuple[str, str]]
        """
        for part in self._client.chat(
            model=self._model,
            options={"num_ctx": self._num_ctx, "temperature": self._temperature},
            messages=messages,
            stream=True,
            think=think,
        ):
            yield (
                part["message"].get("thinking", ""),
                part["message"].get("content", ""),
            )


def create_memory() -> Memory:
    """为会话创建 Memory 实例

    :return: 新创建的 Memory 实例，用从 system_prompt.md 读取的默认系统提示词做初始化
    :rtype: Memory
    """
    memory: Memory = Memory()
    memory.set_system_prompt(DEFAULT_SYSTEM_PROMPT)

    return memory


def create_instruct_ollama_llm() -> OllamaLLM:
    """为会话创建 OllamaLLM 实例

    创建非思考模型

    :return: 新创建的 OllamaLLM 实例，用从 config.yaml 读取的默认参数做初始化
    :rtype: OllamaLLM
    """
    instruct_ollama_llm: OllamaLLM = OllamaLLM(OLLAMA_CLIENT)
    instruct_ollama_llm.set_model(DEFAULT_CONFIG["model"]["instruct"])
    instruct_ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    instruct_ollama_llm.set_temperature(
        DEFAULT_CONFIG["model"]["options"]["temperature"]
    )

    return instruct_ollama_llm


def create_thinking_ollama_llm() -> OllamaLLM:
    """为会话创建 OllamaLLM 实例

    创建思考模型

    :return: 新创建的 OllamaLLM 实例，用从 config.yaml 读取的默认参数做初始化
    :rtype: OllamaLLM
    """
    thinking_ollama_llm: OllamaLLM = OllamaLLM(OLLAMA_CLIENT)
    thinking_ollama_llm.set_model(DEFAULT_CONFIG["model"]["thinking"])
    thinking_ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    thinking_ollama_llm.set_temperature(
        DEFAULT_CONFIG["model"]["options"]["temperature"]
    )

    return thinking_ollama_llm


def chat_stream(
    message: str,
    think: bool,
    memory: Memory,
    instruct_ollama_llm: OllamaLLM,
    thinking_ollama_llm: OllamaLLM,
) -> Iterator[tuple[list[dict[str, str]], Memory, OllamaLLM, OllamaLLM]]:
    """生成 AI 响应流

    返回 gradio.Chatbot 组件需要的输入

    :param message: 用户消息
    :type message: str
    :param think: 思考模式开关
    :type think: bool
    :param memory: 记忆模块
    :type memory: Memory
    :param instruct_ollama_llm: 非思考模型
    :type instruct_ollama_llm: OllamaLLM
    :param thinking_ollama_llm: 思考模型
    :type thinking_ollama_llm: OllamaLLM
    :return: (gradio.Chatbot 组件输入, 记忆模块, 非思考模型, 思考模型)
    :rtype: Iterator[tuple[list[dict[str, str]], Memory, OllamaLLM, OllamaLLM]]
    """
    memory.add_user_message(message)

    # 根据对话历史列表更新 gradio.Chatbot 组件
    history: list[dict[str, str]] = memory.get_history()

    # 根据上下文窗口限制下获取的消息列表生成 AI 响应
    context: list[dict[str, str]] = memory.get_context(
        instruct_ollama_llm.get_num_ctx()
    )

    yield (history, memory, instruct_ollama_llm, thinking_ollama_llm)

    history.append({"role": "assistant", "content": ""})

    messages: list[dict[str, str]] = [memory.get_system_prompt()] + context

    if not think:
        for _, answer_word in instruct_ollama_llm.chat(messages, False):
            history[-1]["content"] += answer_word

            yield (history, memory, instruct_ollama_llm, thinking_ollama_llm)

        # 没有思考过程，所以 AI 消息和 AI 响应相同
        memory.add_ai_message(history[-1]["content"])
        memory.add_ai_response(history[-1]["content"])

        yield (history, memory, instruct_ollama_llm, thinking_ollama_llm)
    else:
        thinking_process: str = ""

        for think_word, answer_word in thinking_ollama_llm.chat(messages, True):
            if think_word:
                thinking_process += think_word

                # 将思考过程包括在 <details> 标签内
                history[-1]["content"] = (
                    "<details>\n"
                    + "<summary>Thinking process</summary>\n"
                    + thinking_process
                    + "\n</details>\n\n"
                )

            if answer_word:
                history[-1]["content"] += answer_word

            yield (history, memory, instruct_ollama_llm, thinking_ollama_llm)

        # AI 消息不包括思考过程
        memory.add_ai_message(
            re.sub(
                r"<details[^>]*>.*?</details>",
                "",
                history[-1]["content"],
                count=1,
                flags=re.DOTALL,
            )
        )

        # AI 响应包括思考过程
        memory.add_ai_response(history[-1]["content"])

        yield (history, memory, instruct_ollama_llm, thinking_ollama_llm)


def clear_chat_history(memory: Memory) -> tuple[list, Memory]:
    """清空对话历史

    :param memory: 记忆模块
    :type memory: Memory
    :return: (空列表, 清空消息列表和对话历史列表的记忆模块)
    :rtype: tuple[list, Memory]
    """
    memory.clear()

    return ([], memory)


def activate_button(text: str) -> gr.Button:
    """如果输入的文本不为空，则激活按钮

    :param text: 输入的文本
    :type text: str
    :return: 如果 text 不为 None 或空白字符串，则返回可交互的 gr.Button 实例
    :rtype: gradio.Button
    """
    valid_text: bool = text is not None and bool(text.strip())

    return gr.Button(interactive=valid_text)


def save_settings(
    system_prompt: str,
    num_ctx: int,
    temperature: float,
    memory: Memory,
    instruct_ollama_llm: OllamaLLM,
    thinking_ollama_llm: OllamaLLM,
) -> tuple[Memory, OllamaLLM, OllamaLLM]:
    """保存设置

    :param system_prompt: 系统提示词
    :type system_prompt: str
    :param num_ctx: 上下文窗口大小
    :type num_ctx: int
    :param temperature: 温度
    :type num_ctx: float
    :param memory: 记忆模块
    :type memory: Memory
    :param instruct_ollama_llm: 非思考模型
    :type instruct_ollama_llm: OllamaLLM
    :param thinking_ollama_llm: 思考模型
    :type thinking_ollama_llm: OllamaLLM
    :return: (更新的记忆模块, 更新的非思考模型, 更新的思考模型)
    :rtype: tuple[Memory, OllamaLLM, OllamaLLM]
    """
    # 如果系统提示词为空，则采用默认的系统提示词
    if not system_prompt.strip():
        system_prompt = DEFAULT_SYSTEM_PROMPT

    memory.set_system_prompt(system_prompt)
    instruct_ollama_llm.set_num_ctx(num_ctx)
    instruct_ollama_llm.set_temperature(temperature)
    thinking_ollama_llm.set_num_ctx(num_ctx)
    thinking_ollama_llm.set_temperature(temperature)

    gr.Info("Settings saved")

    return (memory, instruct_ollama_llm, thinking_ollama_llm)


def reset_settings(
    memory: Memory, instruct_ollama_llm: OllamaLLM, thinking_ollama_llm: OllamaLLM
) -> tuple[str, int, float, Memory, OllamaLLM, OllamaLLM]:
    """重置设置

    - 设置页面的各个组件恢复默认
    - 记忆模块的系统提示词恢复默认
    - 非思考模型和思考模型的上下文窗口大小和温度恢复默认

    :param memory: 记忆模块
    :type memory: Memory
    :param instruct_ollama_llm: 非思考模型
    :type instruct_ollama_llm: OllamaLLM
    :param thinking_ollama_llm: 思考模型
    :type thinking_ollama_llm: OllamaLLM
    :returns: ("", 默认上下文窗口大小, 默认温度, 重置的记忆模块, 重置的非思考模型, 重置的思考模型)
    :rtype: tuple[str, int, float, Memory, OllamaLLM, OllamaLLM]
    """
    memory.set_system_prompt(DEFAULT_SYSTEM_PROMPT)
    instruct_ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    instruct_ollama_llm.set_temperature(
        DEFAULT_CONFIG["model"]["options"]["temperature"]
    )
    thinking_ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    thinking_ollama_llm.set_temperature(
        DEFAULT_CONFIG["model"]["options"]["temperature"]
    )

    gr.Info("Settings reset")

    return (
        "",
        DEFAULT_CONFIG["model"]["options"]["num_ctx"],
        DEFAULT_CONFIG["model"]["options"]["temperature"],
        memory,
        instruct_ollama_llm,
        thinking_ollama_llm,
    )


with gr.Blocks(title="Ollama Chat", css=CSS) as demo:
    # 记忆模块每个会话一个实例
    memory_state: gr.State = gr.State(value=create_memory)

    # 非思考模型每个会话一个实例
    instruct_ollama_llm_state: gr.State = gr.State(value=create_instruct_ollama_llm)

    # 思考模型每个会话一个实例
    thinking_ollama_llm_state: gr.State = gr.State(value=create_thinking_ollama_llm)

    # 介绍
    gr.HTML('<h1 align="center">Chatbot based on Ollama</h1>')

    # 聊天界面设计
    with gr.Tab("Chat"):
        chat_history_windows: gr.Chatbot = gr.Chatbot(type="messages", show_label=False)

        input_textbox: gr.Textbox = gr.Textbox(
            label="Input field", lines=5, max_lines=10
        )

        with gr.Row():
            think_mode: gr.Checkbox = gr.Checkbox(label="Think")
            send_button: gr.Button = gr.Button(value="Send", interactive=False)
            clear_button: gr.Button = gr.Button(value="Clear")

        # 临时变量，点击发送按钮后，在清空输入框前保存输入框内容
        tmp_text: gr.Text = gr.Text(visible=False)

    # 聊天功能实现
    input_textbox.change(
        fn=activate_button, inputs=[input_textbox], outputs=[send_button]
    )

    send_button.click(
        fn=lambda x: ("", x),
        inputs=[input_textbox],
        outputs=[input_textbox, tmp_text],
    ).then(
        fn=chat_stream,
        inputs=[
            tmp_text,
            think_mode,
            memory_state,
            instruct_ollama_llm_state,
            thinking_ollama_llm_state,
        ],
        outputs=[
            chat_history_windows,
            memory_state,
            instruct_ollama_llm_state,
            thinking_ollama_llm_state,
        ],
    ).then(
        fn=lambda: "", inputs=None, outputs=[tmp_text]
    )

    clear_button.click(
        fn=clear_chat_history,
        inputs=[memory_state],
        outputs=[chat_history_windows, memory_state],
    ).then(fn=lambda: "", inputs=None, outputs=[input_textbox])

    # 设置界面设计
    with gr.Tab("Settings"):
        system_prompt_textbox: gr.Textbox = gr.Textbox(
            label="System prompt",
            info="System prompt is a hidden instruction preset for a LLM, guiding it to generate responses that meet expectations.",
            lines=5,
            max_lines=10,
        )

        num_ctx_slider: gr.Slider = gr.Slider(
            label="Size of context windows",
            info="Sets the size of the context window used to generate the next token.",
            value=DEFAULT_CONFIG["model"]["options"]["num_ctx"],
            minimum=1024,
            maximum=128 * 1024,
            step=1024,
        )

        temperature_slider: gr.Slider = gr.Slider(
            label="Temperature",
            info="The temperature of the model. Increasing the temperature will make the model answer more creatively.",
            value=DEFAULT_CONFIG["model"]["options"]["temperature"],
            minimum=0.0,
            maximum=1.0,
            step=0.1,
        )

        with gr.Row():
            save_button: gr.Button = gr.Button(value="Save")
            reset_button: gr.Button = gr.Button(value="Reset")

    # 设置功能实现
    save_button.click(
        fn=save_settings,
        inputs=[
            system_prompt_textbox,
            num_ctx_slider,
            temperature_slider,
            memory_state,
            instruct_ollama_llm_state,
            thinking_ollama_llm_state,
        ],
        outputs=[memory_state, instruct_ollama_llm_state, thinking_ollama_llm_state],
    )

    reset_button.click(
        fn=reset_settings,
        inputs=[memory_state, instruct_ollama_llm_state, thinking_ollama_llm_state],
        outputs=[
            system_prompt_textbox,
            num_ctx_slider,
            temperature_slider,
            memory_state,
            instruct_ollama_llm_state,
            thinking_ollama_llm_state,
        ],
    )

if __name__ == "__main__":
    FAVICON_PATH: str | None = (Path(__file__).parent / "ollama-logo.png").as_posix()

    if not Path(FAVICON_PATH).exists():
        print("[WARNING] Favicon not found, launching without favicon")
        FAVICON_PATH = None

    demo.launch(favicon_path=FAVICON_PATH)
