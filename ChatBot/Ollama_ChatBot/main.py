import gradio as gr
import yaml

from ollama import Client
from ollama import Message


def chatbot_response(user_content: str, chat_history: list):
    system_message = Message(role="system", content=config["system_content"])
    chat_history_messages = [
        Message(role=message["role"], content=message["content"])
        for message in chat_history
    ]
    user_message = Message(role="user", content=user_content)
    messages = [system_message] + chat_history_messages + [user_message]

    response = ""
    for part in client.chat(
        model=config["model"], messages=messages, options=config["options"], stream=True
    ):
        response += part["message"]["content"]
        yield response


if __name__ == "__main__":
    with open("./config.yaml", "r") as f:
        config = yaml.safe_load(f)

    if config:
        print(f"[INFO]           host = {config["host"]}")
        print(f"[INFO]          model = {config["model"]}")
        print(f"[INFO] system_content = {config["system_content"]}")
        print(f"[INFO]        options = {config["options"]}")

        client = Client(host=config["host"], headers={"x-some-header": "some-value"})

        demo = gr.ChatInterface(
            fn=chatbot_response,
            type="messages",
            title="ChatBot",
            description="Please enter your question, and I will do my best to answer it.",
        )
        demo.launch()
