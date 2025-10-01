import gradio as gr
import ollama
import sys
import yaml

from pathlib import Path
from typing import Iterator


# 读取默认配置
CONFIG_PATH: str = (Path(__file__).parent / "config.yaml").as_posix()

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        DEFAULT_CONFIG: dict = yaml.safe_load(f)
        print("[INFO] config.yaml read successfully")
except Exception as e:
    print("[ERROR] Failed to read config.yaml")
    sys.exit(1)


# 读取默认系统提示词
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
    OLLAMA_CLIENT.list()
    print(f"[INFO] Ollama service is available")
except Exception as e:
    print(f"[ERROR] Ollama service is unavailable: {e}")
    sys.exit(1)


class Memory:
    """
    记忆模块：管理对话历史
    """

    def __init__(self) -> None:
        self._system_prompt: dict = {"role": "system", "content": ""}
        self._messages: list[dict[str, str]] = []

    def set_system_prompt(self, prompt: str) -> None:
        """
        设置系统提示词
        """
        self._system_prompt["content"] = prompt

    def add_user_message(self, message: str) -> None:
        """
        添加用户消息
        """
        self._messages.append({"role": "user", "content": message})

    def add_ai_response(self, response: str) -> None:
        """
        添加 AI 回复
        """
        self._messages.append({"role": "assistant", "content": response})

    def get_system_prompt(self) -> dict[str, str]:
        """
        获取系统提示词
        """
        return self._system_prompt

    def get_history(self) -> list[dict[str, str]]:
        """
        获取完整对话历史
        """
        return self._messages.copy()

    def clear(self) -> None:
        """
        清空记忆
        """
        self._messages.clear()

    # TODO 应该根据 num_ctx 和历史消息的长度来确定 n
    def get_last_n_messages(self, n: int) -> list[dict[str, str]]:
        """
        获取最近 n 条消息
        """
        return self._messages[-n:] if n > 0 else []

    def __len__(self) -> int:
        """
        返回消息总数
        """
        return len(self._messages)


class OllamaLLM:
    """
    Ollama LLM 模块
    """

    def __init__(self, client: ollama.Client) -> None:
        self._client: ollama.Client = client
        self._model: str = ""
        self._num_ctx: int = 2048
        self._temperature: float = 0.7

    def set_model(self, model: str) -> None:
        """
        设置模型名
        """
        self._model: str = model

    def set_num_ctx(self, num_ctx: int) -> None:
        """
        设置上下文窗口大小
        """
        self._num_ctx: int = num_ctx

    def set_temperature(self, temperature: float) -> None:
        """
        设置温度，温度范围 [0, 1.0]
        """
        self._temperature: float = temperature

    def chat(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """
        生成 AI 回复
        """
        for part in self._client.chat(
            model=self._model,
            options={"num_ctx": self._num_ctx, "temperature": self._temperature},
            messages=messages,
            stream=True,
        ):
            yield part["message"]["content"]


def create_memory():
    """
    为会话单独创建 Memory 实例
    """

    memory: Memory = Memory()
    memory.set_system_prompt(DEFAULT_SYSTEM_PROMPT)

    return memory


def create_ollama_llm():
    """
    为会话单独创建 OllamaLLM 实例
    """

    ollama_llm: OllamaLLM = OllamaLLM(OLLAMA_CLIENT)
    ollama_llm.set_model(DEFAULT_CONFIG["model"]["name"])
    ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    ollama_llm.set_temperature(DEFAULT_CONFIG["model"]["options"]["temperature"])

    return ollama_llm


def chat_stream(
    message: str, memory: Memory, ollama_llm: OllamaLLM
) -> Iterator[tuple[list[dict[str, str]], Memory, OllamaLLM]]:
    """
    输入用户消息，生成 LLM 的回答流，并返回 Chatbot 需要的输入
    """

    memory.add_user_message(message)
    history: list[dict[str, str]] = memory.get_history()

    yield (history, memory, ollama_llm)

    history.append({"role": "assistant", "content": ""})
    messages: list[dict[str, str]] = [memory.get_system_prompt()] + history

    for word in ollama_llm.chat(messages):
        history[-1]["content"] += word

        yield (history, memory, ollama_llm)

    memory.add_ai_response(history[-1]["content"])

    yield (history, memory, ollama_llm)


def clear_chat_history(memory: Memory) -> tuple[list, Memory]:
    """
    清空对话历史
    """

    memory.clear()

    # 清空 Chatbot 显示和对话记忆
    return ([], memory)


def activate_button(text: str) -> gr.Button:
    """
    如果输入的文本不为空，则激活按钮
    """
    return gr.Button(interactive=bool(text.strip()))


def save_settings(
    system_prompt: str,
    num_ctx: int,
    temperature: float,
    memory: Memory,
    ollama_llm: OllamaLLM,
) -> tuple[Memory, OllamaLLM]:
    """
    保存设置
    """

    # 如果系统提示词为空，则采用默认的系统提示词
    if not system_prompt.strip():
        system_prompt = DEFAULT_SYSTEM_PROMPT

    memory.set_system_prompt(system_prompt)
    ollama_llm.set_num_ctx(num_ctx)
    ollama_llm.set_temperature(temperature)

    gr.Info("Settings saved")

    return (memory, ollama_llm)


def reset_settings(
    memory: Memory, ollama_llm: OllamaLLM
) -> tuple[str, int, float, Memory, OllamaLLM]:
    """
    重置设置
    """

    memory.set_system_prompt(DEFAULT_SYSTEM_PROMPT)
    ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    ollama_llm.set_temperature(DEFAULT_CONFIG["model"]["options"]["temperature"])

    gr.Info("Settings reset")

    return (
        "",
        DEFAULT_CONFIG["model"]["options"]["num_ctx"],
        DEFAULT_CONFIG["model"]["options"]["temperature"],
        memory,
        ollama_llm,
    )


# 隐藏 Chatbot 右上角的“垃圾桶”图标
CSS = """
button[title="清空对话"] {
    display: none !important;
}
"""


with gr.Blocks(title="Ollama Chat", css=CSS) as demo:
    # 记忆模块每个会话一个实例
    memory_state: gr.State = gr.State(value=create_memory)

    # Ollama LLM 模块每个会话一个实例
    ollama_llm_state: gr.State = gr.State(value=create_ollama_llm)

    # 介绍
    intro: gr.HTML = gr.HTML("<center><h1>🤖 Chatbot based on Ollama</h1></center>")

    # 聊天界面设计
    with gr.Tab("Chat"):
        chat_history_windows: gr.Chatbot = gr.Chatbot(type="messages", show_label=False)

        input_textbox: gr.Textbox = gr.Textbox(
            label="Input field", lines=5, max_lines=10
        )

        with gr.Row():
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
        inputs=[tmp_text, memory_state, ollama_llm_state],
        outputs=[chat_history_windows, memory_state, ollama_llm_state],
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
            ollama_llm_state,
        ],
        outputs=[memory_state, ollama_llm_state],
    )

    reset_button.click(
        fn=reset_settings,
        inputs=[memory_state, ollama_llm_state],
        outputs=[
            system_prompt_textbox,
            num_ctx_slider,
            temperature_slider,
            memory_state,
            ollama_llm_state,
        ],
    )

if __name__ == "__main__":
    FAVICON_PATH: str = (Path(__file__).parent / "ollama-logo.png").as_posix()
    demo.launch(favicon_path=FAVICON_PATH)
