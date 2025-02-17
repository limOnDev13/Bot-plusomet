"""The module responsible for configuring the celery."""

from celery import Celery

from server.config.app_config import CeleryConfig, get_config

celery_config: CeleryConfig = get_config().celery

app = Celery("celery_app")

app.conf.update(
    broker_url=celery_config.broker,
    result_backed=celery_config.backend,
    accept_content=celery_config.accept_content,
    result_expires=celery_config.result_expires,
)

app.autodiscover_tasks(["server.tasks"])
