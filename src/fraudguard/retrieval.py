import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

from .knowledge import knowledge_to_text


# --------------------------------------------------
# EMBEDDING MODEL CONFIGURATION
# --------------------------------------------------

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


# --------------------------------------------------
# LOAD EMBEDDING MODEL
# --------------------------------------------------

def load_embedding_model():
    """
    Load the Sentence Transformer model used
    to generate embeddings for fraud knowledge
    and search queries.
    """

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    return model


# --------------------------------------------------
# CREATE KNOWLEDGE EMBEDDINGS
# --------------------------------------------------

def create_knowledge_embeddings(
    embedding_model,
    knowledge: list[dict]
) -> np.ndarray:
    """
    Convert fraud knowledge documents into
    normalized embedding vectors.
    """

    if not knowledge:
        raise ValueError(
            "Knowledge base cannot be empty."
        )

    # Convert each structured knowledge document
    # into embedding-ready text
    texts = [
        knowledge_to_text(pattern)
        for pattern in knowledge
    ]

    # Generate normalized embeddings
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # FAISS expects float32 vectors
    embeddings = embeddings.astype(
        "float32"
    )

    return embeddings


# --------------------------------------------------
# CREATE FAISS INDEX
# --------------------------------------------------

def create_faiss_index(
    embeddings: np.ndarray
):
    """
    Create a FAISS inner-product index.

    Because our embeddings are normalized,
    inner product behaves like cosine similarity.
    """

    # Check that embeddings exist
    if embeddings.size == 0:
        raise ValueError(
            "Embeddings cannot be empty."
        )

    # Embeddings should have shape:
    # (number_of_documents, dimensions)
    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a "
            "2-dimensional array."
        )

    # Example:
    # (10, 384)
    #
    # 10  = documents
    # 384 = embedding dimensions

    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatIP(
        dimension
    )

    # Add knowledge embeddings
    index.add(
        embeddings
    )

    return index


# --------------------------------------------------
# SEARCH FRAUD KNOWLEDGE
# --------------------------------------------------

def search_fraud_knowledge(
    query: str,
    embedding_model,
    index,
    knowledge: list[dict],
    top_k: int = 3
) -> list[dict]:
    """
    Search the fraud knowledge base using
    semantic similarity.

    Returns the top matching fraud patterns
    together with their similarity scores
    and source information.
    """

    # --------------------------------------------------
    # VALIDATE QUERY
    # --------------------------------------------------

    if not isinstance(query, str):
        raise ValueError(
            "Search query must be a string."
        )

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    # --------------------------------------------------
    # VALIDATE KNOWLEDGE
    # --------------------------------------------------

    if not knowledge:
        raise ValueError(
            "Knowledge base cannot be empty."
        )

    # --------------------------------------------------
    # VALIDATE TOP_K
    # --------------------------------------------------

    if not isinstance(top_k, int):
        raise ValueError(
            "top_k must be an integer."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0."
        )

    # We cannot retrieve more documents
    # than actually exist.
    top_k = min(
        top_k,
        len(knowledge)
    )

    # --------------------------------------------------
    # CREATE QUERY EMBEDDING
    # --------------------------------------------------

    query_embedding = (
        embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
    )

    # FAISS expects float32
    query_embedding = (
        query_embedding.astype(
            "float32"
        )
    )

    # --------------------------------------------------
    # SEARCH FAISS
    # --------------------------------------------------

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    # --------------------------------------------------
    # BUILD RESULTS
    # --------------------------------------------------

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):

        # Defensive check.
        # FAISS can return -1 when a requested
        # neighbor is unavailable.
        if index_position < 0:
            continue

        pattern = knowledge[
            int(index_position)
        ]

        result = {
            "id": pattern["id"],

            "title": pattern["title"],

            "category": pattern[
                "category"
            ],

            "description": pattern[
                "description"
            ],

            "indicators": pattern[
                "indicators"
            ],

            "recommended_actions": pattern[
                "recommended_actions"
            ],

            "source": pattern[
                "source"
            ],

            "source_url": pattern[
                "source_url"
            ],

            "similarity_score": float(
                score
            )
        }

        results.append(
            result
        )

    return results
