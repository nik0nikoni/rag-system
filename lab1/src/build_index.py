import shutil

import log_config
from loguru import logger

from loader import load_all
from cleaner import clean_all
from chunker import chunk_all
from vectorstore import build_store, DB_PATH


def build_index(data_dir: str = "data", db_path: str = DB_PATH) -> None:
    logger.info("=== Старт индексации ===")

    shutil.rmtree(db_path, ignore_errors=True)   # чистим старую базу, чтобы не было дублей

    docs = load_all(data_dir)
    cleaned = clean_all(docs)
    chunks = chunk_all(cleaned)
    build_store(chunks, db_path=db_path)

    logger.success("=== Индексация завершена ===")


if __name__ == "__main__":
    build_index()