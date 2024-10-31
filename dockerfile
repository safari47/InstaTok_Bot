FROM python:latest

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y postgresql-client && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app app