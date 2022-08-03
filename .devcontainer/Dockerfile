ARG VARIANT="3.10-bullseye"
ARG PY_POETRY_HOME="/opt/poetry"
ARG PY_POETRY_VERSION="1.1"

FROM python:${VARIANT}

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV DEBIAN_FRONTEND=dialog