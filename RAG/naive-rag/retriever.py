import yaml

from embedder import embedder
from pathlib import Path
from typing import List
from vector_db import vector_db


CONFIG_YAML_PATH = Path(__file__).parent / "config.yaml"


class Retriever:
    def __init__(self, config):
        self.n_results = config["n_results"]

    def query(self, text_list) -> List[List]:
        query_embeddings = embedder.embed(text_list)
        results = vector_db.collection.query(
            query_embeddings=query_embeddings,
            n_results=self.n_results,
            include=["documents"],
        )["documents"]
        if results is not None:
            return results
        else:
            return [[]]


if CONFIG_YAML_PATH.exists() and CONFIG_YAML_PATH.is_file():
    config = yaml.safe_load(CONFIG_YAML_PATH.read_text(encoding="utf-8"))
    retriever = Retriever(config["retriever"])
