from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Загружает модель один раз и переиспользует при следующих вызовах."""
    global _embeddings
    if _embeddings is None:
        logger.info(f"Загружаю embedding-модель: {MODEL_NAME}")
        _embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        logger.success("Модель загружена")
    return _embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    logger.info(f"Считаю embeddings для {len(texts)} текстов")
    vectors = get_embeddings().embed_documents(texts)
    logger.success(f"Embeddings готовы, размерность вектора: {len(vectors[0])}")
    return vectors