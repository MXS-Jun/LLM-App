import requests


class Embedder:
    def __init__(self, config):
        self.config = config

    def embed(self, text_list: list):
        headers = {
            "Authorization": f"Bearer {self.config["api_key"]}",
            "Content-Type": "application/json",
        }
        data = {"model": self.config["model"], "input": text_list}
        response = requests.post(self.config["url"], headers=headers, json=data)
        if response.status_code == 200:
            return [elem["embedding"] for elem in response.json()["data"]]
        else:
            return []
