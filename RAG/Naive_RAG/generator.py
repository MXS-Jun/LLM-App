from ollama import Client
from ollama import Message


class Generator:
    def __init__(self, config):
        self.config = config
        self.client = Client(
            host=self.config["host"], headers={"x-some-header": "some-value"}
        )

    def generate(self, user_content: str, chat_history: list):
        system_message = Message(role="system", content=self.config["system_content"])
        chat_history_messages = [
            Message(role=message["role"], content=message["content"])
            for message in chat_history
        ]
        user_message = Message(role="user", content=user_content)
        messages = [system_message] + chat_history_messages + [user_message]

        for part in self.client.chat(
            model=self.config["model"],
            messages=messages,
            options=self.config["options"],
            stream=True,
        ):
            yield part["message"]["content"]
