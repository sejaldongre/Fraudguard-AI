from src.fraudguard.context import (
    build_context_query
)


def test_context_query():

    context = {
        "payment_channel": "online",
        "transactions_10m": 12,
        "failed_attempts_10m": 8,
        "account_access_anomaly": False,
        "customer_reported_phishing": False,
        "card_not_present": True,
        "merchant_mismatch": False
    }

    query = build_context_query(
        context
    )

    assert "online" in query

    assert (
        "12 transactions"
        in query
    )

    assert (
        "8 failed payment attempts"
        in query
    )

    assert (
        "physical payment card"
        in query
    )


def test_account_anomaly_context():

    context = {
        "account_access_anomaly": True
    }

    query = build_context_query(
        context
    )

    assert (
        "unauthorized account access"
        in query
    )


def test_phishing_context():

    context = {
        "customer_reported_phishing":
            True
    }

    query = build_context_query(
        context
    )

    assert "phishing" in query


def test_empty_context():

    context = {}

    query = build_context_query(
        context
    )

    assert (
        "No specific interpretable "
        "fraud context was provided."
        == query
    )
