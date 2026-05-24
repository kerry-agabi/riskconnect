import type { SubmissionStatus } from "../api/types";

export interface ActiveProcessing {
  submissionId: string;
  fileName: string;
  currentStep: string;
  percent: number;
}

export interface TerminalResult {
  submissionId: string;
  fileName: string;
  status: SubmissionStatus;
  error: string | null;
}

interface StatusAreaProps {
  active?: ActiveProcessing | null;
  result?: TerminalResult | null;
}

export function StatusArea({ active = null, result = null }: StatusAreaProps) {
  // Show terminal result if processing is complete
  if (result) {
    return <TerminalResultCard result={result} />;
  }

  if (!active) {
    return (
      <section
        className="status-area status-area--idle"
        aria-label="Processing status"
      >
        <p className="status-idle-text">No active processing</p>
      </section>
    );
  }

  const clampedPercent = Math.max(0, Math.min(100, active.percent));

  return (
    <section className="status-area" aria-label="Processing status">
      <div className="status-header">
        <span className="status-filename" title={active.fileName}>
          {active.fileName}
        </span>
        <span className="status-percent">{clampedPercent}%</span>
      </div>
      <div
        className="status-progress-track"
        role="progressbar"
        aria-valuenow={clampedPercent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Processing ${clampedPercent}% complete`}
      >
        <div
          className="status-progress-fill"
          style={{ width: `${clampedPercent}%` }}
        />
      </div>
      <p className="status-step">{active.currentStep}</p>
    </section>
  );
}

function TerminalResultCard({ result }: { result: TerminalResult }) {
  const { status, fileName, error } = result;

  if (status === "READY") {
    return (
      <section
        className="status-area status-result status-result--success"
        aria-label="Processing complete"
      >
        <div className="status-result-icon" aria-hidden="true">
          &#10003;
        </div>
        <div className="status-result-content">
          <p className="status-result-title">Processing Complete</p>
          <p className="status-result-filename" title={fileName}>
            {fileName}
          </p>
          <p className="status-result-detail">
            Triage brief and extracted data are ready for review.
          </p>
        </div>
        <button type="button" className="btn btn-primary" disabled>
          View Summary
        </button>
      </section>
    );
  }

  if (status === "NEEDS_REVIEW") {
    return (
      <section
        className="status-area status-result status-result--warning"
        aria-label="Review required"
      >
        <div className="status-result-icon" aria-hidden="true">
          &#9888;
        </div>
        <div className="status-result-content">
          <p className="status-result-title">Review Required</p>
          <p className="status-result-filename" title={fileName}>
            {fileName}
          </p>
          <p className="status-result-detail">
            Processing completed but key data is missing or ambiguous. Manual
            review is needed before the brief can be finalized.
          </p>
        </div>
        <button type="button" className="btn btn-secondary" disabled>
          Review Submission
        </button>
      </section>
    );
  }

  // FAILED
  return (
    <section
      className="status-area status-result status-result--error"
      aria-label="Processing failed"
      role="alert"
    >
      <div className="status-result-icon" aria-hidden="true">
        &#10007;
      </div>
      <div className="status-result-content">
        <p className="status-result-title">Processing Failed</p>
        <p className="status-result-filename" title={fileName}>
          {fileName}
        </p>
        {error && <p className="status-result-error">{error}</p>}
      </div>
    </section>
  );
}
