"""
FraudGuard semantic retrieval evaluation.

Evaluates the existing SentenceTransformer + FAISS
retrieval pipeline using labeled fraud-context queries.

Metrics:
- Hit@1
- Hit@3
- Mean Reciprocal Rank (MRR)
"""

from src.fraudguard.knowledge import load_fraud_knowledge
from src.fraudguard.retrieval import (
    load_embedding_model,
    create_knowledge_embeddings,
    create_faiss_index,
    search_fraud_knowledge,
)


# ============================================================
# EVALUATION DATASET
# ============================================================

EVALUATION_CASES = [
    {
        "name": "Card-Not-Present Fraud",
        "query": (
            "An online payment was made remotely and the "
            "physical payment card was not present during "
            "the transaction."
        ),
        "expected_id": "fraud_001",
    },
    {
        "name": "Account Takeover",
        "query": (
            "An unauthorized person gained access to a "
            "customer account and unexpected account "
            "activity was observed."
        ),
        "expected_id": "fraud_002",
    },
    {
        "name": "Card Testing",
        "query": (
            "There was a sudden spike in failed card "
            "payments with many repeated card validation "
            "attempts in a short period."
        ),
        "expected_id": "fraud_003",
    },
    {
        "name": "Identity Fraud",
        "query": (
            "Someone used another person's personal and "
            "financial information without permission to "
            "open accounts and make transactions."
        ),
        "expected_id": "fraud_004",
    },
    {
        "name": "Phishing and Social Engineering",
        "query": (
            "The customer received an urgent message "
            "impersonating a trusted organization and was "
            "asked to click a link and provide account "
            "information."
        ),
        "expected_id": "fraud_005",
    },
    {
        "name": "Transaction Velocity Abuse",
        "query": (
            "An unusually large number of payment attempts "
            "occurred within a very short period with "
            "rapid repeated transaction activity."
        ),
        "expected_id": "fraud_006",
    },
    {
        "name": "Stolen Payment Card Fraud",
        "query": (
            "A customer's compromised payment card details "
            "were used without the legitimate cardholder's "
            "permission to make suspicious payments."
        ),
        "expected_id": "fraud_007",
    },
    {
        "name": "Merchant Fraud",
        "query": (
            "A merchant shows suspicious transaction "
            "patterns, abnormal dispute activity, and "
            "possible involvement in fraudulent payments."
        ),
        "expected_id": "fraud_008",
    },
    {
        "name": "Transaction Laundering",
        "query": (
            "A merchant appears to be submitting payment "
            "transactions on behalf of another business "
            "and misrepresenting the source of the "
            "transactions."
        ),
        "expected_id": "fraud_009",
    },
    {
        "name": "Unauthorized Payment Fraud",
        "query": (
            "The legitimate cardholder does not recognize "
            "a completed payment and reports that the "
            "payment credentials were used without "
            "permission."
        ),
        "expected_id": "fraud_010",
    },
]


# ============================================================
# HELPER
# ============================================================

def find_rank(
    results: list[dict],
    expected_id: str,
):
    """
    Return the 1-based rank of the expected document.

    Returns None when the expected document does not
    appear in the retrieved results.
    """

    for rank, result in enumerate(
        results,
        start=1,
    ):
        if result["id"] == expected_id:
            return rank

    return None


# ============================================================
# EVALUATION
# ============================================================

def evaluate_retrieval():
    """
    Run labeled queries through FraudGuard's existing
    semantic retrieval pipeline and calculate Hit@1,
    Hit@3 and Mean Reciprocal Rank.
    """

    print("=" * 70)
    print("FraudGuard Semantic Retrieval Evaluation")
    print("=" * 70)

    # --------------------------------------------------------
    # Load knowledge
    # --------------------------------------------------------

    print("\nLoading fraud knowledge...")

    knowledge = load_fraud_knowledge()

    print(
        f"Loaded {len(knowledge)} "
        "knowledge documents."
    )

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    embedding_model = load_embedding_model()

    # --------------------------------------------------------
    # Build embeddings + FAISS index
    # --------------------------------------------------------

    print("Creating knowledge embeddings...")

    embeddings = create_knowledge_embeddings(
        embedding_model,
        knowledge,
    )

    print(
        "Embedding matrix shape:",
        embeddings.shape,
    )

    print("Creating FAISS index...")

    index = create_faiss_index(
        embeddings
    )

    print(
        f"FAISS documents indexed: "
        f"{index.ntotal}"
    )

    # --------------------------------------------------------
    # Metric counters
    # --------------------------------------------------------

    hit_at_1 = 0
    hit_at_3 = 0
    reciprocal_rank_total = 0.0

    # --------------------------------------------------------
    # Evaluate each query
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("Individual Retrieval Results")
    print("=" * 70)

    for case_number, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):

        # Retrieve all documents so MRR can determine
        # the exact rank of the expected document.
        results = search_fraud_knowledge(
            query=case["query"],
            embedding_model=embedding_model,
            index=index,
            knowledge=knowledge,
            top_k=len(knowledge),
        )

        rank = find_rank(
            results,
            case["expected_id"],
        )

        if rank == 1:
            hit_at_1 += 1

        if rank is not None and rank <= 3:
            hit_at_3 += 1

        if rank is not None:
            reciprocal_rank_total += (
                1.0 / rank
            )

        top_result = results[0]

        print(
            f"\n[{case_number}] "
            f"{case['name']}"
        )

        print(
            f"Expected : "
            f"{case['expected_id']}"
        )

        print(
            f"Top Match: "
            f"{top_result['id']} - "
            f"{top_result['title']}"
        )

        print(
            f"Score    : "
            f"{top_result['similarity_score']:.4f}"
        )

        if rank is None:
            print(
                "Rank     : NOT RETRIEVED"
            )
        else:
            print(
                f"Rank     : {rank}"
            )

        # Show top 3 for debugging / interpretation.
        print("Top 3:")

        for result_rank, result in enumerate(
            results[:3],
            start=1,
        ):
            marker = (
                "*"
                if result["id"]
                == case["expected_id"]
                else " "
            )

            print(
                f"  {marker}#{result_rank} "
                f"{result['id']} - "
                f"{result['title']} "
                f"({result['similarity_score']:.4f})"
            )

    # --------------------------------------------------------
    # Final metrics
    # --------------------------------------------------------

    total_cases = len(
        EVALUATION_CASES
    )

    hit_1_score = (
        hit_at_1 / total_cases
    )

    hit_3_score = (
        hit_at_3 / total_cases
    )

    mrr = (
        reciprocal_rank_total
        / total_cases
    )

    print("\n" + "=" * 70)
    print("Final Retrieval Metrics")
    print("=" * 70)

    print(
        f"Evaluation Cases : "
        f"{total_cases}"
    )

    print(
        f"Hit@1            : "
        f"{hit_at_1}/{total_cases} "
        f"({hit_1_score:.2%})"
    )

    print(
        f"Hit@3            : "
        f"{hit_at_3}/{total_cases} "
        f"({hit_3_score:.2%})"
    )

    print(
        f"MRR              : "
        f"{mrr:.4f}"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    evaluate_retrieval()
