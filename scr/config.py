# ZIPs, price range, frequency, selectors

# config.py
ZIPS = ["44129"]                # list of ZIPs (dynamic)
PRICE_MIN = 25000
PRICE_MAX = 300000
MAX_LISTINGS_PER_ZIP = 150     # safety cap for demo
OUTPUT_DIR = "data/outputs"
RAW_HTML_DIR = "data/raw_html"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
KEYWORD_LIST = [
    "house needs work", "needs work", "needs TLC", "investor special",
    "fixer upper", "cash only", "sell my house fast", "cash for house",
    "as-is", "quick sale", "handyman special"
]
