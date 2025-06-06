import os
import json
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import pymysql

# RDS credentials
RDS_HOST = "insurance-fraud-db.cobaiu8aw8xi.us-east-1.rds.amazonaws.com"
RDS_PORT = 3306
RDS_DB = "insurance_fraud_db"
RDS_USER = "admin"
RDS_PASSWORD = "NeeharSatti1998"

def fetch_recent_predictions(limit=10):
    try:
        conn = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DB,
            port=RDS_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT timestamp, prediction, probability 
                FROM predictions 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to RDS: {e}")
        return pd.DataFrame()

API_URL = "http://fastapi:8000/predict"

st.title("Insurance Fraud Detection")
st.markdown("Enter the claim details below to check if it's fraudulent.")

age = st.number_input("Age", min_value=18, max_value=100, value=35)

policy_state = st.selectbox("Policy State", ["IN", "OH", "IL", "IA", "KS"])

policy_csl = st.selectbox("Policy CSL", ["250/500", "500/1000", "100/300"])

policy_deductable = st.selectbox("Policy Deductible", [1000, 2000, 3000])

umbrella_limit = st.number_input("Umbrella Limit", step=100000, value=0)

insured_sex = st.selectbox("Sex", ["MALE", "FEMALE"])

insured_education_level = st.selectbox("Education Level", [
    "PhD", "MD", "JD", "College", "Masters", "High School", "Associate"])

insured_occupation = st.selectbox("Occupation", [
    "sales", "craft-repair", "tech-support", "armed-forces", "exec-managerial", "other-service",
    "machine-op-inspct", "prof-specialty", "transport-moving", "handlers-cleaners",
    "priv-house-serv", "farming-fishing", "protective-serv"])

insured_hobbies = st.selectbox("Hobby", [
    "reading", "skydiving", "sleeping", "chess", "polo", "basketball", "board-games",
    "bungie-jumping", "camping", "cross-fit", "dancing", "exercise", "golf", "hiking",
    "kayaking", "movies", "paintball", "video-games", "yachting"])

insured_relationship = st.selectbox("Relationship", [
    "husband", "wife", "own-child", "not-in-family", "other-relative", "unmarried"])

incident_type = st.selectbox("Incident Type", [
    "Single Vehicle Collision", "Multi-vehicle Collision", "Parked Car", "Vehicle Theft"])

collision_type = st.selectbox("Collision Type", [
    "Rear Collision", "Side Collision", "Front Collision", "unknown"])

incident_severity = st.selectbox("Incident Severity", [
    "Minor Damage", "Major Damage", "Total Loss", "Trivial Damage"])

authorities_contacted = st.selectbox("Authorities Contacted", [
    "Police", "Fire", "Other", "Unknown"])

incident_state = st.selectbox("Incident State", [
    "NY", "OH", "PA", "SC", "VA", "WV"])

incident_city = st.selectbox("Incident City", [
    "Columbus", "Hillsdale", "Northbrook", "Riverwood", "Springfield", "Northbend"])

number_of_vehicles_involved = st.selectbox("Number of Vehicles Involved", [1, 2, 3, 4])

bodily_injuries = st.selectbox("Bodily Injuries", [0, 1, 2])

witnesses = st.selectbox("Witnesses", [0, 1, 2, 3])

police_report_available = st.selectbox("Police Report Available", ["YES", "NO"])

total_claim_amount = st.number_input("Total Claim Amount", value=5000)

auto_make = st.selectbox("Auto Make", [
    "Honda", "Toyota", "Ford", "Chevrolet", "BMW", "Audi", "Mercedes", "Volkswagen",
    "Nissan", "Suburu", "Jeep", "Saab"])

auto_model = st.selectbox("Auto Model", [
    "Civic", "Accord", "Camry", "F150", "Escape", "CRV", "Corolla", "Jetta", "Maxima",
    "Pathfinder", "Legacy", "Fusion", "TL", "Forrestor", "Highlander", "Ultima", "Neon",
    "RAM", "Wrangler", "X5", "X6", "C300", "E400", "M5", "MDX", "ML350", "Malibu", "Passat",
    "RSX", "Silverado", "A3", "A5", "95", "93", "92x", "Grand Cherokee", "Impreza"])

auto_year = st.selectbox("Auto Year", list(range(1996, 2016)))

claim_ratio_bin = st.selectbox("Claim Ratio Bin", ["Low", "Medium", "High"])
if st.button("Predict Fraud"):
    input_data = {
        "age": age,
        "policy_state": policy_state,
        "policy_csl": policy_csl,
        "policy_deductable": policy_deductable,
        "umbrella_limit": umbrella_limit,
        "insured_sex": insured_sex,
        "insured_education_level": insured_education_level,
        "insured_occupation": insured_occupation,
        "insured_hobbies": insured_hobbies,
        "insured_relationship": insured_relationship,
        "incident_type": incident_type,
        "collision_type": collision_type,
        "incident_severity": incident_severity,
        "authorities_contacted": authorities_contacted,
        "incident_state": incident_state,
        "incident_city": incident_city,
        "number_of_vehicles_involved": number_of_vehicles_involved,
        "bodily_injuries": bodily_injuries,
        "witnesses": witnesses,
        "police_report_available": police_report_available,
        "total_claim_amount": total_claim_amount,
        "auto_make": auto_make,
        "auto_model": auto_model,
        "auto_year": auto_year,
        "claim_ratio_bin": claim_ratio_bin
    }

    response = requests.post(API_URL, json=input_data)

    if response.status_code == 200:
        result = response.json()
        st.success(f"Prediction: {result['prediction']}")
        st.info(f"Fraud Probability: {result['fraud_probability']:.2%}")

       
        if "individual_probabilities" in result:
            st.subheader("Model Breakdown (Individual Probabilities)")
            for model_name, prob in result["individual_probabilities"].items():
                st.write(f"- **{model_name.upper()}**: {prob:.2%}")

    else:
        st.error("Error: Failed to get prediction from API.")


st.markdown("---")
st.subheader("Prediction History")


rds_history = fetch_recent_predictions(limit=10)
rds_history["timestamp"] = pd.to_datetime(rds_history["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
if not rds_history.empty:
    st.bar_chart(rds_history.set_index("timestamp")["probability"])
    st.dataframe(rds_history)
else:
    st.write("No prediction data available in RDS.")

