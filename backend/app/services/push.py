"""FCM push notifications (no-op if credentials are not configured)."""
import json, logging
from app.core.config import settings

log = logging.getLogger(__name__)
_app = None


def _init():
    global _app
    if _app or not settings.FCM_CREDENTIALS_JSON:
        return _app
    import firebase_admin
    from firebase_admin import credentials
    cred = credentials.Certificate(json.loads(settings.FCM_CREDENTIALS_JSON))
    _app = firebase_admin.initialize_app(cred)
    return _app


def notify(fcm_token: str | None, title: str, body: str):
    if not fcm_token or not _init():
        log.info("push skipped: %s — %s", title, body)
        return
    from firebase_admin import messaging
    messaging.send(messaging.Message(
        token=fcm_token,
        notification=messaging.Notification(title=title, body=body),
    ))
