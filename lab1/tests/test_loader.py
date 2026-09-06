import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from loader import load_all


def test_load_all_returns_documents():
    docs = load_all("data")
    assert len(docs) > 0, "Loader не нашёл ни одного документа в data/"


def test_documents_have_required_fields():
    docs = load_all("data")
    for doc in docs:
        assert "text" in doc
        assert "source" in doc
        assert "metadata" in doc


def test_documents_are_not_empty():
    docs = load_all("data")
    for doc in docs:
        assert len(doc["text"]) > 0, f"Пустой текст в файле {doc['source']}"