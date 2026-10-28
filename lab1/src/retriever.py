from langchain_core.documents import Document
from loguru import logger

from vectorstore import get_store, DB_PATH


class Retriever:
    def __init__(self, db_path: str = DB_PATH, k: int = 30):
        self.store = get_store(db_path)
        self.k = k

    def retrieve(self, query: str, k: int | None = None) -> list[Document]:
        k = k or self.k
        results = self.store.similarity_search(query, k=k)
        logger.debug(f"Retriever: '{query[:50]}' -> {len(results)} кандидатов")
        return results