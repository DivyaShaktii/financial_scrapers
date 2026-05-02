import pandas as pd

def detect_extrema(df, threshold=0.05, window=3):
    prices = df["Close"].values
    dates = df["Date"].values

    extrema = []

    for i in range(window, len(prices) - window):

        current = prices[i]

        left = prices[i - window:i]
        right = prices[i + 1:i + window + 1]

        # 🔻 LOCAL MIN (structure based)
        if current < min(left) and current < min(right):

            # 🔥 SIGNIFICANCE FILTER
            future_max = max(prices[i:i + window + 5])
            rise = (future_max - current) / current

            if rise >= threshold * 0.5:   # relaxed threshold
                extrema.append({
                    "type": "min",
                    "price": current,
                    "date": str(dates[i])
                })

        # 🔺 LOCAL MAX
        if current > max(left) and current > max(right):

            future_min = min(prices[i:i + window + 5])
            drop = (current - future_min) / current

            if drop >= threshold * 0.5:
                extrema.append({
                    "type": "max",
                    "price": current,
                    "date": str(dates[i])
                })

    # 🔥 EDGE FIX → include last visible dip
    last_price = prices[-1]
    prev_prices = prices[-window-1:-1]

    if last_price < min(prev_prices):
        extrema.append({
            "type": "min",
            "price": last_price,
            "date": str(dates[-1])
        })

    return extrema