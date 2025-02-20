FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATHBUFFERED=1

RUN pip install --upgrade pip uv
COPY pyproject.toml ./
RUN uv sync --no-dev

WORKDIR src
COPY ../producer_consumer/ ./producer_consumer/
COPY ../schemas/ ./schemas/
COPY ./bot/ ./bot/