import requests
import pandas as pd

from indicators import ema20
from telegram import send

BASE = "https://api.mexc.com"

# almeno 5 giorni consecutivi sotto EMA20
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

        if s["isSpotTradingAllowed"] is False:
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

    df.columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for c in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:
        df[c] = df[c].astype(float)

    df["ema20"] = ema20(df)

    return df

def check_signal(df):

    # Candela di breakout = ieri (ultima chiusa)
    breakout = df.iloc[-2]

    # Candela attuale (ancora in formazione)
    current = df.iloc[-1]

    # 1) breakout deve chiudere sopra EMA20
    if breakout["close"] <= breakout["ema20"]:
        return False

    # 2) candela precedente al breakout sotto EMA20
    previous = df.iloc[-3]

    if previous["close"] > previous["ema20"]:
        return False

    # 3) almeno 5 giorni consecutivi sotto EMA20
    count = 0

    for i in range(-8, -3):

        row = df.iloc[i]

        if row["close"] <= row["ema20"]:
            count += 1

    if count < MIN_DAYS_BELOW:
        return False

    # 4) prezzo attuale supera il massimo
    # della candela di breakout
    if current["high"] <= breakout["high"]:
        return False

    return True
