import gradio as gr
import yaml

from openai import Client
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionUserMessageParam
from openai.types.chat import ChatCompletionAssistantMessageParam


def chatbot_response(user_content: str, chat_history: list):
    system_message = ChatCompletionSystemMessageParam(
        role="system", content=config["system_content"]
    )
    chat_history_messages = []
    for message in chat_history:
        if message["role"] == "user":
            chat_history_messages.append(
                ChatCompletionUserMessageParam(role="user", content=message["content"])
            )
        elif message["role"] == "assistant":
            chat_history_messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant", content=message["content"]
                )
            )
    user_message = ChatCompletionUserMessageParam(role="user", content=user_content)
    messages = [system_message] + chat_history_messages + [user_message]

    response = ""
    for part in client.chat.completions.create(
        model=config["model"],
        messages=messages,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        stream=True,
    ):
        content = part.choices[0].delta.content
        if content:
            response += content
            yield response


if __name__ == "__main__":
    with open("./config.yaml", "r") as f:
        config = yaml.safe_load(f)

    if config:
        print(f"[INFO]       base_url = {config['base_url']}")
        print(f"[INFO]          model = {config['model']}")
        print(f"[INFO] system_content = {config['system_content']}")
        print(f"[INFO]     max_tokens = {config['max_tokens']}")
        print(f"[INFO]    temperature = {config['temperature']}")
        print(f"[INFO]          top_p = {config['top_p']}")

        client = Client(base_url=config["base_url"], api_key=config["api_key"])

        demo = gr.ChatInterface(
            fn=chatbot_response,
            type="messages",
            title="ChatBot",
            description="Please enter your question, and I will do my best to answer it.",
        )
        demo.launch()
