from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from bs4 import BeautifulSoup
from loguru import logger


def load_txt_like(path: Path) -> list[dict]:
    logger.debug(f"Загружаю TXT/MD: {path.name}")
    loader = TextLoader(str(path), encoding="utf-8")
    documents = loader.load()
    return [
        {"text": doc.page_content, "source": str(path), "metadata": {**doc.metadata, "filename": path.name}}
        for doc in documents
    ]


def load_pdf_like(path: Path) -> list[dict]:
    logger.debug(f"Загружаю PDF: {path.name}")
    loader = PyPDFLoader(str(path))
    documents = loader.load()

    empty_pages = sum(1 for doc in documents if len(doc.page_content.strip()) == 0)
    if empty_pages > 0:
        logger.warning(f"{path.name}: {empty_pages} пустых страниц из {len(documents)}")

    return [
        {"text": doc.page_content, "source": str(path), "metadata": {**doc.metadata, "filename": path.name}}
        for doc in documents
    ]


def load_html_like(path: Path) -> list[dict]:
    logger.debug(f"Загружаю HTML: {path.name}")
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("div", class_="article-formatted-body")

    if not body:
        logger.warning(f"{path.name}: не найден класс article-formatted-body, использую весь текст страницы")

    text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)
    return [{"text": text, "source": str(path), "metadata": {"filename": path.name}}]


LOADERS = {
    ".txt": load_txt_like,
    ".md": load_txt_like,
    ".pdf": load_pdf_like,
    ".html": load_html_like,
}


def load_all(data_dir: str) -> list[dict]:
    logger.info(f"Начинаю загрузку документов из '{data_dir}'")
    results = []
    for path in Path(data_dir).rglob("*"):
        if path.suffix not in LOADERS:
            continue
        results.extend(LOADERS[path.suffix](path))

    logger.success(f"Загрузка завершена: {len(results)} документов из '{data_dir}'")
    return results