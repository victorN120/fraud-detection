import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.DataFrame({
    'amount': [10, 500, 1000, 20, 750],
    'country': ['US', 'RU', 'CN', 'UK', 'IN'],
    'label': [0, 1, 1, 0, 1]
})

data = pd.get_dummies(data, columns=['country'])
X = data.drop('label', axis=1)
y = data['label']

model = RandomForestClassifier()
model.fit(X, y)
joblib.dump(model, 'fraud_model.pkl')
print("✅ Model trained and saved as fraud_model.pkl")