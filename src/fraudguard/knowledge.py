import json
from pathlib import Path


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


KNOWLEDGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "knowledge"
    / "fraud_patterns.json"
)


# --------------------------------------------------
# REQUIRED KNOWLEDGE FIELDS
# --------------------------------------------------

REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "description",
    "indicators",
    "recommended_actions",
    "source",
    "source_url"
}


# --------------------------------------------------
# KNOWLEDGE VALIDATION
# --------------------------------------------------

def validate_knowledge(
    knowledge: list[dict]
) -> None:
    """
    Validate fraud knowledge-base documents
    before they are used by the RAG pipeline.
    """

    # Knowledge base should not be empty
    if not knowledge:
        raise ValueError(
            "Knowledge base is empty."
        )

    # Store IDs so we can detect duplicates
    ids = set()

    for pattern in knowledge:

        # ------------------------------------------
        # Check required fields
        # ------------------------------------------

        missing_fields = (
            REQUIRED_FIELDS
            - pattern.keys()
        )

        if missing_fields:
            raise ValueError(
                "Knowledge pattern is "
                "missing fields: "
                f"{missing_fields}"
            )

        # ------------------------------------------
        # Validate ID
        # ------------------------------------------

        if not pattern["id"].strip():
            raise ValueError(
                "Knowledge pattern ID "
                "cannot be empty."
            )

        # ------------------------------------------
        # Check duplicate IDs
        # ------------------------------------------

        if pattern["id"] in ids:
            raise ValueError(
                "Duplicate knowledge ID: "
                f"{pattern['id']}"
            )

        ids.add(
            pattern["id"]
        )

        # ------------------------------------------
        # Validate title
        # ------------------------------------------

        if not pattern["title"].strip():
            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has an empty title."
            )

        # ------------------------------------------
        # Validate category
        # ------------------------------------------

        if not pattern["category"].strip():
            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has an empty category."
            )

        # ------------------------------------------
        # Validate description
        # ------------------------------------------

        if not pattern[
            "description"
        ].strip():

            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has an empty description."
            )

        # ------------------------------------------
        # Validate indicators
        # ------------------------------------------

        if not isinstance(
            pattern["indicators"],
            list
        ):
            raise ValueError(
                f"Indicators for "
                f"{pattern['id']} "
                "must be a list."
            )

        if not pattern["indicators"]:
            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has no indicators."
            )

        # ------------------------------------------
        # Validate recommended actions
        # ------------------------------------------

        if not isinstance(
            pattern[
                "recommended_actions"
            ],
            list
        ):
            raise ValueError(
                f"Recommended actions for "
                f"{pattern['id']} "
                "must be a list."
            )

        if not pattern[
            "recommended_actions"
        ]:
            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has no recommended actions."
            )

        # ------------------------------------------
        # Validate source
        # ------------------------------------------

        if not pattern["source"].strip():
            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has no source."
            )

        # ------------------------------------------
        # Validate source URL
        # ------------------------------------------

        if not pattern[
            "source_url"
        ].strip():

            raise ValueError(
                f"Knowledge pattern "
                f"{pattern['id']} "
                "has no source URL."
            )


# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------

def load_fraud_knowledge() -> list[dict]:
    """
    Load and validate fraud-pattern documents
    from the local JSON knowledge base.
    """

    # Make sure the file exists
    if not KNOWLEDGE_PATH.exists():

        raise FileNotFoundError(
            "Knowledge base not found: "
            f"{KNOWLEDGE_PATH}"
        )

    # Read JSON
    with open(
        KNOWLEDGE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        knowledge = json.load(
            file
        )

    # Make sure top-level JSON is a list
    if not isinstance(
        knowledge,
        list
    ):
        raise ValueError(
            "Knowledge base must "
            "contain a JSON list."
        )

    # Validate before returning
    validate_knowledge(
        knowledge
    )

    return knowledge


# --------------------------------------------------
# CONVERT KNOWLEDGE TO EMBEDDING TEXT
# --------------------------------------------------

def knowledge_to_text(
    pattern: dict
) -> str:
    """
    Convert one structured fraud-pattern document
    into text suitable for generating embeddings.
    """

    indicators = "; ".join(
        pattern["indicators"]
    )

    actions = "; ".join(
        pattern[
            "recommended_actions"
        ]
    )

    text = (
        f"Fraud pattern: "
        f"{pattern['title']}. "

        f"Category: "
        f"{pattern['category']}. "

        f"Description: "
        f"{pattern['description']} "

        f"Common indicators: "
        f"{indicators}. "

        f"Recommended actions: "
        f"{actions}."
    )

    return text
