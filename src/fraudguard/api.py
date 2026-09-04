from contextlib import asynccontextmanager

import joblib
import shap

from fastapi import (
    FastAPI,
    HTTPException
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from .config import FRAUD_THRESHOLD

from .predict import (
    MODEL_PATH,
    predict_transaction
)

from .explain import (
    explain_transaction
)

from .knowledge import (
    load_fraud_knowledge
)

from .retrieval import (
    load_embedding_model,
    create_knowledge_embeddings,
    create_faiss_index,
    search_fraud_knowledge
)

from .context import (
    build_context_query
)

from .rag import (
    create_llm_client
)

from .analyze import (
    analyze_transaction
)

from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# ML / AI RESOURCES
# --------------------------------------------------

ml_resources = {}


# --------------------------------------------------
# LAZY EMBEDDING MODEL
# --------------------------------------------------

def get_embedding_model():

    if "embedding_model" not in ml_resources:

        print(
            "Loading embedding model on demand..."
        )

        ml_resources[
            "embedding_model"
        ] = load_embedding_model()

    return ml_resources[
        "embedding_model"
    ]


# --------------------------------------------------
# FASTAPI LIFESPAN
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(
        "Loading FraudGuard resources..."
    )

    # ------------------------------------------
    # LOAD XGBOOST MODEL
    # ------------------------------------------

    print(
        "Loading XGBoost model..."
    )

    ml_resources["model"] = (
        joblib.load(
            MODEL_PATH
        )
    )

    # ------------------------------------------
    # LOAD SHAP EXPLAINER
    # ------------------------------------------

    print(
        "Loading SHAP explainer..."
    )

    ml_resources["explainer"] = (
        shap.TreeExplainer(
            ml_resources["model"]
        )
    )

    # ------------------------------------------
    # LOAD FRAUD KNOWLEDGE
    # ------------------------------------------

    print(
        "Loading fraud knowledge..."
    )

    ml_resources["knowledge"] = (
        load_fraud_knowledge()
    )

    # ------------------------------------------
    # CREATE LLM CLIENT
    # ------------------------------------------

    print(
        "Creating LLM client..."
    )

    ml_resources[
        "llm_client"
    ] = create_llm_client()

    # ------------------------------------------
    # STARTUP COMPLETE
    # ------------------------------------------

    print(
        "FraudGuard resources loaded."
    )

    print(
        "Knowledge documents:",
        len(
            ml_resources[
                "knowledge"
            ]
        )
    )

    # ------------------------------------------
    # APPLICATION RUNNING
    # ------------------------------------------

    yield

    # ------------------------------------------
    # SHUTDOWN
    # ------------------------------------------

    ml_resources.clear()

    print(
        "FraudGuard resources cleared."
    )


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="FraudGuard AI",

    description=(
        "Credit Card Fraud Detection "
        "and Explainability API"
    ),

    version="1.0.0",

    lifespan=lifespan
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# --------------------------------------------------
# INPUT SCHEMA
# --------------------------------------------------

class Transaction(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    Time: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float = Field(
        ge=0
    )


# --------------------------------------------------
# RETRIEVAL REQUEST
# --------------------------------------------------

class RetrievalRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    query: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )


# --------------------------------------------------
# PREDICTION RESPONSE
# --------------------------------------------------

class PredictionResponse(BaseModel):

    prediction: int

    label: str

    fraud_probability: float

    risk_level: str

    threshold: float


# --------------------------------------------------
# SHAP RESPONSE
# --------------------------------------------------

class FeatureExplanation(BaseModel):

    feature: str

    feature_value: float

    shap_value: float

    impact: str


class ShapExplanation(BaseModel):

    base_value: float

    top_features: list[
        FeatureExplanation
    ]

    summary: str


class ExplainResponse(BaseModel):

    prediction: int

    label: str

    fraud_probability: float

    risk_level: str

    threshold: float

    explanation: ShapExplanation


# --------------------------------------------------
# RETRIEVAL RESPONSE
# --------------------------------------------------

class FraudKnowledgeResult(BaseModel):

    id: str

    title: str

    category: str

    description: str

    indicators: list[str]

    recommended_actions: list[str]

    source: str

    source_url: str

    similarity_score: float


class RetrievalResponse(BaseModel):

    query: str

    top_k: int

    results: list[
        FraudKnowledgeResult
    ]


# --------------------------------------------------
# TRANSACTION CONTEXT
# --------------------------------------------------

class TransactionContext(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    payment_channel: str | None = None

    transactions_10m: int = Field(
        default=0,
        ge=0
    )

    failed_attempts_10m: int = Field(
        default=0,
        ge=0
    )

    account_access_anomaly: bool = False

    customer_reported_phishing: bool = False

    card_not_present: bool = False

    merchant_mismatch: bool = False


class AnalyzeRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    transaction: Transaction

    context: TransactionContext

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )


class AnalyzeResponse(BaseModel):

    prediction: PredictionResponse

    explanation: ShapExplanation

    context_query: str

    retrieved_knowledge: list[
        FraudKnowledgeResult
    ]

    analyst_report: str


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message":
            "FraudGuard AI API is running"
    }


# --------------------------------------------------
# HEALTH ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health_check():

    model_loaded = (
        "model"
        in ml_resources
    )

    explainer_loaded = (
        "explainer"
        in ml_resources
    )

    knowledge_loaded = (
        "knowledge"
        in ml_resources
    )

    embedding_model_loaded = (
        "embedding_model"
        in ml_resources
    )

    faiss_loaded = (
        "faiss_index"
        in ml_resources
    )

    llm_client_loaded = (
        "llm_client"
        in ml_resources
    )

    healthy = all([
        model_loaded,
        explainer_loaded,
        knowledge_loaded,
        llm_client_loaded
    ])

    return {

        "status": (
            "healthy"
            if healthy
            else "unhealthy"
        ),

        "model":
            "XGBoost",

        "model_loaded":
            model_loaded,

        "explainer_loaded":
            explainer_loaded,

        "knowledge_loaded":
            knowledge_loaded,

        "embedding_model_loaded":
            embedding_model_loaded,

        "faiss_loaded":
            faiss_loaded,

        "llm_client_loaded":
            llm_client_loaded,

        "knowledge_documents": (
            len(
                ml_resources[
                    "knowledge"
                ]
            )
            if knowledge_loaded
            else 0
        ),

        "faiss_vectors": (
            ml_resources[
                "faiss_index"
            ].ntotal
            if faiss_loaded
            else 0
        ),

        "threshold":
            FRAUD_THRESHOLD
    }


# --------------------------------------------------
# PREDICTION ENDPOINT
# --------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(
    transaction: Transaction
):

    try:

        transaction_data = (
            transaction.model_dump()
        )

        result = (
            predict_transaction(
                transaction_data,
                ml_resources[
                    "model"
                ]
            )
        )

        return result

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )


# --------------------------------------------------
# SHAP EXPLANATION ENDPOINT
# --------------------------------------------------

@app.post(
    "/explain",
    response_model=ExplainResponse
)
def explain(
    transaction: Transaction
):

    try:

        transaction_data = (
            transaction.model_dump()
        )

        # --------------------------------------
        # PREDICTION
        # --------------------------------------

        prediction_result = (
            predict_transaction(
                transaction_data,
                ml_resources[
                    "model"
                ]
            )
        )

        # --------------------------------------
        # SHAP EXPLANATION
        # --------------------------------------

        shap_result = (
            explain_transaction(
                transaction_data,
                ml_resources[
                    "explainer"
                ]
            )
        )

        # --------------------------------------
        # COMBINE RESULTS
        # --------------------------------------

        return {
            **prediction_result,
            "explanation":
                shap_result
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction explanation failed"
            )
        )


# --------------------------------------------------
# KNOWLEDGE RETRIEVAL ENDPOINT
# --------------------------------------------------

@app.post(
    "/retrieve",
    response_model=RetrievalResponse
)
def retrieve_fraud_knowledge(
    request: RetrievalRequest
):

    try:

        embedding_model = (
            get_embedding_model()
        )

        # --------------------------------------
        # CREATE FAISS INDEX IF NEEDED
        # --------------------------------------

        if "faiss_index" not in ml_resources:

            print(
                "Creating FAISS index on demand..."
            )

            knowledge_embeddings = (
                create_knowledge_embeddings(
                    embedding_model,
                    ml_resources["knowledge"]
                )
            )

            ml_resources[
                "faiss_index"
            ] = create_faiss_index(
                knowledge_embeddings
            )

            del knowledge_embeddings

        # --------------------------------------
        # SEARCH KNOWLEDGE
        # --------------------------------------

        results = (
            search_fraud_knowledge(

                query=request.query,

                embedding_model=embedding_model,

                index=(
                    ml_resources[
                        "faiss_index"
                    ]
                ),

                knowledge=(
                    ml_resources[
                        "knowledge"
                    ]
                ),

                top_k=request.top_k
            )
        )

        return {
            "query":
                request.query,

            "top_k":
                len(results),

            "results":
                results
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Knowledge retrieval failed"
            )
        )


# --------------------------------------------------
# CONTEXT RETRIEVAL ENDPOINT
# --------------------------------------------------

@app.post(
    "/context-retrieve",
    response_model=RetrievalResponse
)
def retrieve_from_context(
    context: TransactionContext
):

    try:

        embedding_model = (
            get_embedding_model()
        )

        # --------------------------------------
        # BUILD FAISS INDEX IF NEEDED
        # --------------------------------------

        if "faiss_index" not in ml_resources:

            print(
                "Creating FAISS index on demand..."
            )

            knowledge_embeddings = (
                create_knowledge_embeddings(
                    embedding_model,
                    ml_resources["knowledge"]
                )
            )

            ml_resources[
                "faiss_index"
            ] = create_faiss_index(
                knowledge_embeddings
            )

            del knowledge_embeddings

        # --------------------------------------
        # CONVERT CONTEXT TO DICTIONARY
        # --------------------------------------

        context_data = (
            context.model_dump()
        )

        # --------------------------------------
        # BUILD SEMANTIC QUERY
        # --------------------------------------

        query = (
            build_context_query(
                context_data
            )
        )

        # --------------------------------------
        # SEARCH FAISS
        # --------------------------------------

        results = (
            search_fraud_knowledge(

                query=query,

                embedding_model=embedding_model,

                index=(
                    ml_resources[
                        "faiss_index"
                    ]
                ),

                knowledge=(
                    ml_resources[
                        "knowledge"
                    ]
                ),

                top_k=3
            )
        )

        # --------------------------------------
        # RETURN RESULTS
        # --------------------------------------

        return {
            "query":
                query,

            "top_k":
                len(results),

            "results":
                results
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Context retrieval failed"
            )
        )


# --------------------------------------------------
# ANALYZE ENDPOINT
# --------------------------------------------------

@app.post(
    "/analyze",
    response_model=AnalyzeResponse
)
def analyze(
    request: AnalyzeRequest
):

    try:

        # --------------------------------------
        # PREPARE INPUTS
        # --------------------------------------

        transaction_data = (
            request
            .transaction
            .model_dump()
        )

        context_data = (
            request
            .context
            .model_dump()
        )

        # --------------------------------------
        # XGBOOST PREDICTION
        # --------------------------------------

        prediction_result = (
            predict_transaction(
                transaction_data,
                ml_resources["model"]
            )
        )

        # --------------------------------------
        # SHAP EXPLANATION
        # --------------------------------------

        explanation_result = (
            explain_transaction(
                transaction_data,
                ml_resources["explainer"]
            )
        )

        # --------------------------------------
        # LAZY LOAD EMBEDDING MODEL
        # --------------------------------------

        embedding_model = (
            get_embedding_model()
        )

        # --------------------------------------
        # CREATE FAISS INDEX IF NEEDED
        # --------------------------------------

        if "faiss_index" not in ml_resources:

            print(
                "Creating FAISS index on demand..."
            )

            knowledge_embeddings = (
                create_knowledge_embeddings(
                    embedding_model,
                    ml_resources["knowledge"]
                )
            )

            ml_resources[
                "faiss_index"
            ] = create_faiss_index(
                knowledge_embeddings
            )

            del knowledge_embeddings

        # --------------------------------------
        # RAG + LLM ANALYSIS
        # --------------------------------------

        result = analyze_transaction(

            prediction=prediction_result,

            explanation=explanation_result,

            context=context_data,

            embedding_model=embedding_model,

            faiss_index=(
                ml_resources[
                    "faiss_index"
                ]
            ),

            knowledge=(
                ml_resources[
                    "knowledge"
                ]
            ),

            llm_client=(
                ml_resources[
                    "llm_client"
                ]
            ),

            top_k=request.top_k
        )

        return result

    except Exception as error:

        print(
            "Analyze endpoint error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Fraud analysis failed"
            )
        )
