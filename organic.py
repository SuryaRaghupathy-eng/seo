# import http.client
# import json
# from urllib.parse import urlparse

# # -----------------------------------------
# # SET THESE VALUES
# # -----------------------------------------

# API_KEY = "845ea791fd551e9415b5f97859fef135d51a0c98"

# KEYWORDS = [
#     "Estate Agents in Bedford",
#     "estate agents in aldershot",
#     "Estate Agents in Bournemouth"
# ]

# GL = "gb"  # location
# TARGET_SITE = "belvoir.co.uk"   # domain only is enough
# MAX_PAGES = 5                   # how many SERP pages to scan
# # -----------------------------------------


# def normalize_domain(url):
#     """Extract domain from URL and normalize."""
#     if not url.startswith("http"):
#         url = "http://" + url
#     parsed = urlparse(url)
#     host = (parsed.hostname or "").lower()
#     if host.startswith("www."):
#         host = host[4:]
#     return host


# TARGET_DOMAIN = normalize_domain(TARGET_SITE)


# def domain_matches(result_link):
#     """Check if a search result belongs to the target domain."""
#     if not result_link:
#         return False
#     parsed = urlparse(result_link)
#     host = (parsed.hostname or "").lower()
#     if host.startswith("www."):
#         host = host[4:]
#     return host == TARGET_DOMAIN or host.endswith("." + TARGET_DOMAIN)


# def get_serp_page(keyword, gl, page):
#     """Send request to Serper.dev."""
#     conn = http.client.HTTPSConnection("google.serper.dev")
#     payload = json.dumps({
#         "q": keyword,
#         "gl": gl,
#         "page": page
#     })
#     headers = {
#         "X-API-KEY": API_KEY,
#         "Content-Type": "application/json"
#     }
#     conn.request("POST", "/search", payload, headers)
#     res = conn.getresponse()
#     data = res.read()
#     return json.loads(data.decode("utf-8"))


# def track_keyword(keyword):
#     total_position_count = 0

#     for page in range(1, MAX_PAGES + 1):
#         data = get_serp_page(keyword, GL, page)
#         organic = data.get("organic", [])

#         for index, item in enumerate(organic):
#             total_position_count += 1
#             link = item.get("link", "")

#             if domain_matches(link):
#                 position_on_page = index + 1
#                 overall_position = total_position_count

#                 return {
#                     "keyword": keyword,
#                     "found": True,
#                     "page": page,
#                     "position_on_page": position_on_page,
#                     "overall_position": overall_position
#                 }

#     # Not found in scanned pages
#     return {
#         "keyword": keyword,
#         "found": False,
#         "page": None,
#         "position_on_page": None,
#         "overall_position": None
#     }


# # -----------------------------------------
# # RUN TRACKER
# # -----------------------------------------

# print("Tracking Started...\n")

# for keyword in KEYWORDS:
#     result = track_keyword(keyword)

#     if result["found"]:
#         print(f"Keyword: {result['keyword']}")
#         print(f"→ Found on page {result['page']} at position {result['position_on_page']}")
#         print(f"→ Overall position: {result['overall_position']}\n")
#     else:
#         print(f"Keyword: {result['keyword']}")
#         print("→ Not found in first", MAX_PAGES, "pages\n")
import http.client
import json
import time
from urllib.parse import urlparse

# -----------------------------------------
# SET THESE VALUES
# -----------------------------------------
API_KEY = "845ea791fd551e9415b5f97859fef135d51a0c98"

KEYWORDS = [
    "Estate Agents in Bedford",
    "estate agents in aldershot",
    "Estate Agents in Bournemouth"
]

GL = "gb"
TARGET_SITE = "belvoir.co.uk"
MAX_PAGES = 5
REQUEST_DELAY = 1.0   # seconds delay between requests
# -----------------------------------------


# ----------------- HELPERS -----------------

def normalize_domain(url_or_host):
    """Extract and normalize domain."""
    if not url_or_host:
        return ""
    if "://" in url_or_host:
        parsed = urlparse(url_or_host)
        host = parsed.hostname or ""
    else:
        host = url_or_host
    host = host.lower()
    return host[4:] if host.startswith("www.") else host


TARGET_DOMAIN = normalize_domain(TARGET_SITE)


def domain_matches(result_link):
    """Return True if the result belongs to the target domain."""
    if not result_link:
        return False
    parsed = urlparse(result_link)
    host = (parsed.hostname or "").lower() if parsed.hostname else ""
    if host.startswith("www."):
        host = host[4:]
    return host == TARGET_DOMAIN or host.endswith("." + TARGET_DOMAIN)


def serper_request(endpoint, payload):
    """POST request to serper.dev."""
    conn = http.client.HTTPSConnection("google.serper.dev")
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    conn.request("POST", f"/{endpoint}", json.dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return json.loads(data.decode("utf-8"))


# ----------------- ORGANIC TRACKING -----------------

def track_organic(keyword):
    total_position = 0

    for page in range(1, MAX_PAGES + 1):
        payload = {"q": keyword, "gl": GL, "page": page}
        response = serper_request("search", payload)
        time.sleep(REQUEST_DELAY)

        organic_results = response.get("organic", [])

        for index, item in enumerate(organic_results):
            total_position += 1
            link = item.get("link", "")

            if domain_matches(link):
                return {
                    "found": True,
                    "page": page,
                    "position_on_page": index + 1,
                    "overall_position": total_position,
                    "link": link
                }

    return {"found": False}


# ----------------- LOCAL / PLACES TRACKING -----------------

def track_local(keyword):
    payload = {
        "q": keyword,
        "type": "places",
        "num": 10,
        "page": 1,
        "engine": "google"
    }
    response = serper_request("places", payload)
    time.sleep(REQUEST_DELAY)

    places = response.get("places", [])
    matches = []

    for p in places:
        website = p.get("website", "")
        if domain_matches(website):
            matches.append(website)

    return {
        "total_places": len(places),
        "matches": matches
    }


# ----------------- MAIN SCRIPT -----------------

print("\n====== SERPER RANK TRACKING STARTED ======\n")

for kw in KEYWORDS:
    print(f"\n🔍 Keyword: {kw}")

    organic = track_organic(kw)
    local = track_local(kw)

    # Organic result output
    if organic["found"]:
        print(f"  🌐 Organic Found")
        print(f"     → Page: {organic['page']}")
        print(f"     → Position on Page: {organic['position_on_page']}")
        print(f"     → Overall Position: {organic['overall_position']}")
        print(f"     → URL: {organic['link']}")
    else:
        print("  🌐 Organic: NOT found in first", MAX_PAGES, "pages")

    # Local result output
    if local["matches"]:
        print(f"  📍 Local Pack: FOUND ({len(local['matches'])} matches)")
        for m in local["matches"]:
            print("     →", m)
    else:
        print("  📍 Local Pack: No matching local listings")

print("\n====== TRACKING COMPLETE ======\n")
