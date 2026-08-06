import type { Explanation } from "@/types/fraud";


interface ShapChartProps {
  explanation: Explanation;
}


export default function ShapChart({
  explanation,
}: ShapChartProps) {

  const features =
    explanation.top_features ?? [];


  if (features.length === 0) {

    return (
      <section
        className="
          rounded-2xl
          border
          border-slate-800
          bg-slate-900
          p-7
        "
      >
        <p className="text-slate-400">
          No SHAP explanation is available.
        </p>
      </section>
    );
  }


  const maximumImpact = Math.max(
    ...features.map(
      (feature) =>
        Math.abs(feature.shap_value)
    ),
    1
  );


  return (
    <section
      className="
        rounded-2xl
        border
        border-slate-800
        bg-slate-900
        p-7
      "
    >

      {/* HEADER */}

      <div>

        <p
          className="
            text-sm
            font-semibold
            uppercase
            tracking-wider
            text-cyan-400
          "
        >
          Explainable AI
        </p>


        <h2
          className="
            mt-2
            text-2xl
            font-semibold
            text-white
          "
        >
          Top SHAP Contributors
        </h2>


        <p
          className="
            mt-2
            text-sm
            leading-6
            text-slate-400
          "
        >
          SHAP measures how each feature
          influenced the model&apos;s fraud score
          for this transaction.
        </p>

      </div>


      {/* LEGEND */}

      <div
        className="
          mt-6
          flex
          flex-wrap
          gap-4
          text-xs
          text-slate-400
        "
      >

        <div className="flex items-center gap-2">

          <span
            className="
              h-2.5
              w-2.5
              rounded-full
              bg-red-500
            "
          />

          Increases fraud score

        </div>


        <div className="flex items-center gap-2">

          <span
            className="
              h-2.5
              w-2.5
              rounded-full
              bg-emerald-500
            "
          />

          Decreases fraud score

        </div>

      </div>


      {/* FEATURES */}

      <div className="mt-8 space-y-6">

        {features.map(
          (feature, index) => {

            const percentage =
              (
                Math.abs(
                  feature.shap_value
                ) /
                maximumImpact
              ) * 100;


            const increasesRisk =
              feature.impact ===
              "increases_fraud_score";


            return (
              <div
                key={feature.feature}
                className="
                  rounded-xl
                  border
                  border-slate-800
                  bg-slate-950
                  p-4
                "
              >

                <div
                  className="
                    mb-3
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-3
                  "
                >

                  <div
                    className="
                      flex
                      items-center
                      gap-3
                    "
                  >

                    {/* RANK */}

                    <span
                      className="
                        flex
                        h-7
                        w-7
                        items-center
                        justify-center
                        rounded-lg
                        bg-slate-800
                        text-xs
                        font-semibold
                        text-slate-400
                      "
                    >
                      {index + 1}
                    </span>


                    <div>

                      <p
                        className="
                          font-semibold
                          text-white
                        "
                      >
                        {feature.feature}
                      </p>

                      <p
                        className="
                          text-xs
                          text-slate-500
                        "
                      >
                        Feature value:{" "}
                        {feature.feature_value.toFixed(3)}
                      </p>

                    </div>

                  </div>


                  <div className="text-right">

                    <p
                      className={
                        increasesRisk
                          ? `
                            font-semibold
                            text-red-400
                          `
                          : `
                            font-semibold
                            text-emerald-400
                          `
                      }
                    >
                      {feature.shap_value > 0
                        ? "+"
                        : ""}
                      {feature.shap_value.toFixed(3)}
                    </p>

                    <p
                      className="
                        text-xs
                        text-slate-500
                      "
                    >
                      SHAP impact
                    </p>

                  </div>

                </div>


                {/* IMPACT BAR */}

                <div
                  className="
                    h-2.5
                    overflow-hidden
                    rounded-full
                    bg-slate-800
                  "
                >

                  <div
                    className={`
                      h-full
                      rounded-full
                      transition-all
                      duration-700

                      ${
                        increasesRisk
                          ? "bg-red-500"
                          : "bg-emerald-500"
                      }
                    `}
                    style={{
                      width: `${percentage}%`,
                    }}
                  />

                </div>


                <p
                  className={`
                    mt-2
                    text-xs

                    ${
                      increasesRisk
                        ? "text-red-400/80"
                        : "text-emerald-400/80"
                    }
                  `}
                >
                  {increasesRisk
                    ? "↑ Pushes prediction toward fraud"
                    : "↓ Pushes prediction toward legitimate"}
                </p>

              </div>
            );
          }
        )}

      </div>


      {/* SUMMARY */}

      <div
        className="
          mt-7
          rounded-xl
          border
          border-cyan-900/40
          bg-cyan-500/5
          p-4
        "
      >

        <p
          className="
            text-xs
            font-semibold
            uppercase
            tracking-wider
            text-cyan-400
          "
        >
          Explanation Summary
        </p>

        <p
          className="
            mt-2
            text-sm
            leading-6
            text-slate-300
          "
        >
          {explanation.summary}
        </p>

      </div>


      {/* DISCLAIMER */}

      <p
        className="
          mt-4
          text-xs
          leading-5
          text-slate-500
        "
      >
        V1-V28 are anonymized transformed
        variables. SHAP explains their influence
        on the prediction, but FraudGuard does
        not assign real-world business meanings
        to these features.
      </p>

    </section>
  );
}