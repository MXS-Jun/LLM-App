import gradio as gr
import ollama
import re
import sys
import yaml

from pathlib import Path
from typing import Iterator

from memory import Memory
from ollama_llm import OllamaLLM


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
                    + "<summary>Thinking</summary>\n"
                    + thinking_process
                    + "\n<hr>\n</details>\n\n"
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
    # 重置记忆模块
    memory.set_system_prompt(DEFAULT_SYSTEM_PROMPT)

    # 重置非思考模型
    instruct_ollama_llm.set_num_ctx(DEFAULT_CONFIG["model"]["options"]["num_ctx"])
    instruct_ollama_llm.set_temperature(
        DEFAULT_CONFIG["model"]["options"]["temperature"]
    )

    # 重置思考模型
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
            label="Input Field", lines=5, max_lines=10
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
            minimum=2048,
            maximum=128 * 1024,
            step=512,
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
