import pandas as pd
import requests
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Float, Integer, DateTime, String
from sqlalchemy.orm import declarative_base, sessionmaker
import time
import os




logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,  # Only INFO, WARNING, ERROR, CRITICAL will be logged
    format='%(asctime)s - %(levelname)s - %(message)s'
)



DB_FILE = "database.db"
if not os.path.exists(DB_FILE):
    logging.error(f"Database file {DB_FILE} does not exist!")         #writes the message to pipeline.log
    raise FileNotFoundError(f"{DB_FILE} not found.")                  #halts the program

engine = create_engine(f"sqlite:///{DB_FILE}")     #sqlalchemy's way of connecting to databse (type_of_database absolute_path database_name)
Base = declarative_base()           #creates a special parent class "Base". now any class that inherits "Base" will automatically be treateda as a database table




#
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

Session = sessionmaker(bind=engine)      # it helps to make objects that are used to interact with the database





def run_pipeline(symbol="MSFT"):
    start_time = time.time()
    success = False

    logging.info(f"Monitoring pipeline started for {symbol}")

    try:
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
                "datatype": "json",
                "apikey": "J4YVHGYHLAUEEY9D"
            },
        )

        if response.status_code != 200:
            logging.error(f"API request failed with status {response.status_code}")
            print("ALERT: API request failed!")
            return

        data = response.json()         #convert data into python dictionary

        '''"data will look like this
        {
  "Meta Data": {...},
  "Time Series (Daily)": {
      "2026-03-24": {
          "1. open": "398.07",
          "2. high": "400.63",
          "3. low": "394.79",
          "4. close": "399.95",
          "5. volume": "27733721"
      },
      ...
  }
  
}
'''
    
        if "Time Series (Daily)" not in data:
            logging.error("API returned invalid response or rate limit exceeded")
            print("ALERT: API response invalid!")
            return


        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)    #sorting, so we have oldest -> newest

        

        last7 = df.tail(7)
        last7['price_diff'] = last7['close'] - last7['open']
        last7['daily_return'] = ((last7['close'] - last7['open']) / last7['open']) * 100
        last7['Trend'] = last7['price_diff'].apply(
            lambda x: 'Upward' if x > 0 else ('Downward' if x < 0 else 'Stable')
        )
        logging.info(f"Transformed {len(last7)} rows")

        
        session = Session()      #using the Session() we created eariler






# query return a tuple of dates in the data column, scalar extracts just the values for the tuble. set() removes duplicates   
        existing_dates = set(session.scalars(session.query(StockData.date)))    


        new_rows = 0                     #counter for counting number of rows
        for idx, row in last7.iterrows():       #here ind= date, row=row content i.e. columns
            if idx in existing_dates:
                logging.info(f"Row for {idx.date()} already exists. Skipping insert.")      #checking if the data exits in database, if yes we skip
                continue
# this below block inserts/adds the data in the database if it doesn't already exist
            session.add(StockData(
                date=idx,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                price_diff=row['price_diff'],
                daily_return=row['daily_return'],
                Trend=row['Trend']
            ))
            new_rows += 1

        session.commit()
        success = True
        logging.info(f"Monitoring/insert completed. {new_rows} new rows added.")

    except Exception as e:
        logging.error(f"Pipeline monitoring failed: {e}")
        print("ALERT: Pipeline failed!")
        print("ERROR DETAILS:", e)

    finally:
        end_time = time.time()
        exec_time = round(end_time - start_time, 2)
        if success:
            logging.info(f"Monitoring pipeline finished successfully in {exec_time} seconds")
            print(f"Pipeline ran successfully in {exec_time} seconds!")
        else:
            logging.info(f"Monitoring pipeline failed after {exec_time} seconds")
            print(f"Pipeline failed after {exec_time} seconds.")


if __name__ == "__main__":
    run_pipeline("MSFT")