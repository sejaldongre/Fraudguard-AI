import pandas as pd

from .config import FEATURE_COLUMNS


def get_impact(shap_value: float) -> str:
    """
    Determine whether a feature pushes the model's
    fraud score higher or lower.
    """

    if shap_value > 0:
        return "increases_fraud_score"

    if shap_value < 0:
        return "decreases_fraud_score"

    return "neutral"


def build_explanation_summary(
    explanation: dict
) -> str:
    """
    Create a simple text summary using the top
    SHAP feature contributions.
    """

    top_features = explanation["top_features"]

    increasing = [
        item
        for item in top_features
        if item["impact"] == "increases_fraud_score"
    ]

    decreasing = [
        item
        for item in top_features
        if item["impact"] == "decreases_fraud_score"
    ]

    parts = []

    if increasing:
        feature_names = [
            item["feature"]
            for item in increasing
        ]

        parts.append(
            "Features increasing the model fraud score: "
            + ", ".join(feature_names)
            + "."
        )

    if decreasing:
        feature_names = [
            item["feature"]
            for item in decreasing
        ]

        parts.append(
            "Features decreasing the model fraud score: "
            + ", ".join(feature_names)
            + "."
        )

    if not parts:
        return (
            "No strong directional feature "
            "contributions found."
        )

    return " ".join(parts)


def explain_transaction(
    transaction: dict,
    explainer,
    top_n: int = 5
) -> dict:
    """
    Generate a local SHAP explanation for
    a single transaction.
    """

    # Convert transaction to a one-row DataFrame
    input_data = pd.DataFrame(
        [transaction]
    )

    # Keep exactly the same feature order
    # used during model training
    input_data = input_data[
        FEATURE_COLUMNS
    ]

    # Calculate SHAP values
    shap_values = explainer(
        input_data
    )

    # Get SHAP values for this transaction
    values = shap_values.values[0]

    feature_explanations = []

    for (
        feature,
        feature_value,
        shap_value
    ) in zip(
        FEATURE_COLUMNS,
        input_data.iloc[0].values,
        values
    ):

        shap_value = float(shap_value)

        feature_explanations.append(
            {
                "feature": feature,

                "feature_value": float(
                    feature_value
                ),

                "shap_value": shap_value,

                "impact": get_impact(
                    shap_value
                )
            }
        )

    # Sort according to absolute SHAP contribution
    feature_explanations = sorted(
        feature_explanations,
        key=lambda item: abs(
            item["shap_value"]
        ),
        reverse=True
    )

    # Keep only top N features
    top_features = feature_explanations[
        :top_n
    ]

    result = {
        "base_value": float(
            shap_values.base_values[0]
        ),

        "top_features": top_features
    }

    # Add human-readable summary
    result["summary"] = (
        build_explanation_summary(
            result
        )
    )

    return result
