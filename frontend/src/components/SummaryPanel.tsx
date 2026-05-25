import type {
  SubmissionSummaryResponse,
  ExtractedFacts,
  HazardData,
  AiBrief,
  AiBriefConfidence,
} from "../api/types";

interface SummaryPanelProps {
  summary: SubmissionSummaryResponse | null;
  loading: boolean;
  error: string | null;
  onRetry?: () => void;
  onClose?: () => void;
}

function formatCurrency(value: number): string {
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

function confidenceClass(confidence: AiBriefConfidence): string {
  switch (confidence) {
    case "high":
      return "confidence-pill confidence-pill--high";
    case "medium":
      return "confidence-pill confidence-pill--medium";
    case "low":
    default:
      return "confidence-pill confidence-pill--low";
  }
}

export function SummaryPanel({
  summary,
  loading,
  error,
  onRetry,
  onClose,
}: SummaryPanelProps) {
  return (
    <section className="summary-panel" aria-labelledby="summary-heading">
      <div className="summary-panel-header">
        <h2 id="summary-heading" className="panel-heading">
          Triage Brief
        </h2>
        {onClose && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onClose}
          >
            Close
          </button>
        )}
      </div>

      {loading && (
        <div className="summary-loading" aria-live="polite">
          <span className="upload-spinner" aria-hidden="true" />
          <span>Loading triage brief...</span>
        </div>
      )}

      {!loading && error && (
        <div className="summary-error" role="alert">
          <p>{error}</p>
          {onRetry && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onRetry}>
              Retry
            </button>
          )}
        </div>
      )}

      {!loading && !error && summary && (
        <div className="summary-grid">
          <ExtractedFactsBlock extracted={summary.extracted} />
          <HazardsBlock hazards={summary.hazards} />
          <AiBriefBlock brief={summary.aiBrief} />
          <SourcesBlock sources={summary.sources ?? []} />
        </div>
      )}
    </section>
  );
}

function DataRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="data-row">
      <dt className="data-row-label">{label}</dt>
      <dd className="data-row-value">{value ?? <span className="data-empty">-</span>}</dd>
    </div>
  );
}

function ExtractedFactsBlock({ extracted }: { extracted: ExtractedFacts | null }) {
  const address = extracted?.address ?? null;
  const limits = extracted?.limits ?? null;
  const missingFields = extracted?.missingFields ?? [];
  const addressLine = address
    ? [address.line1, address.city, address.state, address.postalCode]
        .filter(Boolean)
        .join(", ")
    : "";

  return (
    <div className="summary-block">
      <h3 className="summary-block-title">Extracted Facts</h3>
      {extracted ? (
        <dl className="data-list">
          <DataRow label="Insured" value={extracted.insuredName || undefined} />
          <DataRow label="Address" value={addressLine || undefined} />
          <DataRow label="Industry" value={extracted.industry || undefined} />
          <DataRow label="Coverage" value={extracted.requestedCoverage || undefined} />
          <DataRow
            label="Building limit"
            value={
              limits?.building != null ? formatCurrency(limits.building) : undefined
            }
          />
          <DataRow
            label="BPP limit"
            value={
              limits?.businessPersonalProperty != null
                ? formatCurrency(limits.businessPersonalProperty)
                : undefined
            }
          />
        </dl>
      ) : (
        <p className="summary-empty">No extracted facts were saved for this submission.</p>
      )}

      {missingFields.length > 0 && (
        <div className="missing-fields" role="note">
          <span className="missing-fields-label">Missing or unconfirmed</span>
          <ul className="missing-fields-list">
            {missingFields.map((field) => (
              <li key={field} className="missing-field-chip">
                {field}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function HazardsBlock({ hazards }: { hazards: HazardData | null }) {
  const topHazards = hazards?.topHazards ?? [];
  const stormEntries = hazards?.stormEventCounts10Yr
    ? Object.entries(hazards.stormEventCounts10Yr)
    : [];

  return (
    <div className="summary-block">
      <h3 className="summary-block-title">Hazard Profile</h3>
      {hazards ? (
        <dl className="data-list">
          <DataRow label="FEMA risk rating" value={hazards.femaRiskRating || undefined} />
          <DataRow
            label="Disaster declarations"
            value={
              hazards.recentDisasterDeclarations != null
                ? String(hazards.recentDisasterDeclarations)
                : undefined
            }
          />
        </dl>
      ) : (
        <p className="summary-empty">No hazard data was saved for this submission.</p>
      )}

      {topHazards.length > 0 && (
        <div className="hazard-tags">
          {topHazards.map((h) => (
            <span key={h} className="hazard-tag">
              {h}
            </span>
          ))}
        </div>
      )}

      {stormEntries.length > 0 && (
        <table className="storm-table">
          <caption className="storm-caption">Storm events (10 yr)</caption>
          <tbody>
            {stormEntries.map(([type, count]) => (
              <tr key={type}>
                <th scope="row">{type.replace(/([A-Z])/g, " $1").trim()}</th>
                <td>{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function AiBriefBlock({ brief }: { brief: AiBrief | null }) {
  const riskFlags = brief?.riskFlags ?? [];
  const questionsForBroker = brief?.questionsForBroker ?? [];

  return (
    <div className="summary-block summary-block--brief">
      <div className="brief-header">
        <h3 className="summary-block-title">AI Triage Brief</h3>
        {brief?.confidence && (
          <span className={confidenceClass(brief.confidence)}>
            {brief.confidence} confidence
          </span>
        )}
      </div>

      <p className="brief-disclaimer" role="note">
        AI-generated draft for broker review. Verify all facts and figures
        against source documents before acting.
      </p>

      {brief?.executiveSummary ? (
        <p className="brief-summary">{brief.executiveSummary}</p>
      ) : (
        <p className="summary-empty">No AI brief was saved for this submission.</p>
      )}

      {riskFlags.length > 0 && (
        <div className="brief-section">
          <h4 className="brief-subtitle">Risk flags</h4>
          <ul className="brief-list">
            {riskFlags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {questionsForBroker.length > 0 && (
        <div className="brief-section">
          <h4 className="brief-subtitle">Questions for broker</h4>
          <ul className="brief-list">
            {questionsForBroker.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function SourcesBlock({
  sources,
}: {
  sources: SubmissionSummaryResponse["sources"];
}) {
  if (sources.length === 0) return null;
  return (
    <div className="summary-block">
      <h3 className="summary-block-title">Sources</h3>
      <ul className="sources-list">
        {sources.map((source) => (
          <li key={source.url}>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
            >
              {source.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
