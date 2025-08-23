import requests

from typing import List


class Reranker:
    def __init__(self, config):
        self.config = config

    def rerank(self, query: str, documents: List):
        headers = {
            "Authorization": f"Bearer {self.config["api_key"]}",
            "Content-Type": "application/json",
        }
        data = {"model": self.config["model"], "query": query, "documents": documents}

        response = requests.post(url=self.config["url"], headers=headers, json=data)

        if response.status_code == 200:
            reranked_documents = [
                documents[elem["index"]] for elem in response.json()["results"]
            ]
            top_k = int(self.config["top_k"])
            if top_k < len(reranked_documents):
                return reranked_documents[:top_k]
            else:
                return reranked_documents
        else:
            return []
