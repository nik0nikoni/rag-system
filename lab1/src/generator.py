import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

PROMPT = """Ты помощник, который отвечает на вопросы строго по приведённому контексту.
Если в контексте нет ответа, так и скажи: "В базе нет информации по этому вопросу."
Не используй знания, которых нет в контексте. Отвечай по-русски, кратко.

Контекст:
{context}

Вопрос: {question}

Ответ:"""

NO_ANSWER = "В базе нет информации по этому вопросу."


def _to_text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


class Generator:
    def __init__(self, model: str = MODEL):
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=0)

    def generate(self, question: str, docs: list[Document]) -> str:
        if not docs:
            logger.info("Generator: контекста нет, LLM не вызываю")
            return NO_ANSWER

        context = "\n\n".join(f"[{i + 1}] {d.page_content}" for i, d in enumerate(docs))
        logger.debug(f"Generator: вызываю модель, чанков в контексте: {len(docs)}")
        response = self.llm.invoke(PROMPT.format(context=context, question=question))
        return _to_text(response.content)