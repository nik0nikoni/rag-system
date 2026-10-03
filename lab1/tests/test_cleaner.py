import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.cleaner import normalize_whitespace, remove_short_lines_noise, clean_document, clean_all


def test_normalize_whitespace_collapses_spaces():
    text = "Привет    мир"
    result = normalize_whitespace(text)
    assert result == "Привет мир"


def test_normalize_whitespace_collapses_newlines():
    text = "Строка 1\n\n\n\nСтрока 2"
    result = normalize_whitespace(text)
    assert result == "Строка 1\n\nСтрока 2"


def test_normalize_whitespace_strips_edges():
    text = "   текст с пробелами по краям   "
    result = normalize_whitespace(text)
    assert result == "текст с пробелами по краям"


def test_clean_document_drops_short_text():
    doc = {"text": "ок", "source": "test.txt", "metadata": {}}
    result = clean_document(doc, min_text_length=30)
    assert result is None


def test_clean_document_keeps_long_text():
    doc = {"text": "Это достаточно длинный текст для прохождения проверки минимальной длины.", "source": "test.txt", "metadata": {}}
    result = clean_document(doc, min_text_length=30)
    assert result is not None
    assert result["text"] == doc["text"].strip()


def test_clean_all_filters_empty_documents():
    docs = [
        {"text": "Нормальный длинный текст документа для проверки.", "source": "a.txt", "metadata": {}},
        {"text": "", "source": "b.txt", "metadata": {}},
        {"text": "ок", "source": "c.txt", "metadata": {}},
    ]
    result = clean_all(docs, min_text_length=20)
    assert len(result) == 1
    assert result[0]["source"] == "a.txt"