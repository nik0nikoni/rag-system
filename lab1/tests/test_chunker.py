import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.chunker import chunk_document, chunk_all


def test_chunk_document_splits_long_text():
    doc = {"text": "а" * 1000, "source": "test.txt", "metadata": {}}
    chunks = chunk_document(doc, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 1


def test_chunk_document_keeps_short_text_as_one_chunk():
    doc = {"text": "Короткий текст.", "source": "test.txt", "metadata": {}}
    chunks = chunk_document(doc, chunk_size=500, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Короткий текст."


def test_chunk_document_preserves_metadata():
    doc = {"text": "а" * 1000, "source": "test.txt", "metadata": {"filename": "test.txt"}}
    chunks = chunk_document(doc, chunk_size=500, chunk_overlap=100)
    assert all(c["metadata"]["filename"] == "test.txt" for c in chunks)
    assert all("chunk_index" in c["metadata"] for c in chunks)


def test_chunk_all_processes_multiple_documents():
    docs = [
        {"text": "а" * 1000, "source": "a.txt", "metadata": {}},
        {"text": "б" * 1000, "source": "b.txt", "metadata": {}},
    ]
    chunks = chunk_all(docs, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 2
    sources = {c["source"] for c in chunks}
    assert sources == {"a.txt", "b.txt"}