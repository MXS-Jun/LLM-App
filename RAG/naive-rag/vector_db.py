import chromadb
import json
import shutil
import yaml

from embedder import embedder
from pathlib import Path


CONFIG_YAML_PATH = Path(__file__).parent / "config.yaml"
JSONLS_PATH = Path(__file__).parent / "jsonls"
COLLECTION_PATH = Path(__file__).parent / "collection"


class VectorDB:
    def __init__(self, config):
        self.config = config
        self.client = chromadb.PersistentClient(path=COLLECTION_PATH.as_posix())
        self.collection = self.client.get_or_create_collection(
            name=self.config["collection_name"]
        )

    def update_collection(self, batch_size=16):
        json_obj_list = []
        for jsonl_path in JSONLS_PATH.rglob("*.jsonl"):
            if jsonl_path.is_file():
                jsonl_data = jsonl_path.read_text(encoding="utf-8")
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
            datas["ids"].append(json_obj["chunk_id"])
            datas["documents"].append(json_obj["chunk_content"])
            datas["metadatas"].append(json_obj["metadata"])
        for start in range(0, len(json_obj_list), batch_size):
            end = min(start + batch_size, len(json_obj_list))
            text_list = []
            for json_obj in json_obj_list[start:end]:
                if json_obj["metadata"]["chunk_type"] == "text":
                    text_list.append(json_obj["chunk_content"])
                elif json_obj["metadata"]["chunk_type"] == "table":
                    text_list.append(json_obj["metadata"]["chunk_summary"])
                elif json_obj["metadata"]["chunk_type"] == "image":
                    text_list.append(json_obj["metadata"]["chunk_summary"])
            datas["embeddings"] += embedder.embed(text_list)

        self.collection.add(
            ids=datas["ids"],
            embeddings=datas["embeddings"],
            documents=datas["documents"],
            metadatas=datas["metadatas"],
        )

        print(f"[INFO] collection '{self.config["collection_name"]}' is up to date")

        return True


if CONFIG_YAML_PATH.exists() and CONFIG_YAML_PATH.is_file():
    config = yaml.safe_load(CONFIG_YAML_PATH.read_text(encoding="utf-8"))
    vector_db = VectorDB(config["vector_db"])
