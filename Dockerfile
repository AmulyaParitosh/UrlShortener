FROM python:3.11-slim

LABEL org.opencontainers.image.source https://github.com/AmulyaParitosh/UrlShortener
LABEL org.opencontainers.image.description="UrlShortener Container Image"
LABEL org.opencontainers.image.licenses=MIT

RUN pip install poetry==1.3.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY serviceAccountKey.json ./
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY UrlShortener/src ./UrlShortener/src
COPY UrlShortener/__init__.py ./UrlShortener/__init__.py

RUN poetry install --without dev

CMD ["poetry", "run", "uvicorn", "UrlShortener:app", "--host", "0.0.0.0", "--port", "80"]
