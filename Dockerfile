FROM python:3.14-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=ghcr.io/casey/just:latest /just /usr/local/bin/


WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

ADD pyproject.toml uv.lock ./
RUN uv sync --locked

ADD ./app ./app
ADD Justfile ./


FROM python:3.14-slim-bookworm


WORKDIR /app

# Copy only the necessary installed packages and application code from the builder stage
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin/just /usr/local/bin/
COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run"]