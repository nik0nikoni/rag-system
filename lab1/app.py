import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.append(str(BASE_DIR / "src"))

import log_config  # noqa: F401
import gradio as gr
from loguru import logger

from pipeline import RAGPipeline

pipeline = RAGPipeline()   # создаётся один раз при запуске


def chat(message: str, history: list) -> str:
    if not message.strip():
        return "Введите вопрос."
    try:
        result = pipeline.query(message)
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        return "Не удалось получить ответ от модели (сервис временно недоступен). Попробуйте ещё раз через минуту."

    answer = result["answer"]
    if result["sources"]:
        sources = "\n".join(f"- `{s['source']}` (оценка {s['score']})" for s in result["sources"])
        answer += f"\n\n**Источники:**\n{sources}"
    return answer


demo = gr.ChatInterface(
    fn=chat,
    title="RAG по статьям Хабра",
    description="Задайте вопрос по статьям. Если ответа в базе нет, система так и скажет.",
    examples=["Что такое Redis?", "Как установить Docker?", "Как использовать LangGraph?"],
)

if __name__ == "__main__":
    demo.launch()