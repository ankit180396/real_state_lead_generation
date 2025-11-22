# score.py
from config import KEYWORD_LIST
import re


def clean_price(value):
    """
    Safely normalize Zillow price formats:
    "$125,000+" → 125000
    "—", "Contact agent", None → None
    """
    if value is None:
        return None

    # Already numeric
    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str):
        # Remove $, commas, +, spaces, etc.
        cleaned = (
            value.replace("$", "")
                 .replace(",", "")
                 .replace("+", "")
                 .strip()
        )

        # ensure it's digits-only
        if cleaned.isdigit():
            return int(cleaned)

        return None

    return None


def safe_int(x):
    """Safely convert days_on_market to int."""
    try:
        return int(x)
    except:
        return None


def score_listing(listing):
    """
    Rule-based additive motivation score.
    Returns score 0 .. 100
    """

    score = 0

    # -----------------------------
    # DESCRIPTION + KEYWORDS
    # -----------------------------
    desc = (listing.get("description") or "").lower()

    for kw in KEYWORD_LIST:
        if kw.lower() in desc:
            score += 7

    # High-impact signals
    if re.search(r"\bcash\b", desc):
        score += 12

    if re.search(r"\bas-?is\b", desc):
        score += 10

    # -----------------------------
    # DAYS ON MARKET
    # -----------------------------
    dom = safe_int(listing.get("days_on_market"))
    if dom is not None and dom >= 30:
        score += 10

    # -----------------------------
    # FSBO
    # -----------------------------
    if listing.get("fsbo"):
        score += 8

    # -----------------------------
    # PRICE SIGNALS
    # -----------------------------
    raw_price = listing.get("price")
    price = clean_price(raw_price)

    if price is not None:
        if price < 50000:
            score += 6
        elif price < 100000:
            score += 4

    # -----------------------------
    # FINAL CLAMP
    # -----------------------------
    return min(score, 100)


def tier_from_score(score):
    if score >= 60:
        return "Tier A"
    if score >= 35:
        return "Tier B"
    return "Tier C"
