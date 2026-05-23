import os
import pandas as pd
import json
from collections import OrderedDict

# Define the folder path
folder_path = "GMB Insights"

# Get CSV files sorted by name order (or use os.listdir if needed)
csv_files = sorted(
    [entry for entry in os.scandir(folder_path) if entry.is_file() and entry.name.endswith(".csv")],
    key=lambda x: x.name  # Sort by filename to maintain order from UI
)

# Use an Ordered Dictionary to preserve order
all_data = OrderedDict()

# Loop through each CSV file in the correct order
for entry in csv_files:
    file_path = entry.path  # Get full file path
    file_name = entry.name  # Get file name

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert DataFrame to dictionary (preserving row order)
    data_dict = df.to_dict(orient="records")

    # Store data with filename as key
    all_data[file_name] = data_dict

# Define output JSON file path
json_file_path = "GMB_Insights.json"

# Write data to JSON file while maintaining order
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(all_data, json_file, indent=4)

print(f"JSON file created successfully: {json_file_path}")

# ---------------------------- #
# Convert JSON to CSV (with description row appearing once)
# ---------------------------- #

# Load the JSON file
with open(json_file_path, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Extract all data while keeping the description row only once
flattened_data = []
description_row_added = False  # Track if the description row is already added

for file_name, records in data.items():
    cleaned_records = []
    
    for i, record in enumerate(records):
        if i == 0:  # First row (description row)
            if not description_row_added:
                cleaned_records.append(record)  # Keep it only once
                description_row_added = True
        else:
            cleaned_records.append(record)  # Keep all actual data rows
    
    # Append cleaned records to flattened data
    for record in cleaned_records:
        record["Source_File"] = file_name  # Add filename column for reference
        flattened_data.append(record)

# Convert to DataFrame
df = pd.DataFrame(flattened_data)

# Define CSV output path
csv_output_path = "GMB_Insights_Combined.csv"

# Save as CSV
df.to_csv(csv_output_path, index=False, encoding="utf-8")

print(f"CSV file created successfully: {csv_output_path}")
