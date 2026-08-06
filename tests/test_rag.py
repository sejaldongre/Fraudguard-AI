from src.fraudguard.rag import (
    build_rag_prompt,
    determine_analysis_mode,
)


# ============================================================
# TEST DATA
# ============================================================

FRAUD_PREDICTION = {
    "prediction": 1,
    "label": "Fraud",
    "fraud_probability": 0.9886,
    "risk_level": "HIGH",
    "threshold": 0.4,
}


LOW_RISK_PREDICTION = {
    "prediction": 0,
    "label": "Legitimate",
    "fraud_probability": 0.0001,
    "risk_level": "LOW",
    "threshold": 0.4,
}


MEDIUM_RISK_PREDICTION = {
    "prediction": 0,
    "label": "Legitimate",
    "fraud_probability": 0.30,
    "risk_level": "MEDIUM",
    "threshold": 0.4,
}


EXPLANATION = {
    "base_value": -6.38,

    "top_features": [
        {
            "feature": "V17",
            "feature_value": -2.83,
            "shap_value": 3.20,
            "impact": "increases_fraud_score",
        },
        {
            "feature": "V14",
            "feature_value": -4.28,
            "shap_value": 2.47,
            "impact": "increases_fraud_score",
        },
    ],

    "summary": (
        "Features increasing the model fraud score: "
        "V17, V14."
    ),
}


RETRIEVED_KNOWLEDGE = [
    {
        "id": "fraud_001",

        "title": "Card-Not-Present Fraud",

        "category": "payment_fraud",

        "description": (
            "Fraud involving payment card information "
            "used in an online or remote transaction."
        ),

        "indicators": [
            "Unauthorized online payment activity",
            "Repeated suspicious payment attempts",
        ],

        "recommended_actions": [
            "Apply additional verification",
            "Review related transaction activity",
        ],

        "source": "Stripe",

        "source_url": (
            "https://docs.stripe.com/"
            "disputes/prevention/fraud-types"
        ),

        "similarity_score": 0.54,
    }
]


# ============================================================
# ANALYSIS MODE TESTS
# ============================================================

def test_high_risk_analysis_mode():

    mode = determine_analysis_mode(
        FRAUD_PREDICTION
    )

    assert mode == "fraud_investigation"


def test_low_risk_analysis_mode():

    mode = determine_analysis_mode(
        LOW_RISK_PREDICTION
    )

    assert mode == "low_risk_review"


def test_medium_risk_analysis_mode():

    mode = determine_analysis_mode(
        MEDIUM_RISK_PREDICTION
    )

    assert mode == "cautious_review"


# ============================================================
# PROMPT TESTS
# ============================================================

def test_build_fraud_rag_prompt():

    context_query = (
        "The payment channel is online. "
        "There were 12 transactions within 10 minutes. "
        "There were 8 failed payment attempts within "
        "10 minutes. "
        "The physical payment card was not present "
        "during the transaction."
    )

    prompt = build_rag_prompt(
        prediction=FRAUD_PREDICTION,
        explanation=EXPLANATION,
        context_query=context_query,
        retrieved_knowledge=RETRIEVED_KNOWLEDGE,
    )

    assert isinstance(prompt, str)

    assert len(prompt) > 0

    assert "fraud_investigation" in prompt

    assert "Card-Not-Present Fraud" in prompt

    assert "V17" in prompt

    # Probability is formatted as a percentage in the
    # current RAG prompt.
    assert "98.86%" in prompt

    assert context_query in prompt


def test_build_low_risk_rag_prompt():

    context_query = (
        "The payment channel is in_store. "
        "There were 1 transactions within 10 minutes."
    )

    prompt = build_rag_prompt(
        prediction=LOW_RISK_PREDICTION,
        explanation=EXPLANATION,
        context_query=context_query,
        retrieved_knowledge=RETRIEVED_KNOWLEDGE,
    )

    assert isinstance(prompt, str)

    assert "low_risk_review" in prompt

    assert (
        "No strong fraud-pattern alignment"
        in prompt
    )

    assert (
        "No fraud-specific intervention"
        in prompt
    )

    assert context_query in prompt


# ============================================================
# GROUNDING TESTS
# ============================================================

def test_prompt_contains_anonymized_feature_rule():

    prompt = build_rag_prompt(
        prediction=FRAUD_PREDICTION,
        explanation=EXPLANATION,
        context_query="Online transaction.",
        retrieved_knowledge=RETRIEVED_KNOWLEDGE,
    )

    assert "V1-V28" in prompt

    assert "anonymized" in prompt.lower()


def test_prompt_contains_similarity_warning():

    prompt = build_rag_prompt(
        prediction=FRAUD_PREDICTION,
        explanation=EXPLANATION,
        context_query="Online transaction.",
        retrieved_knowledge=RETRIEVED_KNOWLEDGE,
    )

    assert (
        "Similarity scores represent semantic relevance"
        in prompt
    )

    assert (
        "They are NOT fraud probabilities"
        in prompt
    )


def test_prompt_contains_recommendation_grounding():

    prompt = build_rag_prompt(
        prediction=LOW_RISK_PREDICTION,
        explanation=EXPLANATION,
        context_query="Single in-store transaction.",
        retrieved_knowledge=RETRIEVED_KNOWLEDGE,
    )

    assert (
        "Never recommend controls unsupported by supplied"
        in prompt
    )

    assert (
        "transaction context."
        in prompt
    )


# ============================================================
# EMPTY KNOWLEDGE TEST
# ============================================================

def test_prompt_with_empty_knowledge():

    prompt = build_rag_prompt(
        prediction=LOW_RISK_PREDICTION,
        explanation=EXPLANATION,
        context_query="Single in-store transaction.",
        retrieved_knowledge=[],
    )

    assert (
        "No fraud knowledge documents were retrieved."
        in prompt
    )
