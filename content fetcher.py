# # import requests
# # import json
# # import csv
# # from bs4 import BeautifulSoup

# # # ----------------------------------
# # # EXISTING CODE (UNCHANGED)
# # # ----------------------------------

# # def extract_text_from_url(url):
# #     headers = {
# #         "User-Agent": "Mozilla/5.0"
# #     }

# #     response = requests.get(url, headers=headers, timeout=20)
# #     response.raise_for_status()

# #     soup = BeautifulSoup(response.text, "html.parser")

# #     # Remove obvious junk
# #     for tag in soup([
# #         "script", "style", "noscript", "svg",
# #         "form", "button", "nav", "footer",
# #         "header", "aside"
# #     ]):
# #         tag.decompose()

# #     body = soup.body
# #     if not body:
# #         return ""

# #     lines = []

# #     for el in body.find_all(["h1", "h2", "h3", "p", "li"], recursive=True):
# #         text = el.get_text(" ", strip=True)

# #         # Skip empty / UI junk
# #         if not text:
# #             continue
# #         if text.lower() in {"submit", "contact us", "read more"}:
# #             continue
# #         if "cookie" in text.lower():
# #             continue

# #         lines.append(text)

# #     # Deduplicate while preserving order
# #     seen = set()
# #     cleaned = []
# #     for line in lines:
# #         if line not in seen:
# #             seen.add(line)
# #             cleaned.append(line)

# #     return "\n\n".join(cleaned)


# # # ----------------------------------
# # # GEMINI META DESCRIPTION GENERATION
# # # ----------------------------------

# # GEMINI_API_KEY = "AIzaSyAlF6hAeHsvMQex4wZPTceZSCfJMIrvV18"

# # GEMINI_URL = (
# #     "https://generativelanguage.googleapis.com/v1beta/models/"
# #     "gemini-2.5-flash-lite:generateContent"
# #     f"?key={GEMINI_API_KEY}"
# # )

# # def generate_meta_description(page_text):
# #     prompt = f"""
# # You are an SEO expert.

# # Write ONE meta description for the page content below.

# # Rules:
# # - Maximum 160 characters
# # - SEO optimised
# # - Clear and professional tone
# # - No quotes
# # - No emojis

# # Page content:
# # {page_text}
# # """

# #     payload = {
# #         "contents": [
# #             {
# #                 "parts": [
# #                     {"text": prompt}
# #                 ]
# #             }
# #         ]
# #     }

# #     headers = {
# #         "Content-Type": "application/json"
# #     }

# #     response = requests.post(
# #         GEMINI_URL,
# #         headers=headers,
# #         data=json.dumps(payload),
# #         timeout=30
# #     )
# #     response.raise_for_status()

# #     data = response.json()
# #     return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# # # ----------------------------------
# # # CSV EXPORT FUNCTION
# # # ----------------------------------

# # def export_to_csv(filename, url, meta_description):
# #     with open(filename, mode="w", newline="", encoding="utf-8") as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["URL", "Meta Description", "Character Count"])
# #         writer.writerow([
# #             url,
# #             meta_description,
# #             len(meta_description)
# #         ])


# # # ----------------------------------
# # # MAIN
# # # ----------------------------------

# # if __name__ == "__main__":
# #     url = "https://www.belvoir.co.uk/leicester-central-estate-agents/international-students/"

# #     text = extract_text_from_url(url)

# #     print("\n--- Extracted Page Text ---\n")
# #     print(text)

# #     meta_description = generate_meta_description(text)

# #     print("\n--- Generated Meta Description ---\n")
# #     print(meta_description)

# #     export_to_csv("meta_description_output.csv", url, meta_description)

# #     print("\n--- CSV Exported: meta_description_output.csv ---\n")
# # import requests
# # import json
# # import csv
# # from bs4 import BeautifulSoup

# # # ----------------------------------
# # # EXISTING CODE (UNCHANGED)
# # # ----------------------------------

# # def extract_text_from_url(url):
# #     headers = {
# #         "User-Agent": "Mozilla/5.0"
# #     }

# #     response = requests.get(url, headers=headers, timeout=20)
# #     response.raise_for_status()

# #     soup = BeautifulSoup(response.text, "html.parser")

# #     # Remove obvious junk
# #     for tag in soup([
# #         "script", "style", "noscript", "svg",
# #         "form", "button", "nav", "footer",
# #         "header", "aside"
# #     ]):
# #         tag.decompose()

# #     body = soup.body
# #     if not body:
# #         return ""

# #     lines = []

# #     for el in body.find_all(["h1", "h2", "h3", "p", "li"], recursive=True):
# #         text = el.get_text(" ", strip=True)

# #         # Skip empty / UI junk
# #         if not text:
# #             continue
# #         if text.lower() in {"submit", "contact us", "read more"}:
# #             continue
# #         if "cookie" in text.lower():
# #             continue

# #         lines.append(text)

# #     # Deduplicate while preserving order
# #     seen = set()
# #     cleaned = []
# #     for line in lines:
# #         if line not in seen:
# #             seen.add(line)
# #             cleaned.append(line)

# #     return "\n\n".join(cleaned)


# # # ----------------------------------
# # # GEMINI META DESCRIPTION GENERATION
# # # ----------------------------------

# # GEMINI_API_KEY = "AIzaSyD1vXq0FXi6-jlthqmYLX69hKmMM5lMm0k"

# # GEMINI_URL = (
# #     "https://generativelanguage.googleapis.com/v1beta/models/"
# #     "gemini-2.5-flash-lite:generateContent"
# #     f"?key={GEMINI_API_KEY}"
# # )

# # def generate_meta_description(page_text):
# #     prompt = f"""
# # You are an SEO expert.

# # Write ONE meta description for the page content below.

# # Rules:
# # - Maximum 160 characters
# # - SEO optimised
# # - Mention the brand name 'Belvoir' in the description 
# # - No quotes
# # - No emojis
# # - Clear and professional tone

# # Page content:
# # {page_text}
# # """

# #     payload = {
# #         "contents": [
# #             {
# #                 "parts": [
# #                     {"text": prompt}
# #                 ]
# #             }
# #         ]
# #     }

# #     headers = {
# #         "Content-Type": "application/json"
# #     }

# #     response = requests.post(
# #         GEMINI_URL,
# #         headers=headers,
# #         data=json.dumps(payload),
# #         timeout=30
# #     )
# #     response.raise_for_status()

# #     data = response.json()
# #     return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# # # ----------------------------------
# # # MAIN – BULK URL LOOP + CSV EXPORT
# # # ----------------------------------

# # if __name__ == "__main__":

# #     urls = [
# #         "https://www.belvoir.co.uk/kirkcaldy-estate-agents/guide-to-selling/",
# #         "https://www.belvoir.co.uk/kirkcaldy-estate-agents/landlord-advice/",
# #         "https://www.belvoir.co.uk/leamington-spa-estate-agents/complaints-procedure/",
# #         "https://www.belvoir.co.uk/leamington-spa-estate-agents/emergency-details/",
# #         "https://www.belvoir.co.uk/leamington-spa-estate-agents/sales/"
# #     ]

# #     output_file = "meta_descriptions_bulk.csv"

# #     with open(output_file, mode="w", newline="", encoding="utf-8") as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["URL", "Meta Description", "Character Count"])

# #         for url in urls:
# #             print(f"\nProcessing: {url}")

# #             try:
# #                 text = extract_text_from_url(url)
# #                 meta_description = generate_meta_description(text)

# #                 writer.writerow([
# #                     url,
# #                     meta_description,
# #                     len(meta_description)
# #                 ])

# #                 print("Meta Description:", meta_description)
# #                 print("Page Content:", text)
# #             except Exception as e:
# #                 print(f"Failed for {url}: {e}")
# #                 writer.writerow([url, "ERROR", ""])

# #     print(f"\n--- CSV Exported Successfully: {output_file} ---")
# import requests
# import json
# import csv
# from bs4 import BeautifulSoup

# # ----------------------------------
# # EXISTING CODE (UNCHANGED)
# # ----------------------------------

# def extract_text_from_url(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     response = requests.get(url, headers=headers, timeout=20)
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, "html.parser")

#     # Remove obvious junk
#     for tag in soup([
#         "script", "style", "noscript", "svg",
#         "form", "button", "nav", "footer",
#         "header", "aside"
#     ]):
#         tag.decompose()

#     body = soup.body
#     if not body:
#         return ""

#     lines = []

#     for el in body.find_all(["h1", "h2", "h3", "p", "li"], recursive=True):
#         text = el.get_text(" ", strip=True)

#         # Skip empty / UI junk
#         if not text:
#             continue
#         if text.lower() in {"submit", "contact us", "read more"}:
#             continue
#         if "cookie" in text.lower():
#             continue

#         lines.append(text)

#     # Deduplicate while preserving order
#     seen = set()
#     cleaned = []
#     for line in lines:
#         if line not in seen:
#             seen.add(line)
#             cleaned.append(line)

#     return "\n\n".join(cleaned)


# # ----------------------------------
# # GEMINI META DESCRIPTION GENERATION
# # ----------------------------------

# GEMINI_API_KEY = "AIzaSyACrd0cPC_dW1AvRKEjzGM1z4vzYTWib-o"

# GEMINI_URL = (
#     "https://generativelanguage.googleapis.com/v1beta/models/"
#     "gemini-2.5-flash-lite:generateContent"
#     f"?key={GEMINI_API_KEY}"
# )

# def generate_meta_description(page_text):
#     prompt = f"""
# You are an SEO expert.

# Write ONE meta description for the page content below.

# Rules:
# - Maximum 160 characters
# - SEO optimised
# - Mention the brand name 'Belvoir' in the description
# - No quotes
# - No emojis
# - Clear and professional tone

# Page content:
# {page_text}
# """

#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {"text": prompt}
#                 ]
#             }
#         ]
#     }

#     headers = {
#         "Content-Type": "application/json"
#     }

#     response = requests.post(
#         GEMINI_URL,
#         headers=headers,
#         data=json.dumps(payload),
#         timeout=30
#     )
#     response.raise_for_status()

#     data = response.json()
#     return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# # ----------------------------------
# # MAIN – BULK URL LOOP + CSV EXPORT
# # ----------------------------------

# if __name__ == "__main__":

#     urls = [
# "https://www.belvoir.co.uk/manchester-north-estate-agents/lettings-services/",
# "https://www.belvoir.co.uk/manchester-north-estate-agents/the-sales-process-explained/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/6-easy-steps-to-move-to-belvoir/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/application-process/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/are-you-covered/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/buyers-guide/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/conveyancing/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/deposit-protection/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/emergency-contractors/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/flatfair/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/safety-regulations/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/so-what-happens-next/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/step-by-step-guide-to-selling/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/tenant-flatfair/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/vendors/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/what-is-fair-wear-tear-on-a-rental-property/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/what-is-the-rental-value-of-my-property/",
# "https://www.belvoir.co.uk/mansfield-estate-agents/what-to-consider-before-renting/",
# "https://www.belvoir.co.uk/market-harborough-estate-agents/landlord-fees-and-services/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/building-and-content-insurance/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/extensive-local-knowledge/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/franklyn-financial-management/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/landlord-roadshow/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/marketing-your-property/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/sales-progression/",
# "https://www.belvoir.co.uk/melton-mowbray-estate-agents/selling/",
# "https://www.belvoir.co.uk/milton-keynes-estate-agents/general-data-protection-regulations/",
# "https://www.belvoir.co.uk/milton-keynes-estate-agents/landlord-advice/",
# "https://www.belvoir.co.uk/milton-keynes-estate-agents/tenant-advice/",
# "https://www.belvoir.co.uk/moray-estate-agents/guide-to-switching-letting-agents/",
# "https://www.belvoir.co.uk/moray-estate-agents/services-for-landlords/",
# "https://www.belvoir.co.uk/moray-estate-agents/tenant-applications/",
# "https://www.belvoir.co.uk/newark-estate-agents/tenant-emergency-advice/",
# "https://www.belvoir.co.uk/newbury-estate-agents/conveyancing/",
# "https://www.belvoir.co.uk/newbury-estate-agents/fair-processing-policy/",
# "https://www.belvoir.co.uk/newbury-estate-agents/marketing-the-belvoir-way/",
# "https://www.belvoir.co.uk/newbury-estate-agents/premium-marketing/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/behaving-in-a-tenant-like-manner/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/easy-steps-to-move-to-belvoir/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/information-for-tenants/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/renting-out-your-property/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/tenant-repairs/",
# "https://www.belvoir.co.uk/newcastle-central-estate-agents/tenants-nil-deposit-scheme/",
# "https://www.belvoir.co.uk/newcastle-under-lyme-estate-agents/hmo-overview/",
# "https://www.belvoir.co.uk/newcastle-under-lyme-estate-agents/how-to-change-letting-agents/",
# "https://www.belvoir.co.uk/newcastle-under-lyme-estate-agents/properties/student-properties/",
# "https://www.belvoir.co.uk/newcastle-under-lyme-estate-agents/tenant-registration-form/",
# "https://www.belvoir.co.uk/norfolk-estate-agents/renters-reform-bill/",
# "https://www.belvoir.co.uk/norfolk-estate-agents/usaf-housing/",
# "https://www.belvoir.co.uk/northampton-estate-agents/estate-agency-services/",
# "https://www.belvoir.co.uk/northampton-estate-agents/problem-tenancies/",
# "https://www.belvoir.co.uk/northampton-estate-agents/property-refurbishment/",
# "https://www.belvoir.co.uk/northwich-estate-agents/5-easy-steps-to-move-to-belvoir/",
# "https://www.belvoir.co.uk/northwich-estate-agents/affordability/",
# "https://www.belvoir.co.uk/northwich-estate-agents/a-guide-to-renting-a-property/",
# "https://www.belvoir.co.uk/northwich-estate-agents/case-studies/",
# "https://www.belvoir.co.uk/northwich-estate-agents/congleton-letting-agents/",
# "https://www.belvoir.co.uk/northwich-estate-agents/deposits/",
# "https://www.belvoir.co.uk/northwich-estate-agents/guidelines-for-vacating-tenants/",
# "https://www.belvoir.co.uk/northwich-estate-agents/holmes-chapel/",
# "https://www.belvoir.co.uk/northwich-estate-agents/inventories/",
# "https://www.belvoir.co.uk/northwich-estate-agents/knutsford/",
# "https://www.belvoir.co.uk/northwich-estate-agents/landlords-checklist/",
# "https://www.belvoir.co.uk/northwich-estate-agents/middlewich/",
# "https://www.belvoir.co.uk/northwich-estate-agents/moving-overseas/",
# "https://www.belvoir.co.uk/northwich-estate-agents/our-area-northwich/",
# "https://www.belvoir.co.uk/northwich-estate-agents/our-values/",
# "https://www.belvoir.co.uk/northwich-estate-agents/personal-and-property-health/",
# "https://www.belvoir.co.uk/northwich-estate-agents/property-preparation-checklist/",
# "https://www.belvoir.co.uk/northwich-estate-agents/rent-in-advance/",
# "https://www.belvoir.co.uk/northwich-estate-agents/reviews-congleton/",
# "https://www.belvoir.co.uk/northwich-estate-agents/sanbach/",
# "https://www.belvoir.co.uk/northwich-estate-agents/tax-compliance-for-landlords/",
# "https://www.belvoir.co.uk/northwich-estate-agents/tenant-affordability/",
# "https://www.belvoir.co.uk/northwich-estate-agents/vlogs/",
# "https://www.belvoir.co.uk/northwich-estate-agents/winsford/",
# "https://www.belvoir.co.uk/nottingham-central-estate-agents/emergency-contractors/",
# "https://www.belvoir.co.uk/nottingham-central-estate-agents/nbs/",
# "https://www.belvoir.co.uk/nottingham-central-estate-agents/sales/",
# "https://www.belvoir.co.uk/perth-estate-agents/complaints-procedure/",
# "https://www.belvoir.co.uk/perth-estate-agents/emergency-contact-number/",
# "https://www.belvoir.co.uk/perth-estate-agents/guide-to-selling/",
# "https://www.belvoir.co.uk/perth-estate-agents/landlord-advice/",
# "https://www.belvoir.co.uk/perth-estate-agents/landlord-services-and-fees/",
# "https://www.belvoir.co.uk/perth-estate-agents/sell-my-home/",
# "https://www.belvoir.co.uk/peterborough-estate-agents/guide-to-selling-your-home-in-peterborough/",
# "https://www.belvoir.co.uk/peterborough-estate-agents/guide-to-tenancy-deposits/",
# "https://www.belvoir.co.uk/peterborough-estate-agents/how-to-apply-for-a-property/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/cleaning-companies/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/free-downloadable-guides/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/guidelines-for-vacating/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/investment-property-sourcing-service/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/mortgage-advice-2/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/portfolio-investments-project-management/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/removals/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/report-repairs/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/solicitors/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/useful_document/how-to-test-your-smoke-detector/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/what-documents-do-i-need-to-provide/",
# "https://www.belvoir.co.uk/portsmouth-estate-agents/what-happens-to-my-holding-money/",
# "https://www.belvoir.co.uk/rugby-estate-agents/best-lettings-agent-in-west-midlands/",
# "https://www.belvoir.co.uk/rugby-estate-agents/invest-in-rugby/",
# "https://www.belvoir.co.uk/rugby-estate-agents/landlord-privacy-policy/",
# "https://www.belvoir.co.uk/rugby-estate-agents/safeagent-status/",
# "https://www.belvoir.co.uk/rugby-estate-agents/tenant-charges/",
# "https://www.belvoir.co.uk/rugby-estate-agents/tenant-privacy-policy/",
# "https://www.belvoir.co.uk/shrewsbury-estate-agents/landlord-event-october-2025/",
# "https://www.belvoir.co.uk/sleaford-estate-agents/application-process/",
# "https://www.belvoir.co.uk/sleaford-estate-agents/are-you-covered/",
# "https://www.belvoir.co.uk/sleaford-estate-agents/switch/",
# "https://www.belvoir.co.uk/sleaford-estate-agents/what-happens-next/",
# "https://www.belvoir.co.uk/sleaford-estate-agents/what-you-need-to-consider/",
# "https://www.belvoir.co.uk/southampton-estate-agents/information-regarding-tenant-fees-in-southampton/",
# "https://www.belvoir.co.uk/st-albans-estate-agents/5-top-tips-for-choosing-an-agent/",
# "https://www.belvoir.co.uk/st-albans-estate-agents/landlord-fees-and-services/",
# "https://www.belvoir.co.uk/st-albans-estate-agents/landlord-privacy-policy/",
# "https://www.belvoir.co.uk/st-albans-estate-agents/tenant-responsibilities/",
# "https://www.belvoir.co.uk/st-albans-estate-agents/tenants-privacy-policy/",
# "https://www.belvoir.co.uk/stamford-estate-agents/covid-update/",
# "https://www.belvoir.co.uk/stamford-estate-agents/selling/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/buyer-information/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/contact-us-haydock/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/haydock/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/market-insights-haydock/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/reviews-haydock/",
# "https://www.belvoir.co.uk/st-helens-estate-agents/seller-information￼/",
# "https://www.belvoir.co.uk/stirling-estate-agents/application-process/",
# "https://www.belvoir.co.uk/stirling-estate-agents/landlord-fees-and-services/",
# "https://www.belvoir.co.uk/stirling-estate-agents/lettings/",
# "https://www.belvoir.co.uk/stirling-estate-agents/out-of-hours/",
# "https://www.belvoir.co.uk/stirling-estate-agents/sales/",
# "https://www.belvoir.co.uk/stirling-estate-agents/tenants-winter-preparation/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/abbey-hulton-bucknall/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/biddulph/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/burslem-tunstall-smallthorne/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/case-studies/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/case-study/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/commercial-properties/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/expanding-your-portfolio/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/fixed-fee-conveyancing/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/freeholder-landlords/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/hanley-etruria/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/how-to-protect-yourself/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/investors/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/leek/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/leek-2/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/longton/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/our-sponsored-humanitarian-project/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/privacy-policy-2/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/reasons-to-invest/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/resident-management-companies/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/step-by-step-guide-to-selling/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/stoke-on-trent/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/switching-agent/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/tenant-resources/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/tenants-rewards-platform/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/the-process/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/werrington-stockton-brook/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/what-is-block-management/",
# "https://www.belvoir.co.uk/stoke-on-trent-estate-agents/where-to-buy-in-stoke-on-trent/",
# "https://www.belvoir.co.uk/stratford-upon-avon-estate-agents/case-study/",
# "https://www.belvoir.co.uk/stratford-upon-avon-estate-agents/community/",
# "https://www.belvoir.co.uk/stratford-upon-avon-estate-agents/selling-with-belvoir-stratford-upon-avon/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/behaving-in-a-tenant-like-manner/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/easy-steps-to-move-to-belvoir/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/information-for-tenants/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/renting-out-your-property/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/tenant-repairs/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/privacy-policies/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/sellers-mortgage-advice/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/solicitors/",
# "https://www.belvoir.co.uk/sutton-estate-agents/area-guide/",
# "https://www.belvoir.co.uk/sutton-estate-agents/property-management/",
# "https://www.belvoir.co.uk/swansea-estate-agents/charity-work/",
# "https://www.belvoir.co.uk/swansea-estate-agents/community-charity-work/",
# "https://www.belvoir.co.uk/swansea-estate-agents/contract-holders/",
# "https://www.belvoir.co.uk/swansea-estate-agents/join-our-team/",
# "https://www.belvoir.co.uk/swansea-estate-agents/mumbles/",
# "https://www.belvoir.co.uk/swansea-estate-agents/online-auctions/",
# "https://www.belvoir.co.uk/swansea-estate-agents/renting-homes-act-landlord-info/",
# "https://www.belvoir.co.uk/swansea-estate-agents/renting-homes-act-overview/",
# "https://www.belvoir.co.uk/swansea-estate-agents/rent-smart-wales/",
# "https://www.belvoir.co.uk/swansea-estate-agents/sketty/",
# "https://www.belvoir.co.uk/swansea-estate-agents/upcoming-major-legal-changes-affecting-the-private-rental-sector-in-wales/",
# "https://www.belvoir.co.uk/tadley-estate-agents/area-guide/",
# "https://www.belvoir.co.uk/tadley-estate-agents/estate-agents-jargon-buster-for-buyers-sellers-landlords-and-tenants/",
# "https://www.belvoir.co.uk/tadley-estate-agents/landlord-mot/",
# "https://www.belvoir.co.uk/tadley-estate-agents/sign-up-to-our-newsletter/",
# "https://www.belvoir.co.uk/telford-estate-agents/corporate-lettings/",
# "https://www.belvoir.co.uk/telford-estate-agents/free-property-appraisal/",
# "https://www.belvoir.co.uk/telford-estate-agents/maintenance-tips/",
# "https://www.belvoir.co.uk/telford-estate-agents/private-rental-sector-midlands/",
# "https://www.belvoir.co.uk/telford-estate-agents/sath-app-and-belvoir-telford/",
# "https://www.belvoir.co.uk/telford-estate-agents/sell-your-property/",
# "https://www.belvoir.co.uk/thanet-estate-agents/privacy-policy-2/",
# "https://www.belvoir.co.uk/thirsk-estate-agents/complaints/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/estate-agents-jargon-buster-for-buyers-sellers-landlords-and-tenants/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/landlord-mot/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/sign-up-to-our-newsletter/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/5-easy-steps-for-landlords-to-switch-to-belvoir/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-studies/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-1/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-2/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-3/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/complaints-procedure/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/crowborough/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/full-management-plus/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/full-management-service/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/let-only-service/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/modern-auction/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/nil-deposit-scheme/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/part-management-service/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/contact-us/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/landlord-fees/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/privacy-policy/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/properties/for-rent/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/switch-to-belvoir/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/tenant-info/"
#     ]

#     output_file = "meta_descriptions_bulk.csv"

#     with open(output_file, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)

#         # ✅ UPDATED HEADER
#         writer.writerow([
#             "URL",
#             "Meta Description",
#             "Character Count",
#             "Page Content"
#         ])

#         for url in urls:
#             print(f"\nProcessing: {url}")

#             try:
#                 text = extract_text_from_url(url)
#                 meta_description = generate_meta_description(text)

#                 writer.writerow([
#                     url,
#                     meta_description,
#                     len(meta_description),
#                     text
#                 ])

#                 print("Meta Description:", meta_description)
#                 print("Page Content:", text)

#             except Exception as e:
#                 print(f"Failed for {url}: {e}")
#                 writer.writerow([url, "ERROR", "", ""])

#     print(f"\n--- CSV Exported Successfully: {output_file} ---")

import requests
import json
import csv
import sys
from bs4 import BeautifulSoup

# ----------------------------------
# EXISTING CODE (UNCHANGED)
# ----------------------------------

def extract_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup([
        "script", "style", "noscript", "svg",
        "form", "button", "nav", "footer",
        "header", "aside"
    ]):
        tag.decompose()

    body = soup.body
    if not body:
        return ""

    lines = []

    for el in body.find_all(["h1", "h2", "h3", "p", "li"], recursive=True):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        if text.lower() in {"submit", "contact us", "read more"}:
            continue
        if "cookie" in text.lower():
            continue
        lines.append(text)

    seen = set()
    cleaned = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            cleaned.append(line)

    return "\n\n".join(cleaned)


# ----------------------------------
# GEMINI META DESCRIPTION GENERATION
# ----------------------------------

GEMINI_API_KEY = "AIzaSyBEeQrH9LR77wVmxjHnq52R21WQ3RTwdkU"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent"
    f"?key={GEMINI_API_KEY}"
)

def generate_meta_description(page_text):
    prompt = f"""
You are an SEO expert.

Write ONE meta description for the page content below.

Rules:
- Maximum 160 characters
- SEO optimised
- Mention the brand name 'Belvoir'
- No quotes
- No emojis
- Clear and professional tone

Page content:
{page_text}
"""

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30
    )

    response.raise_for_status()  # <-- 429 originates here

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# ----------------------------------
# MAIN – BULK URL LOOP + CSV EXPORT
# ----------------------------------

if __name__ == "__main__":

    urls = [


"https://www.belvoir.co.uk/inverness-estate-agents/properties-for-sale-in-inverness-belvoir/"
# "https://www.belvoir.co.uk/stratford-upon-avon-estate-agents/community/",
# "https://www.belvoir.co.uk/stratford-upon-avon-estate-agents/selling-with-belvoir-stratford-upon-avon/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/behaving-in-a-tenant-like-manner/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/easy-steps-to-move-to-belvoir/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/information-for-tenants/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/renting-out-your-property/",
# "https://www.belvoir.co.uk/sunderland-estate-agents/tenant-repairs/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/privacy-policies/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/sellers-mortgage-advice/",
# "https://www.belvoir.co.uk/sutton-coldfield-estate-agents/solicitors/",
# "https://www.belvoir.co.uk/sutton-estate-agents/area-guide/",
# "https://www.belvoir.co.uk/sutton-estate-agents/property-management/",
# "https://www.belvoir.co.uk/swansea-estate-agents/charity-work/",
# "https://www.belvoir.co.uk/swansea-estate-agents/community-charity-work/",
# "https://www.belvoir.co.uk/swansea-estate-agents/contract-holders/",
# "https://www.belvoir.co.uk/swansea-estate-agents/join-our-team/",
# "https://www.belvoir.co.uk/swansea-estate-agents/mumbles/",
# "https://www.belvoir.co.uk/swansea-estate-agents/online-auctions/",
# "https://www.belvoir.co.uk/swansea-estate-agents/renting-homes-act-landlord-info/",
# "https://www.belvoir.co.uk/swansea-estate-agents/renting-homes-act-overview/",
# "https://www.belvoir.co.uk/swansea-estate-agents/rent-smart-wales/",
# "https://www.belvoir.co.uk/swansea-estate-agents/sketty/",
# "https://www.belvoir.co.uk/swansea-estate-agents/upcoming-major-legal-changes-affecting-the-private-rental-sector-in-wales/",
# "https://www.belvoir.co.uk/tadley-estate-agents/area-guide/",
# "https://www.belvoir.co.uk/tadley-estate-agents/estate-agents-jargon-buster-for-buyers-sellers-landlords-and-tenants/",
# "https://www.belvoir.co.uk/tadley-estate-agents/landlord-mot/",
# "https://www.belvoir.co.uk/tadley-estate-agents/sign-up-to-our-newsletter/",
# "https://www.belvoir.co.uk/telford-estate-agents/corporate-lettings/",
# "https://www.belvoir.co.uk/telford-estate-agents/free-property-appraisal/",
# "https://www.belvoir.co.uk/telford-estate-agents/maintenance-tips/",
# "https://www.belvoir.co.uk/telford-estate-agents/private-rental-sector-midlands/",
# "https://www.belvoir.co.uk/telford-estate-agents/sath-app-and-belvoir-telford/",
# "https://www.belvoir.co.uk/telford-estate-agents/sell-your-property/",
# "https://www.belvoir.co.uk/thanet-estate-agents/privacy-policy-2/",
# "https://www.belvoir.co.uk/thirsk-estate-agents/complaints/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/estate-agents-jargon-buster-for-buyers-sellers-landlords-and-tenants/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/landlord-mot/",
# "https://www.belvoir.co.uk/tilehurst-estate-agents/sign-up-to-our-newsletter/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/5-easy-steps-for-landlords-to-switch-to-belvoir/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-studies/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-1/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-2/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/case-study-3/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/complaints-procedure/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/crowborough/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/full-management-plus/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/full-management-service/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/let-only-service/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/modern-auction/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/nil-deposit-scheme/",
# "https://www.belvoir.co.uk/tunbridge-wells-estate-agents/part-management-service/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/contact-us/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/landlord-fees/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/privacy-policy/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/properties/for-rent/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/switch-to-belvoir/",
# "https://www.belvoir.co.uk/tynedale-letting-agents/tenant-info/"
    ]

    output_file = "meta_descriptions_bulk.csv"

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Meta Description", "Character Count", "Page Content"])

        for url in urls:
            print(f"\nProcessing: {url}")

            try:
                text = extract_text_from_url(url)
                meta_description = generate_meta_description(text)

                writer.writerow([
                    url,
                    meta_description,
                    len(meta_description),
                    text
                ])

                print("Meta Description:", meta_description)

            except Exception as e:
                error_msg = str(e)
                print(f"Failed for {url}: {error_msg}")

                writer.writerow([url, "ERROR", "", ""])

                # 🚨 HARD STOP ON RATE LIMIT (429)
                if "429" in error_msg:
                    print("\n🚨 429 Too Many Requests detected.")
                    print("✅ CSV saved with all processed URLs so far.")
                    sys.exit(1)

    print(f"\n--- CSV Exported Successfully: {output_file} ---")
