from flask import Flask, render_template, redirect, url_for, request, jsonify
import pandas as pd
import joblib
import json
import os
import csv

# Current directory
current_dir = os.path.dirname(__file__)

# Flask app
app = Flask(__name__, static_folder='static', template_folder='template')

# Function to predict loan approval
def ValuePredictor(data=pd.DataFrame):
    model_name = 'bin/xgboostModel.pkl'  # Model filename
    model_dir = os.path.join(current_dir, model_name)  # Path to model
    loaded_model = joblib.load(open(model_dir, 'rb'))  # Load the model
    result = loaded_model.predict(data)  # Predict
    return result[0]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

# Prediction route
@app.route('/prediction', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Collect form data
        form_data = {
            "Name": request.form['name'].strip().lower(),
            "Gender": request.form['gender'].strip().lower(),
            "Education": request.form['education'],
            "Self_Employed": request.form['self_employed'],
            "Marital_Status": request.form['marital_status'],
            "Dependents": request.form['dependents'],
            "Applicant_Income": request.form['applicant_income'],
            "Coapplicant_Income": request.form['coapplicant_income'],
            "Loan_Amount": request.form['loan_amount'],
            "Loan_Term": request.form['loan_term'],
            "Property_Area": request.form['property_area'],
        }

        # Load schema file with column names
        schema_name = 'data/columns_set.json'
        schema_dir = os.path.join(current_dir, schema_name)
        with open(schema_dir, 'r') as f:
            cols = json.loads(f.read())

        schema_cols = cols['data_columns']

        # Update categorical values
        for col_prefix in ['Dependents', 'Property_Area']:
            col_name = f"{col_prefix}_{form_data[col_prefix]}"
            if col_name in schema_cols:
                schema_cols[col_name] = 1

        # Update numerical values
        schema_cols.update({
            'ApplicantIncome': form_data["Applicant_Income"],
            'CoapplicantIncome': form_data["Coapplicant_Income"],
            'LoanAmount': form_data["Loan_Amount"],
            'Loan_Amount_Term': form_data["Loan_Term"],
            'Gender_Male': form_data["Gender"],
            'Married_Yes': form_data["Marital_Status"],
            'Education_Not Graduate': form_data["Education"],
            'Self_Employed_Yes': form_data["Self_Employed"]
        })

        # Convert to DataFrame
        df = pd.DataFrame([schema_cols], dtype=float)

        # Predict loan approval
        result = ValuePredictor(data=df)

        # Store prediction result
        prediction_text = f"Dear {form_data['Name']}, your loan is approved!" if int(result) == 1 else f"Sorry {form_data['Name']}, your loan is rejected!"
        form_data["Prediction"] = "Approved" if int(result) == 1 else "Rejected"

        # Save to CSV
        csv_file = 'loan_applications.csv'
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=form_data.keys())
            if not file_exists:
                writer.writeheader()  # Write header if file is new
            writer.writerow(form_data)

        return render_template('prediction.html', prediction=prediction_text)
    
    else:
        return render_template('error.html', prediction="An error occurred.")

# Document verification route
@app.route('/document_verification')
def document_verification():
    return redirect("http://127.0.0.1:5001/")  # Change to actual URL of document verification app

if __name__ == '__main__':
    app.run(debug=True)
