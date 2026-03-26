import schedule
import time
from etl import run_pipeline as run_etl
from logging_and_monitoring import run_pipeline as run_monitoring

def job():
    print("Starting etl pipeline...")
    try:
        run_etl("MSFT")
        print("ETL pipeline finished successfully.")
    except Exception as e:
        print(f"ETL pipeline failed: {e}")

    print("Starting logging_and_monitoring pipeline...")
    try:
        run_monitoring("MSFT")
        print("Monitoring pipeline finished successfully.")
    except Exception as e:
        print(f"Monitoring pipeline failed: {e}")


schedule.every().day.at("21:00").do(job)

print("Scheduler started. Waiting for 9 PM...")

while True:
    schedule.run_pending()     #this checks if any scheduled task is due right now and then executes it
    time.sleep(60)             #  loop wakes up every 60 secondss