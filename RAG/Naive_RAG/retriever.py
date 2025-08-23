from embedder import Embedder
from typing import List
from vector_db import VectorDB


class Retriever:
    def __init__(self, config):
        self.n_results = config["n_results"]

    def set_embedder(self, embedder: Embedder):
        self.embedder = embedder

    def set_vector_db(self, vector_db: VectorDB):
        self.vector_db = vector_db

    def query(self, text_list) -> List[List]:
        query_embeddings = self.embedder.embed(text_list)
        results = self.vector_db.collection.query(
            query_embeddings=query_embeddings,
            n_results=self.n_results,
            include=["documents"],
        )["documents"]
        if results is not None:
            return results
        else:
            return [[]]
