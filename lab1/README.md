# Lab 1 — RAG по статьям Хабра

## Цель

Сделать вопросно-ответную систему (RAG) по статьям с Хабра. Пользователь задаёт вопрос на русском, система ищет подходящие фрагменты статей и отвечает только по ним. Если в базе нет ответа, система говорит: «В базе нет информации по этому вопросу.»

## Архитектура

```
lab1/
├── app.py               # веб-чат на Gradio
├── main.py              # консольный вариант того же чата
├── data/                # исходные документы (.html, .txt, .md, .pdf)
├── chroma_db/           # векторная база (создаётся build_index.py)
├── logs/pipeline.log    # логи loguru
├── src/
│   ├── grabber.py       # скачивание статей пользователя с habr.com
│   ├── loader.py        # загрузка .txt/.md/.pdf/.html
│   ├── cleaner.py       # нормализация текста, отбрасывание мусора
│   ├── chunker.py       # разбиение на чанки
│   ├── embedder.py      # модель эмбеддингов
│   ├── vectorstore.py   # Chroma: построение и поиск
│   ├── build_index.py   # фаза индексации целиком
│   ├── retriever.py     # поиск кандидатов в Chroma
│   ├── reranker.py      # переранжирование cross-encoder'ом
│   ├── filters.py       # фильтр по порогу оценки
│   ├── generator.py     # генерация ответа через Gemini
│   └── pipeline.py      # фаза ответа целиком + трейсинг Langfuse
└── tests/
```

### Фаза индексации (`src/build_index.py`)

Выполняется один раз, а потом заново после каждого изменения `data/`.

1. **Grabber** (`grabber.py`, необязательный шаг, запускается вручную) — скачивает HTML-статьи пользователя Хабра в `data/` как `habr_<id>.html`.
2. **Loader** (`loader.py`) — рекурсивно читает `data/`. Из HTML берётся только тело статьи (`div.article-formatted-body`), PDF читается постранично.
3. **Cleaner** (`cleaner.py`) — схлопывает пробелы и пустые строки, убирает строки-мусор. Документы короче 30 символов отбрасываются.
4. **Chunker** (`chunker.py`) — `RecursiveCharacterTextSplitter`, `chunk_size=500`, `chunk_overlap=100`.
5. **Embedder + Vectorstore** (`embedder.py`, `vectorstore.py`) — эмбеддинги считает `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Чанки пишутся в Chroma (`chroma_db/`, коллекция `habr_articles`) пачками по 500.

Перед индексацией старая `chroma_db/` удаляется, чтобы не появлялись дубли.

### Фаза ответа (`src/pipeline.py`, класс `RAGPipeline`)

1. **Retrieve** — similarity search в Chroma, берутся 30 кандидатов (`TOP_K_RETRIEVE`).
2. **Rerank** — cross-encoder `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` переоценивает кандидатов и оставляет 5 лучших (`TOP_K_FINAL`).
3. **Filter** — отбрасываются чанки с `rerank_score < 0.0` (`MIN_SCORE`). По замерам релевантные чанки получают от ~0.7, нерелевантные — ниже −1.7.
4. **Generate** — Gemini (`ChatGoogleGenerativeAI`, `temperature=0`, 2 повтора, таймаут 30 с) отвечает строго по контексту. Если после фильтра не осталось ни одного чанка, LLM не вызывается и сразу возвращается «нет информации».

Результат — ответ и список источников (файл и лучшая оценка reranker'а по нему). Каждый шаг (`retrieve`, `rerank`, `filter`, `generate`) и запрос целиком (`rag-query`) пишутся в Langfuse как спаны. Вызов LLM трейсится через `langfuse.langchain.CallbackHandler`.

## Запуск через pixi

Все команды выполняются из папки `lab1/`: пути `data/`, `chroma_db/` и `logs/` относительные.

```bash
pixi install                          # создать окружение (Python 3.10 + зависимости из pixi.toml)

pixi run python src/build_index.py    # фаза индексации: data/ -> chroma_db/
pixi run python app.py                # веб-чат Gradio, по умолчанию http://127.0.0.1:7860
pixi run python main.py               # консольный чат (exit — выход)
```

При первом запуске с Hugging Face скачиваются модели эмбеддингов и reranker'а, на это нужно время и интернет.

Скачать свежие статьи (необязательно):

```bash
pixi run python -c "import sys; sys.path.append('src'); from grabber import grab_all; grab_all('<username>', max_pages=5)"
```

После этого нужно снова запустить `build_index.py`.

## Настройка `.env`

Скопируйте шаблон и заполните его:

```bash
cp .env.example .env
```

| Переменная | Обязательна | Описание |
|---|---|---|
| `GOOGLE_API_KEY` | да | Ключ Gemini API (Google AI Studio). Нужен на шаге генерации. |
| `LLM_MODEL` | нет | Модель Gemini, по умолчанию `gemini-3.8-flash`. |
| `LANGFUSE_PUBLIC_KEY` | для трейсинга | Публичный ключ проекта Langfuse. |
| `LANGFUSE_SECRET_KEY` | для трейсинга | Секретный ключ проекта Langfuse. |
| `LANGFUSE_HOST` | для трейсинга | Адрес Langfuse, например `https://cloud.langfuse.com`. |

Переменные загружаются через `python-dotenv` в `pipeline.py` и `generator.py`. Файл `.env` не должен попадать в git.

## Тесты

```bash
pixi run pytest tests/ -v
```

- `test_loader`, `test_cleaner`, `test_chunker`, `test_filters` — быстрые unit-тесты. `test_loader` читает реальную папку `data/`, поэтому pytest нужно запускать из `lab1/`.
- `test_embedder`, `test_reranker` — загружают реальные модели (при первом запуске нужен интернет).
- `test_vectorstore`, `test_retriever` — строят временную Chroma во временной папке и не трогают `chroma_db/`.

Генерация (Gemini) тестами не покрыта, поэтому для тестов не нужны ни `GOOGLE_API_KEY`, ни ключи Langfuse.

## Ограничения

- **Маленький корпус**: около 40 статей одного автора. На вопросы за пределами этих тем система честно отвечает «нет информации».
- **Индексация только полная**: `build_index.py` каждый раз удаляет и пересобирает всю базу, инкрементального обновления нет.
- **Нет памяти диалога**: каждый вопрос обрабатывается отдельно, история чата в pipeline не передаётся.
- **Порог фильтра подобран вручную** (`MIN_SCORE = 0.0`) на небольшом наборе запросов и может не подойти для другого корпуса.
- **Размер чанка в символах** (500/100), без учёта структуры статьи. Код и таблицы могут разрезаться посередине.
- **Парсер HTML привязан к вёрстке Хабра** (`article-formatted-body`). Для других сайтов берётся весь текст страницы вместе с навигацией.
- **Зависимость от внешних сервисов**: генерации нужен доступ к Gemini API. При ошибке API пользователь видит сообщение «сервис временно недоступен».
- **Только CPU, только Windows**: в `pixi.toml` указана платформа `win-64`. Модели работают на CPU, поэтому первый запрос после старта медленный.
- **Grabber** не умеет обходить ограничения частоты запросов Хабра (между запросами пауза 1 с) и не имеет отдельной команды запуска.
