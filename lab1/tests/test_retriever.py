import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from vectorstore import build_store
from retriever import Retriever


@pytest.fixture(scope="module")
def retriever(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("chroma"))
    chunks = [
        {"text": "Векторная база данных хранит эмбеддинги и ищет похожие по смыслу тексты",
         "source": "a.html", "metadata": {"chunk_index": 0}},
        {"text": "FastAPI это веб-фреймворк для создания API на Python",
         "source": "b.html", "metadata": {"chunk_index": 0}},
        {"text": "Рецепт борща: свёкла, капуста, говядина и картофель",
         "source": "c.html", "metadata": {"chunk_index": 0}},
    ]
    build_store(chunks, db_path=path)
    return Retriever(db_path=path, k=2)


def test_returns_default_k(retriever):
    assert len(retriever.retrieve("эмбеддинги")) == 2


def test_k_can_be_overridden(retriever):
    assert len(retriever.retrieve("эмбеддинги", k=3)) == 3


def test_finds_relevant_chunk_first(retriever):
    results = retriever.retrieve("как хранить векторы эмбеддингов", k=1)
    assert results[0].metadata["source"] == "a.html"