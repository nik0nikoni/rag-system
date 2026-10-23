import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from vectorstore import build_store, search


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
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
    return path


def test_search_returns_requested_number(db_path):
    results = search("поиск по эмбеддингам", k=2, db_path=db_path)
    assert len(results) == 2


def test_search_finds_relevant_chunk_first(db_path):
    results = search("как хранить векторы эмбеддингов", k=1, db_path=db_path)
    assert results[0].metadata["source"] == "a.html"


def test_search_keeps_metadata(db_path):
    results = search("веб-фреймворк на Python", k=1, db_path=db_path)
    assert results[0].metadata["source"] == "b.html"
    assert "chunk_index" in results[0].metadata