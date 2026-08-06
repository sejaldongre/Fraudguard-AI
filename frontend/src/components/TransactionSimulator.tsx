"use client";

import { useState } from "react";

import {
  FRAUD_TRANSACTION,
  LEGITIMATE_TRANSACTION,
} from "@/lib/demoData";

import type {
  Transaction,
  TransactionContext,
  AnalysisScenario,
} from "@/types/fraud";


// ==========================================================
// TYPES
// ==========================================================

export type DemoScenario = AnalysisScenario;


type TransactionSimulatorProps = {
  scenario: DemoScenario;

  transaction: Transaction;

  context: TransactionContext;

  analyzing: boolean;

  backendOnline: boolean | null;

  onScenarioChange: (
    scenario: DemoScenario
  ) => void;

  onTransactionChange: (
    transaction: Transaction
  ) => void;

  onContextChange: (
    context: TransactionContext
  ) => void;

  onAnalyze: () => void;
};


// ==========================================================
// MODEL FEATURE NAMES
// ==========================================================

const MODEL_FEATURES: Array<keyof Transaction> =
  Array.from(
    { length: 28 },
    (_, index) =>
      `V${index + 1}` as keyof Transaction
  );


// ==========================================================
// COMPONENT
// ==========================================================

export default function TransactionSimulator({
  scenario,
  transaction,
  context,
  analyzing,
  backendOnline,
  onScenarioChange,
  onTransactionChange,
  onContextChange,
  onAnalyze,
}: TransactionSimulatorProps) {

  const [showAdvancedFeatures, setShowAdvancedFeatures] =
    useState(false);


  // ========================================================
  // MODE FLAGS
  // ========================================================

  const isCustomTransaction =
    scenario === "custom_transaction";

  const contextEditable =
    isCustomTransaction;


  // ========================================================
  // SAFE TRANSACTION VALUES
  // ========================================================

  const time =
    Number.isFinite(transaction.Time)
      ? transaction.Time
      : 0;

  const amount =
    Number.isFinite(transaction.Amount)
      ? transaction.Amount
      : 0;


  // ========================================================
  // SAFE CONTEXT VALUES
  // ========================================================

  const paymentChannel =
    context.payment_channel ?? "online";

  const transactionCount =
    context.transactions_10m ?? 0;

  const failedAttempts =
    context.failed_attempts_10m ?? 0;

  const cardNotPresent =
    context.card_not_present ?? false;

  const accountAccessAnomaly =
    context.account_access_anomaly ?? false;

  const customerReportedPhishing =
    context.customer_reported_phishing ?? false;

  const merchantMismatch =
    context.merchant_mismatch ?? false;


  // ========================================================
  // UPDATE TRANSACTION
  // ========================================================

  function updateTransaction<
    K extends keyof Transaction
  >(
    field: K,
    value: Transaction[K]
  ) {

    onTransactionChange({
      ...transaction,
      [field]: value,
    });
  }


  // ========================================================
  // LOAD DATASET SAMPLE INTO CUSTOM TRANSACTION
  // ========================================================

  function loadTransactionSample(sample: Transaction) {
    onTransactionChange({
      ...sample,
    });

    if (scenario !== "custom_transaction") {
      onScenarioChange("custom_transaction");
    }
  }


  // ========================================================
  // UPDATE CONTEXT
  // ========================================================

  function updateContext<
    K extends keyof TransactionContext
  >(
    field: K,
    value: TransactionContext[K]
  ) {

    onContextChange({
      ...context,
      [field]: value,
    });
  }


  // ========================================================
  // SCENARIO INFORMATION
  // ========================================================

  const scenarioLabel =
    scenario === "fraud"
      ? "Known Fraud Transaction"
      : scenario === "legitimate"
        ? "Known Legitimate Transaction"
        : "Custom Transaction Analysis";


  const scenarioColor =
    scenario === "fraud"
      ? "text-red-400"
      : scenario === "legitimate"
        ? "text-emerald-400"
        : "text-violet-400";


  // ========================================================
  // RENDER
  // ========================================================

  return (

    <section
      className="
        mt-12
        rounded-2xl
        border
        border-slate-800
        bg-slate-900
        p-6
        md:p-8
      "
    >

      {/* ====================================================
          HEADER
      ==================================================== */}

      <div>

        <p
          className="
            text-xs
            font-semibold
            uppercase
            tracking-[0.2em]
            text-cyan-400
          "
        >
          Transaction Simulator
        </p>


        <h3
          className="
            mt-2
            text-2xl
            font-semibold
            text-white
          "
        >
          Test the FraudGuard pipeline
        </h3>


        <p
          className="
            mt-3
            max-w-4xl
            text-sm
            leading-6
            text-slate-400
          "
        >
          Select a known dataset transaction or create
          a custom transaction. XGBoost analyzes
          Time, Amount and the anonymized V1-V28
          model features while contextual signals
          support semantic retrieval and grounded
          AI analysis.
        </p>

      </div>


      {/* ====================================================
          SCENARIO SELECTOR
      ==================================================== */}

      <div
        className="
          mt-8
          grid
          gap-4
          md:grid-cols-3
        "
      >

        {/* FRAUD DEMO */}

        <ScenarioButton
          title="Fraud Demo"
          description="Real Class = 1 transaction from the credit-card fraud dataset."
          selected={scenario === "fraud"}
          selectedClasses="
            border-red-500/60
            bg-red-500/10
          "
          badgeClasses="
            bg-red-500/10
            text-red-400
          "
          onClick={() =>
            onScenarioChange("fraud")
          }
        />


        {/* LEGITIMATE DEMO */}

        <ScenarioButton
          title="Legitimate Demo"
          description="Real Class = 0 transaction from the credit-card fraud dataset."
          selected={scenario === "legitimate"}
          selectedClasses="
            border-emerald-500/60
            bg-emerald-500/10
          "
          badgeClasses="
            bg-emerald-500/10
            text-emerald-400
          "
          onClick={() =>
            onScenarioChange("legitimate")
          }
        />


        {/* CUSTOM TRANSACTION */}

        <ScenarioButton
          title="Custom Transaction"
          description="Modify the actual transaction features sent to the XGBoost fraud model."
          selected={
            scenario === "custom_transaction"
          }
          selectedClasses="
            border-violet-500/60
            bg-violet-500/10
          "
          badgeClasses="
            bg-violet-500/10
            text-violet-400
          "
          onClick={() =>
            onScenarioChange(
              "custom_transaction"
            )
          }
        />

      </div>


      {/* ====================================================
          CURRENT SCENARIO
      ==================================================== */}

      <div
        className="
          mt-6
          rounded-xl
          border
          border-slate-800
          bg-slate-950/60
          px-5
          py-4
        "
      >

        <p className="text-sm text-slate-400">

          Current scenario:{" "}

          <span
            className={`
              font-semibold
              ${scenarioColor}
            `}
          >
            {scenarioLabel}
          </span>

        </p>

      </div>


      {/* ====================================================
          CUSTOM TRANSACTION MODEL INPUT
      ==================================================== */}

      {isCustomTransaction && (

        <div
          className="
            mt-8
            rounded-2xl
            border
            border-violet-500/20
            bg-violet-500/[0.03]
            p-5
            md:p-6
          "
        >

          <div
            className="
              flex
              flex-wrap
              items-start
              justify-between
              gap-4
            "
          >

            <div>

              <p
                className="
                  text-xs
                  font-semibold
                  uppercase
                  tracking-[0.18em]
                  text-violet-400
                "
              >
                Machine Learning Input
              </p>

              <h4
                className="
                  mt-2
                  text-lg
                  font-semibold
                  text-slate-100
                "
              >
                Custom Transaction Features
              </h4>

              <p
                className="
                  mt-2
                  max-w-3xl
                  text-sm
                  leading-6
                  text-slate-400
                "
              >
                These values are sent directly
                to the trained XGBoost model.
                Changing them can alter the fraud
                probability, decision and SHAP
                explanation.
              </p>

            </div>


            <span
              className="
                rounded-full
                border
                border-violet-500/30
                bg-violet-500/10
                px-3
                py-1
                text-xs
                font-medium
                text-violet-300
              "
            >
              ML Input Editable
            </span>

          </div>


          {/* DATASET SAMPLE LOADERS */}

          <div
            className="
              mt-6
              flex
              flex-wrap
              items-center
              gap-3
            "
          >
            <button
              type="button"
              onClick={() =>
                loadTransactionSample(FRAUD_TRANSACTION)
              }
              className="
                rounded-xl
                border
                border-red-500/40
                bg-red-500/10
                px-4
                py-2.5
                text-sm
                font-semibold
                text-red-300
                transition
                hover:border-red-400/60
                hover:bg-red-500/15
              "
            >
              Load Fraud Sample
            </button>

            <button
              type="button"
              onClick={() =>
                loadTransactionSample(LEGITIMATE_TRANSACTION)
              }
              className="
                rounded-xl
                border
                border-emerald-500/40
                bg-emerald-500/10
                px-4
                py-2.5
                text-sm
                font-semibold
                text-emerald-300
                transition
                hover:border-emerald-400/60
                hover:bg-emerald-500/15
              "
            >
              Load Legitimate Sample
            </button>

            <p
              className="
                text-xs
                leading-5
                text-slate-500
              "
            >
              Loads a complete dataset transaction into
              Time, Amount and V1-V28. You can then edit
              any value before analysis.
            </p>
          </div>


          {/* TIME + AMOUNT */}

          <div
            className="
              mt-6
              grid
              gap-5
              md:grid-cols-2
            "
          >

            <div>

              <label
                htmlFor="custom-time"
                className="
                  text-sm
                  font-medium
                  text-slate-300
                "
              >
                Time
              </label>

              <input
                id="custom-time"
                type="number"
                step="any"
                value={time}
                onChange={(event) => {

                  const parsed =
                    Number(event.target.value);

                  updateTransaction(
                    "Time",
                    Number.isFinite(parsed)
                      ? parsed
                      : 0
                  );

                }}
                className="
                  mt-2
                  w-full
                  rounded-xl
                  border
                  border-slate-700
                  bg-slate-950
                  px-4
                  py-3
                  text-sm
                  text-white
                  outline-none
                  transition
                  focus:border-violet-500
                "
              />

              <p
                className="
                  mt-2
                  text-xs
                  text-slate-500
                "
              >
                Dataset transaction time feature.
              </p>

            </div>


            <div>

              <label
                htmlFor="custom-amount"
                className="
                  text-sm
                  font-medium
                  text-slate-300
                "
              >
                Amount
              </label>

              <input
                id="custom-amount"
                type="number"
                min={0}
                step="0.01"
                value={amount}
                onChange={(event) => {

                  const parsed =
                    Number(event.target.value);

                  updateTransaction(
                    "Amount",
                    Number.isFinite(parsed)
                      ? Math.max(0, parsed)
                      : 0
                  );

                }}
                className="
                  mt-2
                  w-full
                  rounded-xl
                  border
                  border-slate-700
                  bg-slate-950
                  px-4
                  py-3
                  text-sm
                  text-white
                  outline-none
                  transition
                  focus:border-violet-500
                "
              />

              <p
                className="
                  mt-2
                  text-xs
                  text-slate-500
                "
              >
                Transaction amount supplied to
                the fraud model.
              </p>

            </div>

          </div>


          {/* ADVANCED FEATURES */}

          <div
            className="
              mt-6
              overflow-hidden
              rounded-xl
              border
              border-slate-800
              bg-slate-950/70
            "
          >

            <button
              type="button"
              onClick={() =>
                setShowAdvancedFeatures(
                  (current) => !current
                )
              }
              className="
                flex
                w-full
                items-center
                justify-between
                gap-4
                px-5
                py-4
                text-left
                transition
                hover:bg-slate-900
              "
            >

              <div>

                <p
                  className="
                    text-sm
                    font-semibold
                    text-slate-200
                  "
                >
                  Advanced ML Features
                </p>

                <p
                  className="
                    mt-1
                    text-xs
                    text-slate-500
                  "
                >
                  Edit anonymized V1-V28
                  transformed features.
                </p>

              </div>


              <span
                className="
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-lg
                  bg-violet-500/10
                  text-lg
                  font-semibold
                  text-violet-300
                "
              >
                {showAdvancedFeatures
                  ? "−"
                  : "+"}
              </span>

            </button>


            {showAdvancedFeatures && (

              <div
                className="
                  border-t
                  border-slate-800
                  p-5
                "
              >

                <div
                  className="
                    grid
                    gap-4
                    sm:grid-cols-2
                    lg:grid-cols-4
                  "
                >

                  {MODEL_FEATURES.map(
                    (feature) => {

                      const featureValue =
                        Number(
                          transaction[feature]
                        );

                      return (

                        <div key={feature}>

                          <label
                            htmlFor={`feature-${feature}`}
                            className="
                              text-xs
                              font-semibold
                              text-slate-400
                            "
                          >
                            {feature}
                          </label>

                          <input
                            id={`feature-${feature}`}
                            type="number"
                            step="any"
                            value={
                              Number.isFinite(
                                featureValue
                              )
                                ? featureValue
                                : 0
                            }
                            onChange={(
                              event
                            ) => {

                              const parsed =
                                Number(
                                  event.target
                                    .value
                                );

                              updateTransaction(
                                feature,
                                Number.isFinite(
                                  parsed
                                )
                                  ? parsed
                                  : 0
                              );

                            }}
                            className="
                              mt-2
                              w-full
                              rounded-lg
                              border
                              border-slate-700
                              bg-slate-950
                              px-3
                              py-2.5
                              text-sm
                              text-white
                              outline-none
                              transition
                              focus:border-violet-500
                            "
                          />

                        </div>

                      );
                    }
                  )}

                </div>


                <div
                  className="
                    mt-5
                    rounded-lg
                    border
                    border-amber-500/20
                    bg-amber-500/5
                    p-4
                  "
                >

                  <p
                    className="
                      text-xs
                      leading-5
                      text-amber-200/80
                    "
                  >
                    V1-V28 are anonymized
                    transformed variables from
                    the credit-card fraud dataset.
                    FraudGuard does not assign
                    real-world business meanings
                    to these features.
                  </p>

                </div>

              </div>

            )}

          </div>


          {/* ML SUMMARY */}

          <div
            className="
              mt-6
              grid
              gap-4
              sm:grid-cols-3
            "
          >

            <SummaryCard
              label="Time"
              value={time.toFixed(2)}
            />

            <SummaryCard
              label="Amount"
              value={`$${amount.toFixed(2)}`}
            />

            <SummaryCard
              label="Model Features"
              value="V1 – V28"
            />

          </div>

        </div>

      )}


      {/* ====================================================
          TRANSACTION CONTEXT HEADER
      ==================================================== */}

      <div
        className="
          mt-8
          flex
          flex-wrap
          items-center
          justify-between
          gap-4
        "
      >

        <div>

          <h4
            className="
              text-lg
              font-semibold
              text-slate-100
            "
          >
            Transaction Context
          </h4>


          <p
            className="
              mt-1
              text-sm
              text-slate-500
            "
          >
            {contextEditable
              ? "Edit the contextual signals below."
              : "Select Custom Transaction to edit these signals."}
          </p>

        </div>


        {contextEditable && (

          <span
            className="
              rounded-full
              border
              border-cyan-500/30
              bg-cyan-500/10
              px-3
              py-1
              text-xs
              font-medium
              text-cyan-300
            "
          >
            Editable
          </span>

        )}

      </div>


      {/* ====================================================
          BASIC CONTEXT INPUTS
      ==================================================== */}

      <div
        className="
          mt-6
          grid
          gap-5
          md:grid-cols-2
        "
      >

        {/* PAYMENT CHANNEL */}

        <div>

          <label
            htmlFor="payment-channel"
            className="
              text-sm
              font-medium
              text-slate-300
            "
          >
            Payment Channel
          </label>


          <select
            id="payment-channel"
            value={paymentChannel}
            disabled={!contextEditable}
            onChange={(event) =>
              updateContext(
                "payment_channel",
                event.target.value
              )
            }
            className="
              mt-2
              w-full
              rounded-xl
              border
              border-slate-700
              bg-slate-950
              px-4
              py-3
              text-sm
              text-white
              outline-none
              transition
              focus:border-cyan-500
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          >

            <option value="online">
              Online
            </option>

            <option value="in_store">
              In Store
            </option>

            <option value="mobile">
              Mobile
            </option>

          </select>

        </div>


        {/* TRANSACTIONS */}

        <div>

          <label
            htmlFor="transactions-10m"
            className="
              text-sm
              font-medium
              text-slate-300
            "
          >
            Transactions in last 10 minutes
          </label>


          <input
            id="transactions-10m"
            type="number"
            min={0}
            max={100}
            value={transactionCount}
            disabled={!contextEditable}
            onChange={(event) => {

              const parsed =
                Number(event.target.value);

              updateContext(
                "transactions_10m",
                Number.isFinite(parsed)
                  ? Math.max(0, parsed)
                  : 0
              );

            }}
            className="
              mt-2
              w-full
              rounded-xl
              border
              border-slate-700
              bg-slate-950
              px-4
              py-3
              text-sm
              text-white
              outline-none
              transition
              focus:border-cyan-500
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          />

        </div>


        {/* FAILED ATTEMPTS */}

        <div>

          <label
            htmlFor="failed-attempts-10m"
            className="
              text-sm
              font-medium
              text-slate-300
            "
          >
            Failed attempts in last 10 minutes
          </label>


          <input
            id="failed-attempts-10m"
            type="number"
            min={0}
            max={100}
            value={failedAttempts}
            disabled={!contextEditable}
            onChange={(event) => {

              const parsed =
                Number(event.target.value);

              updateContext(
                "failed_attempts_10m",
                Number.isFinite(parsed)
                  ? Math.max(0, parsed)
                  : 0
              );

            }}
            className="
              mt-2
              w-full
              rounded-xl
              border
              border-slate-700
              bg-slate-950
              px-4
              py-3
              text-sm
              text-white
              outline-none
              transition
              focus:border-cyan-500
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          />

        </div>


        {/* CARD PRESENCE */}

        <div>

          <p
            className="
              text-sm
              font-medium
              text-slate-300
            "
          >
            Card Presence
          </p>


          <button
            type="button"
            disabled={!contextEditable}
            onClick={() =>
              updateContext(
                "card_not_present",
                !cardNotPresent
              )
            }
            className={`
              mt-2
              w-full
              rounded-xl
              border
              px-4
              py-3
              text-left
              text-sm
              font-medium
              transition
              disabled:cursor-not-allowed
              disabled:opacity-60

              ${
                cardNotPresent
                  ? `
                      border-orange-500/50
                      bg-orange-500/10
                      text-orange-300
                    `
                  : `
                      border-emerald-500/40
                      bg-emerald-500/10
                      text-emerald-300
                    `
              }
            `}
          >
            {cardNotPresent
              ? "Card Not Present"
              : "Physical Card Present"}
          </button>

        </div>

      </div>


      {/* ====================================================
          ADDITIONAL FRAUD SIGNALS
      ==================================================== */}

      <div className="mt-9">

        <h4
          className="
            text-lg
            font-semibold
            text-slate-100
          "
        >
          Additional Fraud Signals
        </h4>


        <p
          className="
            mt-1
            text-sm
            text-slate-500
          "
        >
          These interpretable signals help
          FraudGuard retrieve relevant fraud
          patterns.
        </p>

      </div>


      <div
        className="
          mt-5
          grid
          gap-4
          md:grid-cols-3
        "
      >

        <SignalButton
          title="Account Access Anomaly"
          description="Unexpected or unauthorized account access was observed."
          active={accountAccessAnomaly}
          disabled={!contextEditable}
          onClick={() =>
            updateContext(
              "account_access_anomaly",
              !accountAccessAnomaly
            )
          }
        />


        <SignalButton
          title="Customer Reported Phishing"
          description="The customer reported a suspicious phishing or impersonation message."
          active={customerReportedPhishing}
          disabled={!contextEditable}
          onClick={() =>
            updateContext(
              "customer_reported_phishing",
              !customerReportedPhishing
            )
          }
        />


        <SignalButton
          title="Merchant Mismatch"
          description="Payment activity appears inconsistent with the merchant's business activity."
          active={merchantMismatch}
          disabled={!contextEditable}
          onClick={() =>
            updateContext(
              "merchant_mismatch",
              !merchantMismatch
            )
          }
        />

      </div>


      {/* ====================================================
          CONTEXT SUMMARY
      ==================================================== */}

      <div
        className="
          mt-8
          grid
          gap-4
          sm:grid-cols-2
          lg:grid-cols-4
        "
      >

        <SummaryCard
          label="Channel"
          value={
            paymentChannel === "in_store"
              ? "In Store"
              : paymentChannel === "mobile"
                ? "Mobile"
                : "Online"
          }
        />


        <SummaryCard
          label="Transactions"
          value={String(transactionCount)}
        />


        <SummaryCard
          label="Failed Attempts"
          value={String(failedAttempts)}
        />


        <SummaryCard
          label="Card"
          value={
            cardNotPresent
              ? "Not Present"
              : "Present"
          }
          valueClass={
            cardNotPresent
              ? "text-orange-300"
              : "text-emerald-300"
          }
        />

      </div>


      {/* ====================================================
          ARCHITECTURE EXPLANATION
      ==================================================== */}

      <div
        className="
          mt-7
          rounded-xl
          border
          border-slate-800
          bg-slate-950/60
          p-5
        "
      >

        {isCustomTransaction ? (

          <p
            className="
              text-xs
              leading-6
              text-slate-500
            "
          >
            In Custom Transaction mode, Time,
            Amount and V1-V28 are sent to the
            XGBoost fraud model. The contextual
            signals remain separate and are used
            to build the semantic retrieval query
            and support the grounded AI analyst.
          </p>

        ) : (

          <p
            className="
              text-xs
              leading-6
              text-slate-500
            "
          >
            These contextual signals are used to
            build the semantic retrieval query and
            support the grounded AI analyst. They
            do not modify the anonymized V1-V28
            features used by the XGBoost fraud
            model.
          </p>

        )}

      </div>


      {/* ====================================================
          ANALYZE BUTTON
      ==================================================== */}

      <div
        className="
          mt-7
          flex
          flex-wrap
          items-center
          gap-4
        "
      >

        <button
          type="button"
          onClick={onAnalyze}
          disabled={
            analyzing ||
            backendOnline !== true
          }
          className="
            rounded-xl
            bg-cyan-500
            px-7
            py-3
            font-semibold
            text-slate-950
            transition
            hover:bg-cyan-400
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          {analyzing
            ? "Analyzing..."
            : "Analyze Transaction"}
        </button>


        {isCustomTransaction && (

          <p
            className="
              text-xs
              font-medium
              text-violet-400
            "
          >
            ⚙ Custom transaction analysis enabled
          </p>

        )}


        {backendOnline === false && (

          <p
            className="
              text-xs
              font-medium
              text-red-400
            "
          >
            Backend must be online before analysis.
          </p>

        )}

      </div>

    </section>
  );
}


// ==========================================================
// SCENARIO BUTTON
// ==========================================================

type ScenarioButtonProps = {
  title: string;

  description: string;

  selected: boolean;

  selectedClasses: string;

  badgeClasses: string;

  onClick: () => void;
};


function ScenarioButton({
  title,
  description,
  selected,
  selectedClasses,
  badgeClasses,
  onClick,
}: ScenarioButtonProps) {

  return (

    <button
      type="button"
      onClick={onClick}
      className={`
        rounded-xl
        border
        p-5
        text-left
        transition-all

        ${
          selected
            ? selectedClasses
            : `
                border-slate-700
                bg-slate-950
                hover:border-slate-600
              `
        }
      `}
    >

      <div
        className="
          flex
          items-center
          justify-between
          gap-3
        "
      >

        <p
          className="
            font-semibold
            text-slate-100
          "
        >
          {title}
        </p>


        {selected && (

          <span
            className={`
              rounded-full
              px-2
              py-1
              text-xs
              font-semibold
              ${badgeClasses}
            `}
          >
            Selected
          </span>

        )}

      </div>


      <p
        className="
          mt-2
          text-xs
          leading-5
          text-slate-400
        "
      >
        {description}
      </p>

    </button>
  );
}


// ==========================================================
// SIGNAL BUTTON
// ==========================================================

type SignalButtonProps = {
  title: string;

  description: string;

  active: boolean;

  disabled: boolean;

  onClick: () => void;
};


function SignalButton({
  title,
  description,
  active,
  disabled,
  onClick,
}: SignalButtonProps) {

  return (

    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`
        rounded-xl
        border
        p-5
        text-left
        transition
        disabled:cursor-not-allowed
        disabled:opacity-60

        ${
          active
            ? `
                border-red-500/50
                bg-red-500/10
              `
            : `
                border-slate-700
                bg-slate-950
              `
        }
      `}
    >

      <div
        className="
          flex
          items-start
          justify-between
          gap-4
        "
      >

        <div>

          <p
            className="
              text-sm
              font-semibold
              text-slate-200
            "
          >
            {title}
          </p>


          <p
            className="
              mt-2
              text-xs
              leading-5
              text-slate-400
            "
          >
            {description}
          </p>

        </div>


        <span
          className={`
            rounded-full
            px-2
            py-1
            text-xs
            font-semibold

            ${
              active
                ? `
                    bg-red-500/10
                    text-red-400
                  `
                : `
                    bg-slate-800
                    text-slate-400
                  `
            }
          `}
        >
          {active ? "Yes" : "No"}
        </span>

      </div>

    </button>
  );
}


// ==========================================================
// SUMMARY CARD
// ==========================================================

type SummaryCardProps = {
  label: string;

  value: string;

  valueClass?: string;
};


function SummaryCard({
  label,
  value,
  valueClass = "text-slate-200",
}: SummaryCardProps) {

  return (

    <div
      className="
        rounded-xl
        border
        border-slate-800
        bg-slate-950
        p-5
      "
    >

      <p
        className="
          text-xs
          uppercase
          tracking-wider
          text-slate-500
        "
      >
        {label}
      </p>


      <p
        className={`
          mt-2
          font-semibold
          ${valueClass}
        `}
      >
        {value}
      </p>

    </div>
  );
}