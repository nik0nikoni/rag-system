from langchain_chroma import Chroma
from langchain_core.documents import Document
from loguru import logger

from embedder import get_embeddings

DB_PATH = "chroma_db"
COLLECTION_NAME = "habr_articles"
BATCH_SIZE = 500


def get_store(db_path: str = DB_PATH) -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=db_path,
    )


def build_store(chunks: list[dict], db_path: str = DB_PATH) -> Chroma:
    logger.info(f"Индексирую {len(chunks)} чанков в '{db_path}'")
    store = get_store(db_path)

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        docs = [
            Document(
                page_content=c["text"],
                metadata={**c["metadata"], "source": c["source"]},
            )
            for c in batch
        ]
        store.add_documents(docs)
        logger.debug(f"Проиндексировано {min(start + BATCH_SIZE, len(chunks))} из {len(chunks)}")

    logger.success(f"Индексация завершена: {len(chunks)} чанков")
    return store


def search(query: str, k: int = 10, db_path: str = DB_PATH) -> list[Document]:
    store = get_store(db_path)
    results = store.similarity_search(query, k=k)
    logger.debug(f"Поиск '{query[:50]}': найдено {len(results)} чанков")
    return results