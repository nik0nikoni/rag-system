from dotenv import load_dotenv
from langfuse import observe
from loguru import logger

load_dotenv()  # ключи Langfuse должны быть в окружении до первого вызова

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

    @observe(name="retrieve")
    def _retrieve(self, question: str):
        return self.retriever.retrieve(question)

    @observe(name="rerank")
    def _rerank(self, question: str, candidates):
        return self.reranker.rerank(question, candidates)

    @observe(name="filter")
    def _filter(self, reranked):
        return apply_filters(reranked, min_score=MIN_SCORE)

    @observe(name="generate")
    def _generate(self, question: str, docs):
        return self.generator.generate(question, docs)

    @staticmethod
    def _build_sources(docs) -> list[dict]:
        best: dict[str, float] = {}
        for d in docs:
            src = d.metadata["source"]
            score = d.metadata["rerank_score"]
            if src not in best or score > best[src]:
                best[src] = score
        return [{"source": s, "score": round(sc, 2)} for s, sc in best.items()]

    @observe(name="rag-query")
    def query(self, question: str) -> dict:
        candidates = self._retrieve(question)
        reranked = self._rerank(question, candidates)
        filtered = self._filter(reranked)
        answer = self._generate(question, filtered)

        sources = self._build_sources(filtered)
        logger.info(f"Вопрос обработан: {len(filtered)} чанков, {len(sources)} источников")
        return {"answer": answer, "sources": sources}