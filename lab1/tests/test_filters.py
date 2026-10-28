import sys
from pathlib import Path

from langchain_core.documents import Document

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from filters import apply_filters


def make_docs():
    return [
        Document(page_content="a", metadata={"source": "x", "rerank_score": 0.9}),
        Document(page_content="b", metadata={"source": "y", "rerank_score": 0.5}),
        Document(page_content="c", metadata={"source": "x", "rerank_score": 0.1}),
    ]


def test_no_filters_keeps_everything():
    assert len(apply_filters(make_docs())) == 3


def test_min_score_drops_low_scores():
    result = apply_filters(make_docs(), min_score=0.4)
    assert [d.page_content for d in result] == ["a", "b"]


def test_sources_filter():
    result = apply_filters(make_docs(), sources=["x"])
    assert [d.page_content for d in result] == ["a", "c"]


def test_max_docs_limits_count():
    assert len(apply_filters(make_docs(), max_docs=1)) == 1


def test_missing_score_is_dropped_when_threshold_set():
    docs = [Document(page_content="n", metadata={"source": "x"})]
    assert apply_filters(docs, min_score=0.0) == []


def test_empty_input():
    assert apply_filters([]) == []