FROM python:3.12.12-alpine3.22

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .
EXPOSE 8000

WORKDIR /

ENV UV_COMPILE_BYTECODE=1

RUN apk add postgresql-dev
RUN uv sync