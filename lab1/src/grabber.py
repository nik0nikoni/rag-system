import time
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from loguru import logger


BASE_URL = "https://habr.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (educational RAG project, Chisinau Technical University)"}


def get_article_links(username: str, max_pages: int = 5) -> list[str]:
    logger.info(f"Начинаю сбор ссылок для пользователя '{username}', страниц: {max_pages}")
    links = []
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}/ru/users/{username}/articles/"
        else:
            url = f"{BASE_URL}/ru/users/{username}/articles/page{page}/"

        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            logger.warning(f"Страница {page} вернула статус {response.status_code}, останавливаюсь")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        found = soup.find_all("a", href=re.compile(r"/articles/\d+/?$"))
        for a in found:
            href = a["href"]
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in links:
                links.append(full_url)

        logger.debug(f"Страница {page}: найдено ссылок всего {len(links)}")
        time.sleep(1)

    logger.info(f"Сбор ссылок завершён, итого найдено: {len(links)}")
    return links


def download_article(url: str, save_dir: str = "data") -> str:
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Не удалось скачать {url}: {e}")
        raise

    article_id = url.rstrip("/").split("/")[-1]
    filename = f"habr_{article_id}.html"
    path = Path(save_dir) / filename
    path.write_text(response.text, encoding="utf-8")

    logger.debug(f"Скачано: {filename}")
    time.sleep(1)
    return str(path)


def grab_all(username: str, max_pages: int = 5, save_dir: str = "data") -> list[str]:
    Path(save_dir).mkdir(exist_ok=True)
    links = get_article_links(username, max_pages)
    saved_files = []
    for link in links:
        try:
            saved_files.append(download_article(link, save_dir))
        except requests.RequestException:
            continue

    logger.success(f"Grabber завершил работу: скачано {len(saved_files)} из {len(links)} статей")
    return saved_files