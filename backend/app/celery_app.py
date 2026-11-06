"""Celery application — Redis broker, video/publish task queue.

The worker imports app.pipeline and app.publisher (see include= below) so the
task functions get registered. The API process uses celery.send_task() by name,
so it never needs to import the heavy ML/ffmpeg dependencies.
"""
from celery import Celery
from .config import REDIS_URL

celery = Celery(
    "voxreel",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.pipeline", "app.publisher"],
)

celery.conf.update(
    task_default_queue="videos",
    # We store job state in Redis directly via store.update(), so we don't
    # need Celery's result backend — ignore it to keep Redis clean.
    task_ignore_result=True,
    # Hard 30-min limit, soft at 29 min so the task can store a clean error.
    task_time_limit=1800,
    task_soft_time_limit=1740,
    # One task at a time per worker process — video jobs are long and heavy.
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,  # recycle after 10 jobs to free ML model memory
)
