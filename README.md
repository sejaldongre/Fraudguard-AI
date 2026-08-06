# 🛡️ FraudGuard AI

### Explainable Fraud Detection with XGBoost, SHAP, Semantic Retrieval, and Grounded Generative AI

FraudGuard AI is an end-to-end fraud analysis system that combines **machine learning**, **explainable AI**, **semantic retrieval**, and **grounded generative AI** to detect suspicious transactions and provide interpretable evidence for fraud investigation.

Instead of returning only a fraud probability, FraudGuard provides multiple layers of analysis:

- 🧠 **XGBoost** predicts transaction fraud risk.
- 📊 **SHAP** explains which anonymized transaction features influenced the prediction.
- 🔎 **Sentence Transformers + FAISS** retrieve relevant fraud patterns from a curated knowledge base.
- 🤖 **Grounded Generative AI** combines model evidence, supplied transaction context, and retrieved fraud knowledge into a structured analyst report.
- 💻 **Next.js dashboard** provides an interactive interface for exploring fraud and legitimate scenarios.

The system is designed as a **decision-support tool for fraud investigation**, not as a replacement for human analysts.

---

## ✨ Key Features

### 🧠 Machine Learning Fraud Detection

FraudGuard uses a trained **XGBoost classifier** to estimate the probability that a transaction is fraudulent.

The model receives:

- `Time`
- `Amount`
- anonymized transformed features `V1-V28`

The contextual fraud signals used by the RAG system remain separate from these model features.

---

### 📊 Explainable AI with SHAP

Every prediction is accompanied by a SHAP explanation showing which features contributed most strongly to the model's fraud score.

Example:

```text
V17 → increases fraud score
V14 → increases fraud score
V10 → increases fraud score
V4  → increases fraud score
V12 → increases fraud score
```

Because `V1-V28` are anonymized transformed variables, FraudGuard does not assign unsupported real-world meanings to them.

---

### 🔎 Semantic Fraud Knowledge Retrieval

FraudGuard converts interpretable transaction context into a natural-language retrieval query.

Example:

```text
The payment channel is online.
There were 12 transactions within 10 minutes.
There were 8 failed payment attempts within 10 minutes.
The physical payment card was not present during the transaction.
```

The query is embedded using:

**Sentence Transformers — `all-MiniLM-L6-v2`**

Fraud knowledge documents are stored as normalized embeddings and searched using:

**FAISS `IndexFlatIP`**

Because the embeddings are normalized, inner-product similarity behaves like cosine similarity.

Retrieved knowledge can include patterns such as:

- Card-Not-Present Fraud
- Account Takeover
- Card Testing
- Identity Fraud
- Phishing and Social Engineering
- Transaction Velocity Abuse
- Stolen Payment Card Fraud
- Merchant Fraud
- Transaction Laundering
- Unauthorized Payment Fraud

Similarity represents **semantic relevance**, not the probability that a particular fraud technique occurred.

---

### 🤖 Grounded AI Fraud Analyst

FraudGuard uses a grounded LLM analysis layer to combine:

1. XGBoost prediction
2. Fraud probability and risk level
3. SHAP evidence
4. Supplied contextual signals
5. Retrieved fraud knowledge

The generated analyst report is organized into sections such as:

- 🛡️ Risk Assessment
- 📊 Model Evidence
- 🔎 Relevant Fraud Context
- ✅ Recommended Actions
- ⚠️ Limitations

The prompt includes grounding constraints intended to prevent the LLM from:

- treating semantic similarity as fraud probability,
- inventing meanings for anonymized `V1-V28` features,
- claiming retrieved fraud patterns are confirmed,
- recommending controls unsupported by the supplied evidence.

---

## 🏗️ System Architecture

FraudGuard deliberately keeps **model evidence** and **contextual retrieval evidence** separate until the grounded AI analysis stage.

```text
                     ┌──────────────────────────────┐
                     │      Transaction Input       │
                     └──────────────┬───────────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
     ┌───────────────────────┐             ┌───────────────────────┐
     │ ML Transaction Data   │             │ Transaction Context   │
     │                       │             │                       │
     │ Time                  │             │ Payment Channel       │
     │ Amount                │             │ Transactions / 10 min │
     │ V1-V28                │             │ Failed Attempts       │
     └───────────┬───────────┘             │ Card Presence         │
                 │                         │ Account Anomaly       │
                 ▼                         │ Phishing Report       │
        ┌─────────────────┐                │ Merchant Mismatch     │
        │     XGBoost     │                └───────────┬───────────┘
        └────────┬────────┘                            │
                 │                                     ▼
                 ▼                         ┌───────────────────────┐
     ┌───────────────────────┐             │ Natural-Language     │
     │ Fraud Probability     │             │ Context Query         │
     │ Prediction            │             └───────────┬───────────┘
     │ Risk Level            │                         │
     └───────────┬───────────┘                         ▼
                 │                         ┌───────────────────────┐
                 ▼                         │ Sentence Transformer  │
        ┌─────────────────┐                │ all-MiniLM-L6-v2     │
        │      SHAP       │                └───────────┬───────────┘
        └────────┬────────┘                            │
                 │                                     ▼
                 ▼                              ┌──────────────┐
        ┌─────────────────┐                     │    FAISS     │
        │ Model Evidence  │                     └──────┬───────┘
        └────────┬────────┘                            │
                 │                                     ▼
                 │                         ┌───────────────────────┐
                 │                         │ Retrieved Fraud       │
                 │                         │ Knowledge             │
                 │                         └───────────┬───────────┘
                 │                                     │
                 └──────────────────┬──────────────────┘
                                    │
                                    ▼
                         ┌───────────────────────┐
                         │   Grounded LLM       │
                         │   Fraud Analyst      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Structured Analyst    │
                         │ Report                │
                         └───────────────────────┘
```

### Why separate ML features and context?

The XGBoost model was trained on the original transaction feature space:

```text
Time + Amount + V1-V28
```

Contextual information such as payment channel, failed attempts, phishing reports, or account anomalies is **not injected into the trained model**.

Instead, these signals are used for semantic retrieval and grounded reasoning.

This prevents the application from presenting contextual signals as if they were features the trained model actually learned from.

---

## 🧪 Interactive Analysis Modes

The FraudGuard dashboard contains three analysis modes.

### 🚨 Fraud Demo

Loads a known fraudulent transaction together with suspicious contextual signals.

Useful for demonstrating:

- high fraud probability,
- fraud-increasing SHAP evidence,
- relevant semantic retrieval,
- high-risk grounded analysis.

### ✅ Legitimate Demo

Loads a legitimate transaction with low-risk contextual information.

Useful for demonstrating that FraudGuard does not interpret the mere retrieval of fraud knowledge as proof of fraud.

### 🛠️ Custom Transaction

Allows users to modify:

- Time
- Amount
- V1-V28
- payment channel
- transaction velocity
- failed attempts
- card presence
- account access anomaly
- phishing report
- merchant mismatch

This mode demonstrates an important architectural property:

> Changes to model features affect XGBoost and SHAP, while contextual signals independently affect semantic retrieval and grounded AI reasoning.

---

## 📈 Machine Learning Evaluation

Multiple models were evaluated before selecting XGBoost.

| Model                      |  Precision |     Recall |         F1 |    ROC-AUC | Average Precision |
| -------------------------- | ---------: | ---------: | ---------: | ---------: | ----------------: |
| Logistic Regression (0.50) |     0.8485 |     0.5895 |     0.6957 |     0.9563 |            0.6923 |
| Logistic Regression (0.10) |     0.8434 |     0.7368 |     0.7865 |     0.9563 |            0.6923 |
| Random Forest              |     0.9718 |     0.7263 |     0.8313 |     0.9239 |            0.7876 |
| **XGBoost**                | **0.9726** | **0.7474** | **0.8452** | **0.9760** |        **0.8312** |

### Final XGBoost Results

| Metric            |     Result |
| ----------------- | ---------: |
| Accuracy          | **99.95%** |
| Precision         | **97.26%** |
| Recall            | **74.74%** |
| F1 Score          | **84.52%** |
| ROC-AUC           | **97.60%** |
| Average Precision | **83.12%** |

Because fraud detection is a highly imbalanced classification problem, **precision, recall, F1, ROC-AUC, and Average Precision are more informative than accuracy alone**.

---

## 🔍 Semantic Retrieval Evaluation

The retrieval system was independently evaluated using a controlled set of **10 labeled fraud-context queries**, with one query corresponding to each fraud pattern in the current knowledge base.

Metrics:

| Retrieval Metric           |           Result |
| -------------------------- | ---------------: |
| Hit@1                      | **10/10 — 100%** |
| Hit@3                      | **10/10 — 100%** |
| Mean Reciprocal Rank (MRR) |       **1.0000** |

The evaluation covers:

1. Card-Not-Present Fraud
2. Account Takeover
3. Card Testing
4. Identity Fraud
5. Phishing and Social Engineering
6. Transaction Velocity Abuse
7. Stolen Payment Card Fraud
8. Merchant Fraud
9. Transaction Laundering
10. Unauthorized Payment Fraud

### Evaluation Caveat

These results represent a **controlled retrieval evaluation over a small 10-document knowledge base**.

The evaluation queries were designed to correspond to known fraud categories in the knowledge base. Therefore, the 100% Hit@1 result should **not** be interpreted as 100% RAG accuracy or guaranteed performance on arbitrary real-world fraud investigations.

Future evaluation can include:

- paraphrased queries,
- ambiguous fraud scenarios,
- overlapping fraud patterns,
- irrelevant/negative queries,
- larger knowledge bases,
- human relevance judgments.

---

## 📚 Fraud Knowledge Base

The current knowledge base contains curated fraud-pattern documents covering payment, account, identity, social-engineering, behavioral, and merchant-related fraud.

Each document contains:

```text
ID
Title
Category
Description
Indicators
Recommended Actions
Source
Source URL
```

Sources currently include material from organizations such as:

- Stripe
- Federal Bureau of Investigation
- Federal Trade Commission
- Visa

Retrieved documents are used as **supporting contextual knowledge** rather than confirmed fraud labels.

---

## 🧪 Automated Testing

FraudGuard includes automated backend tests covering:

- API behavior
- transaction-context query generation
- RAG prompt construction
- analysis-mode selection
- grounding rules
- semantic retrieval
- knowledge retrieval behavior

Run the test suite with:

```bash
pytest -v
```

The current backend test suite passes successfully.

---

## 💻 Dashboard

The frontend provides an interactive fraud-analysis dashboard containing:

- transaction simulator,
- fraud probability visualization,
- risk-level display,
- SHAP feature evidence,
- semantic retrieval results,
- fraud-pattern similarity scores,
- retrieved fraud indicators,
- grounded AI analyst report,
- semantic retrieval query,
- custom transaction controls.

### Dashboard Screenshots

> Add final project screenshots here before publishing the repository.

Example structure:

```markdown
### Fraud Analysis

![Fraud Analysis](docs/images/fraud-analysis.png)

### Legitimate Analysis

![Legitimate Analysis](docs/images/legitimate-analysis.png)

### Custom Transaction

![Custom Transaction](docs/images/custom-transaction.png)
```

---

## 🛠️ Tech Stack

### Machine Learning

- Python
- XGBoost
- scikit-learn
- NumPy
- Pandas

### Explainability

- SHAP

### Semantic Retrieval / RAG

- Sentence Transformers
- `all-MiniLM-L6-v2`
- FAISS
- curated fraud knowledge base

### Generative AI

- Groq
- grounded prompt construction

### Backend

- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- React Markdown
- remark-gfm

### Testing

- pytest
- FastAPI TestClient / HTTPX

---

## 📁 Project Structure

```text
FraudGuard-AI/
│
├── data/
│   ├── knowledge/
│   │   └── fraud_patterns.json
│   └── raw/
│       └── creditcard.csv
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── ...
│
├── models/
│   └── trained model artifacts
│
├── notebooks/
│   └── model-development notebooks
│
├── src/
│   └── fraudguard/
│       ├── analyze.py
│       ├── api.py
│       ├── config.py
│       ├── context.py
│       ├── explain.py
│       ├── knowledge.py
│       ├── predict.py
│       ├── rag.py
│       └── retrieval.py
│
├── tests/
│   ├── test_api.py
│   ├── test_context.py
│   ├── test_rag.py
│   └── test_retrieval.py
│
├── evaluate_retrieval.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd FraudGuard-AI
```

---

### 2. Create a Python virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in the appropriate backend/project location used by the application.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

> Never commit API keys or secrets to Git.

---

### 5. Start the FastAPI backend

From the project root:

```bash
uvicorn src.fraudguard.api:app --reload
```

The API will typically run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation will typically be available at:

```text
http://127.0.0.1:8000/docs
```

---

### 6. Install frontend dependencies

Open another terminal:

```bash
cd frontend
npm install
```

---

### 7. Start the frontend

```bash
npm run dev
```

Then open the localhost address shown by Next.js in the terminal.

---

## 🔄 Analysis Pipeline

When a transaction is analyzed, FraudGuard performs the following sequence:

```text
1. Receive transaction features and contextual signals
                    ↓
2. Run XGBoost fraud prediction
                    ↓
3. Generate SHAP explanation
                    ↓
4. Convert supplied context into a retrieval query
                    ↓
5. Embed the query using all-MiniLM-L6-v2
                    ↓
6. Search fraud knowledge using FAISS
                    ↓
7. Construct a grounded RAG prompt
                    ↓
8. Generate the AI fraud analyst report
                    ↓
9. Return prediction + SHAP + retrieval + report
                    ↓
10. Render the analysis in the Next.js dashboard
```

---

## 🧠 Design Principles

### Evidence Separation

Model evidence and contextual evidence remain separate until the grounded analysis stage.

### Explainability

Predictions are accompanied by SHAP feature contributions rather than presented as unexplained scores.

### Retrieval Grounding

The LLM receives retrieved fraud knowledge rather than relying only on its internal knowledge.

### Retrieval ≠ Classification

Semantic similarity is treated as retrieval relevance and never presented as fraud probability.

### Responsible Interpretation

Anonymized model features are not assigned fabricated business meanings.

### Human-in-the-Loop

AI-generated analysis is intended to support fraud investigation rather than replace human judgment.

---

## ⚠️ Limitations

FraudGuard is a portfolio/research-oriented fraud-analysis system and has several important limitations:

- `V1-V28` are anonymized transformed variables and do not have known real-world interpretations.
- SHAP explains model influence but does not establish the real-world cause of fraud.
- Semantic similarity does not prove that a retrieved fraud technique occurred.
- The current fraud knowledge base is intentionally small.
- The controlled retrieval evaluation does not represent arbitrary production traffic.
- Contextual signals depend on the completeness and quality of supplied information.
- The ML model is trained on a specific historical fraud dataset and may not generalize to changing real-world fraud distributions.
- LLM-generated analysis can still contain errors and should be reviewed by a human investigator.
- Production fraud systems require additional monitoring, security, governance, drift detection, and compliance controls.

---

## 🚀 Future Improvements

Potential extensions include:

- larger fraud knowledge bases,
- hybrid lexical + semantic retrieval,
- reranking retrieved documents,
- adversarial and ambiguous retrieval evaluation,
- model and data drift monitoring,
- calibrated fraud probabilities,
- analyst feedback loops,
- production authentication and authorization,
- persistent investigation history,
- observability and tracing,
- containerized deployment,
- CI/CD pipelines.

---

## 👤 Author

**Sejal**

Built as an end-to-end AI/ML engineering portfolio project demonstrating:

- machine learning model development and evaluation,
- fraud detection with XGBoost,
- explainable AI using SHAP,
- semantic search with Sentence Transformers and FAISS,
- Retrieval-Augmented Generation,
- grounded LLM reasoning,
- FastAPI backend engineering,
- Next.js and TypeScript frontend development,
- automated testing,
- ML and retrieval evaluation,
- responsible AI design.

### Connect

- **GitHub:** Add your GitHub profile URL
- **LinkedIn:** Add your LinkedIn profile URL

---

## 📄 Disclaimer

FraudGuard AI is intended for educational, research, and portfolio demonstration purposes.

The system should **not** be used as the sole basis for financial decisions, fraud accusations, account restrictions, or other high-impact actions. Model predictions, retrieved knowledge, SHAP explanations, and AI-generated reports should be reviewed alongside appropriate human investigation and domain-specific controls.

---

## ⭐ Project Summary

FraudGuard demonstrates how multiple AI techniques can be combined while preserving clear evidence boundaries:

**XGBoost** detects risk.  
**SHAP** explains the model.  
**Sentence Transformers + FAISS** retrieve contextual fraud knowledge.  
**Grounded Generative AI** turns those evidence sources into an analyst-friendly report.  
**FastAPI + Next.js** expose the complete workflow as an interactive application.

The goal is not simply to predict fraud, but to make fraud predictions **explainable, contextual, testable, and useful for investigation**.
