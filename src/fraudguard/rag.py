from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CREATE LLM CLIENT
# ============================================================

def create_llm_client() -> Groq:
    """
    Create the Groq client used by FraudGuard.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    return Groq(api_key=api_key)


# ============================================================
# RISK-AWARE ANALYSIS MODE
# ============================================================

def determine_analysis_mode(
    prediction: dict[str, Any],
) -> str:
    """
    Determine how retrieved fraud knowledge should be
    interpreted.

    This does NOT modify the ML prediction or threshold.
    It only controls how the LLM reasons about the
    retrieved knowledge.
    """

    label = str(
        prediction.get("label", "")
    ).strip().lower()

    risk_level = str(
        prediction.get("risk_level", "")
    ).strip().upper()

    probability = float(
        prediction.get(
            "fraud_probability",
            0.0,
        )
    )

    if (
        label == "fraud"
        or risk_level == "HIGH"
    ):
        return "fraud_investigation"

    if (
        risk_level == "MEDIUM"
        or probability >= 0.20
    ):
        return "cautious_review"

    return "low_risk_review"


# ============================================================
# FORMAT SHAP EVIDENCE
# ============================================================

def _format_model_evidence(
    explanation: dict[str, Any],
) -> str:
    """
    Convert SHAP explanation output into clean evidence
    text for the LLM.
    """

    top_features = explanation.get(
        "top_features",
        [],
    )

    if not top_features:
        return "No SHAP feature evidence was supplied."

    lines: list[str] = []

    for feature in top_features:

        feature_name = feature.get(
            "feature",
            "Unknown",
        )

        feature_value_raw = feature.get(
            "feature_value",
            "Unknown",
        )

        shap_value_raw = feature.get(
            "shap_value",
            "Unknown",
        )

        impact = feature.get(
            "impact",
            "Unknown",
        )

        try:
            feature_value = (
                f"{float(feature_value_raw):.3f}"
            )
        except (TypeError, ValueError):
            feature_value = str(feature_value_raw)

        try:
            shap_value = (
                f"{float(shap_value_raw):+.3f}"
            )
        except (TypeError, ValueError):
            shap_value = str(shap_value_raw)

        lines.append(
            (
                f"- Feature: {feature_name}\n"
                f"  Feature value: {feature_value}\n"
                f"  SHAP contribution: {shap_value}\n"
                f"  Impact: {impact}"
            )
        )

    return "\n".join(lines)


# ============================================================
# FORMAT RETRIEVED KNOWLEDGE
# ============================================================

def _format_retrieved_knowledge(
    retrieved_knowledge: list[dict[str, Any]],
) -> str:
    """
    Convert FAISS retrieval results into grounded
    knowledge text for the LLM.
    """

    if not retrieved_knowledge:
        return (
            "No fraud knowledge documents were retrieved."
        )

    sections: list[str] = []

    for index, document in enumerate(
        retrieved_knowledge,
        start=1,
    ):

        title = document.get(
            "title",
            "Unknown",
        )

        category = document.get(
            "category",
            "Unknown",
        )

        description = document.get(
            "description",
            "",
        )

        indicators = document.get(
            "indicators",
            [],
        )

        recommended_actions = document.get(
            "recommended_actions",
            [],
        )

        source = document.get(
            "source",
            "Unknown",
        )

        source_url = document.get(
            "source_url",
            "",
        )

        similarity_raw = document.get(
            "similarity_score",
            0.0,
        )

        try:
            similarity_score = (
                f"{float(similarity_raw) * 100:.1f}%"
            )
        except (TypeError, ValueError):
            similarity_score = str(similarity_raw)

        if indicators:
            indicator_text = "\n".join(
                f"- {indicator}"
                for indicator in indicators
            )
        else:
            indicator_text = (
                "- No indicators supplied"
            )

        if recommended_actions:
            action_text = "\n".join(
                f"- {action}"
                for action in recommended_actions
            )
        else:
            action_text = (
                "- No recommended actions supplied"
            )

        sections.append(
            f"""
DOCUMENT {index}

Title:
{title}

Category:
{category}

Description:
{description}

Indicators:
{indicator_text}

Recommended actions:
{action_text}

Source:
{source}

Source URL:
{source_url}

Semantic similarity score:
{similarity_score}
""".strip()
        )

    return (
        "\n\n"
        "----------------------------------------"
        "\n\n"
    ).join(sections)


# ============================================================
# BUILD RAG PROMPT
# ============================================================

def build_rag_prompt(
    prediction: dict[str, Any],
    explanation: dict[str, Any],
    context_query: str,
    retrieved_knowledge: list[dict[str, Any]],
) -> str:
    """
    Build the grounded, risk-aware FraudGuard prompt.
    """

    analysis_mode = determine_analysis_mode(
        prediction
    )

    model_evidence = _format_model_evidence(
        explanation
    )

    knowledge_text = _format_retrieved_knowledge(
        retrieved_knowledge
    )

    # ========================================================
    # MODEL PREDICTION VALUES
    # ========================================================

    label = prediction.get(
        "label",
        "Unknown",
    )

    probability_raw = prediction.get(
        "fraud_probability",
        0.0,
    )

    risk_level = prediction.get(
        "risk_level",
        "Unknown",
    )

    threshold_raw = prediction.get(
        "threshold",
        "Unknown",
    )

    try:
        probability = (
            f"{float(probability_raw) * 100:.2f}%"
        )
    except (TypeError, ValueError):
        probability = str(probability_raw)

    try:
        threshold = (
            f"{float(threshold_raw) * 100:.0f}%"
        )
    except (TypeError, ValueError):
        threshold = str(threshold_raw)

    # ========================================================
    # SHAP EXPLANATION VALUES
    # ========================================================

    base_value_raw = explanation.get(
        "base_value",
        "Unknown",
    )

    try:
        base_value = (
            f"{float(base_value_raw):.3f}"
        )
    except (TypeError, ValueError):
        base_value = str(base_value_raw)

    explanation_summary = explanation.get(
        "summary",
        "",
    )

    # ========================================================
    # MAIN PROMPT
    # ========================================================

    prompt = f"""
You are FraudGuard AI, an assistant supporting a human
financial-fraud analyst.

Generate a careful, concise and grounded fraud-analysis
report using ONLY the evidence supplied below.

The report is displayed inside a professional fraud
investigation dashboard.

Your response MUST therefore be easy to scan visually.

Use short paragraphs, Markdown headings and bullet points.

Never produce large walls of text.


============================================================
EVIDENCE SOURCES
============================================================

Keep these four evidence sources separate:

1. Machine-learning prediction
2. SHAP model explanation
3. Supplied transaction context
4. Retrieved fraud-domain knowledge

Never invent relationships between these evidence sources.


============================================================
ANALYSIS MODE
============================================================

{analysis_mode}


============================================================
MODEL PREDICTION
============================================================

Prediction label:
{label}

Fraud probability:
{probability}

Risk level:
{risk_level}

Decision threshold:
{threshold}


============================================================
MODEL EXPLANATION
============================================================

SHAP base value:
{base_value}

Top SHAP features:

{model_evidence}

Explanation summary:

{explanation_summary}


============================================================
SUPPLIED TRANSACTION CONTEXT
============================================================

{context_query}


============================================================
RETRIEVED FRAUD KNOWLEDGE
============================================================

{knowledge_text}


============================================================
CORE INTERPRETATION RULE
============================================================

The machine-learning prediction is the primary
transaction-level risk signal.

Retrieved fraud documents are reference knowledge.

Retrieving a fraud document does NOT mean that the fraud
pattern occurred.

Semantic similarity is NOT fraud probability.

Compare the supplied transaction context with the
indicators in the retrieved knowledge before claiming
that a pattern aligns with the transaction.


============================================================
RISK-AWARE ANALYSIS POLICY
============================================================


-----------------------------
FRAUD INVESTIGATION MODE
-----------------------------

If ANALYSIS MODE is:

fraud_investigation

then:

- Treat the model result as high-risk evidence.

- Compare supplied contextual signals against retrieved
  fraud indicators.

- Clearly explain which patterns align with the supplied
  context.

- Use cautious language such as:

  "consistent with"

  "aligns with"

  "partially aligns with"

  "may indicate"

  "could be associated with"

- Never claim that a fraud technique has been proven.

- Recommend controls only when they are BOTH:

  1. supported by retrieved knowledge

  AND

  2. relevant to the supplied context.


-----------------------------
CAUTIOUS REVIEW MODE
-----------------------------

If ANALYSIS MODE is:

cautious_review

then:

- Treat the model result as uncertain or borderline.

- Carefully compare context with retrieved indicators.

- Clearly distinguish matching and non-matching
  indicators.

- Do not recommend aggressive fraud intervention simply
  because a fraud document was retrieved.

- Prefer proportionate review or monitoring where
  supported.


-----------------------------
LOW RISK REVIEW MODE
-----------------------------

If ANALYSIS MODE is:

low_risk_review

then:

- Start from the fact that the model classified the
  transaction as legitimate / low risk.

- Retrieved fraud documents are ONLY reference knowledge.

- Check whether supplied contextual signals contradict
  the low-risk model result.

- Do NOT imply that a fraud pattern exists simply because
  FAISS retrieved a related document.

- If no meaningful contextual match exists, explicitly
  state:

  "No strong fraud-pattern alignment was identified from
  the supplied context."

- Do NOT recommend blocking, CAPTCHA, additional
  authentication, rate limiting, account suspension,
  card blocking or manual fraud investigation unless the
  supplied context itself supports such action.

- Do NOT copy generic recommendations from retrieved
  documents when their indicators are absent.

- For clearly legitimate transactions without meaningful
  contextual warning signs, explicitly state:

  "No fraud-specific intervention is indicated based on
  the available evidence."


============================================================
GROUNDING RULES
============================================================

RULE 1 — ANONYMIZED FEATURES

V1-V28 are anonymized transformed variables.

Their real-world meanings are unknown.

Never assign business meanings to V1-V28.

Never say that a V feature represents:

- device behavior
- card behavior
- location
- merchant information
- payment channel
- customer behavior
- account behavior
- fraud technique
- IP information
- authentication behavior

or any other real-world concept.


RULE 2 — SHAP

SHAP values explain how the model used each feature.

They do NOT explain why fraud occurred.

They do NOT identify a fraud technique.


RULE 3 — CONTEXT

Transaction context is separate from V1-V28.

Never claim contextual information was inferred from
the anonymized features.


RULE 4 — RETRIEVAL

Retrieved fraud documents are reference knowledge.

Retrieval does NOT prove applicability.


RULE 5 — SIMILARITY SCORE

Similarity scores represent semantic relevance.

They are NOT fraud probabilities.

For example:

53.9% semantic similarity

does NOT mean:

53.9% probability of that fraud technique.


RULE 6 — NO INVENTED ATTRIBUTES

Never invent:

- merchant details
- device fingerprint
- IP address
- geolocation
- customer history
- cardholder confirmation
- authentication outcome
- transaction history

unless explicitly supplied.


RULE 7 — FRAUD PATTERN CLAIMS

Never claim that a particular fraud technique definitely
occurred unless supplied evidence establishes it.


RULE 8 — RECOMMENDATIONS

Every recommendation must satisfy BOTH:

1. Supported by retrieved fraud knowledge.

2. Relevant to supplied transaction context.


RULE 9 — LOW-RISK TRANSACTIONS

For low-risk transactions, do not generate fraud-control
recommendations merely because they appear in retrieved
documents.


RULE 10 — MODEL VS CONTEXT

Do not contradict the model prediction unless supplied
context contains evidence justifying the concern.


RULE 11 — DOCUMENT TITLES

A retrieved document title is NOT transaction evidence.


RULE 12 — NO FABRICATION

Never fabricate:

- model values
- SHAP values
- fraud indicators
- contextual signals
- recommendations
- sources
- fraud techniques


============================================================
REQUIRED MARKDOWN REPORT FORMAT
============================================================

Return CLEAN MARKDOWN.

Use exactly these five section headings and exactly this
order:

## Risk Assessment

## Model Evidence

## Relevant Fraud Context

## Recommended Actions

## Limitations


============================================================
DISPLAY RULES
============================================================

The response will be rendered using ReactMarkdown inside
the FraudGuard dashboard.

Therefore:

- Use the exact Markdown headings shown above.
- Keep paragraphs short.
- Use bullet points for scan-friendly information.
- Do not create large blocks of text.
- Do not use Markdown tables.
- Do not use HTML.
- Do not use code blocks.
- Do not add extra sections.
- Do not write an introduction before Risk Assessment.
- Do not write a conclusion after Limitations.
- Do not repeat information unnecessarily.
- Prefer fraud-pattern titles instead of saying only
  "DOCUMENT 1", "DOCUMENT 2", etc.


============================================================
SECTION 1 — RISK ASSESSMENT
============================================================

Use:

## Risk Assessment

Write ONE short paragraph.

Include:

- model prediction
- fraud probability
- risk level
- decision threshold where useful
- overall interpretation

Important values may be emphasized using Markdown bold.

Example style:

"The model classified this transaction as **Fraud** with
a fraud probability of **98.86%**. The assigned risk level
is **HIGH**, exceeding the **40%** decision threshold.
The transaction should therefore be treated as high-risk
evidence."

Do NOT copy the example unless it matches the supplied
evidence.

For low-risk transactions clearly state that the model
classified the transaction as legitimate / low risk.


============================================================
SECTION 2 — MODEL EVIDENCE
============================================================

Use:

## Model Evidence

Start with ONE short sentence.

Then show each important SHAP feature as a separate
Markdown bullet.

Preferred structure:

- **V17** — value `-2.830` · SHAP `+3.201` · increases fraud score
- **V14** — value `-4.289` · SHAP `+2.479` · increases fraud score
- **V10** — value `-2.772` · SHAP `+2.163` · increases fraud score

Each bullet must include:

- feature name
- feature value
- SHAP contribution
- whether it increases or decreases the model fraud score

After the feature bullets add this as a separate
blockquote-style note:

> **Interpretation note:** V1-V28 are anonymized
> transformed variables; their real-world meanings are
> unknown.

Never place this note inside the final SHAP feature
bullet.

Never assign real-world meanings to V1-V28.


============================================================
SECTION 3 — RELEVANT FRAUD CONTEXT
============================================================

Use:

## Relevant Fraud Context

Do NOT create one long paragraph.

First write this subheading on its own line:

**Supplied Contextual Signals**

Leave one blank line after the subheading.

Then list each supplied contextual signal as a separate
Markdown bullet.

After the final contextual-signal bullet, leave one blank
line.

Then write this subheading on its own line:

**Fraud-Pattern Alignment**

Leave one blank line after the subheading.

Then list each fraud-pattern comparison as a separate
Markdown bullet.

IMPORTANT:

- Never place "Fraud-Pattern Alignment" on the same line
  as a contextual-signal bullet.
- Never place a fraud-pattern comparison inside a
  contextual-signal bullet.
- Every bullet must end before the next subheading begins.
- Leave a blank line before and after each subheading.

For a low-risk transaction with no meaningful contextual
matches include:

After all fraud-pattern bullets, leave one blank line.

For a low-risk transaction with no meaningful contextual
matches, write this as its OWN final bullet:

- **Overall alignment:** No strong fraud-pattern alignment
  was identified from the supplied context.

Never append "Overall alignment" to the preceding bullet.

============================================================
SECTION 4 — RECOMMENDED ACTIONS
============================================================

Use:

## Recommended Actions

Every recommendation must be a separate Markdown bullet.

Use short, action-oriented wording.

Preferred structure:

- **Apply additional verification** before approving the
  suspicious payment.

- **Review related transaction activity** for repeated
  suspicious attempts.

- **Use applicable fraud controls** supported by the
  retrieved knowledge and supplied context.

Every action must be supported by BOTH:

1. supplied transaction context
2. retrieved fraud knowledge

For high-risk transactions:

Provide relevant fraud-control actions where supported.

For cautious-review transactions:

Provide proportionate monitoring or review where
supported.

For low-risk transactions without meaningful warning
signals use:

- **No fraud-specific intervention indicated** — the
  available evidence does not support additional
  fraud-control action.

Do not invent recommendations just to fill the section.


============================================================
SECTION 5 — LIMITATIONS
============================================================

Use:

## Limitations

Every limitation must be a separate Markdown bullet.

Use concise language.

Include relevant limitations using this style:

- **Anonymized features:** V1-V28 have no known real-world
  interpretation.

- **SHAP scope:** SHAP explains model influence, not the
  underlying cause of fraud.

- **Context completeness:** Supplied contextual information
  may be incomplete.

- **Retrieval scope:** Semantic retrieval finds related
  knowledge rather than confirmed fraud types.

- **Evidence boundary:** Retrieved knowledge does not prove
  that a specific fraud technique occurred.

Do not combine all limitations into one paragraph.


============================================================
NUMERIC FORMATTING
============================================================

Use clean, reader-friendly numeric formatting.

Fraud probability:

- Express as percentage.
- Maximum 2 decimal places.
- Example: 98.86%

Decision threshold:

- Express as percentage.
- Maximum 2 decimal places.
- Example: 40%

SHAP values:

- Maximum 3 decimal places.
- Preserve positive or negative sign.
- Examples: +3.201 or -1.427

Feature values:

- Maximum 3 decimal places.

Semantic similarity:

- Express as percentage when mentioned.
- Maximum 1 decimal place.
- Example: 53.9%
- Never call semantic similarity fraud probability.

Do not reproduce unnecessary floating-point precision.


============================================================
FINAL INSTRUCTIONS
============================================================

Use evidence-based language.

Be concise but useful.

Optimize the response for a fraud analyst scanning a
dashboard.

Use Markdown bullets wherever they improve readability.

Highlight important labels and values using **bold**
sparingly.

Do not exaggerate risk.

Do not minimize supported risk.

Never invent facts.

Never assign meanings to V1-V28.

Never interpret similarity score as fraud probability.

Never recommend controls unsupported by supplied
transaction context.

Follow the exact report structure.

Generate the analyst report now.
""".strip()

    return prompt


# ============================================================
# GENERATE FRAUD REPORT
# ============================================================

def generate_fraud_report(
    client: Groq,
    prediction: dict[str, Any],
    explanation: dict[str, Any],
    context_query: str,
    retrieved_knowledge: list[dict[str, Any]],
    model: str | None = None,
) -> str:
    """
    Generate a grounded FraudGuard analyst report.

    This function name is preserved because analyze.py
    imports generate_fraud_report.
    """

    prompt = build_rag_prompt(
        prediction=prediction,
        explanation=explanation,
        context_query=context_query,
        retrieved_knowledge=retrieved_knowledge,
    )

    model_name = (
        model
        or os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )
    )

    response = client.chat.completions.create(
        model=model_name,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful financial-fraud "
                    "analysis assistant. "
                    "Follow all grounding and risk-aware "
                    "instructions exactly. "
                    "Never invent meanings for anonymized "
                    "model features. "
                    "Use concise reader-friendly numeric "
                    "formatting. "
                    "Return clean Markdown designed for a "
                    "financial fraud investigation dashboard. "
                    "Use the exact requested section headings. "
                    "Prefer structured bullet points and short "
                    "paragraphs over dense prose."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=0.1,

        max_tokens=1600,
    )

    if not response.choices:
        raise RuntimeError(
            "The LLM returned no response."
        )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise RuntimeError(
            "The LLM returned an empty analyst report."
        )

    return content.strip()


# ============================================================
# BACKWARD-COMPATIBLE ALIAS
# ============================================================

def generate_analyst_report(
    prediction: dict[str, Any],
    explanation: dict[str, Any],
    context_query: str,
    retrieved_knowledge: list[dict[str, Any]],
    client: Groq | None = None,
    model: str | None = None,
) -> str:
    """
    Compatibility wrapper for older tests or scripts.
    """

    if client is None:
        client = create_llm_client()

    return generate_fraud_report(
        client=client,
        prediction=prediction,
        explanation=explanation,
        context_query=context_query,
        retrieved_knowledge=retrieved_knowledge,
        model=model,
    )
