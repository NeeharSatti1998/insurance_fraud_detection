from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import boto3
import mysql.connector
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# --- S3 Model Loading ---
MODEL_DIR = "/tmp/model"
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

# --- RDS Configuration ---
DB_CONFIG = {
    'host': 'insurance-fraud-db.cobaiu8aw8xi.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'NeeharSatti1998',
    'database': 'insurance_fraud_db',
    'port': 3306
}

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

# --- Store Prediction to RDS ---
def store_prediction(input_data, prediction_result, probability):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        INSERT INTO predictions (
            age, policy_state, policy_csl, policy_deductable, umbrella_limit,
            insured_sex, insured_education_level, insured_occupation,
            insured_hobbies, insured_relationship, incident_type, collision_type,
            incident_severity, authorities_contacted, incident_state, incident_city,
            number_of_vehicles_involved, bodily_injuries, witnesses, police_report_available,
            total_claim_amount, auto_make, auto_model, auto_year, claim_ratio_bin,
            prediction, probability
        ) VALUES (%s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s)
        """

        values = (
            input_data["age"], input_data["policy_state"], input_data["policy_csl"], input_data["policy_deductable"], input_data["umbrella_limit"],
            input_data["insured_sex"], input_data["insured_education_level"], input_data["insured_occupation"],
            input_data["insured_hobbies"], input_data["insured_relationship"], input_data["incident_type"], input_data["collision_type"],
            input_data["incident_severity"], input_data["authorities_contacted"], input_data["incident_state"], input_data["incident_city"],
            input_data["number_of_vehicles_involved"], input_data["bodily_injuries"], input_data["witnesses"], input_data["police_report_available"],
            input_data["total_claim_amount"], input_data["auto_make"], input_data["auto_model"], input_data["auto_year"], input_data["claim_ratio_bin"],
            prediction_result, probability
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        print("Prediction stored in RDS")
    except Exception as e:
        print("RDS storage failed:", e)

# --- Prediction Endpoint ---
@app.post("/predict")
def predict_fraud(claim: InsuranceClaim):
    input_dict = claim.dict()
    processed_input = preprocess_input(input_dict)

    prediction = model.predict(processed_input)[0]
    overall_prob = round(float(model.predict_proba(processed_input)[0][1]), 3)
    result = "FRAUD" if prediction == 1 else "NOT FRAUD"

    store_prediction(input_dict, result, overall_prob)

    individual_probs = {}
    if hasattr(model, "named_estimators_"):
        for name, estimator in model.named_estimators_.items():
            if hasattr(estimator, "predict_proba"):
                prob = estimator.predict_proba(processed_input)[0][1]
                individual_probs[name] = round(float(prob), 3)

    return {
        "prediction": result,
        "fraud_probability": overall_prob,
        "individual_probabilities": individual_probs
    }
