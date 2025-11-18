# entry point that writes CSV

# run_weekly.py
from config import ZIPS, OUTPUT_DIR
from scraper import scrape_zillow
from utils import ensure_dirs, timestamp_str, write_csv
from score import score_listing, tier_from_score
import os

def run():
    ensure_dirs()
    timestamp = timestamp_str()
    all_rows = []
    for z in ZIPS:
        print("Scraping zip:", z)
        rows = scrape_zillow(z)
        for r in rows:
            r["scrape_date"] = timestamp
            # compute score
            sc = score_listing(r)
            r["score"] = sc
            r["tier"] = tier_from_score(sc)
            # ensure consistent CSV headers: stringify booleans
            r["fsbo"] = bool(r.get("fsbo"))
            all_rows.append(r)
    if not all_rows:
        print("No rows scraped.")
        return
    filename = os.path.join(OUTPUT_DIR, f"leads_{timestamp}.csv")
    write_csv(all_rows, filename)
    print("Wrote CSV:", filename)
    # small run summary
    tiers = {"Tier A":0, "Tier B":0, "Tier C":0}
    for r in all_rows:
        tiers[r["tier"]] += 1
    print("Run summary:", tiers)

if __name__ == "__main__":
    run()
