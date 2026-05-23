import json
import csv
import os

def json_to_csv(input_path, output_path):
    # Read the JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        # Each line is a separate JSON object
        data = [json.loads(line) for line in f]
    
    # Prepare CSV output
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'query', 'position', 'title', 'address', 
            'latitude', 'longitude', 'rating', 
            'ratingCount', 'category', 'phoneNumber', 
            'website', 'cid'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each query result
        for entry in data:
            query = entry['query']
            places = entry['response'][0]['places']
            
            for place in places:
                row = {
                    'query': query,
                    'position': place.get('position', ''),
                    'title': place.get('title', ''),
                    'address': place.get('address', ''),
                    'latitude': place.get('latitude', ''),
                    'longitude': place.get('longitude', ''),
                    'rating': place.get('rating', ''),
                    'ratingCount': place.get('ratingCount', ''),
                    'category': place.get('category', ''),
                    'phoneNumber': place.get('phoneNumber', '').replace('\n', ' ').strip(),
                    'website': place.get('website', ''),
                    'cid': place.get('cid', '')
                }
                writer.writerow(row)

if __name__ == '__main__':
    # Input and output file paths (using raw strings)
    input_json = r"c:/Users/SuryaRaghupathy/OneDrive - Nurtur Limited/Desktop/Git code import/portfolio-website/results/estate_agents_results.json"
    output_csv = r"c:/Users/SuryaRaghupathy/OneDrive - Nurtur Limited/Desktop/Git code import/portfolio-website/results/estate_agents_results.csv"
    
    # Convert forward slashes to backslashes if needed (Windows)
    input_json = os.path.normpath(input_json)
    output_csv = os.path.normpath(output_csv)
    
    # Convert JSON to CSV
    json_to_csv(input_json, output_csv)
    print(f"CSV file saved as {output_csv}")