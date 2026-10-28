import sys
from pathlib import Path

import pytest
from langchain_core.documents import Document

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from reranker import Reranker


@pytest.fixture(scope="module")
def reranker():
    return Reranker(top_k=2)


@pytest.fixture
def docs():
    return [
        Document(page_content="Рецепт борща: свёкла, капуста, говядина", metadata={"source": "c"}),
        Document(page_content="Векторная база данных хранит эмбеддинги и ищет по смыслу", metadata={"source": "a"}),
        Document(page_content="FastAPI это веб-фреймворк для Python", metadata={"source": "b"}),
    ]


def test_returns_top_k(reranker, docs):
    assert len(reranker.rerank("как работает векторная база", docs)) == 2


def test_most_relevant_first(reranker, docs):
    result = reranker.rerank("как работает векторная база", docs)
    assert result[0].metadata["source"] == "a"


def test_adds_score(reranker, docs):
    result = reranker.rerank("как работает векторная база", docs)
    assert "rerank_score" in result[0].metadata


def test_empty_input(reranker):
    assert reranker.rerank("вопрос", []) == []