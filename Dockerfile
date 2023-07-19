FROM python:3.11.4-alpine3.18

WORKDIR /app

RUN apk add git

RUN pip3 install poetry==1.5.1

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main --no-interaction --no-ansi

COPY . /app
