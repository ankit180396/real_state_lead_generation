# rule-based motivation scoring

# score.py
from config import KEYWORD_LIST
import re

def score_listing(listing):
    """
    Rule-based additive scoring.
    listing: dict with keys like description, days_on_market, price, flags (fsbo)
    returns score int 0..100
    """
    score = 0
    desc = (listing.get("description") or "").lower()
    # keyword hits
    for kw in KEYWORD_LIST:
        if kw.lower() in desc:
            score += 7
    # common high weight keywords
    if re.search(r"\bcash\b", desc):
        score += 12
    if re.search(r"\bas-?is\b", desc):
        score += 10
    # DOM
    dom = listing.get("days_on_market")
    try:
        if dom and int(dom) >= 30:
            score += 10
    except:
        pass
    # FSBO flag
    if listing.get("fsbo"):
        score += 8
    # Price low-end (potential investor targets)
    price = listing.get("price")
    if price:
        if price < 50000:
            score += 6
        elif price < 100000:
            score += 4
    # clamp
    if score > 100:
        score = 100
    return score

def tier_from_score(score):
    if score >= 60:
        return "Tier A"
    if score >= 35:
        return "Tier B"
    return "Tier C"
