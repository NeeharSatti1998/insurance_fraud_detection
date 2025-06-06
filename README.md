
# Insurance Fraud Detection – MLOps Pipeline with Monitoring and Visualization

This project is a full-stack MLOps pipeline for detecting insurance fraud using machine learning. It includes a FastAPI backend for predictions, Prometheus for metrics scraping, Streamlit for displaying results interactively, and Docker for orchestration.

---

## Project Architecture

**Components:**

- **FastAPI:** Serves fraud predictions from a trained ML model.
- **Prometheus:** Scrapes metrics from FastAPI for monitoring.
- **Streamlit:** Web dashboard to view model predictions and user interface.
- **Docker Compose:** Orchestrates all services.

---

## Machine Learning Model

- **Models Used:** Soft Voting Classifier (ensemble of LightGBM, XGBoost, Logistic Regression)
- **Input Features:** Includes categorical and numerical features like age, occupation, claim amount, policy details, etc.
- **Output:** Binary classification – fraud or not fraud.
- **Training:** Model is trained on a cleaned version of the insurance claim dataset and saved as `model/soft_voting_model_1.pkl`.

---

## Folder Structure

```
insurance_risk/
├── app/
│   └── main.py                   # FastAPI backend
├── streamlit_app/
│   └── streamlit_app.py          # Streamlit frontend
├── model/
│   └── soft_voting_model_1.pkl   # Trained ML model
├── requirements.txt              # Python dependencies
├── Dockerfile                    # For FastAPI container
├── Dockerfile.streamlit          # For Streamlit container
├── docker-compose.yml            # Docker Compose config
└── README.md                     # Project documentation
```

---

## How It Works

### 1. FastAPI Prediction Endpoint

- **URL:** `http://localhost:8000/predict`
- **Accepts:** POST request with claim details
- **Returns:**

```json
{
  "prediction": "NOT FRAUD",
  "fraud_probability": 0.058
}
```

---

### 2. Streamlit Frontend

- User inputs claim details via interactive widgets
- Sends POST request to FastAPI
- Displays prediction and fraud probability
- Shows last 10 predictions as a history bar chart and table

---

## Dockerized Setup

### Build and Run All Services

```bash
docker-compose up --build
```

### Containers Created

- `fraud_api` – FastAPI prediction backend
- `streamlit_ui` – Streamlit frontend dashboard

---

## Environment Configuration

Ensure your `.env` is properly set if needed. All static configuration is within the `docker-compose.yml`.

---

## Monitoring (Optional)

Prometheus can be extended to track API performance by scraping `/metrics`. FastAPI exposes custom metrics if enabled.

---

## Future Improvements

- Store predictions in a MySQL RDS database
- Add Prometheus + Grafana for monitoring
- Add authentication to Streamlit app
- Deploy on AWS EC2 for full cloud hosting
