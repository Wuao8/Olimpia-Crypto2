import json
import os

FILE = "sent.json"


def load_sent():

    if not os.path.exists(FILE):
        return set()

    with open(FILE, "r") as f:
        return set(json.load(f))


def save_sent(sent):

    with open(FILE, "w") as f:
        json.dump(list(sent), f, indent=2)
