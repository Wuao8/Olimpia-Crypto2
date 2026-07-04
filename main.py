import requests
import pandas as pd

from indicators import ema20
from telegram import send
from state import load_sent, save_sent

BASE = "https://api.mexc.com"

MIN_DAYS_BELOW = 5


def get_symbols():

    data = requests.get(
        BASE + "/api/v3/exchangeInfo",
        timeout=20
    ).json()

    symbols = []

    for s in data["symbols"]:

        if s["status"] != "1":
            continue

        if s["quoteAsset"] != "USDT":
            continue

        if not s["isSpotTradingAllowed"]:
            continue

        symbols.append(s["symbol"])

    return symbols


def get_klines(symbol):

    url = BASE + "/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 60
    }

    data = requests.get(
        url,
        params=params,
        timeout=20
    ).json()

    df = pd.DataFrame(data)

    df = df.iloc[:, :6]

    df.columns = ["time", "open", "high", "low", "close", "volume"]

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)

    df["ema20"] = ema20(df)

    return df


def check_signal(df):

    breakout = df.iloc[-2]
    current = df.iloc[-1]
    previous = df.iloc[-3]

    if breakout["close"] <= breakout["ema20"]:
        return False

    if previous["close"] > previous["ema20"]:
        return False

    count = 0

    for i in range(-8, -3):
        if df.iloc[i]["close"] <= df.iloc[i]["ema20"]:
            count += 1

    if count < MIN_DAYS_BELOW:
        return False

    if current["high"] <= breakout["high"]:
        return False

    return True


def main():

    sent = load_sent()

    symbols = get_symbols()

    print(f"Scansione {len(symbols)} coppie...")

    for symbol in symbols:

        try:

            df = get_klines(symbol)

            if check_signal(df):

                if symbol not in sent:

                    breakout = df.iloc[-2]

                    msg = (
                        "🚀 BREAKOUT EMA20 DAILY\n\n"
                        f"{symbol}\n\n"
                        f"Breakout High: {breakout['high']:.8f}\n"
                        f"Close: {df.iloc[-1]['close']:.8f}"
                    )

                    send(msg)

                    print("SENT:", symbol)

                    sent.add(symbol)

        except Exception as e:
            print(symbol, e)

    save_sent(sent)


if __name__ == "__main__":
    main()
