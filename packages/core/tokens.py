import hashlib
import hmac

from packages.core import settings


def generate_unsubscribe_token(email: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        email.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_unsubscribe_token(email: str, token: str) -> bool:
    expected = generate_unsubscribe_token(email)
    return hmac.compare_digest(expected, token)
