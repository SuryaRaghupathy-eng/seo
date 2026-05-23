"""
scraper_playwright.py — Estate Agent Scraper (All Portals)
===========================================================
Uses Playwright (real Chromium browser) to bypass bot-detection on
OnTheMarket, Zoopla, and Rightmove.

SETUP (once):
    pip install playwright beautifulsoup4 lxml --break-system-packages
    playwright install chromium

RUN:
    # All portals, 1 page each:
    python scraper_playwright.py --location tunbridge-wells --pages 1

    # Specific portals, 3 pages:
    python scraper_playwright.py --location tunbridge-wells --pages 3 --portals otm rightmove

    # Zoopla only, visible browser so you can solve the challenge:
    python scraper_playwright.py --location tunbridge-wells --pages 2 --portals zoopla

FLAGS:
    --location    Location slug (default: tunbridge-wells)
    --pages       Listing pages to scrape per portal (default: 1)
    --portals     Space-separated list: otm zoopla rightmove  (default: all)
    --headless    Run browser invisibly (challenges harder to solve manually)
    --delay       Seconds between page loads (default: 2)

OUTPUT:
    otm_<location>.csv
    zoopla_<location>.csv
    rightmove_<location>.csv
    combined_<location>.csv
"""

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass, fields, asdict
from urllib.parse import urljoin

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.exit(
        "\n[ERROR] Playwright is not installed.\n"
        "Run the following and try again:\n"
        "  pip install playwright --break-system-packages\n"
        "  playwright install chromium\n"
    )

from bs4 import BeautifulSoup


# ─────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────

@dataclass
class AgentRecord:
    portal: str
    agent_name: str
    branch_url: str
    properties_for_sale: str = ""
    properties_to_rent: str = ""
    raw_stats: str = ""


FIELDNAMES = [f.name for f in fields(AgentRecord)]

# These must all appear together to count as a real bot-challenge page.
# Using multi-signal detection avoids false positives from ordinary page content.
CHALLENGE_SIGNAL_SETS = [
    ["captcha"],
    ["cf-browser-verification"],
    ["verify you are human"],
    ["just a moment", "checking your browser"],
    ["security check", "not a robot"],
    ["bot detection"],
]


# ─────────────────────────────────────────────
# Browser helpers
# ─────────────────────────────────────────────

def is_challenge(html: str) -> bool:
    """Return True only when the page is clearly a bot-challenge wall."""
    low = html.lower()
    return any(all(s in low for s in sig_set) for sig_set in CHALLENGE_SIGNAL_SETS)


def navigate(page, url: str, delay: float = 2.0, pause_on_challenge: bool = False) -> str:
    """
    Load a URL in the Playwright page. Returns page HTML.
    pause_on_challenge=True → ask user to solve manually (only used for Zoopla).
    """
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    except PWTimeout:
        print(f"  [WARN] Timeout loading {url}")
        return ""

    time.sleep(delay)
    html = page.content()

    if is_challenge(html):
        if pause_on_challenge:
            print(
                f"\n  ⚠️  Bot challenge detected on {url}\n"
                "     Please solve it in the browser window, then press ENTER here."
            )
            input("  Press ENTER after solving the challenge … ")
            html = page.content()
        else:
            print(f"  [WARN] Challenge page detected on {url} — skipping.")

    return html


# ─────────────────────────────────────────────
# OnTheMarket (OTM)
# ─────────────────────────────────────────────

OTM_BASE = "https://www.onthemarket.com"


def otm_parse_listing(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    results = []

    # Each agent card has a div with classes space-x-3 and mr-2
    link_divs = soup.find_all(
        "div",
        class_=lambda c: c and "space-x-3" in c.split() and "mr-2" in c.split()
    )

    for div in link_divs:
        links = div.find_all("a", href=True)
        for_sale_url = ""
        to_rent_url = ""

        for a in links:
            href = a["href"]
            text = a.get_text(" ", strip=True).lower()
            full = urljoin(OTM_BASE, href)
            if "sale" in text or "for-sale" in href:
                for_sale_url = full
            elif "rent" in text or "to-rent" in href or "let-agreed" in href:
                to_rent_url = full

        if not for_sale_url and not to_rent_url:
            continue

        # Derive branch URL
        branch_url = ""
        sample = for_sale_url or to_rent_url
        m = re.search(r"(/agents/branch/[^/]+/)", sample)
        if m:
            branch_url = urljoin(OTM_BASE, m.group(1))

        # Agent name — walk up the DOM
        agent_name = ""
        parent = div.parent
        for _ in range(8):
            if parent is None:
                break
            for tag in ["h2", "h3", "h4", "strong"]:
                el = parent.find(tag)
                if el and el.get_text(strip=True):
                    agent_name = el.get_text(strip=True)
                    break
            if agent_name:
                break
            parent = parent.parent

        results.append({
            "agent_name": agent_name,
            "branch_url": branch_url,
            "for_sale_url": for_sale_url,
            "to_rent_url": to_rent_url,
        })

    return results


OTM_STATS_KEY_CLASSES = ["text-denim", "@xs/list-col:font-bold"]


def otm_parse_stats(html: str) -> str:
    """Extract stats spans from an OTM branch/properties detail page."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    spans = soup.find_all(
        "span",
        class_=lambda c: c and all(k in c for k in OTM_STATS_KEY_CLASSES)
    )
    texts = [s.get_text(" ", strip=True) for s in spans if s.get_text(strip=True)]
    return " | ".join(texts)


def scrape_otm(location: str, pages: int, page_obj, delay: float, pause: bool) -> list[AgentRecord]:
    print(f"\n{'='*60}")
    print(f"  OnTheMarket — {location}  ({pages} page(s))")
    print(f"{'='*60}")
    records: list[AgentRecord] = []

    for p in range(1, pages + 1):
        url = f"{OTM_BASE}/agents/{location}/?page={p}"
        print(f"  Listing page {p}: {url}")
        html = navigate(page_obj, url, delay=delay, pause_on_challenge=False)
        if not html:
            break

        agents = otm_parse_listing(html)
        if not agents:
            print("  No agents found on this page.")
            break

        print(f"  Found {len(agents)} agent(s)")
        for ag in agents:
            print(f"    • {ag['agent_name'] or '(unnamed)'} → {ag['branch_url']}")

            sale_html = navigate(page_obj, ag["for_sale_url"], delay=delay, pause_on_challenge=False) if ag["for_sale_url"] else ""
            rent_html = navigate(page_obj, ag["to_rent_url"],  delay=delay, pause_on_challenge=False) if ag["to_rent_url"]  else ""

            sale_stats = otm_parse_stats(sale_html)
            rent_stats = otm_parse_stats(rent_html)

            records.append(AgentRecord(
                portal="OnTheMarket",
                agent_name=ag["agent_name"],
                branch_url=ag["branch_url"],
                properties_for_sale=ag["for_sale_url"],
                properties_to_rent=ag["to_rent_url"],
                raw_stats=f"SALE STATS: {sale_stats} | RENT STATS: {rent_stats}",
            ))

    print(f"  OTM total: {len(records)}")
    return records


# ─────────────────────────────────────────────
# Zoopla
# ─────────────────────────────────────────────

ZOOPLA_BASE = "https://www.zoopla.co.uk"


def zoopla_parse_listing(html: str) -> list[dict]:
    if is_challenge(html):
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []

    link_wrappers = soup.find_all("div", class_=lambda c: c and "zIndexStyle" in c)
    if not link_wrappers:
        link_wrappers = soup.find_all("a", href=re.compile(r"/find-agents/branch/"))

    for wrapper in link_wrappers:
        a_tag = (
            wrapper.find("a", href=re.compile(r"/find-agents/branch/"))
            if wrapper.name != "a"
            else wrapper
        )
        if not a_tag:
            continue

        branch_url = urljoin(ZOOPLA_BASE, a_tag["href"])
        agent_name = a_tag.get_text(strip=True)
        stats: dict = {}

        card = a_tag
        for _ in range(12):
            card = card.parent
            if card is None:
                break
            stat_rows = card.find_all(
                "div", class_=lambda c: c and "infoAndStatsAreaRowStyle" in c
            )
            if stat_rows:
                heading = card.find(["h2", "h3", "h4"])
                if heading:
                    agent_name = heading.get_text(strip=True)
                for row in stat_rows:
                    dt = row.find("dt")
                    dd = row.find("dd")
                    if dt and dd:
                        stats[dt.get_text(strip=True)] = dd.get_text(strip=True)
                break

        results.append({"agent_name": agent_name, "branch_url": branch_url, "stats": stats})

    return results


def scrape_zoopla(location: str, pages: int, page_obj, delay: float, pause: bool) -> list[AgentRecord]:
    print(f"\n{'='*60}")
    print(f"  Zoopla — {location}  ({pages} page(s))")
    print(f"{'='*60}")
    records: list[AgentRecord] = []

    for p in range(1, pages + 1):
        url = f"{ZOOPLA_BASE}/find-agents/{location}/?pn={p}"
        print(f"  Listing page {p}: {url}")

        # Navigate first (no auto-pause — we always pause manually for Zoopla)
        try:
            page_obj.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as exc:
            print(f"  [WARN] Error loading {url}: {exc}")
            break

        time.sleep(delay)

        # Always pause so user can solve any verification before we scrape
        print(
            "\n  ⏸  Zoopla loaded. If you see a verification/challenge, solve it now."
            "\n     Once the agent listing is visible, press ENTER to continue."
        )
        input("  Press ENTER to continue … ")

        html = page_obj.content()
        if not html:
            break

        agents = zoopla_parse_listing(html)
        if not agents:
            print("  No agents parsed — debug HTML saved to zoopla_debug.html")
            with open("zoopla_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            break

        print(f"  Found {len(agents)} agent(s)")
        for ag in agents:
            stats_str = " | ".join(f"{k}: {v}" for k, v in ag["stats"].items())
            print(f"    • {ag['agent_name']} — {stats_str}")
            records.append(AgentRecord(
                portal="Zoopla",
                agent_name=ag["agent_name"],
                branch_url=ag["branch_url"],
                raw_stats=stats_str,
            ))

    print(f"  Zoopla total: {len(records)}")
    return records


# ─────────────────────────────────────────────
# Rightmove
# ─────────────────────────────────────────────

RM_BASE = "https://www.rightmove.co.uk"


def rm_cap(location: str) -> str:
    return location[0].upper() + location[1:] if location else location


def rm_parse_listing(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    agents = []
    seen: set[str] = set()

    # Agent links: /estate-agents/<slug>.html  but NOT the listing page itself
    # They look like: /estate-agents/agent/1234/AgentName.html
    for a in soup.find_all("a", href=re.compile(r"/estate-agents/agent/")):
        href = a["href"].split("?")[0]
        if href in seen:
            continue
        seen.add(href)
        agents.append({
            "agent_name": a.get_text(" ", strip=True),
            "branch_url": urljoin(RM_BASE, href),
        })

    # Fallback: broader pattern
    if not agents:
        for a in soup.find_all("a", href=re.compile(r"/estate-agents/[^/]+\.html")):
            href = a["href"].split("?")[0]
            # Skip the location listing page itself
            if re.match(r"/estate-agents/[A-Z][^/]+\.html$", href) and href not in seen:
                seen.add(href)
                agents.append({
                    "agent_name": a.get_text(" ", strip=True),
                    "branch_url": urljoin(RM_BASE, href),
                })

    return agents


def rm_parse_tabs(html: str) -> dict:
    if not html:
        return {}
    soup = BeautifulSoup(html, "lxml")

    tabs_div = soup.find("div", attrs={"data-testid": "tabs"})
    if not tabs_div:
        tabs_div = soup.find(
            "div",
            class_=lambda c: c and "tabs_tabs__" in c and "propertyList" in c
        )
    if not tabs_div:
        return {}

    result = {}
    for btn in tabs_div.find_all("button"):
        text = btn.get_text(strip=True)
        if "sale" in text.lower():
            result["for_sale"] = text
        elif "rent" in text.lower():
            result["to_rent"] = text

    return result


def scrape_rightmove(location: str, pages: int, page_obj, delay: float, pause: bool) -> list[AgentRecord]:
    loc_cap = rm_cap(location)
    print(f"\n{'='*60}")
    print(f"  Rightmove — {loc_cap}  ({pages} page(s))")
    print(f"{'='*60}")
    records: list[AgentRecord] = []

    for p in range(1, pages + 1):
        url = f"{RM_BASE}/estate-agents/{loc_cap}.html?page={p}"
        print(f"  Listing page {p}: {url}")
        html = navigate(page_obj, url, delay=delay, pause_on_challenge=False)
        if not html:
            break

        agents = rm_parse_listing(html)
        if not agents:
            print("  No agent links found — stopping pagination.")
            # Save HTML for debugging
            with open(f"rightmove_debug_page{p}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  Debug HTML saved to rightmove_debug_page{p}.html")
            break

        print(f"  Found {len(agents)} agent link(s)")
        for ag in agents:
            print(f"    • Visiting {ag['branch_url']}")
            branch_html = navigate(page_obj, ag["branch_url"], delay=delay, pause_on_challenge=False)
            tabs = rm_parse_tabs(branch_html)
            for_sale = tabs.get("for_sale", "")
            to_rent  = tabs.get("to_rent", "")
            print(f"      {ag['agent_name']} | {for_sale} | {to_rent}")
            records.append(AgentRecord(
                portal="Rightmove",
                agent_name=ag["agent_name"],
                branch_url=ag["branch_url"],
                properties_for_sale=for_sale,
                properties_to_rent=to_rent,
            ))

    print(f"  Rightmove total: {len(records)}")
    return records


# ─────────────────────────────────────────────
# CSV output
# ─────────────────────────────────────────────

def write_csv(filename: str, records: list[AgentRecord]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(asdict(r) for r in records)
    print(f"  💾 Saved → {filename}  ({len(records)} row(s))")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Estate agent scraper — OTM / Zoopla / Rightmove (Playwright)"
    )
    parser.add_argument("--location", default="tunbridge-wells",
                        help="Location slug, e.g. tunbridge-wells  (default: tunbridge-wells)")
    parser.add_argument("--pages", type=int, default=1,
                        help="Listing pages to scrape per portal  (default: 1)")
    parser.add_argument("--portals", nargs="+",
                        choices=["otm", "zoopla", "rightmove"],
                        default=["otm", "zoopla", "rightmove"],
                        help="Which portals to scrape  (default: all)")
    parser.add_argument("--headless", action="store_true",
                        help="Run browser invisibly (you cannot solve challenges manually)")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Seconds to wait between page loads  (default: 2.0)")
    args = parser.parse_args()

    pause = not args.headless  # Only pause for manual solve when browser is visible

    print(f"\n{'='*60}")
    print(f"  Estate Agent Scraper")
    print(f"  Location : {args.location}")
    print(f"  Portals  : {', '.join(args.portals)}")
    print(f"  Pages    : {args.pages}")
    print(f"  Headless : {args.headless}")
    print(f"  Delay    : {args.delay}s")
    print(f"{'='*60}\n")

    all_records: list[AgentRecord] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-GB",
            timezone_id="Europe/London",
        )
        page = context.new_page()

        if "otm" in args.portals:
            recs = scrape_otm(args.location, args.pages, page, args.delay, pause)
            write_csv(f"otm_{args.location}.csv", recs)
            all_records.extend(recs)

        if "zoopla" in args.portals:
            recs = scrape_zoopla(args.location, args.pages, page, args.delay, pause)
            write_csv(f"zoopla_{args.location}.csv", recs)
            all_records.extend(recs)

        if "rightmove" in args.portals:
            recs = scrape_rightmove(args.location, args.pages, page, args.delay, pause)
            write_csv(f"rightmove_{args.location}.csv", recs)
            all_records.extend(recs)

        browser.close()

    if all_records:
        write_csv(f"combined_{args.location}.csv", all_records)

    print("\n✅ Done.")


if __name__ == "__main__":
    main()