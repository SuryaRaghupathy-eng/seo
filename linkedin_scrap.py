from bs4 import BeautifulSoup
import pandas as pd

# TXT file path
file_path = r"C:\Users\SuryaRaghupathy\OneDrive - Nurtur Limited\Desktop\Git code import\portfolio-website\public\webscrappeddata\Linkedinautomate\New Text Document.txt"

# Read HTML content
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse HTML
soup = BeautifulSoup(html_content, "html.parser")

# Find all connection cards
cards = soup.find_all("li", class_="mn-connection-card")

data = []

for index, card in enumerate(cards, start=1):

    # Name
    name_tag = card.find(
        "span",
        class_="mn-connection-card__name"
    )
    name = name_tag.get_text(strip=True) if name_tag else ""

    # Occupation / Job Role
    occupation_tag = card.find(
        "span",
        class_="mn-connection-card__occupation"
    )
    occupation = occupation_tag.get_text(strip=True) if occupation_tag else ""

    # Profile Link
    link_tag = card.find(
        "a",
        class_="ember-view mn-connection-card__link"
    )

    if link_tag and link_tag.get("href"):
        profile_link = "https://www.linkedin.com" + link_tag.get("href")
    else:
        profile_link = ""

    # Print scraped values one by one
    print(f"\n========== Person {index} ==========")
    print("Name:", name)
    print("Occupation:", occupation)
    print("Profile Link:", profile_link)

    # Append to list
    data.append({
        "Name": name,
        "Occupation": occupation,
        "Profile Link": profile_link
    })

# Create DataFrame
df = pd.DataFrame(data)

# Export CSV
output_file = r"C:\Users\SuryaRaghupathy\OneDrive - Nurtur Limited\Desktop\Git code import\portfolio-website\public\webscrappeddata\Linkedinautomate\linkedin_connections.csv"

df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("\n===================================")
print(f"CSV exported successfully: {output_file}")
print("Total profiles scraped:", len(df))