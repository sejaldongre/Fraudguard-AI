import numpy as np
import faiss

from fastembed import TextEmbedding

from .knowledge import knowledge_to_text


# --------------------------------------------------
# EMBEDDING MODEL CONFIGURATION
# --------------------------------------------------

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


# --------------------------------------------------
# FASTEMBED WRAPPER
# --------------------------------------------------

class FraudGuardEmbeddingModel:
    """
    Lightweight embedding adapter for FraudGuard.

    Uses FastEmbed/ONNX Runtime instead of
    Sentence Transformers/PyTorch so the API can
    run within Render's memory-constrained instance.
    """

    def __init__(self):
        self.model = TextEmbedding(
            model_name=EMBEDDING_MODEL_NAME,
            threads=1,
            lazy_load=True,
        )

    def encode(
        self,
        texts,
        normalize_embeddings=True,
        is_query=False,
        **kwargs,
    ) -> np.ndarray:
        """
        Generate embeddings with a SentenceTransformer-like
        interface so the rest of FraudGuard does not need
        to change.
        """

        texts = list(texts)

        if is_query:
            embeddings = list(
                self.model.query_embed(texts)
            )
        else:
            embeddings = list(
                self.model.passage_embed(texts)
            )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        if normalize_embeddings:
            norms = np.linalg.norm(
                embeddings,
                axis=1,
                keepdims=True,
            )
            embeddings = embeddings / np.maximum(
                norms,
                1e-12,
            )

        return embeddings


# --------------------------------------------------
# LOAD EMBEDDING MODEL
# --------------------------------------------------

def load_embedding_model():
    """
    Load the lightweight FastEmbed model used to
    generate embeddings for fraud knowledge and
    search queries.
    """

    return FraudGuardEmbeddingModel()


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

    texts = [
        knowledge_to_text(pattern)
        for pattern in knowledge
    ]

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        is_query=False,
    )

    return embeddings.astype("float32")


# --------------------------------------------------
# CREATE FAISS INDEX
# --------------------------------------------------

def create_faiss_index(
    embeddings: np.ndarray
):
    """
    Create a FAISS inner-product index.

    Because embeddings are normalized,
    inner product behaves like cosine similarity.
    """

    if embeddings.size == 0:
        raise ValueError(
            "Embeddings cannot be empty."
        )

    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2-dimensional array."
        )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

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
    """

    if not isinstance(query, str):
        raise ValueError(
            "Search query must be a string."
        )

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    if not knowledge:
        raise ValueError(
            "Knowledge base cannot be empty."
        )

    if not isinstance(top_k, int):
        raise ValueError(
            "top_k must be an integer."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0."
        )

    top_k = min(top_k, len(knowledge))

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        is_query=True,
    )

    query_embedding = query_embedding.astype("float32")

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0],
    ):
        if index_position < 0:
            continue

        pattern = knowledge[int(index_position)]

        result = {
            "id": pattern["id"],
            "title": pattern["title"],
            "category": pattern["category"],
            "description": pattern["description"],
            "indicators": pattern["indicators"],
            "recommended_actions": pattern["recommended_actions"],
            "source": pattern["source"],
            "source_url": pattern["source_url"],
            "similarity_score": float(score),
        }

        results.append(result)

    return results
