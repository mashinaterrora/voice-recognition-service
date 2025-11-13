FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y python3-dev gcc ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY ../pyproject.toml /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY docker /app/
