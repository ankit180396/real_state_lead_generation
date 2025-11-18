from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
import json
import pandas as pd
import time

def scrape_zillow(zipcode: str, min_price=25000, max_price=300000, pages=3):
    """
    Scrapes Zillow for the given ZIP code, price range, and number of pages.
    Returns a list of listings.
    """

    all_listings = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 800},
        )

        page = context.new_page()
        stealth_sync(page)

        for page_num in range(1, pages + 1):
            # Build URL with page and price filters
            url = (
                f"https://www.zillow.com/homes/{zipcode}_rb/"
                f"?searchQueryState=%7B%22pagination%22:%7B%22currentPage%22:{page_num}%7D,"
                f"%22usersSearchTerm%22:%22{zipcode}%22,"
                f"%22filterState%22:%7B%22price%22:%7B%22min%22:{min_price},%22max%22:{max_price}%7D%7D,"
                f"%22isListVisible%22:true%7D"
            )

            print(f"\n🌐 Loading page {page_num}: {url}")
            page.goto(url, wait_until="networkidle", timeout=120000)
            time.sleep(3)  # let React JSON load

            # Bypass bot check if visible (Press & Hold)
            try:
                if page.locator("text=Press & Hold").is_visible(timeout=2000):
                    print("⚠️ Bot check detected → simulating human hold...")
                    box = page.locator(".captcha-solver").bounding_box()
                    page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                    page.mouse.down()
                    time.sleep(3.2)
                    page.mouse.up()
                    time.sleep(2)
            except:
                pass

            # Extract Zillow React JSON
            try:
                json_text = page.locator("script#__NEXT_DATA__").inner_text()
                data = json.loads(json_text)
                results = (
                    data.get('props', {})
                        .get('pageProps', {})
                        .get('searchPageState', {})
                        .get('cat1', {})
                        .get('searchResults', {})
                        .get('listResults', [])
                )
            except Exception:
                print("❌ Failed to get listings on this page")
                continue

            if not results:
                print("⚠️ No results on this page. Possibly end of listings.")
                break

            print(f"✅ Found {len(results)} listings on page {page_num}")

            # Parse listings
            for item in results:
                all_listings.append({
                    "address": item.get("address"),
                    "price": item.get("price"),
                    "beds": item.get("beds"),
                    "baths": item.get("baths"),
                    "sqft": item.get("area"),
                    "status": item.get("statusText"),
                    "zestimate": item.get("zestimate"),
                    "lat": item.get("latLong", {}).get("latitude"),
                    "lng": item.get("latLong", {}).get("longitude"),
                    "url": "https://www.zillow.com" + item.get("detailUrl", ""),
                    "is_fsbo": item.get("hdpData", {}).get("homeInfo", {}).get("isFSBO", False),
                })

        browser.close()

    print(f"\n🌟 Total listings collected: {len(all_listings)}")
    return all_listings


def save_to_csv(listings, filename="zillow_listings.csv"):
    df = pd.DataFrame(listings)
    df.to_csv(filename, index=False)
    print(f"📁 Saved {len(df)} listings → {filename}")


if __name__ == "__main__":
    # Example usage
    zip_code = "44129"
    listings = scrape_zillow(zip_code, min_price=25000, max_price=300000, pages=3)
    save_to_csv(listings)


rows = scrape_zillow("44129")
print(rows)
