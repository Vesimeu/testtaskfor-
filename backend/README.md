# Backend - File Exchange MVP

Бэкенд MVP-проекта файлообменника, построенный на чистой архитектуре NextCore (FastAPI + SQLAlchemy + Dishka + Celery).

## 📋 Содержание (Навигация)

- [Описание проекта](#описание-проекта)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
  - [Требования](#требования)
  - [Установка и настройка](#установка-и-настройка)
  - [Переменные окружения](#переменные-окружения)
  - [Применение миграций](#применение-миграций)
  - [Запуск приложения](#запуск-приложения)
  - [Запуск Celery воркера](#запуск-celery-воркера)

---

## Описание проекта

Проект представляет собой API файлообменника, который позволяет загружать файлы, валидировать метаданные, запускать фоновый анализ угроз и вести ленту алертов. 

В проекте используется:
- **FastAPI** — асинхронный веб-фреймворк.
- **Dishka** — Dependency Injection контейнер для разделения слоев.
- **SQLAlchemy 2.0 (asyncpg/psycopg2)** — ORM для работы с БД PostgreSQL.
- **Celery** — обработчик фоновых задач.
- **Pydantic v2** — DTO для валидации запросов и ответов.

---

## Структура проекта

```
src/
  api/
    routers/          # FastAPI роутеры (files_router, alerts_router)
    dto/              # Схемы валидации Pydantic (DTO)
    router.py         # Объединение всех роутеров
  core/
    config.py         # Настройки приложения и загрузка dotenv
    db.py             # Асинхронные и синхронные сессии SQLAlchemy
    exceptions.py     # Бизнес-исключения доменной области
    container.py      # Провайдеры Dishka и сборка DI контейнера
  models/             # SQLAlchemy ORM модели (Base, StoredFile, Alert)
  repository/         # Слой репозиториев (BaseRepository, FileRepository, AlertRepository)
  services/           # Слой бизнес-логики (FileService, AlertService, FileProcessingService)
  tasks/              # Celery-воркер и регистрация фоновых задач
app.py                # Инициализация и запуск приложения FastAPI
```

---

## Быстрый старт

### Требования

- **Python 3.11+**
- **PostgreSQL 13+**
- **Redis 6+** (для брокера Celery)
- **Poetry** (для управления зависимостями)

### Установка и настройка

1. **Создать виртуальное окружение**
   ```bash
   py -3.11 -m venv .venv
   ```

2. **Активировать виртуальное окружение**
   - Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```

3. **Установить Poetry** (если ещё не установлен)
   ```bash
   pip install poetry
   ```

4. **Установить зависимости проекта**
   ```bash
   poetry install
   ```

### Переменные окружения

1. **Скопировать шаблон переменных окружения** (находится в корневом каталоге проекта):
   ```bash
   cp ../simple.env .env
   ```

2. **Отредактировать `.env` и заполнить необходимые значения**

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ваш_пароль
POSTGRES_HOST=localhost
PGPORT=5432
POSTGRES_DB=имя_базы_данных
REDIS_URL=redis://localhost:6379/0
```

---

### Применение миграций

Применить все миграции базы данных (включая миграцию каскадного удаления алертов):
```bash
poetry run alembic upgrade head
```

---

### Запуск приложения

Запустить сервер разработки FastAPI (Uvicorn) с автоперезагрузкой при изменении кода:
```bash
poetry run uvicorn src.app:app --reload --port 8000
```

После запуска бэкенд будет доступен по адресу:
- **API**: `http://localhost:8000`
- **Интерактивная документация Swagger**: `http://localhost:8000/docs`

---

### Запуск Celery воркера

Фоновые задачи требуют запущенного сервера **Redis**.

Запустите Celery-воркер следующей командой:

- **Windows (локально)**:
  ```bash
  poetry run celery -A src.tasks.celery_app worker -l info -P solo
  ```
  *(Флаг `-P solo` обязателен на Windows во избежание системных блокировок billiard/multiprocessing).*

- **Linux / macOS / Docker**:
  ```bash
  poetry run celery -A src.tasks.celery_app worker -l info
  ```
