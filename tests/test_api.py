import pytest

from fastapi.testclient import TestClient

from src.fraudguard.api import app


# --------------------------------------------------
# TEST CLIENT
# --------------------------------------------------

@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client


# --------------------------------------------------
# ROOT TEST
# --------------------------------------------------

def test_root(client):

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message":
        "FraudGuard AI API is running"
    }


# --------------------------------------------------
# HEALTH TEST
# --------------------------------------------------

def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["model"] == "XGBoost"

    assert data["model_loaded"] is True

    assert (
        data["explainer_loaded"]
        is True
    )

    assert data["threshold"] == 0.40


# --------------------------------------------------
# MISSING FEATURES TEST
# --------------------------------------------------

def test_missing_features(client):

    response = client.post(
        "/predict",
        json={
            "Time": 100,
            "Amount": 500
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# NEGATIVE AMOUNT TEST
# --------------------------------------------------

def test_negative_amount(client):

    transaction = {
        "Time": 100,

        **{
            f"V{i}": 0.0
            for i in range(1, 29)
        },

        "Amount": -500
    }

    response = client.post(
        "/predict",
        json=transaction
    )

    assert response.status_code == 422


# --------------------------------------------------
# EXTRA FIELD TEST
# --------------------------------------------------

def test_extra_field(client):

    transaction = {
        "Time": 100,

        **{
            f"V{i}": 0.0
            for i in range(1, 29)
        },

        "Amount": 500,

        "RandomFeature": 123
    }

    response = client.post(
        "/predict",
        json=transaction
    )

    assert response.status_code == 422


# --------------------------------------------------
# EXPLAIN ENDPOINT TEST
# --------------------------------------------------

def test_explain(client):

    transaction = {
        "Time": 0.0,

        **{
            f"V{i}": 0.0
            for i in range(1, 29)
        },

        "Amount": 100.0
    }

    response = client.post(
        "/explain",
        json=transaction
    )

    assert response.status_code == 200

    data = response.json()

    # Check prediction fields
    assert "prediction" in data
    assert "label" in data
    assert "fraud_probability" in data
    assert "risk_level" in data
    assert "threshold" in data

    # Check explanation exists
    assert "explanation" in data

    explanation = (
        data["explanation"]
    )

    assert (
        "base_value"
        in explanation
    )

    assert (
        "top_features"
        in explanation
    )

    assert (
        "summary"
        in explanation
    )

    # Summary must be text
    assert isinstance(
        explanation["summary"],
        str
    )

    # We requested maximum 5
    # explanation features
    assert len(
        explanation["top_features"]
    ) <= 5

    # Validate each SHAP feature
    for feature in explanation[
        "top_features"
    ]:

        assert (
            "feature"
            in feature
        )

        assert (
            "feature_value"
            in feature
        )

        assert (
            "shap_value"
            in feature
        )

        assert (
            "impact"
            in feature
        )

        assert feature[
            "impact"
        ] in [
            "increases_fraud_score",
            "decreases_fraud_score",
            "neutral"
        ]


# --------------------------------------------------
# INVALID EXPLAIN REQUEST TEST
# --------------------------------------------------

def test_explain_invalid_transaction(
    client
):

    response = client.post(
        "/explain",
        json={
            "Time": 100,
            "Amount": -500
        }
    )

    assert response.status_code == 422

# --------------------------------------------------
# RETRIEVE ENDPOINT TEST
# --------------------------------------------------


def test_retrieve(client):

    response = client.post(
        "/retrieve",
        json={
            "query": (
                "Many small payment attempts "
                "failed within a short period."
            ),
            "top_k": 3
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "query" in data
    assert "top_k" in data
    assert "results" in data

    assert len(
        data["results"]
    ) == 3

    for result in data["results"]:

        assert "id" in result
        assert "title" in result
        assert "category" in result

        assert (
            "description"
            in result
        )

        assert (
            "similarity_score"
            in result
        )

        assert "source" in result

        assert (
            "source_url"
            in result
        )


# --------------------------------------------------
# EMPTY RETRIEVAL QUERY TEST
# --------------------------------------------------

def test_retrieve_empty_query(
    client
):

    response = client.post(
        "/retrieve",
        json={
            "query": "",
            "top_k": 3
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# INVALID TOP_K API TEST
# --------------------------------------------------

def test_retrieve_invalid_top_k(
    client
):

    response = client.post(
        "/retrieve",
        json={
            "query":
                "Suspicious payments",

            "top_k": 0
        }
    )

    assert response.status_code == 422
