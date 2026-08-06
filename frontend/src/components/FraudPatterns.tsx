import type {
  FraudKnowledge,
} from "@/types/fraud";


interface FraudPatternsProps {
  patterns: FraudKnowledge[];
}


export default function FraudPatterns({
  patterns,
}: FraudPatternsProps) {

  if (!patterns || patterns.length === 0) {

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

        <p
          className="
            text-sm
            font-semibold
            uppercase
            tracking-wider
            text-cyan-400
          "
        >
          Semantic Retrieval
        </p>

        <h2
          className="
            mt-2
            text-2xl
            font-semibold
            text-white
          "
        >
          Relevant Fraud Patterns
        </h2>

        <p
          className="
            mt-5
            text-sm
            text-slate-400
          "
        >
          No related fraud knowledge was
          retrieved for this transaction.
        </p>

      </section>
    );
  }


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

      <p
        className="
          text-sm
          font-semibold
          uppercase
          tracking-wider
          text-cyan-400
        "
      >
        Semantic Retrieval
      </p>


      <h2
        className="
          mt-2
          text-2xl
          font-semibold
          text-white
        "
      >
        Relevant Fraud Patterns
      </h2>


      <p
        className="
          mt-2
          text-sm
          leading-6
          text-slate-400
        "
      >
        FraudGuard retrieves related fraud
        knowledge using semantic similarity
        search over the fraud knowledge base.
        Similarity indicates retrieval relevance,
        not the probability that the fraud type
        occurred.
      </p>


      {/* CARDS */}

      <div
        className="
          mt-7
          grid
          gap-5
          lg:grid-cols-3
        "
      >

        {patterns.map(
          (pattern, index) => {

            const similarity =
              Math.min(
                Math.max(
                  pattern.similarity_score *
                    100,
                  0
                ),
                100
              );


            return (
              <article
                key={pattern.id}
                className="
                  flex
                  flex-col
                  rounded-xl
                  border
                  border-slate-800
                  bg-slate-950
                  p-5
                  transition
                  hover:border-slate-700
                "
              >

                {/* TOP */}

                <div
                  className="
                    flex
                    items-start
                    justify-between
                    gap-3
                  "
                >

                  <div>

                    <p
                      className="
                        text-xs
                        font-medium
                        text-slate-500
                      "
                    >
                      Match #{index + 1}
                    </p>


                    <h3
                      className="
                        mt-1
                        font-semibold
                        text-white
                      "
                    >
                      {pattern.title}
                    </h3>

                  </div>


                  <span
                    className="
                      shrink-0
                      rounded-full
                      bg-cyan-500/10
                      px-2.5
                      py-1
                      text-xs
                      font-semibold
                      text-cyan-400
                    "
                  >
                    {similarity.toFixed(1)}%
                  </span>

                </div>


                {/* CATEGORY */}

                <div className="mt-3">

                  <span
                    className="
                      rounded-md
                      bg-slate-800
                      px-2
                      py-1
                      text-xs
                      text-slate-400
                    "
                  >
                    {pattern.category}
                  </span>

                </div>


                {/* SIMILARITY */}

                <div className="mt-5">

                  <div
                    className="
                      mb-2
                      flex
                      justify-between
                      text-xs
                      text-slate-500
                    "
                  >
                    <span>
                      Semantic relevance
                    </span>

                    <span>
                      {similarity.toFixed(1)}%
                    </span>
                  </div>


                  <div
                    className="
                      h-1.5
                      overflow-hidden
                      rounded-full
                      bg-slate-800
                    "
                  >

                    <div
                      className="
                        h-full
                        rounded-full
                        bg-cyan-500
                      "
                      style={{
                        width:
                          `${similarity}%`,
                      }}
                    />

                  </div>

                </div>


                {/* DESCRIPTION */}

                <p
                  className="
                    mt-5
                    text-sm
                    leading-6
                    text-slate-400
                  "
                >
                  {pattern.description}
                </p>


                {/* INDICATORS */}

                <div className="mt-5">

                  <p
                    className="
                      text-xs
                      font-semibold
                      uppercase
                      tracking-wider
                      text-slate-500
                    "
                  >
                    Key Indicators
                  </p>


                  <ul
                    className="
                      mt-3
                      space-y-2
                      text-sm
                      text-slate-400
                    "
                  >

                    {pattern.indicators
                      .slice(0, 3)
                      .map(
                        (
                          indicator,
                          indicatorIndex
                        ) => (

                          <li
                            key={`${pattern.id}-${indicatorIndex}`}
                            className="
                              flex
                              gap-2
                            "
                          >

                            <span
                              className="
                                text-cyan-400
                              "
                            >
                              •
                            </span>

                            <span>
                              {indicator}
                            </span>

                          </li>

                        )
                      )}

                  </ul>

                </div>


                {/* SOURCE */}

                <div
                  className="
                    mt-auto
                    border-t
                    border-slate-800
                    pt-5
                  "
                >

                  <a
                    href={pattern.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                      text-sm
                      font-medium
                      text-cyan-400
                      transition
                      hover:text-cyan-300
                    "
                  >
                    Source: {pattern.source} ↗
                  </a>

                </div>

              </article>
            );
          }
        )}

      </div>


      {/* RETRIEVAL NOTE */}

      <div
        className="
          mt-6
          rounded-xl
          border
          border-slate-800
          bg-slate-950
          p-4
        "
      >

        <p
          className="
            text-xs
            leading-5
            text-slate-500
          "
        >
          Retrieved patterns provide contextual
          knowledge for the AI analyst. A high
          similarity score means the knowledge
          document is semantically related to the
          supplied context; it does not confirm
          that the corresponding fraud technique
          occurred.
        </p>

      </div>

    </section>
  );
}