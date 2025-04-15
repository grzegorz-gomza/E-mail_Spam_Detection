import pandas as pd
import numpy as np
import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

# Load model
filename = "app/spam_detection_model.pkl"
with open(filename, 'rb') as file:
    model = pickle.load(file)

class_names = np.array(['Not a Spam', 'Spam'])

# FastAPI app instance
app = FastAPI(
    title="Spam Model Classifier API",
    description="An API to classify email as Spam or Ham using a trained ML model.",
    version="1.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class EmailRequest(BaseModel):
    email: str

# Response model
class PredictionResponse(BaseModel):
    prediction: str
    confidence: float

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Spam Model Classifier API - running."}

@app.post("/predict", response_model=PredictionResponse)
def predict(data: EmailRequest):
    """
    Predicts whether the given email is Spam or Ham, and returns probability/confidence.
    """
    if not data.email or not isinstance(data.email, str):
        raise HTTPException(status_code=400, detail="Invalid input: email is required as a string.")

    try:
        # Reshape as Series for model's pipeline
        email_series = pd.Series([data.email])

        # Prediction (0 or 1)
        pred_idx = model.predict(email_series)[0]
        pred_label = class_names[pred_idx]

        # Probability/confidence (take prob of "Spam" class)
        proba = model.predict_proba(email_series)[0]
        conf = float(np.max(proba))  # confidence for predicted class

        return PredictionResponse(prediction=pred_label, confidence=conf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
