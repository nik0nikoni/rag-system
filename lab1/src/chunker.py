from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger


def chunk_document(doc: dict, chunk_size: int = 500, chunk_overlap: int = 100) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(doc["text"])

    result = []
    for i, chunk_text in enumerate(chunks):
        result.append({
            "text": chunk_text,
            "source": doc["source"],
            "metadata": {**doc["metadata"], "chunk_index": i, "total_chunks": len(chunks)},
        })

    return result


def chunk_all(docs: list[dict], chunk_size: int = 500, chunk_overlap: int = 100) -> list[dict]:
    logger.info(f"Начинаю разбиение {len(docs)} документов на чанки (size={chunk_size}, overlap={chunk_overlap})")

    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)

    logger.success(f"Разбиение завершено: получено {len(all_chunks)} чанков из {len(docs)} документов")
    return all_chunks