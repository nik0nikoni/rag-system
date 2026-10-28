from langchain_core.documents import Document
from loguru import logger
from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


class Reranker:
    def __init__(self, model_name: str = MODEL_NAME, top_k: int = 5):
        logger.info(f"Загружаю reranker-модель: {model_name}")
        self.model = CrossEncoder(model_name)
        self.top_k = top_k

    def rerank(self, query: str, docs: list[Document], top_k: int | None = None) -> list[Document]:
        if not docs:
            return []
        top_k = top_k or self.top_k
        scores = self.model.predict([(query, d.page_content) for d in docs])

        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:top_k]
        for doc, score in ranked:
            doc.metadata["rerank_score"] = float(score)

        logger.debug(f"Reranker: {len(docs)} -> {len(ranked)}")
        return [doc for doc, _ in ranked]