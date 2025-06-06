from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import boto3

app = FastAPI()

# --- S3 Model Loading ---
MODEL_DIR = "/tmp/model"  # Temporary dir in container
MODEL_PATH = os.path.join(MODEL_DIR, "soft_voting_model_1.pkl")
COLUMNS_PATH = os.path.join(MODEL_DIR, "model_columns.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

s3 = boto3.client('s3')
BUCKET_NAME = "insurance-model-bucket"

def download_if_not_exists(s3_key, local_path):
    if not os.path.exists(local_path):
        print(f"Downloading {s3_key} from S3...")
        s3.download_file(BUCKET_NAME, s3_key, local_path)
    else:
        print(f"{local_path} already exists. Skipping download.")

download_if_not_exists("soft_voting_model_1.pkl", MODEL_PATH)
download_if_not_exists("model_columns.pkl", COLUMNS_PATH)

model = joblib.load(MODEL_PATH)
model_columns = joblib.load(COLUMNS_PATH)

# --- Input Schema ---
class InsuranceClaim(BaseModel):
    age: int
    policy_state: str
    policy_csl: str
    policy_deductable: int
    umbrella_limit: int
    insured_sex: str
    insured_education_level: str
    insured_occupation: str
    insured_hobbies: str
    insured_relationship: str
    incident_type: str
    collision_type: str
    incident_severity: str
    authorities_contacted: str
    incident_state: str
    incident_city: str
    number_of_vehicles_involved: int
    bodily_injuries: int
    witnesses: int
    police_report_available: str
    total_claim_amount: float
    auto_make: str
    auto_model: str
    auto_year: int
    claim_ratio_bin: str

# --- Preprocessing ---
def preprocess_input(data: dict):
    df = pd.DataFrame([data])
    df_encoded = pd.get_dummies(df)
    df_encoded = df_encoded.reindex(columns=model_columns, fill_value=0)
    return df_encoded

# --- Store Prediction (RDS DISABLED) ---
def store_prediction(input_data, prediction_result, probability):
    print("RDS storage skipped (disabled during EC2/S3 testing phase).")

# --- Prediction Endpoint ---
@app.post("/predict")
def predict_fraud(claim: InsuranceClaim):
    input_dict = claim.dict()
    processed_input = preprocess_input(input_dict)

    # Final Soft Voting Result
    prediction = model.predict(processed_input)[0]
    overall_prob = round(model.predict_proba(processed_input)[0][1], 3)
    result = "FRAUD" if prediction == 1 else "NOT FRAUD"

    # Optional: Save later to RDS
    store_prediction(input_dict, result, overall_prob)

    # Individual estimator probabilities
    individual_probs = {}
    if hasattr(model, "named_estimators_"):  # VotingClassifier attribute
        for name, estimator in model.named_estimators_.items():
            if hasattr(estimator, "predict_proba"):  # Safety check
                prob = estimator.predict_proba(processed_input)[0][1]
                individual_probs[name] = round(prob, 3)

    return {
        "prediction": result,
        "fraud_probability": overall_prob,
        "individual_probabilities": individual_probs
    }