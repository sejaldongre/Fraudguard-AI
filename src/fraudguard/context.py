def build_context_query(
    context: dict
) -> str:
    """
    Convert interpretable transaction context
    into natural-language text suitable for
    semantic retrieval.

    These signals are separate from the
    anonymized V1-V28 model features.
    """

    statements = []

    # ------------------------------------------
    # PAYMENT CHANNEL
    # ------------------------------------------

    payment_channel = context.get(
        "payment_channel"
    )

    if payment_channel:

        statements.append(
            f"The payment channel is "
            f"{payment_channel}."
        )

    # ------------------------------------------
    # TRANSACTION VELOCITY
    # ------------------------------------------

    transactions = context.get(
        "transactions_10m",
        0
    )

    if transactions == 1:

        statements.append(
            "There was 1 transaction "
            "within 10 minutes."
        )

    elif transactions > 1:

        statements.append(
            f"There were {transactions} "
            "transactions within "
            "10 minutes."
        )

    # ------------------------------------------
    # FAILED PAYMENT ATTEMPTS
    # ------------------------------------------

    failed_attempts = context.get(
        "failed_attempts_10m",
        0
    )

    if failed_attempts == 1:

        statements.append(
            "There was 1 failed payment "
            "attempt within 10 minutes."
        )

    elif failed_attempts > 1:

        statements.append(
            f"There were {failed_attempts} "
            "failed payment attempts "
            "within 10 minutes."
        )

    # ------------------------------------------
    # ACCOUNT ACCESS ANOMALY
    # ------------------------------------------

    if context.get(
        "account_access_anomaly",
        False
    ):

        statements.append(
            "Unexpected or unauthorized "
            "account access was observed."
        )

    # ------------------------------------------
    # PHISHING REPORT
    # ------------------------------------------

    if context.get(
        "customer_reported_phishing",
        False
    ):

        statements.append(
            "The customer reported receiving "
            "a suspicious phishing or "
            "impersonation message."
        )

    # ------------------------------------------
    # CARD NOT PRESENT
    # ------------------------------------------

    if context.get(
        "card_not_present",
        False
    ):

        statements.append(
            "The physical payment card was "
            "not present during the transaction."
        )

    # ------------------------------------------
    # MERCHANT MISMATCH
    # ------------------------------------------

    if context.get(
        "merchant_mismatch",
        False
    ):

        statements.append(
            "The payment activity appears "
            "inconsistent with the merchant's "
            "declared business activity."
        )

    # ------------------------------------------
    # NO USEFUL CONTEXT
    # ------------------------------------------

    if not statements:

        return (
            "No specific interpretable fraud "
            "context was provided."
        )

    return " ".join(
        statements
    )
