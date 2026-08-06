from .context import build_context_query

from .retrieval import (
    search_fraud_knowledge
)

from .rag import (
    generate_fraud_report
)


def analyze_transaction(
    prediction: dict,
    explanation: dict,
    context: dict,
    embedding_model,
    faiss_index,
    knowledge: list[dict],
    llm_client,
    top_k: int = 3
) -> dict:
    """
    Combine:

    1. ML fraud prediction
    2. SHAP explanation
    3. Transaction context
    4. FAISS fraud-knowledge retrieval
    5. Grounded LLM analyst report

    into one complete FraudGuard analysis.
    """

    # ==================================================
    # 1. BUILD SEMANTIC CONTEXT QUERY
    # ==================================================

    context_query = build_context_query(
        context
    )

    # ==================================================
    # 2. RETRIEVE RELEVANT FRAUD KNOWLEDGE
    # ==================================================

    retrieved_knowledge = (
        search_fraud_knowledge(
            query=context_query,
            embedding_model=embedding_model,
            index=faiss_index,
            knowledge=knowledge,
            top_k=top_k
        )
    )

    # ==================================================
    # 3. GENERATE GROUNDED LLM REPORT
    # ==================================================

    report = generate_fraud_report(
        client=llm_client,
        prediction=prediction,
        explanation=explanation,
        context_query=context_query,
        retrieved_knowledge=retrieved_knowledge
    )

    # ==================================================
    # 4. RETURN COMPLETE ANALYSIS
    # ==================================================

    return {
        "prediction": prediction,
        "explanation": explanation,
        "context_query": context_query,
        "retrieved_knowledge": retrieved_knowledge,
        "analyst_report": report
    }
