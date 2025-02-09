from flask import Flask, request, jsonify, render_template
import pytesseract
import cv2
import os
import pandas as pd
from datetime import datetime
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load CSVs into memory
users_csv_path = "users.csv"
loan_csv_path = "loan_applications.csv"

df_users = pd.read_csv(users_csv_path)
df_loans = pd.read_csv(loan_csv_path)

# Function to clean name
def clean_name(name):
    name = name.strip()
    name = re.sub(r"[^a-zA-Z\s]", "", name)  # Remove non-alphabet characters
    return name.strip()

# Function to extract text from image
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

# Function to extract Aadhaar details
def extract_aadhaar_details(text):
    name_pattern = r"(?i)(?:name|naam)[:\s]*([A-Za-z ]+)"
    gender_pattern = r"\b(Male|Female)\b"

    name = re.search(name_pattern, text)
    gender_number = re.search(gender_pattern, text)

    return {
        "name": clean_name(name.group(1)) if name else None,
        "gender_number": gender_number.group() if gender_number else None
    }

# Function to compare with both CSVs
def compare_with_csv(extracted_data):
    if not extracted_data["name"] or not extracted_data["gender_number"]:
        return None

    extracted_name = extracted_data["name"].strip().lower()
    extracted_aadhaar = extracted_data["gender_number"].strip()

    # Normalize users.csv data
    df_users['name'] = df_users['name'].astype(str).str.strip().str.lower()
    df_users['gender_number'] = df_users['gender_number'].astype(str).str.strip()

    # Normalize loan_applications.csv data
    df_loans['name'] = df_loans['name'].astype(str).str.strip().str.lower()
    df_loans['gender_number'] = df_loans['gender_number'].astype(str).str.strip()

    # Check if a match exists in both CSVs
    user_match = df_users[
        (df_users['name'] == extracted_name) & (df_users['gender_number'] == extracted_aadhaar)
    ]
    
    loan_match = df_loans[
        (df_loans['name'] == extracted_name) & (df_loans['gender_number'] == extracted_aadhaar)
    ]

    if not user_match.empty and not loan_match.empty:
        return {"message": "Document verified, you're good to go"}
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    text = extract_text_from_image(file_path)
    extracted_data = extract_aadhaar_details(text)

    matched_record = compare_with_csv(extracted_data)

    if matched_record:
        return jsonify(matched_record)
    else:
        return jsonify({"match_found": False, "message": "No matching record found in users or loan applications database."})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
