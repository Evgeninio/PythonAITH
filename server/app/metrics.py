from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

ORDERS_CREATED_TOTAL = Counter(
    "orders_created_total",
    "Total created orders",
)

BROKER_PUBLISH_TOTAL = Counter(
    "broker_publish_total",
    "Total broker publish attempts",
    ["result"],
)

BROKER_PUBLISH_DURATION_SECONDS = Histogram(
    "broker_publish_duration_seconds",
    "Broker publish duration in seconds",
)
