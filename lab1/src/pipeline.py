from loguru import logger

from filters import apply_filters
from generator import Generator
from reranker import Reranker
from retriever import Retriever

MIN_SCORE = 0.0   # подобран по замерам: релевантные чанки от ~0.7, мусор ниже -1.7
TOP_K_RETRIEVE = 30
TOP_K_FINAL = 5


class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever(k=TOP_K_RETRIEVE)
        self.reranker = Reranker(top_k=TOP_K_FINAL)
        self.generator = Generator()

    def query(self, question: str) -> dict:
        candidates = self.retriever.retrieve(question)
        reranked = self.reranker.rerank(question, candidates)
        filtered = apply_filters(reranked, min_score=MIN_SCORE)
        answer = self.generator.generate(question, filtered)

        sources = [
            {"source": d.metadata["source"], "score": round(d.metadata["rerank_score"], 2)}
            for d in filtered
        ]
        logger.info(f"Вопрос обработан: {len(filtered)} источников")
        return {"answer": answer, "sources": sources}