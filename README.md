# Mailbridge

Mailbridge is a lightweight scaffold for receiving mail events, deduplicating and routing them, then forwarding to Telegram and Mattermost.

## Архитектурный выбор: B вместо A

Выбран **вариант B: разделение web и worker**, а не "всё в одном" процессе (A).

Почему B лучше для этого проекта:
- Web-сервис отвечает только за HTTP endpoints (`/health`, `/stats`, опционально `/metrics`).
- Worker изолирует polling и dispatch-логику, что проще масштабировать независимо.
- Фейлы в polling-пайплайне не блокируют HTTP readiness/liveness.
- Для Docker/Compose проще разделить ресурсы и рестарты по роли сервиса.

## Установка и локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.main:app
flask run --host 0.0.0.0 --port 8080
```

Worker:

```bash
python -m app.worker
```

## Конфиг

1. Основной путь: `/etc/mailbridge/config.toml`.
2. Fallback/override: переменные `MAILBRIDGE_*`.

Пример:

```toml
app_name = "mailbridge"
sqlite_path = "/data/mailbridge.db"
log_dir = "/var/log/mailbridge"
polling_interval_seconds = 30
secret_key = "replace-this"
profiling_enabled = false
metrics_enabled = true
timezone = "UTC"

[flask]
host = "0.0.0.0"
port = 8080

[retry_policy]
max_retries = 3
backoff_seconds = 1.5
```

## Docker

```bash
docker compose up --build
```

Сервисы:
- `web`: Flask HTTP interface.
- `worker`: polling/processing loop.

Volumes:
- `/etc/mailbridge` — конфигурация.
- `/var/log/mailbridge` — логи.
- `/data` — SQLite.

## Подключение Telegram/Mattermost

Текущий scaffold содержит routing/formatting слой. Интеграция транспортов выполняется в worker pipeline:
- Telegram: Bot API token + chat mapping.
- Mattermost: incoming webhook URL + channel mapping.

Рекомендуется добавить secret management через env (`MAILBRIDGE_*`) и не хранить токены в TOML.

## Логи и метрики

- Файловые логи:
  - `/var/log/mailbridge/app.log`
  - `/var/log/mailbridge/error.log`
- Docker mode: structured JSON logs в stdout.
- Внутренние тайминги + success/error counters для:
  - `fetch_mail`, `parse_mail`, `db_save`, `send_telegram`, `send_mattermost`
- Опциональный endpoint `/metrics` при включенном `metrics_enabled` и доступном `prometheus-client`.

## Миграции

В текущем scaffold выбран подход `metadata.create_all()` для быстрой инициализации схемы.

План на следующую версию:
1. Добавить Alembic.
2. Сгенерировать baseline migration.
3. Перевести CI на `alembic upgrade head`.

## Ограничения и roadmap

Текущие ограничения:
- Транспорт Telegram/Mattermost не реализован (только форматирование и роутинг).
- Dedup in-memory (после перезапуска state теряется).
- Нет ретраев на уровне внешних API вызовов.

Roadmap:
- Персистентный dedup store (SQLite/Redis).
- Полный retry/backoff слой и DLQ.
- Реализация transport adapters.
- Alembic migrations + rollback strategy.
- Production-grade observability (traces, labels, alerting).
