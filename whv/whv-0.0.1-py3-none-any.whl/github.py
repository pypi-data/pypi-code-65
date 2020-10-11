import hmac
import hashlib


def verify(payload: bytes, secret: bytes, signature: bytes) -> bool:
    """Verifies a GitHub webhook.

    Args:
        payload (bytes): the json body of your request
        secret (bytes): the webhook secret set on GitHub
        signature (bytes): the content of your requests X-Hub-Signature header
    """
    digest = hmac.new(
        key=secret, msg=payload, digestmod=hashlib.sha1).hexdigest()

    predicted = ('sha1=' + digest).encode()
    return hmac.compare_digest(predicted, signature)
