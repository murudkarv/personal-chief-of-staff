import os
from typing import Optional

import requests

WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v25.0")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")


def parse_whatsapp_message(payload: dict) -> Optional[dict]:
    """
    Parse incoming WhatsApp webhook payload and extract message information.
    Returns: {
        "from": phone_number,
        "message_type": "text" | "audio" | "image" | etc,
        "text": message_content,
        "message_id": id,
        "timestamp": timestamp
    }
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None

        message = messages[0]
        message_from = message.get("from")
        message_type = message.get("type", "text")
        message_id = message.get("id")
        timestamp = message.get("timestamp")

        text = None
        if message_type == "text":
            text = message.get("text", {}).get("body")
        elif message_type == "button":
            text = message.get("button", {}).get("text")

        return {
            "from": message_from,
            "message_type": message_type,
            "text": text,
            "message_id": message_id,
            "timestamp": timestamp,
        }
    except Exception as e:
        print(f"Error parsing WhatsApp message: {e}")
        return None


def send_whatsapp_message(to_phone: str, message_text: str) -> bool:
    """Send a text message via WhatsApp."""
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        print("WhatsApp credentials not configured")
        return False

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message_text},
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


def mark_message_as_read(message_id: str) -> bool:
    """Mark a received message as read."""
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        return False

    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return False
