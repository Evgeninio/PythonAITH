FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    psycopg[binary] \
    aio-pika \
    prometheus-client \
    pydantic \
    pydantic-settings \
    httpx \
    pytest \
    pytest-cov


COPY app /app/app
COPY tests /app/tests

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
