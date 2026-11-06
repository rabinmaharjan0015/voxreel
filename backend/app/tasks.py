from .celery_app import celery

QUEUE_NAME = "videos"


def enqueue(jid: str, payload: dict):
    # payload has NO api keys; those travel separately, encrypted, and expire.
    # send_task by name so the API process doesn't import heavy ML deps.
    celery.send_task("app.pipeline.run_job", args=[jid, payload], queue=QUEUE_NAME)
