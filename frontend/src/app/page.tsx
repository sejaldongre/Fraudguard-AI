"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  analyzeTransaction,
  checkHealth,
} from "@/lib/api";

import {
  FRAUD_CONTEXT,
  FRAUD_TRANSACTION,
  LEGITIMATE_CONTEXT,
  LEGITIMATE_TRANSACTION,
} from "@/lib/demoData";

import type {
  AnalyzeResponse,
  Transaction,
  TransactionContext,
} from "@/types/fraud";

import RiskOverview from "@/components/RiskOverview";
import ShapChart from "@/components/ShapChart";
import FraudPatterns from "@/components/FraudPatterns";
import AnalystReport from "@/components/AnalystReport";

import TransactionSimulator, {
  type DemoScenario,
} from "@/components/TransactionSimulator";


// ==========================================================
// PAGE
// ==========================================================

export default function Home() {

  // ========================================================
  // STATE
  // ========================================================

  const [backendOnline, setBackendOnline] =
    useState<boolean | null>(null);

  const [analysis, setAnalysis] =
    useState<AnalyzeResponse | null>(null);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [analysisError, setAnalysisError] =
    useState<string | null>(null);

  const [scenario, setScenario] =
    useState<DemoScenario>("fraud");


  // ========================================================
  // CUSTOM TRANSACTION CONTEXT
  // ========================================================

  const [customContext, setCustomContext] =
    useState<TransactionContext>({
      payment_channel: "online",
      transactions_10m: 5,
      failed_attempts_10m: 2,
      account_access_anomaly: false,
      customer_reported_phishing: false,
      card_not_present: true,
      merchant_mismatch: false,
    });


  // ========================================================
  // CUSTOM TRANSACTION
  // ========================================================

  /*
   * Start the custom transaction from the known fraud
   * transaction.
   *
   * This gives the user a valid transaction-shaped starting
   * point instead of arbitrary zero values for V1-V28.
   */

  const [
    customTransaction,
    setCustomTransaction,
  ] = useState<Transaction>({
    ...FRAUD_TRANSACTION,
  });


  // ========================================================
  // BACKEND HEALTH CHECK
  // ========================================================

  useEffect(() => {

    async function loadHealth() {

      try {

        const health =
          await checkHealth();

        setBackendOnline(
          health.status === "healthy"
        );

      } catch {

        setBackendOnline(false);

      }

    }

    loadHealth();

  }, []);


  // ========================================================
  // CURRENT CONTEXT
  // ========================================================

  /*
   * Fraud Demo:
   *     Uses the fraud demo context.
   *
   * Legitimate Demo:
   *     Uses the legitimate demo context.
   *
   * Custom Transaction:
   *     Uses editable custom context.
   */

  const currentContext: TransactionContext =
    scenario === "fraud"
      ? FRAUD_CONTEXT
      : scenario === "legitimate"
        ? LEGITIMATE_CONTEXT
        : customContext;


  // ========================================================
  // CURRENT TRANSACTION
  // ========================================================

  /*
   * Fraud Demo:
   *     Fixed fraud dataset transaction.
   *
   * Legitimate Demo:
   *     Fixed legitimate dataset transaction.
   *
   * Custom Transaction:
   *     Uses the editable custom transaction.
   */

  const currentTransaction: Transaction =
    scenario === "fraud"
      ? FRAUD_TRANSACTION
      : scenario === "legitimate"
        ? LEGITIMATE_TRANSACTION
        : customTransaction;


  // ========================================================
  // CHANGE SCENARIO
  // ========================================================

  function changeScenario(
    newScenario: DemoScenario
  ) {

    setScenario(newScenario);

    /*
     * Clear the previous result so the user does not see
     * an old analysis belonging to another scenario.
     */

    setAnalysis(null);

    setAnalysisError(null);

  }


  // ========================================================
  // RUN ANALYSIS
  // ========================================================

  async function runAnalysis() {

    setAnalyzing(true);

    setAnalysisError(null);

    setAnalysis(null);

    try {

      /*
       * IMPORTANT:
       *
       * currentTransaction now resolves the correct ML
       * transaction for all three simulator modes.
       *
       * In Custom Transaction mode this is the transaction
       * edited by the user.
       */

      const result =
        await analyzeTransaction({
          transaction: currentTransaction,
          context: currentContext,
          top_k: 3,
        });

      setAnalysis(result);

    } catch (error) {

      if (error instanceof Error) {

        setAnalysisError(
          error.message
        );

      } else {

        setAnalysisError(
          "Unknown analysis error."
        );

      }

    } finally {

      setAnalyzing(false);

    }

  }


  // ========================================================
  // UI
  // ========================================================

  return (

    <main
      className="
        min-h-screen
        bg-slate-950
        text-white
      "
    >

      {/* ====================================================
          HEADER
      ==================================================== */}

      <header
        className="
          border-b
          border-slate-800
          bg-slate-950/95
        "
      >

        <div
          className="
            mx-auto
            flex
            max-w-7xl
            items-center
            justify-between
            px-6
            py-5
          "
        >

          <div>

            <h1
              className="
                text-2xl
                font-bold
                tracking-tight
              "
            >
              🛡️ FraudGuard AI
            </h1>

            <p
              className="
                mt-1
                text-sm
                text-slate-400
              "
            >
              Explainable Financial Fraud Intelligence
            </p>

          </div>


          {/* BACKEND STATUS */}

          <div
            className="
              flex
              items-center
              gap-2
              rounded-full
              border
              border-slate-700
              px-4
              py-2
            "
          >

            <span
              className={`
                h-2.5
                w-2.5
                rounded-full

                ${
                  backendOnline === true
                    ? "bg-emerald-400"
                    : backendOnline === false
                      ? "bg-red-400"
                      : "bg-yellow-400"
                }
              `}
            />


            <span
              className="
                text-sm
                text-slate-300
              "
            >

              {backendOnline === true
                ? "System Online"
                : backendOnline === false
                  ? "Backend Offline"
                  : "Checking..."}

            </span>

          </div>

        </div>

      </header>


      {/* ====================================================
          CONTENT
      ==================================================== */}

      <section
        className="
          mx-auto
          max-w-7xl
          px-6
          py-12
        "
      >

        {/* ==================================================
            HERO
        ================================================== */}

        <div className="max-w-3xl">

          <p
            className="
              mb-3
              text-sm
              font-semibold
              uppercase
              tracking-widest
              text-cyan-400
            "
          >
            AI Fraud Intelligence Platform
          </p>


          <h2
            className="
              text-4xl
              font-bold
              tracking-tight
              md:text-5xl
            "
          >
            Detect suspicious transactions.
            Understand why.
          </h2>


          <p
            className="
              mt-6
              text-lg
              leading-8
              text-slate-400
            "
          >
            FraudGuard combines XGBoost, SHAP
            explainability, semantic retrieval and
            grounded generative AI to provide
            transparent fraud risk analysis.
          </p>

        </div>


        {/* ==================================================
            PIPELINE CARDS
        ================================================== */}

        <div
          className="
            mt-12
            grid
            gap-5
            md:grid-cols-3
          "
        >

          {/* XGBOOST */}

          <div
            className="
              rounded-2xl
              border
              border-slate-800
              bg-slate-900
              p-6
            "
          >

            <div
              className="
                mb-4
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-xl
                bg-cyan-500/10
              "
            >
              ⚡
            </div>


            <p className="text-sm text-slate-400">
              Detection
            </p>


            <h3
              className="
                mt-2
                text-xl
                font-semibold
              "
            >
              XGBoost Risk Engine
            </h3>


            <p
              className="
                mt-3
                text-sm
                leading-6
                text-slate-400
              "
            >
              Fraud probability using the trained
              transaction classification model.
            </p>

          </div>


          {/* SHAP */}

          <div
            className="
              rounded-2xl
              border
              border-slate-800
              bg-slate-900
              p-6
            "
          >

            <div
              className="
                mb-4
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-xl
                bg-cyan-500/10
              "
            >
              📊
            </div>


            <p className="text-sm text-slate-400">
              Explainability
            </p>


            <h3
              className="
                mt-2
                text-xl
                font-semibold
              "
            >
              SHAP Evidence
            </h3>


            <p
              className="
                mt-3
                text-sm
                leading-6
                text-slate-400
              "
            >
              Understand which anonymized transaction
              features influenced each prediction.
            </p>

          </div>


          {/* RAG */}

          <div
            className="
              rounded-2xl
              border
              border-slate-800
              bg-slate-900
              p-6
            "
          >

            <div
              className="
                mb-4
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-xl
                bg-cyan-500/10
              "
            >
              🧠
            </div>


            <p className="text-sm text-slate-400">
              Investigation
            </p>


            <h3
              className="
                mt-2
                text-xl
                font-semibold
              "
            >
              RAG Fraud Analyst
            </h3>


            <p
              className="
                mt-3
                text-sm
                leading-6
                text-slate-400
              "
            >
              Retrieve relevant fraud patterns and
              generate a grounded analyst report.
            </p>

          </div>

        </div>


        {/* ==================================================
            TRANSACTION SIMULATOR
        ================================================== */}

        <TransactionSimulator
          scenario={scenario}
          transaction={currentTransaction}
          context={currentContext}
          analyzing={analyzing}
          backendOnline={backendOnline}
          onScenarioChange={changeScenario}
          onTransactionChange={setCustomTransaction}
          onContextChange={setCustomContext}
          onAnalyze={runAnalysis}
        />


        {/* ==================================================
            LOADING
        ================================================== */}

        {analyzing && (

          <div
            className="
              mt-8
              rounded-2xl
              border
              border-cyan-900/40
              bg-cyan-950/10
              p-6
            "
          >

            <div
              className="
                flex
                items-center
                gap-4
              "
            >

              <div
                className="
                  h-5
                  w-5
                  animate-spin
                  rounded-full
                  border-2
                  border-cyan-400
                  border-t-transparent
                "
              />


              <div>

                <p
                  className="
                    font-medium
                    text-cyan-300
                  "
                >
                  FraudGuard is analyzing the transaction
                </p>


                <p
                  className="
                    mt-1
                    text-sm
                    text-slate-500
                  "
                >
                  Running XGBoost prediction, SHAP
                  explainability, semantic retrieval and
                  grounded AI investigation...
                </p>

              </div>

            </div>

          </div>

        )}


        {/* ==================================================
            ERROR
        ================================================== */}

        {analysisError && (

          <div
            className="
              mt-8
              rounded-2xl
              border
              border-red-900
              bg-red-950/30
              p-6
            "
          >

            <p
              className="
                font-semibold
                text-red-400
              "
            >
              Analysis Failed
            </p>


            <p
              className="
                mt-2
                text-sm
                text-red-300
              "
            >
              {analysisError}
            </p>

          </div>

        )}


        {/* ==================================================
            RESULTS
        ================================================== */}

        {analysis && (

          <div className="mt-10 space-y-6">

            {/* ================================================
                ANALYZED SCENARIO
            ================================================ */}

            <div
              className="
                flex
                flex-wrap
                items-center
                justify-between
                gap-3
              "
            >

              <div>

                <p
                  className="
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-slate-500
                  "
                >
                  Analyzed Scenario
                </p>


                <p
                  className="
                    mt-1
                    font-semibold
                    text-slate-200
                  "
                >

                  {scenario === "fraud"
                    ? "🚨 Known Fraud Transaction (Class = 1)"
                    : scenario === "legitimate"
                      ? "✓ Known Legitimate Transaction (Class = 0)"
                      : "🧪 Custom Transaction Analysis"}

                </p>

              </div>

            </div>


            {/* ==================================================
                1. RISK ASSESSMENT
            ================================================== */}

            <RiskOverview
              prediction={analysis.prediction}
            />


            {/* ==================================================
                2. EXPLAINABLE AI
            ================================================== */}

            <ShapChart
              explanation={analysis.explanation}
            />


            {/* ==================================================
                3. SEMANTIC RETRIEVAL
            ================================================== */}

            <FraudPatterns
              patterns={
                analysis.retrieved_knowledge
              }
            />


            {/* ==================================================
                4. GROUNDED GENERATIVE AI
            ================================================== */}

            <AnalystReport
              report={
                analysis.analyst_report
              }
            />


            {/* ==================================================
                SEMANTIC QUERY
            ================================================== */}

            <section
              className="
                rounded-2xl
                border
                border-slate-800
                bg-slate-900
                p-6
              "
            >

              <p
                className="
                  text-xs
                  font-semibold
                  uppercase
                  tracking-wider
                  text-slate-500
                "
              >
                Semantic Retrieval Query
              </p>


              <p
                className="
                  mt-3
                  text-sm
                  leading-6
                  text-slate-400
                "
              >
                {analysis.context_query}
              </p>


              <div
                className="
                  mt-4
                  border-t
                  border-slate-800
                  pt-4
                "
              >

                <p
                  className="
                    text-xs
                    leading-5
                    text-slate-500
                  "
                >
                  This query is generated from supplied
                  transaction context and used for semantic
                  retrieval. It is separate from the
                  anonymized V1-V28 model features.
                </p>

              </div>

            </section>


            {/* ==================================================
                CUSTOM TRANSACTION MODE NOTE
            ================================================== */}



            {scenario === "custom_transaction" && (

              <section
                className="
                  rounded-2xl
                  border
                  border-violet-900/40
                  bg-violet-950/10
                  p-6
                "
              >

                <p
                  className="
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-violet-400
                  "
                >
                  Custom Transaction Mode
                </p>


                <p
                  className="
                    mt-3
                    text-sm
                    leading-6
                    text-slate-400
                  "
                >
                  Time, Amount and the anonymized V1-V28
                  transaction features were supplied directly
                  to the XGBoost fraud model. Changes to these
                  values can affect the fraud probability and
                  SHAP explanation.
                </p>


                <p
                  className="
                    mt-3
                    text-sm
                    leading-6
                    text-slate-400
                  "
                >
                  Contextual signals are also editable in
                  Custom Transaction mode. They remain separate from the
                  model features and are used to construct the
                  semantic retrieval query and support grounded
                  AI reasoning.
                </p>

              </section>

            )}

          </div>

        )}


        {/* ==================================================
            FOOTER
        ================================================== */}

        <footer
          className="
            mt-16
            border-t
            border-slate-800
            py-8
          "
        >

          <div
            className="
              flex
              flex-col
              gap-2
              text-sm
              text-slate-500
              md:flex-row
              md:items-center
              md:justify-between
            "
          >

            <p>
              FraudGuard AI
            </p>

            <p>
              XGBoost • SHAP • FAISS • RAG •
              FastAPI • Next.js
            </p>

          </div>

        </footer>

      </section>

    </main>
  );
}