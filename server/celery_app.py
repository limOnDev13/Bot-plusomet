"""The module responsible for configuring the celery."""

from dataclasses import asdict

from celery import Celery

from server.config.app_config import CeleryConfig, get_config

celery_config: CeleryConfig = get_config().celery

app = Celery("celery_app")

app.conf.update(asdict(celery_config))

app.autodiscover_tasks(["server.tasks"])
