def fetch_stock_data(symbol="MSFT"):
    import pandas as pd
    import requests

    key = "J4YVHGYHLAUEEY9D"
    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "datatype": "json",
        "apikey": key
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error {response.status_code}")
        return None

    data = response.json()

    # Safe extraction
    if "Time Series (Daily)" not in data:
        print("API limit reached or invalid response")
        return None

    daily_data = data["Time Series (Daily)"]

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(daily_data, orient="index")
    df.columns = ['open', 'high', 'low', 'close', 'volume']

    # Convert data types
    df = df.astype(float)

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    # Sort properly
    df.sort_index(inplace=True)

    # Get last 7 days
    last_seven_days = df.tail(7)

    return df, last_seven_days

df, last7 = fetch_stock_data("MSFT")

print(last7)
