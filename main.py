import os
import json
import requests
import pandas as pd
from ta.trend import EMAIndicator

BASE_URL = "https://api.mexc.com"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "state.json"


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram non configurato.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=15
    )


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_usdt_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"

    data = requests.get(url, timeout=20).json()

    symbols = []

    for s in data["symbols"]:
        if (
            s["status"] == "1"
            and s["quoteAsset"] == "USDT"
            and s["isSpotTradingAllowed"]
        ):
            symbols.append(s["symbol"])

    return symbols

def get_daily_dataframe(symbol):

    url = (
        f"{BASE_URL}/api/v3/klines"
        f"?symbol={symbol}&interval=1d&limit=50"
    )

    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return None

    data = r.json()

    if len(data) < 25:
        return None

    df = pd.DataFrame(data)

    df = df.iloc[:, :6]
    df.columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    df["close"] = df["close"].astype(float)

    df["ema20"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    return df


def crossed_up(df):

    prev = df.iloc[-2]
    last = df.iloc[-1]

    return (
        prev["close"] <= prev["ema20"]
        and
        last["close"] > last["ema20"]
    )

def main():

    print("Scansione MEXC...")

    state = load_state()

    symbols = get_usdt_symbols()

    print(f"Trovate {len(symbols)} coppie USDT")

    for symbol in symbols:

        try:

            df = get_daily_dataframe(symbol)

            if df is None:
                continue

            signal = crossed_up(df)

            if signal and not state.get(symbol, False):

                price = round(df.iloc[-1]["close"], 8)

                message = (
                    f"🚀 EMA20 DAILY CROSS\n\n"
                    f"{symbol}\n"
                    f"Prezzo: {price}"
                )

                print(message)

                send_telegram(message)

                state[symbol] = True

            elif not signal:

                state[symbol] = False

        except Exception as e:

            print(symbol, e)

    save_state(state)

    print("Fine scansione.")


if __name__ == "__main__":
    main()
