from rq import Queue
from . import store

QUEUE_NAME = "videos"


def enqueue(jid: str, payload: dict):
    q = Queue(QUEUE_NAME, connection=store.rq_conn)
    # payload has NO api keys; those travel separately, encrypted, and expire.
    q.enqueue("app.pipeline.run_job", jid, payload, job_timeout=1800, result_ttl=0, failure_ttl=3600)
