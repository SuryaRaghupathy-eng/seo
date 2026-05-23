import json
import csv

# Provide the full path to the JSON file
json_file_path = 'C:/Users/SuryaRaghupathy/OneDrive - Nurtur Limited/Desktop/Git code import/all_properties - CJ Hole.json'

try:
    # Load the JSON data from the file with the correct encoding
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Check if the data is a dictionary or list
    if isinstance(data, dict):  # Single dictionary
        data = [data]  # Convert to a list for consistency

    # Check if the data is a list
    if isinstance(data, list) and len(data) > 0:
        # Open a CSV file to write
        csv_file_path = 'C:/Users/SuryaRaghupathy/OneDrive - Nurtur Limited/Desktop/Git code import/output.csv'

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Create a CSV writer object
            csv_writer = csv.writer(csv_file)

            # Extract the header from the keys of the first item in the list
            header = data[0].keys()
            csv_writer.writerow(header)

            # Write the data (values)
            for item in data:
                csv_writer.writerow(item.values())

        print("JSON data successfully written to CSV.")
    else:
        print("Error: JSON data is not in the expected format or is empty.")

except FileNotFoundError:
    print(f"Error: The file '{json_file_path}' was not found.")
except json.JSONDecodeError:
    print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
