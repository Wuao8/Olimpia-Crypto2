import os
import json

FILE = "sent.json"

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        sent = set(json.load(f))
else:
    sent = set()


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
                    f"Prezzo: {df.iloc[-1]['close']:.8f}"
                )

                send(msg)

                print(symbol)

                sent.add(symbol)

    except Exception as e:

        print(symbol, e)


with open(FILE, "w") as f:
    json.dump(list(sent), f)
