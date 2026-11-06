import httpx

transport = None  # tests inject httpx.MockTransport here


class PublishError(Exception):
    pass


def client(timeout: float = 300) -> httpx.Client:
    return httpx.Client(transport=transport, timeout=timeout, follow_redirects=True)
