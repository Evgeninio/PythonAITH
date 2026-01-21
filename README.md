# PythonProjectAITH

Учебный backend-проект с демонстрацией микросервисной архитектуры:

**API → Message Broker → Consumer → Database**

## Архитектура

Система состоит из следующих компонентов:

- **API (FastAPI)**  
  Принимает HTTP-запросы, сохраняет данные в БД, публикует события в RabbitMQ,
  отдает метрики Prometheus.
- **Consumer (Python)**  
  Подписывается на очередь RabbitMQ и обрабатывает события.
- **PostgreSQL**  
  Основная база данных.
- **RabbitMQ**  
  Брокер сообщений.
- **Prometheus**  
  Сбор метрик с API.
- **Grafana**  
  Визуализация метрик.

### Сценарий работы
1. Клиент отправляет `POST /orders`
2. API сохраняет заказ в БД (`status = NEW`)
3. API публикует событие `order.created`
4. Consumer получает сообщение
5. Consumer обновляет заказ (`status = PROCESSED`)


## 📁 Структура проекта

```text
pythonback-aith/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI: запуск тестов и проверка покрытия
│
├── server/                        # HTTP API (FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── orders.py          # Роуты для работы с заказами
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # SQLAlchemy модели
│   │   │   └── session.py         # Создание DB-сессий
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── publisher.py       # Публикация событий в RabbitMQ
│   │   │
│   │   ├── __init__.py
│   │   ├── main.py                # Точка входа FastAPI
│   │   ├── metrics.py             # Prometheus-метрики
│   │   └── settings.py            # Конфигурация сервиса
│   │
│   ├── tests/                     # Тесты сервера
│   │   ├── conftest.py
│   │   ├── test_health_and_metrics.py
│   │   ├── test_orders.py
│   │   ├── test_orders_happy_path.py
│   │   ├── test_orders_publish_failed.py
│   │   └── test_orders_validation.py
│   │
│   ├── Dockerfile                 # Docker-образ API
│   └── pyproject.toml             # Зависимости сервера
│
├── consumer/                      # Consumer (RabbitMQ worker)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── db.py                  # Работа с БД
│   │   ├── main.py                # Точка входа consumer
│   │   ├── settings.py            # Конфигурация
│   │   └── worker.py              # Обработка сообщений из RabbitMQ
│   │
│   ├── tests/
│   │   └── test_worker.py         # Тесты consumer
│   │
│   ├── Dockerfile                 # Docker-образ consumer
│   └── pyproject.toml             # Зависимости consumer
│
├── monitoring/
│   ├── prometheus.yml             # Конфигурация Prometheus
│   └── grafana/                   # (опционально) provisioning Grafana
│
├── docker-compose.yml             # Запуск всей системы одной командой
├── .gitignore                     # Игнорируемые файлы
└── README.md                      # Документация проекта


## Запуск проекта

### Запуск

```bash
docker compose up --build -d
```

### Проверка контейнеров:

``` bash
docker compose ps
```

# API

### Healthcheck

```
GET http://localhost:8000/health
```
```
{"status":"ok"}
```

### Swagger UI

```
http://localhost:8000/docs
```

### Создание заказа

```
POST http://localhost:8000/orders
```

#### Пример тела запроса:
```
{
  "customer_id": 1,
  "items": [{"sku": "abc", "qty": 2}],
  "total": 10.5
}
```

### Получение заказа
```
GET http://localhost:8000/orders/{id}
```

### Grafana

```
http://localhost:3000
```