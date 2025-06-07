# Insurance Fraud Detection – MLOps Pipeline with Monitoring and Visualization

This project is a full-stack MLOps pipeline for detecting insurance fraud using machine learning. It includes a FastAPI backend for predictions, Prometheus for metrics scraping, Grafana for visualization, Streamlit for displaying results interactively, and Docker for orchestration.

---

## Project Architecture

**Components:**

- **FastAPI:** Serves fraud predictions from a trained ML model and exposes `/metrics` endpoint.
- **Prometheus:** Scrapes metrics (latency, error rates, traffic) from FastAPI.
- **Grafana:** Visualizes prediction latency, error rate, volume, and uptime via dashboards.
- **Streamlit:** Web dashboard to view model predictions and interact via forms.
- **Docker Compose:** Orchestrates all services.

---

## Machine Learning Model

- **Models Used:** Soft Voting Classifier (LightGBM, XGBoost, Logistic Regression)
- **Input Features:** Age, occupation, claim amount, policy info, etc.
- **Output:** Binary classification – fraud or not fraud
- **Training:** Trained offline on a cleaned insurance dataset

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
├── Dockerfile                    # FastAPI container
├── Dockerfile.streamlit          # Streamlit container
├── docker-compose.yml            # Service orchestration
└── README.md                     # Documentation
```

---

## API Endpoint

### `POST /predict`

- Accepts JSON input of insurance claim features
- Returns:
```json
{
  "prediction": "FRAUD",
  "fraud_probability": 0.734,
  "individual_probabilities": {
    "lightgbm": 0.69,
    "xgboost": 0.74,
    "logistic": 0.76
  }
}
```

---

## Streamlit Frontend

- Inputs user data via forms
- Calls FastAPI endpoint and shows result
- Displays last 10 predictions (bar + table)

---

## Dockerized Setup

### Build and Run

```bash
docker-compose up --build
```

Services launched:

- `fraud_api`: FastAPI backend
- `streamlit_ui`: Streamlit dashboard
- `prometheus`: Metric scraping
- `grafana`: Dashboard visualization

---

## Grafana Monitoring Dashboard

### Panels:

1. **Avg Prediction Latency (Success)** – with red threshold (1s)
2. **Prediction Volume Per Hour** – colored bars per status code
3. **CPU and Memory Usage**
4. **Model Prediction Error Rate (4xx)**
5. **Model Prediction API Traffic**
6. **Uptime Panel** – displays uptime in minutes

---

## Alerts Configured

1. **High Prediction Latency (Success):**
   - Triggers when avg latency > 1s
2. **High Prediction Error Rate:**
   - Triggers when rate of 4xx > 0.01
3. **No Prediction Traffic:**
   - Triggers if prediction volume is zero

---

## Uptime Tracking

Panel: `time() - process_start_time_seconds` with unit set to minutes.

---

##  Future Enhancements

- Add Slack/email notification for Grafana alerts
- Horizontal scaling with load balancer
- Streamlit login/authentication
- CI/CD integration for auto-deployments
