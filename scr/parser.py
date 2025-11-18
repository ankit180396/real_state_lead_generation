# HTML -> normalized dict

# parser.py
from bs4 import BeautifulSoup
import re
import usaddress

def parse_listing_from_card(card_html):
    """
    Given a listing card HTML (string), return a partial dict.
    This function extracts common fields; the scraper will augment.
    """
    soup = BeautifulSoup(card_html, "lxml")
    out = {}
    # Address
    addr = None
    addr_tag = soup.select_one("address")
    if addr_tag:
        addr = addr_tag.get_text(strip=True)
    else:
        # fallback
        title = soup.select_one("h3")
        if title:
            addr = title.get_text(strip=True)
    if addr:
        out["property_address"] = addr
        # attempt to parse zip
        try:
            parsed = usaddress.tag(addr)
            out["parsed_addr"] = parsed[0]
        except Exception:
            out["parsed_addr"] = {}
    # Price
    price_tag = soup.select_one("[data-test='property-card-price'], .list-card-price")
    if price_tag:
        out["price_raw"] = price_tag.get_text(strip=True)
        out["price"] = extract_price(out["price_raw"])
    # Beds/baths/sqft
    info = soup.select_one(".list-card-details, .property-meta")
    if info:
        text = info.get_text(" | ", strip=True)
        out["meta_raw"] = text
    return out

def extract_price(text):
    if not text: 
        return None
    text = text.replace(",", "").strip()
    m = re.search(r"\$?(\d+)", text)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None

def find_fsbo_from_page(soup):
    """
    Attempt to detect if listing is FSBO on given page soup.
    Checks for 'For sale by owner' or 'FSBO' text.
    """
    text = soup.get_text(" ", strip=True).lower()
    if "for sale by owner" in text or "fsbo" in text:
        return True
    return False
