# 🏦 ChurnIQ — Bank Customer Churn Intelligence

Predictive Modeling and Risk Scoring for Bank Customer Churn using Machine Learning.

---

## 📌 Project Overview

ChurnIQ is an ML-powered dashboard that predicts whether a bank customer is likely to churn, assigns a risk probability score, and provides explainable insights into churn drivers.

Built for the **European Central Bank** as part of the **Unified Mentor Internship Program**.

---

## 🤖 ML Models Used

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Gradient Boosting | 86.85% | 86.84% |
| Random Forest | 86.50% | 85.68% |
| Decision Tree | 85.80% | 83.60% |
| Logistic Regression | 80.85% | 77.34% |

---

## 📊 Dashboard Modules

1. **Risk Calculator** — Enter customer details and get instant churn probability
2. **EDA & Insights** — Visual analysis of churn drivers
3. **Model Performance** — Compare all 4 ML models
4. **What-If Simulator** — Adjust parameters and see real-time risk changes

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Train models first
python models/train.py

# Run the app
streamlit run app/app.py
```

---

## 📁 Project Structure

```
PythonProject1/
├── app/
│   └── app.py              # Streamlit dashboard
├── data/
│   └── European_Bank.csv   # Dataset
├── models/
│   ├── gb_model.pkl        # Gradient Boosting
│   ├── rf_model.pkl        # Random Forest
│   ├── dt_model.pkl        # Decision Tree
│   ├── lr_model.pkl        # Logistic Regression
│   ├── scaler.pkl          # StandardScaler
│   ├── feature_names.json  # Feature list
│   └── results.json        # Model metrics
├── reports/
│   ├── Research_Paper.docx
│   └── Executive_Summary.docx
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Streamlit** — Dashboard
- **Scikit-learn** — ML Models
- **Pandas / NumPy** — Data Processing
- **Plotly** — Interactive Charts
