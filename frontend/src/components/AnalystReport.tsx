"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface AnalystReportProps {
  report: string;
}

interface ReportSection {
  title: string;
  content: string;
}

const SECTION_CONFIG: Record<
  string,
  {
    icon: string;
    label: string;
    border: string;
    background: string;
  }
> = {
  "Risk Assessment": {
    icon: "🛡️",
    label: "Risk Assessment",
    border: "border-cyan-500/30",
    background: "bg-cyan-500/5",
  },

  "Model Evidence": {
    icon: "📊",
    label: "Model Evidence",
    border: "border-blue-500/30",
    background: "bg-blue-500/5",
  },

  "Relevant Fraud Context": {
    icon: "🔎",
    label: "Relevant Fraud Context",
    border: "border-violet-500/30",
    background: "bg-violet-500/5",
  },

  "Recommended Actions": {
    icon: "✅",
    label: "Recommended Actions",
    border: "border-emerald-500/30",
    background: "bg-emerald-500/5",
  },

  Limitations: {
    icon: "⚠️",
    label: "Limitations",
    border: "border-amber-500/30",
    background: "bg-amber-500/5",
  },
};

/*
|--------------------------------------------------------------------------
| REPORT PARSER
|--------------------------------------------------------------------------
|
| The LLM returns:
|
| **Risk Assessment**
| text...
|
| **Model Evidence**
| text...
|
| etc.
|
| This function separates those sections so we can display each one
| as its own visual card.
|
*/

function parseReport(report: string): ReportSection[] {
  const sectionNames = [
    "Risk Assessment",
    "Model Evidence",
    "Relevant Fraud Context",
    "Recommended Actions",
    "Limitations",
  ];

  let normalized = report.trim();

  /*
   * Support both:
   *
   * **Risk Assessment**
   *
   * and
   *
   * ## Risk Assessment
   */

  sectionNames.forEach((section) => {
    const boldRegex = new RegExp(
      `\\*\\*${section}\\*\\*`,
      "g"
    );

    normalized = normalized.replace(
      boldRegex,
      `## ${section}`
    );
  });

  const headingRegex =
    /^##\s+(Risk Assessment|Model Evidence|Relevant Fraud Context|Recommended Actions|Limitations)\s*$/gm;

  const matches = [
    ...normalized.matchAll(headingRegex),
  ];

  if (matches.length === 0) {
    return [
      {
        title: "AI Analysis",
        content: normalized,
      },
    ];
  }

  const sections: ReportSection[] = [];

  matches.forEach((match, index) => {
    const title = match[1];

    const start =
      (match.index ?? 0) + match[0].length;

    const end =
      index + 1 < matches.length
        ? matches[index + 1].index
        : normalized.length;

    const content = normalized
      .slice(start, end)
      .trim();

    sections.push({
      title,
      content,
    });
  });

  return sections;
}

/*
|--------------------------------------------------------------------------
| MAIN COMPONENT
|--------------------------------------------------------------------------
*/

export default function AnalystReport({
  report,
}: AnalystReportProps) {
  if (!report) {
    return null;
  }

  const sections = parseReport(report);

  return (
    <section
      className="
        rounded-2xl
        border
        border-cyan-900/50
        bg-slate-900
        p-7
      "
    >
      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="flex items-start gap-4">
        <div
          className="
            flex
            h-12
            w-12
            shrink-0
            items-center
            justify-center
            rounded-xl
            border
            border-cyan-500/20
            bg-cyan-500/10
            text-xl
          "
        >
          🤖
        </div>

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
            Grounded Generative AI
          </p>

          <h2
            className="
              mt-1
              text-2xl
              font-semibold
              text-white
            "
          >
            AI Fraud Analyst
          </h2>

          <p
            className="
              mt-2
              text-sm
              leading-6
              text-slate-400
            "
          >
            Generated using the model result,
            SHAP evidence, supplied context and
            retrieved fraud knowledge.
          </p>
        </div>
      </div>

      {/* ==================================================
          REPORT SECTIONS
      ================================================== */}

      <div className="mt-7 space-y-5">
        {sections.map((section, index) => {
          const config =
            SECTION_CONFIG[section.title];

          /*
           * Fallback in case the LLM returns
           * an unexpected section.
           */

          const icon =
            config?.icon ?? "📄";

          const label =
            config?.label ?? section.title;

          const border =
            config?.border ??
            "border-slate-700";

          const background =
            config?.background ??
            "bg-slate-950";

          return (
            <article
              key={`${section.title}-${index}`}
              className={`
                overflow-hidden
                rounded-xl
                border
                ${border}
                ${background}
              `}
            >
              {/* SECTION HEADER */}

              <div
                className="
                  flex
                  items-center
                  gap-3
                  border-b
                  border-slate-800/80
                  px-5
                  py-4
                "
              >
                <div
                  className="
                    flex
                    h-9
                    w-9
                    shrink-0
                    items-center
                    justify-center
                    rounded-lg
                    bg-slate-950
                    text-base
                  "
                >
                  {icon}
                </div>

                <h3
                  className="
                    text-base
                    font-semibold
                    text-white
                  "
                >
                  {label}
                </h3>
              </div>

              {/* SECTION CONTENT */}

              <div
                className="
                  px-5
                  py-5
                  text-sm
                  leading-7
                  text-slate-300

                  [&_p]:my-3
                  first:[&_p]:mt-0
                  last:[&_p]:mb-0

                  [&_strong]:font-semibold
                  [&_strong]:text-white

                  [&_ul]:my-4
                  [&_ul]:space-y-3

                  [&_ol]:my-4
                  [&_ol]:space-y-3

                  [&_li]:relative
                  [&_li]:rounded-lg
                  [&_li]:border
                  [&_li]:border-slate-800
                  [&_li]:bg-slate-950/70
                  [&_li]:px-4
                  [&_li]:py-3
                  [&_li]:text-slate-300

                  [&_ul_li]:ml-0
                  [&_ul_li]:list-none

                  [&_ol]:list-none
                  [&_ol]:counter-reset-[item]

                  [&_blockquote]:my-4
                  [&_blockquote]:rounded-lg
                  [&_blockquote]:border-l-4
                  [&_blockquote]:border-cyan-500
                  [&_blockquote]:bg-slate-950
                  [&_blockquote]:px-4
                  [&_blockquote]:py-3

                  [&_table]:my-5
                  [&_table]:w-full
                  [&_table]:border-collapse

                  [&_th]:border
                  [&_th]:border-slate-700
                  [&_th]:bg-slate-800
                  [&_th]:p-3
                  [&_th]:text-left
                  [&_th]:font-semibold
                  [&_th]:text-white

                  [&_td]:border
                  [&_td]:border-slate-800
                  [&_td]:p-3
                  [&_td]:align-top
                "
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    /*
                     * Custom bullet rendering.
                     */

                    li({ children }) {
                      return (
                        <li>
                          <div className="flex gap-3">
                            <span
                              className="
                                mt-[9px]
                                h-2
                                w-2
                                shrink-0
                                rounded-full
                                bg-cyan-400
                              "
                            />

                            <div className="flex-1">
                              {children}
                            </div>
                          </div>
                        </li>
                      );
                    },
                  }}
                >
                  {section.content}
                </ReactMarkdown>
              </div>
            </article>
          );
        })}
      </div>

      {/* ==================================================
          DISCLAIMER
      ================================================== */}

      <div
        className="
          mt-5
          flex
          items-start
          gap-2
          rounded-lg
          border
          border-slate-800
          bg-slate-950/50
          px-4
          py-3
          text-xs
          leading-5
          text-slate-500
        "
      >
        <span className="text-slate-400">
          ⓘ
        </span>

        <p>
          AI-generated analysis should support,
          not replace, human fraud investigation.
        </p>
      </div>
    </section>
  );
}