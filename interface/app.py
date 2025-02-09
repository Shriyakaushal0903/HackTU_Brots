from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load trained model and encoders
model, label_encoders = joblib.load("loan_model.pkl")  # Unpack correctly
# Load the label encoders

# Function to preprocess input data
def preprocess_input(form_data):
    processed_data = []
    
    # List of categorical columns
    categorical_cols = ["Gender", "Married", "Education", "Self_Employed", "Property_Area"]

    # Encode categorical values
    for col in categorical_cols:
        if form_data[col] in label_encoders[col].classes_:
            processed_data.append(label_encoders[col].transform([form_data[col]])[0])
        else:
            return {"error": f"Invalid value '{form_data[col]}' for {col}"}

    # Convert "Dependents" column (handles "3+" case)
    dependents = form_data["Dependents"]
    if dependents == "3+":
        processed_data.append(3)
    elif dependents.isdigit():
        processed_data.append(int(dependents))
    else:
        return {"error": f"Invalid value '{dependents}' for Dependents"}

    # Append numerical values
    try:
        processed_data.extend([
            float(form_data["ApplicantIncome"]),
            float(form_data["CoapplicantIncome"]),
            float(form_data["LoanAmount"]),
            float(form_data["Loan_Amount_Term"])
        ])
    except ValueError:
        return {"error": "Invalid numerical values in input data"}

    return [processed_data]  # Return as list for model input

# Route for frontend
@app.route('/')
def home():
    return render_template('index.html')

# Define prediction route
@app.route('/predict', methods=['POST'])
def predict():
    form_data = request.form  # Get form data from HTML

    # Validate required fields
    required_fields = ["Gender", "Married", "Dependents", "Education", "Self_Employed", 
                       "ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", 
                        "Property_Area"]

    for field in required_fields:
        if field not in form_data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Preprocess input
    input_data = preprocess_input(form_data)
    
    # Check if preprocessing returned an error
    if isinstance(input_data, dict) and "error" in input_data:
        return jsonify(input_data), 400

    # Make prediction
    try:
        prediction = model.predict(input_data)[0]
        loan_status = "Approved" if prediction == 1 else "Rejected"
        return render_template("index.html", prediction=loan_status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
