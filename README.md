# Mini Order Processing System

Учебный backend-проект с демонстрацией микросервисной архитектуры:

**API → Message Broker → Consumer → Database**

Проект полностью запускается локально через **Docker Compose** и покрыт тестами
с общим покрытием **не менее 90%**.

---

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

---

## Структура проекта
├── docker-compose.yml
├── README.md
├── server
│ ├── Dockerfile
│ ├── app
│ │ ├── api
│ │ ├── db
│ │ ├── services
│ │ ├── metrics.py
│ │ ├── settings.py
│ │ └── main.py
│ └── tests
│ └── test_*.py
├── consumer
│ ├── Dockerfile
│ └── app
│ ├── db.py
│ ├── worker.py
│ ├── settings.py
│ └── main.py
└── monitoring
├── prometheus.yml
└── grafana

## Запуск проекта

### Требования
- Docker
- Docker Compose

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