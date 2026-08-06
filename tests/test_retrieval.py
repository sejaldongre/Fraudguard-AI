import pytest

from src.fraudguard.knowledge import (
    load_fraud_knowledge
)

from src.fraudguard.retrieval import (
    load_embedding_model,
    create_knowledge_embeddings,
    create_faiss_index,
    search_fraud_knowledge
)


@pytest.fixture(scope="module")
def retrieval_resources():

    knowledge = (
        load_fraud_knowledge()
    )

    embedding_model = (
        load_embedding_model()
    )

    embeddings = (
        create_knowledge_embeddings(
            embedding_model,
            knowledge
        )
    )

    index = (
        create_faiss_index(
            embeddings
        )
    )

    return {
        "knowledge": knowledge,
        "embedding_model":
            embedding_model,
        "index": index
    }


def test_knowledge_embeddings(
    retrieval_resources
):

    knowledge = retrieval_resources[
        "knowledge"
    ]

    embedding_model = (
        retrieval_resources[
            "embedding_model"
        ]
    )

    embeddings = (
        create_knowledge_embeddings(
            embedding_model,
            knowledge
        )
    )

    assert embeddings.shape[0] == (
        len(knowledge)
    )

    assert embeddings.shape[1] > 0


def test_faiss_index(
    retrieval_resources
):

    index = retrieval_resources[
        "index"
    ]

    knowledge = retrieval_resources[
        "knowledge"
    ]

    assert index.ntotal == len(
        knowledge
    )


def test_semantic_search(
    retrieval_resources
):

    results = search_fraud_knowledge(
        query=(
            "Someone gained unauthorized "
            "access to a customer's "
            "financial account."
        ),

        embedding_model=(
            retrieval_resources[
                "embedding_model"
            ]
        ),

        index=(
            retrieval_resources[
                "index"
            ]
        ),

        knowledge=(
            retrieval_resources[
                "knowledge"
            ]
        ),

        top_k=3
    )

    assert len(results) == 3

    for result in results:

        assert "title" in result
        assert "description" in result
        assert "similarity_score" in result
        assert "source" in result
        assert "source_url" in result


def test_empty_query(
    retrieval_resources
):

    with pytest.raises(
        ValueError
    ):

        search_fraud_knowledge(
            query="",

            embedding_model=(
                retrieval_resources[
                    "embedding_model"
                ]
            ),

            index=(
                retrieval_resources[
                    "index"
                ]
            ),

            knowledge=(
                retrieval_resources[
                    "knowledge"
                ]
            )
        )


def test_invalid_top_k(
    retrieval_resources
):
    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0"
    ):
        search_fraud_knowledge(
            query="Repeated suspicious payment attempts",

            embedding_model=(
                retrieval_resources[
                    "embedding_model"
                ]
            ),

            index=(
                retrieval_resources[
                    "index"
                ]
            ),

            knowledge=(
                retrieval_resources[
                    "knowledge"
                ]
            ),

            top_k=0
        )


def test_large_top_k(
    retrieval_resources
):
    knowledge = retrieval_resources[
        "knowledge"
    ]

    results = search_fraud_knowledge(
        query="Suspicious payment activity",

        embedding_model=(
            retrieval_resources[
                "embedding_model"
            ]
        ),

        index=(
            retrieval_resources[
                "index"
            ]
        ),

        knowledge=knowledge,

        top_k=100
    )

    assert len(results) == len(
        knowledge
    )
