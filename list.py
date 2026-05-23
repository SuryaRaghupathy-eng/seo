import http.client
import json
import time
import csv

# =======================
# CONFIGURATION
# =======================
API_KEY = "31166f8b78c943e8707103d3ea4964d155f39fe9"
HOST = "google.serper.dev"

# Example list of queries and brands
queries_with_brands = [
{"query": "Estate agents in Barton Upon Humber", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Brigg", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Cottingham", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Gainsborough", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Grimsby", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Hull Holderness Road", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Humberston", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Lincoln", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in North Hykeham", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Louth", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Mablethorpe", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Market Rasen", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Scunthorpe", "brand": "https://lovelle.co.uk/"},
{"query": "Estate agents in Skegness", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Barton Upon Humber", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Brigg", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Cottingham", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Gainsborough", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Grimsby", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Hull Holderness Road", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Humberston", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Lincoln", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in North Hykeham", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Louth", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Mablethorpe", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Market Rasen", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Scunthorpe", "brand": "https://lovelle.co.uk/"},
{"query": "Letting agents in Skegness", "brand": "https://lovelle.co.uk/"},
]

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

results = []

# =======================
# SCRAPING LOOP
# =======================
for entry in queries_with_brands:
    query = entry["query"]
    brand = entry["brand"].lower().strip()
    print(f"\n🔍 Searching for '{query}' → Brand target: '{brand}'")

    all_results = []
    rank_found = None
    brand_link = None

    conn = http.client.HTTPSConnection(HOST)

    # Fetch first 5 pages (10 results each)
    for page in range(5):
        start = page * 10 + 1
        payload = json.dumps({
            "q": query,
            "gl": "gb",
            "start": start
        })

        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        result = json.loads(data.decode("utf-8"))

        if "organic" in result:
            all_results.extend(result["organic"])

        time.sleep(1)

    conn.close()

    # Check for brand domain in any result URL
    for idx, item in enumerate(all_results, start=1):
        link = item.get("link", "").lower()
        # Match even if it's a subpage or subdomain
        if brand in link:
            rank_found = idx
            brand_link = link
            break

    if rank_found:
        print(f"✅ {brand} found at position {rank_found} ({brand_link})")
    else:
        print(f"❌ {brand} not found in top 50 results")

    results.append({
        "query": query,
        "brand": brand,
        "rank_position": rank_found if rank_found else "Not Found",
        "brand_link": brand_link if brand_link else ""
    })

# =======================
# SAVE RESULTS
# =======================
with open("multi_brand_rankings.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["query", "brand", "rank_position", "brand_link"])
    writer.writeheader()
    writer.writerows(results)

print("\n✅ Done! Results saved to multi_brand_rankings.csv")
