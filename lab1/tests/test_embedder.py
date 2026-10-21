import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.embedder import embed_texts, get_embeddings


def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


@pytest.fixture(scope="module")
def vectors():
    texts = [
        "FastAPI это современный веб-фреймворк для Python",
        "Как запустить сервер на FastAPI",
        "Рецепт борща с говядиной",
    ]
    return embed_texts(texts)


def test_returns_one_vector_per_text(vectors):
    assert len(vectors) == 3


def test_vector_dimension(vectors):
    assert all(len(v) == 384 for v in vectors)


def test_similar_texts_are_closer_than_different(vectors):
    similar = cosine(vectors[0], vectors[1])
    different = cosine(vectors[0], vectors[2])
    assert similar > different


def test_model_is_loaded_only_once():
    assert get_embeddings() is get_embeddings()