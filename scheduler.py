import os
import time
import schedule
import subprocess
from datetime import datetime
import pandas as pd
from clustering import perform_clustering


def run_spiders():
    """Run all spiders and update the data"""
    print(f"[{datetime.now()}] Starting daily data collection...")

    # Run each spider
    spiders = ['chronicle', 'herald', 'sundaymail']
    for spider in spiders:
        subprocess.run(['scrapy', 'crawl', spider], cwd='.')

    # Combine today's files
    combine_daily_files()

    # Update clustering
    perform_clustering('data/combined_latest.csv')

    print(f"[{datetime.now()}] Daily update completed")


def combine_daily_files():
    """Combine all daily files into one dataset for today"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_dir = 'data/daily'

    # Get all of today's files
    today_files = [f for f in os.listdir(daily_dir) if f.startswith(today)]

    # Combine into one dataframe
    combined_df = pd.DataFrame()
    for file in today_files:
        df = pd.read_csv(os.path.join(daily_dir, file))
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Save combined file
    combined_df.to_csv('data/combined_latest.csv', index=False)

    # Also save dated version for history
    combined_df.to_csv(f'data/combined_{today}.csv', index=False)


def run_scheduler():
    """Run the scheduler to update data daily"""
    # Schedule the job to run at 2 AM every day
    schedule.every().day.at("02:00").do(run_spiders)

    # Run once immediately on startup to have data
    run_spiders()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('data/daily', exist_ok=True)
    run_scheduler()