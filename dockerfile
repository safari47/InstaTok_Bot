FROM python:latest

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y postgresql-client && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app 

# FastAPI app assumed to be `main.py` in `app` directory
CMD ["uvicorn", "app.test:app", "--host", "0.0.0.0", "--port", "8000"]
