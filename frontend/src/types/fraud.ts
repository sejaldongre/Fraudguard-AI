// ==================================================
// SCENARIO TYPES
// ==================================================

export type AnalysisScenario =
  | "fraud"
  | "legitimate"
  | "custom_transaction";


// ==================================================
// TRANSACTION
// XGBoost model input
// ==================================================

export interface Transaction {
  Time: number;
  Amount: number;

  V1: number;
  V2: number;
  V3: number;
  V4: number;
  V5: number;
  V6: number;
  V7: number;
  V8: number;
  V9: number;
  V10: number;
  V11: number;
  V12: number;
  V13: number;
  V14: number;
  V15: number;
  V16: number;
  V17: number;
  V18: number;
  V19: number;
  V20: number;
  V21: number;
  V22: number;
  V23: number;
  V24: number;
  V25: number;
  V26: number;
  V27: number;
  V28: number;
}


// ==================================================
// TRANSACTION CONTEXT
// Used by semantic retrieval + grounded AI
// ==================================================

export interface TransactionContext {
  payment_channel: string;

  transactions_10m: number;

  failed_attempts_10m: number;

  account_access_anomaly: boolean;

  customer_reported_phishing: boolean;

  card_not_present: boolean;

  merchant_mismatch: boolean;
}


// ==================================================
// ANALYZE REQUEST
// ==================================================

export interface AnalyzeRequest {
  transaction: Transaction;

  context: TransactionContext;

  top_k: number;
}


// ==================================================
// MODEL PREDICTION
// ==================================================

export interface Prediction {
  prediction: number;

  label: string;

  fraud_probability: number;

  risk_level: string;

  threshold: number;
}


// ==================================================
// SHAP FEATURE
// ==================================================

export interface ShapFeature {
  feature: string;

  feature_value: number;

  shap_value: number;

  impact: string;
}


// ==================================================
// SHAP EXPLANATION
// ==================================================

export interface Explanation {
  base_value: number;

  top_features: ShapFeature[];

  summary: string;
}


// ==================================================
// RETRIEVED FRAUD KNOWLEDGE
// ==================================================

export interface FraudKnowledge {
  id: string;

  title: string;

  category: string;

  description: string;

  indicators: string[];

  recommended_actions: string[];

  source: string;

  source_url: string;

  similarity_score: number;
}


// ==================================================
// COMPLETE ANALYSIS RESPONSE
// ==================================================

export interface AnalyzeResponse {
  prediction: Prediction;

  explanation: Explanation;

  context_query: string;

  retrieved_knowledge: FraudKnowledge[];

  analyst_report: string;
}