import os
import requests

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        },
        timeout=20
    )
