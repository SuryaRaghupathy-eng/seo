import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_title(url):
    try:
        # Headers to mimic a web browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }

        # Send a GET request with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and return the title tag content
        title = soup.title.string if soup.title else "No title found"
        return title

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Read the CSV file with bulk URLs
input_file = "keyword_list.csv"
output_file = "titles_output.csv"

# Ensure the file has a column named 'URLs'
try:
    df = pd.read_csv(input_file)
    if 'URLs' not in df.columns:
        raise ValueError("The CSV file must contain a column named 'URLs'.")

    # Initialize a list to store results
    results = []

    # Iterate through each URL and fetch the title
    for index, row in df.iterrows():
        url = row['URLs']
        print(f"Processing: {url}")
        title = fetch_title(url)
        results.append({'URL': url, 'Title': title})

    # Save the results into a new CSV file
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)
    print(f"Titles have been saved to {output_file}")

except FileNotFoundError:
    print(f"File {input_file} not found.")
except Exception as e:
    print(f"An error occurred: {e}")
