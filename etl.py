import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from pprint import pprint
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime


def run_pipeline(symbol="MSFT"):

    # Alphavantage API: provides real-time and historical financial data for stocks
    key = "J4YVHGYHLAUEEY9D"
    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",  # function: what kind of data?, TIME_SERIES_DAILY = daily stock prices
        "symbol": symbol,
        "outputsize": "compact",  # compact = last 100 days
        "datatype": "json",
        "apikey": key,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        pprint(data)
    else:
        print(f"Error {response.status_code}")

    daily_data = data[
        "Time Series (Daily)"
    ]  # daily_data: it is now a dictionary with date as key and OHLC and volume as values
    # print(daily_data)
    """example of daily data
    "2026-03-24": {
      "1. open": "398.07",
      "2. high": "400.63",
      "3. low": "394.79",
      "4. close": "399.95",
      "5. volume": "27733721"
    }"""

    df = pd.DataFrame.from_dict(
        daily_data, orient="index"
    )  # orient=index: this makes keys as rows/index and values as columns in the dataframe
    df.columns = ["open", "high", "low", "close", "volume"]  # renaming column names
    df.index = pd.to_datetime(
        df.index
    )  # converts rows/index from string to proper datetime format for sorting, filtering etc
    df.head()

    df = df.sort_index()  # now the tail has the latest i.e today's data
    lastSevenDays = df.tail(
        7
    )  # lastSevenDays: the last seven days from the 100 data in df
    lastSevenDays.head()

    lastSevenDays = (
        lastSevenDays.ffill()
    )  # ffill(): Forward fill, fills a NaN value with previous rows values

    # as we have already converted rows/index to datetime, its time to convert columns from string to float
    lastSevenDays["open"] = lastSevenDays["open"].astype(float)
    lastSevenDays["high"] = lastSevenDays["high"].astype(float)
    lastSevenDays["low"] = lastSevenDays["low"].astype(float)
    lastSevenDays["close"] = lastSevenDays["close"].astype(float)
    lastSevenDays["volume"] = lastSevenDays["volume"].astype(float)

    # adding some extra columns:
    lastSevenDays["price_diff"] = lastSevenDays["close"] - lastSevenDays["open"]
    lastSevenDays["daily_return"] = (
        (lastSevenDays["close"] - lastSevenDays["open"]) / lastSevenDays["open"]
    ) * 100
    lastSevenDays["Trend"] = lastSevenDays["price_diff"].apply(
        lambda x: "Upward" if x > 0 else ("Downward" if x < 0 else "Stable")
    )

    lastSevenDays

    # Storing into the database:

    # connecting to the database:
    engine = create_engine("sqlite:///database.db")
    Base = declarative_base()

    # defining columns of our table "StockData"
    class StockData(Base):
        __tablename__ = "stock_data"

        id = Column(Integer, primary_key=True, autoincrement=True)
        date = Column(DateTime)
        open = Column(Float)
        high = Column(Float)
        low = Column(Float)
        close = Column(Float)
        volume = Column(Float)
        price_diff = Column(Float)
        daily_return = Column(Float)
        Trend = Column(String)

    Base.metadata.create_all(engine)

    # inserting the data:
    Session = sessionmaker(bind=engine)
    session = Session()

    for index, row in lastSevenDays.iterrows():  # looping over each row
        stock_entry = StockData(
            date=index,
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["volume"],
            price_diff=row["price_diff"],
            daily_return=row["daily_return"],
            Trend=row["Trend"],
        )
        session.add(stock_entry)
    session.commit()  # writing all rows to database


# Add this so the script can still run manually
if __name__ == "__main__":
    run_pipeline("MSFT")
