FROM python:3.11-alpine

RUN apk add --no-cache g++ gcc libxslt-dev libxml2-dev libffi-dev openssl-dev make

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry install

COPY . .

WORKDIR /app

CMD python ./src/serve/server.py