# mailbridge

Bootstrap-проект для маршрутизации входящих email в мессенджеры с веб-интерфейсом и worker-процессом.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
python -m app.web
```

## Worker

```bash
python -m app.worker
```

## Структура

- `app/web` — Flask UI (factory + blueprints + forms + views).
- `app/services` — маршрутизация, обработка почты, доставка, retry.
- `app/adapters` — интеграции с IMAP / Telegram / Mattermost.
- `app/metrics` — counters/timing + `/metrics` endpoint.
- `etc/mailbridge/config.example.toml` — пример конфигурации.
