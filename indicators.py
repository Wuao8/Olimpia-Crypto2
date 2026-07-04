import pandas as pd


def ema20(df):
    return df["close"].ewm(span=20, adjust=False).mean()
