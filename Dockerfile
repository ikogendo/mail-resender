FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY templates ./templates
COPY static ./static

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["python", "-m", "app.web"]
