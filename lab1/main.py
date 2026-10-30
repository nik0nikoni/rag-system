import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)                      # относительные пути (chroma_db, logs) всегда от lab1
sys.path.append(str(BASE_DIR / "src"))

import log_config  # noqa: F401  (настройка логгера)
from pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()
    while True:
        question = input("\nВопрос (exit для выхода): ").strip()
        if question.lower() in ("exit", "quit", ""):
            break
        result = pipeline.query(question)
        print(f"\nОтвет: {result['answer']}")
        for s in result["sources"]:
            print(f"  - {s['source']} (оценка {s['score']})")


if __name__ == "__main__":
    main()