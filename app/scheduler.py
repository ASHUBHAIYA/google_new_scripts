import schedule
import time
from app.utils.scraper import scrape_hindu

def job():
    print("Fetching new articles...")
    scrape_hindu()

schedule.every(4).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)