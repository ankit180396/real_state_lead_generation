import requests
import json
import time
import random
import pandas as pd
from bs4 import BeautifulSoup

BASE_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'dnt': '1',
    'sec-ch-ua': '"Not_A Brand";v="99", "Chromium";v="142"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

# Add YOUR working cookie (use the percent-encoded zguid value)
BASE_HEADERS['cookie'] = (
    "zguid=24|%24d4d881a0-4a9e-48f4-86af-6ac0d5ffe48b;"
    "JSESSIONID=99FBC7801F82F4F559B71FB0C58B6019;"
)


# ------------------------------------------------------
# FETCH WEBPAGE
# ------------------------------------------------------
def fetch_page(url: str):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=BASE_HEADERS, timeout=15)
            if r.status_code == 200:
                return r.text
            print("⚠️ Status", r.status_code)
        except Exception as e:
            print("⚠️ Request error:", e)

        time.sleep(random.uniform(1.5, 3.5))

    print("❌ Failed after retries:", url)
    return None


# ------------------------------------------------------
# DESCRIPTION SCRAPER (NEW!)
# ------------------------------------------------------
def fetch_motivation(listing_url: str):
    """
    Fetches the individual Zillow property page,
    extracts the FULL description text.
    Returns a clean string.
    """
    html = fetch_page(listing_url)
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Zillow property pages ALSO have __NEXT_DATA__
    data_script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not data_script:
        return ""

    try:
        data_json = json.loads(data_script.text)
    except:
        return ""

    # Zillow stores description in:
    #  props.pageProps.gdpClientCache.<LISTING_ID>.property.description
    try:
        cache = json.loads(data_json["props"]["pageProps"]["componentProps"]["gdpClientCache"])
        # first key is the listing ID container
        first_key = list(cache.keys())[0]
        description = cache[first_key]["property"]["description"]
        return description.strip()
    except:
        return ""


# ------------------------------------------------------
# JSON + LIST EXTRACTION
# ------------------------------------------------------
def parse_zillow_json(html: str):
    soup = BeautifulSoup(html, "html.parser")
    data_script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not data_script:
        return None

    try:
        return json.loads(data_script.text)
    except:
        return None


def extract_listings(json_data):
    return (
        json_data.get("props", {})
            .get("pageProps", {})
            .get("searchPageState", {})
            .get("cat1", {})
            .get("searchResults", {})
            .get("listResults", [])
    )


# ------------------------------------------------------
# URL BUILDER
# ------------------------------------------------------
def build_url(zipcode, page, min_p, max_p):
    return ("https://www.zillow.com/homes/for_sale/"
            f"{zipcode}/{min_p}-{max_p}_price/"
    )


# ------------------------------------------------------
# MAIN SCRAPER
# ------------------------------------------------------
def scrape_zillow(zipcode="44129", min_price=25000, max_price=300000, pages=1):
    all_rows = []

    print(f"\n🔍 Scraping ZIP {zipcode} | Price {min_price}-{max_price}\n")

    for page_num in range(1, pages + 1):
        url = build_url(zipcode, page_num, min_price, max_price)
        print(f"🌐 Fetching page {page_num} → {url}")

        html = fetch_page(url)
        if not html:
            continue

        json_data = parse_zillow_json(html)
        if not json_data:
            print("❌ JSON missing — blocked or cookie expired.")
            continue

        listings = extract_listings(json_data)
        if not listings:
            print("⚠️ No more results. Stopping.")
            break

        print(f"✅ Found {len(listings)} listings")

        for item in listings:
            property_url = item.get("detailUrl", "")
            time.sleep(random.uniform(6.0, 8.0))
            # Get detailed description
            description_text = fetch_motivation(property_url)

            row = {
                "address": item.get("address"),
                "price": item.get("price"),
                "beds": item.get("beds"),
                "baths": item.get("baths"),
                "sqft": item.get("area"),
                "status": item.get("statusText"),
                "url": property_url,
                "description": description_text,
                "is_fsbo": item.get("hdpData", {}).get("homeInfo", {}).get("isFSBO", False),
                "zestimate": item.get("zestimate"),
                "lat": item.get("latLong", {}).get("latitude"),
                "lng": item.get("latLong", {}).get("longitude"),
            }

            # Motivation keywords inside description:
            motivation_keywords = [
                kw for kw in ["tlc", "fixer", "cash", "investor", "handyman", "needs work", "as-is"]
                if kw in description_text.lower()
            ]
            row["motivated_keywords"] = motivation_keywords

            all_rows.append(row)


    print(f"\n🏁 DONE. Total collected: {len(all_rows)}")
    return all_rows


# ------------------------------------------------------
# CSV SAVE
# ------------------------------------------------------
def save_to_csv(rows, filename="zillow_listings.csv"):
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"📁 Saved {len(df)} rows → {filename}")


if __name__ == "__main__":
    data = scrape_zillow("44129", min_price=25000, max_price=300000, pages=3)
    save_to_csv(data)
