from langchain_core.documents import Document
from loguru import logger


def apply_filters(
    docs: list[Document],
    min_score: float | None = None,
    sources: list[str] | None = None,
    max_docs: int | None = None,
) -> list[Document]:
    result = docs

    if min_score is not None:
        result = [d for d in result if d.metadata.get("rerank_score", float("-inf")) >= min_score]

    if sources is not None:
        result = [d for d in result if d.metadata.get("source") in sources]

    if max_docs is not None:
        result = result[:max_docs]

    logger.debug(f"Filters: {len(docs)} -> {len(result)}")
    return result