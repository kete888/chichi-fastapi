"""极简的登录凭证：HMAC 签名的 cookie，不依赖任何第三方库。"""

import base64
import hashlib
import hmac
import json
import time

from core.config import settings

COOKIE_NAME = "session"


def _sign(body: str) -> str:
    return hmac.new(
        settings.secret_key.encode(), body.encode(), hashlib.sha256
    ).hexdigest()


def create_token(username: str) -> str:
    payload = {
        "u": username,
        "exp": int(time.time()) + settings.session_hours * 3600,
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    return f"{body}.{_sign(body)}"


def verify_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False

    try:
        body, sig = token.rsplit(".", 1)
    except ValueError:
        return False

    if not hmac.compare_digest(sig, _sign(body)):
        return False

    try:
        padded = body + "=" * (-len(body) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return False

    return data.get("exp", 0) > time.time()


def check_password(username: str, password: str) -> bool:
    ok_user = hmac.compare_digest(username, settings.admin_username)
    ok_pass = hmac.compare_digest(password, settings.admin_password)
    return ok_user and ok_pass
