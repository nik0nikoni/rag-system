from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader


LOADERS = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".md": TextLoader,
}


def load_all(data_dir: str) -> list[dict]:
    results = []
    for path in Path(data_dir).rglob("*"):
        if path.suffix not in LOADERS:
            continue

        loader_class = LOADERS[path.suffix]
        loader = loader_class(str(path), encoding="utf-8") if path.suffix != ".pdf" else loader_class(str(path))
        documents = loader.load()

        for doc in documents:
            results.append({
                "text": doc.page_content,
                "source": str(path),
                "metadata": {**doc.metadata, "filename": path.name},
            })

    return results