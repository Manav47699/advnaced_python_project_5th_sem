import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
from pdf_report import generate_pdf
import os

os.makedirs("reports", exist_ok=True)


def load_data():
    engine = create_engine("sqlite:///database.db")
    df = pd.read_sql("SELECT * FROM stock_data", engine)
    if df.empty:
        raise ValueError("No data found in database")
    required_cols = ["close", "volume", "daily_return", "Trend"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df


def analyze_data(df):
    return {
        "avg_close": round(df["close"].mean(), 2),
        "max_close": round(df["close"].max(), 2),
        "min_close": round(df["close"].min(), 2),
        "total_volume": int(df["volume"].sum()),
    }


def plot_price_trend(df):
    plt.figure()
    plt.plot(df["date"], df["close"])
    plt.title("Closing Price Trend", pad=15)
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("reports/price_trend.png")
    plt.close()


def plot_volume(df):
    plt.figure()
    plt.bar(df["date"], df["volume"])
    plt.title("Trading Volume", pad=15)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("reports/volume.png")
    plt.close()


def plot_returns(df):
    plt.figure()
    sns.histplot(df["daily_return"], kde=True)
    plt.title("Daily Return Distribution", pad=15)
    plt.tight_layout()
    plt.savefig("reports/returns.png")
    plt.close()


def plot_trend(df):
    trend_counts = df["Trend"].value_counts()
    plt.figure()
    trend_counts.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Trend Distribution", pad=15)
    plt.ylabel("")
    plt.savefig("reports/trend.png")
    plt.close()


def save_summary(summary):
    with open("reports/summary.txt", "w") as f:
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")


def save_full_dataset(df):
    df.to_csv("reports/full_dataset.csv", index=False)


def last_seven_days_report(df):
    last7 = df.sort_values("date").tail(7)
    last7 = last7[
        ["date", "open", "high", "low", "close", "volume", "daily_return", "Trend"]
    ]
    last7["date"] = last7["date"].dt.strftime("%Y-%m-%d")
    numeric_cols = ["open", "high", "low", "close", "volume", "daily_return"]
    last7[numeric_cols] = last7[numeric_cols].round(2)
    last7.to_csv("reports/last_7_days.csv", index=False)
    return last7


def run_report():
    df = load_data()
    summary = analyze_data(df)
    plot_price_trend(df)
    plot_volume(df)
    plot_returns(df)
    plot_trend(df)
    save_full_dataset(df)
    save_summary(summary)
    last7 = last_seven_days_report(df)
    generate_pdf(last7, summary)
    print("Report generated successfully!")


if __name__ == "__main__":
    run_report()
