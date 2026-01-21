FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir \
    sqlalchemy \
    psycopg[binary] \
    aio-pika \
    pydantic-settings

COPY app /app/app
COPY tests /app/tests

CMD ["python", "-m", "app.main"]

