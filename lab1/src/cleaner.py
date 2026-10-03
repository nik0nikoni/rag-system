import re
from loguru import logger


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def remove_short_lines_noise(text: str, min_line_length: int = 2) -> str:
    """Убирает отдельные строки-мусор (например, одиночные символы от OCR)."""
    lines = text.split("\n")
    cleaned_lines = [line for line in lines if len(line.strip()) >= min_line_length or line.strip() == ""]
    return "\n".join(cleaned_lines)


def clean_document(doc: dict, min_text_length: int = 30) -> dict | None:
    """Чистит один документ. Возвращает None, если после очистки документ бесполезен."""
    text = doc["text"]
    text = normalize_whitespace(text)
    text = remove_short_lines_noise(text)

    if len(text) < min_text_length:
        logger.debug(f"Отброшен после очистки (слишком короткий): {doc['source']}")
        return None

    cleaned_doc = dict(doc)
    cleaned_doc["text"] = text
    return cleaned_doc


def clean_all(docs: list[dict], min_text_length: int = 30) -> list[dict]:
    logger.info(f"Начинаю очистку {len(docs)} документов")

    cleaned = []
    dropped = 0
    for doc in docs:
        result = clean_document(doc, min_text_length)
        if result is not None:
            cleaned.append(result)
        else:
            dropped += 1

    logger.success(f"Очистка завершена: {len(cleaned)} документов оставлено, {dropped} отброшено")
    return cleaned