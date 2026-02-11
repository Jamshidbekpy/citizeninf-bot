"""
Prometheus metrics — faqat hisoblash, loyiha logikasiga ta'sir qilmaydi.
"""
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

WEBHOOK_REQUESTS = Counter(
    "webhook_requests_total",
    "Total webhook requests received",
)
APPEALS_CREATED = Counter(
    "appeals_created_total",
    "Total appeals created",
    ["district"],
)
CALLBACKS_DONE = Counter(
    "callbacks_done_total",
    "Total admin callbacks (ko'rib chiqildi)",
)


def get_metrics() -> bytes:
    return generate_latest()


def get_metrics_content_type() -> str:
    return CONTENT_TYPE_LATEST
