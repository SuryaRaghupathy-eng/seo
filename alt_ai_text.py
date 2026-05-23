# import pandas as pd
# from PIL import Image
# from transformers import BlipProcessor, BlipForConditionalGeneration
# import os

# # Load the BLIP model and processor
# processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
# model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# # File paths
# input_excel_path = r"C:\Users\SuryaRaghupathy\OneDrive - Nurtur Limited\Desktop\Git code import\image_data.xlsx"
# output_csv_path = r"C:\Users\SuryaRaghupathy\OneDrive - Nurtur Limited\Desktop\Git code import\image_alt_texts.csv"

# # Load the Excel file
# df = pd.read_excel(input_excel_path)

# # Verify that the column containing image paths exists
# if "Image File Path" not in df.columns:  # Replace 'Image Path' with the actual column name in your Excel file
#     raise KeyError("The column 'Image Path' does not exist in the Excel file. Please check the column name.")

# # Initialize a list to store generated alt texts
# alt_texts = []

# # Process each image and generate alt text
# for image_path in df["Image File Path"]:  # Replace 'Image Path' with your actual column name
#     try:
#         # Check if the image file exists
#         if not os.path.exists(image_path):
#             alt_texts.append(f"Image not found: {image_path}")
#             continue

#         # Open and process the image
#         image = Image.open(image_path).convert("RGB")
#         inputs = processor(image, return_tensors="pt")

#         # Generate alt text using the model
#         out = model.generate(**inputs)
#         alt_text = processor.decode(out[0], skip_special_tokens=True)
#         alt_texts.append(alt_text)

#     except Exception as e:
#         # Handle any errors during processing
#         alt_texts.append(f"Error processing image: {e}")

# # Add the alt texts to a new column in the DataFrame
# df["Alt Text"] = alt_texts

# # Save the updated DataFrame to a CSV file
# df.to_csv(output_csv_path, index=False)

# print(f"Alt texts have been generated and saved to {output_csv_path}")
import os
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from io import BytesIO

# -----------------------------
# Disable GPU to avoid WinError 1114
# -----------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force PyTorch to use CPU

# -----------------------------
# Load BLIP model and processor
# -----------------------------
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# -----------------------------
# Image URL
# -----------------------------
image_url = "https://media.smelogin.co.uk/2305/1962/PropertyImages/0_16674869682985.JPG?auto=compress%2Cformat&crop=entropy&fit=crop&fm=webp%2Cjpg&h=256&ixlib=php-2.1.1&or=0&q=60&w=342&s=9a7f1a12cc927c31bdcd9cd00c1f9df3"

# -----------------------------
# Download image and save locally
# -----------------------------
local_path = "property_image.jpg"
if not os.path.exists(local_path):
    response = requests.get(image_url)
    with open(local_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Image saved locally: {local_path}")

# -----------------------------
# Open local image
# -----------------------------
image = Image.open(local_path).convert("RGB")

# -----------------------------
# Generate alt text
# -----------------------------
inputs = processor(image, return_tensors="pt")  # PyTorch tensor on CPU
out = model.generate(**inputs, max_length=30)
alt_text = processor.decode(out[0], skip_special_tokens=True)

# -----------------------------
# Display results
# -----------------------------
print("🖼️ Local Image:", local_path)
print("📝 Generated Alt Text:", alt_text)
