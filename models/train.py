import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pickle, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

print("Loading data...")
df = pd.read_csv(os.path.join(ROOT, "data", "European_Bank.csv"))
df = df.drop(['CustomerId', 'Surname', 'Year'], axis=1)

# Feature Engineering
df['Balance_Salary_Ratio']   = df['Balance'] / (df['EstimatedSalary'] + 1)
df['Age_Tenure_Interaction'] = df['Age'] * df['Tenure']
df['Product_Engagement']     = df['NumOfProducts'] * df['IsActiveMember']
df['Zero_Balance']           = (df['Balance'] == 0).astype(int)
df = pd.get_dummies(df, columns=['Geography', 'Gender'], drop_first=False)

X = df.drop('Exited', axis=1)
y = df['Exited']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print("Training models...")
models = {
    'gb_model': GradientBoostingClassifier(n_estimators=200, random_state=42),
    'rf_model': RandomForestClassifier(n_estimators=200, random_state=42),
    'dt_model': DecisionTreeClassifier(max_depth=6, random_state=42),
    'lr_model': LogisticRegression(max_iter=1000, random_state=42),
}

trained = {}
for name, model in models.items():
    Xtr = X_train_sc if 'lr' in name else X_train
    model.fit(Xtr, y_train)
    trained[name] = model
    print(f"  ✓ {name} trained")

print("Saving models...")
os.makedirs(BASE, exist_ok=True)
for name, model in trained.items():
    with open(os.path.join(BASE, f"{name}.pkl"), "wb") as f:
        pickle.dump(model, f)

with open(os.path.join(BASE, "scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)

with open(os.path.join(BASE, "feature_names.json"), "w") as f:
    json.dump(X.columns.tolist(), f)

# Evaluate
results = {}
name_map = {
    'Logistic Regression': ('lr_model', X_test_sc),
    'Decision Tree':       ('dt_model', X_test),
    'Random Forest':       ('rf_model', X_test),
    'Gradient Boosting':   ('gb_model', X_test),
}
for label, (key, Xte) in name_map.items():
    model = trained[key]
    yp    = model.predict(Xte)
    yprob = model.predict_proba(Xte)[:, 1]
    results[label] = {
        'Accuracy':  round(accuracy_score(y_test, yp) * 100, 2),
        'Precision': round(precision_score(y_test, yp) * 100, 2),
        'Recall':    round(recall_score(y_test, yp) * 100, 2),
        'F1':        round(f1_score(y_test, yp) * 100, 2),
        'ROC-AUC':   round(roc_auc_score(y_test, yprob) * 100, 2),
    }
    print(f"  {label}: Acc={results[label]['Accuracy']}% | AUC={results[label]['ROC-AUC']}%")

with open(os.path.join(BASE, "results.json"), "w") as f:
    json.dump(results, f)

print("\n✅ All models trained and saved successfully!")
print(f"   Features: {X.columns.tolist()}")
