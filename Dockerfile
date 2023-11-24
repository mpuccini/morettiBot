FROM python:3.11-buster as builder

# Install poetry
RUN pip install --upgrade pip && \
    pip install poetry

ENV POETRY_NO_INTERACTIONS=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR='/var/cache/poetry_cache'

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi && rm -rf $POETRY_CACHE_DIR



FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY bot /app/bot




