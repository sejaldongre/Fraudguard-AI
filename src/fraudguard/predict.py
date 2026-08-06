from pathlib import Path

import pandas as pd

from .config import (
    FEATURE_COLUMNS,
    FRAUD_THRESHOLD
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "fraudguard_xgb.joblib"
)


def get_risk_level(
    fraud_probability: float
) -> str:

    if fraud_probability >= 0.70:
        return "HIGH"

    elif fraud_probability >= 0.40:
        return "MEDIUM"

    return "LOW"


def predict_transaction(
    transaction: dict,
    model
) -> dict:

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in transaction
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    input_data = pd.DataFrame(
        [transaction]
    )

    input_data = input_data[
        FEATURE_COLUMNS
    ]

    fraud_probability = float(
        model.predict_proba(
            input_data
        )[0, 1]
    )

    prediction = int(
        fraud_probability
        >= FRAUD_THRESHOLD
    )

    return {
        "prediction": prediction,

        "label": (
            "Fraud"
            if prediction == 1
            else "Legitimate"
        ),

        "fraud_probability":
            fraud_probability,

        "risk_level":
            get_risk_level(
                fraud_probability
        ),

        "threshold":
            FRAUD_THRESHOLD
    }
