import chromadb
import json

from embedder import Embedder
from pathlib import Path


JSONLS = Path(__file__).parent / "jsonls"
COLLECTION = Path(__file__).parent / "collection"


class VectorDB:
    def __init__(self, config):
        self.config = config
        self.client = chromadb.PersistentClient(path=COLLECTION.as_posix())
        self.collection = self.client.get_or_create_collection(
            name=self.config["collection_name"]
        )

    def set_embedder(self, embedder: Embedder):
        self.embedder = embedder

    def update_collection(self, batch_size=16):
        json_obj_list = []
        for jsonl in JSONLS.rglob("*.jsonl"):
            if jsonl.is_file():
                jsonl_data = jsonl.read_text(encoding="utf-8")
                for line in jsonl_data.splitlines():
                    json_obj = json.loads(line)
                    json_obj_list.append(json_obj)

        if self.client.get_collection(name=self.config["collection_name"]) is not None:
            self.client.delete_collection(name=self.config["collection_name"])
        self.collection = self.client.create_collection(
            name=self.config["collection_name"]
        )

        datas = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
        for json_obj in json_obj_list:
            datas["ids"].append(json_obj["id"])
            datas["documents"].append(json_obj["document"])
            datas["metadatas"].append(json_obj["metadata"])
        for start in range(0, len(json_obj_list), batch_size):
            end = min(start + batch_size, len(json_obj_list))
            text_list = []
            for json_obj in json_obj_list[start:end]:
                if json_obj["metadata"]["document_type"] == "text":
                    text_list.append(json_obj["document"])
                elif json_obj["metadata"]["document_type"] == "table":
                    text_list.append(json_obj["metadata"]["document_summary"])
                elif json_obj["metadata"]["document_type"] == "image":
                    text_list.append(json_obj["metadata"]["document_summary"])
            datas["embeddings"] += self.embedder.embed(text_list)

        self.collection.add(
            ids=datas["ids"],
            embeddings=datas["embeddings"],
            documents=datas["documents"],
            metadatas=datas["metadatas"],
        )

        print(f"[INFO] collection '{self.config["collection_name"]}' is up to date")

        return True
