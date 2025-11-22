import requests
import json
from bs4 import BeautifulSoup

url = "https://www.zillow.com/homes/44129_rb/"

headers = {
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
'accept-encoding': 'gzip, deflate, br, zstd',
'accept-language': 'en-US,en;q=0.9',
'cache-control': 'no-cache',
'cookie': 'zguid=24|%24d4d881a0-4a9e-48f4-86af-6ac0d5ffe48b; JSESSIONID=4C42CE98DCB63AD80474DB764C48B01A;',
'dnt': '1',
'pragma': 'no-cache',
'priority': 'u=0, i',
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
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

# Zillow stores listings inside a React JSON blob
data_script = soup.find("script", {"id": "__NEXT_DATA__"})

if not data_script:
    print("No Zillow JSON found — likely blocked")
    print(r.text[:500])
    exit()

data = json.loads(data_script.text)

results = (
    data.get("props", {})
        .get("pageProps", {})
        .get("searchPageState", {})
        .get("cat1", {})
        .get("searchResults", {})
        .get("listResults", [])
)

print(f"Found {len(results)} listings")

for item in results:
    print(item.get("address"), item.get("price"), item.get("statusType"))
