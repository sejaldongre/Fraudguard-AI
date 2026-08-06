import type { Prediction } from "@/types/fraud";


interface RiskOverviewProps {
  prediction: Prediction;
}


export default function RiskOverview({
  prediction,
}: RiskOverviewProps) {

  const probability =
    prediction.fraud_probability * 100;

  const threshold =
    prediction.threshold * 100;

  const isFraud =
    prediction.label.toLowerCase() === "fraud";

  const riskLevel =
    prediction.risk_level.toUpperCase();


  const riskStyle =
    riskLevel === "HIGH"
      ? {
          text: "text-red-400",
          background: "bg-red-500/10",
          border: "border-red-500/30",
          bar: "bg-red-500",
        }
      : riskLevel === "MEDIUM"
        ? {
            text: "text-amber-400",
            background: "bg-amber-500/10",
            border: "border-amber-500/30",
            bar: "bg-amber-500",
          }
        : {
            text: "text-emerald-400",
            background: "bg-emerald-500/10",
            border: "border-emerald-500/30",
            bar: "bg-emerald-500",
          };


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
              text-sm
              font-semibold
              uppercase
              tracking-wider
              text-cyan-400
            "
          >
            Risk Assessment
          </p>

          <h2
            className="
              mt-2
              text-2xl
              font-semibold
              text-white
            "
          >
            Transaction Analysis
          </h2>

          <p
            className="
              mt-2
              text-sm
              text-slate-400
            "
          >
            XGBoost fraud prediction and
            calibrated decision score.
          </p>

        </div>


        <div className="flex gap-2">

          {/* DECISION BADGE */}

          <span
            className={`
              rounded-full
              border
              px-4
              py-2
              text-sm
              font-semibold

              ${
                isFraud
                  ? `
                    border-red-500/30
                    bg-red-500/10
                    text-red-400
                  `
                  : `
                    border-emerald-500/30
                    bg-emerald-500/10
                    text-emerald-400
                  `
              }
            `}
          >
            {prediction.label}
          </span>


          {/* RISK BADGE */}

          <span
            className={`
              rounded-full
              border
              px-4
              py-2
              text-sm
              font-semibold
              ${riskStyle.text}
              ${riskStyle.background}
              ${riskStyle.border}
            `}
          >
            {riskLevel} RISK
          </span>

        </div>

      </div>


      {/* METRICS */}

      <div
        className="
          mt-8
          grid
          gap-4
          md:grid-cols-3
        "
      >

        <MetricCard
          title="Fraud Probability"
          value={`${probability.toFixed(2)}%`}
          subtitle="Model confidence"
          valueClass={riskStyle.text}
        />

        <MetricCard
          title="Decision"
          value={prediction.label}
          subtitle={
            isFraud
              ? "Flagged for investigation"
              : "Below fraud threshold"
          }
          valueClass={
            isFraud
              ? "text-red-400"
              : "text-emerald-400"
          }
        />

        <MetricCard
          title="Risk Level"
          value={riskLevel}
          subtitle="Assigned risk category"
          valueClass={riskStyle.text}
        />

      </div>


      {/* RISK SCORE */}

      <div
        className="
          mt-8
          rounded-xl
          border
          border-slate-800
          bg-slate-950
          p-5
        "
      >

        <div
          className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-2
          "
        >

          <div>

            <p
              className="
                text-sm
                font-medium
                text-slate-300
              "
            >
              Fraud Risk Score
            </p>

            <p
              className="
                mt-1
                text-xs
                text-slate-500
              "
            >
              Probability produced by the
              fraud detection model.
            </p>

          </div>


          <p
            className={`
              text-lg
              font-bold
              ${riskStyle.text}
            `}
          >
            {probability.toFixed(2)}%
          </p>

        </div>


        {/* BAR + THRESHOLD */}

        <div className="mt-5">

          <div
            className="
              relative
              h-3
              rounded-full
              bg-slate-800
            "
          >

            {/* PROBABILITY */}

            <div
              className={`
                h-full
                rounded-full
                transition-all
                duration-700
                ${riskStyle.bar}
              `}
              style={{
                width: `${Math.min(
                  Math.max(probability, 0),
                  100
                )}%`,
              }}
            />


            {/* THRESHOLD MARKER */}

            <div
              className="
                absolute
                top-[-5px]
                h-5
                w-0.5
                bg-white
              "
              style={{
                left: `${Math.min(
                  Math.max(threshold, 0),
                  100
                )}%`,
              }}
            />

          </div>


          <div
            className="
              relative
              mt-2
              h-5
              text-xs
              text-slate-500
            "
          >

            <span className="absolute left-0">
              0%
            </span>

            <span
              className="
                absolute
                -translate-x-1/2
                text-slate-400
              "
              style={{
                left: `${Math.min(
                  Math.max(threshold, 0),
                  100
                )}%`,
              }}
            >
              Threshold {threshold.toFixed(0)}%
            </span>

            <span className="absolute right-0">
              100%
            </span>

          </div>

        </div>

      </div>

    </section>
  );
}


interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  valueClass?: string;
}


function MetricCard({
  title,
  value,
  subtitle,
  valueClass = "text-white",
}: MetricCardProps) {

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
          text-sm
          text-slate-400
        "
      >
        {title}
      </p>


      <p
        className={`
          mt-2
          text-3xl
          font-bold
          ${valueClass}
        `}
      >
        {value}
      </p>


      <p
        className="
          mt-2
          text-xs
          text-slate-500
        "
      >
        {subtitle}
      </p>

    </div>
  );
}