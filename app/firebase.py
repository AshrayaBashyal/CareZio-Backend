import json
import firebase_admin
from firebase_admin import credentials, messaging
from app.config import settings

"""
Firebase integration for sending push notifications.
"""

# If no credentials provided, do not raise — provide a safe stub so local dev works
cred_data = settings.firebase_credentials

if cred_data:
    try:
        cred_dict = json.loads(cred_data)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        HAS_FIREBASE = True
    except json.JSONDecodeError:
        try:
            cred = credentials.Certificate(cred_data)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            HAS_FIREBASE = True
        except Exception as e:
            print(f"[Firebase] Failed to initialize with provided credentials: {e}")
            HAS_FIREBASE = False
    except Exception as e:
        print(f"[Firebase] Error initializing firebase: {e}")
        HAS_FIREBASE = False
else:
    print("[Firebase] No firebase credentials provided — push notifications disabled.")
    HAS_FIREBASE = False

def send_push_notification(token: str, title: str, body: str):
    """
    Send a push notification with the given title and body to a FCM token.
    """
    if not HAS_FIREBASE:
        print(f"[Firebase] Skipping send (no config). Token start: {token[:10] if token else 'N/A'}... Title: {title}")
        return None
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        response = messaging.send(message)
        print(f"[Firebase] Notification sent. Response: {response}")
        return response
    except Exception as e:
        print(f"[Firebase] Failed to send push: {e}")
        return None
