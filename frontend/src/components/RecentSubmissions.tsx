export type SubmissionStatus =
  | "UPLOADED"
  | "QUEUED"
  | "OCR_RUNNING"
  | "EXTRACTING"
  | "ENRICHING"
  | "GENERATING_SUMMARY"
  | "READY"
  | "NEEDS_REVIEW"
  | "FAILED";

export interface SubmissionRow {
  submissionId: string;
  fileName: string;
  status: SubmissionStatus;
  createdAt: string;
}

interface RecentSubmissionsProps {
  submissions?: SubmissionRow[];
  loading?: boolean;
  loadingMore?: boolean;
  error?: string | null;
  hasMore?: boolean;
  onLoadMore?: () => void;
  onSelect?: (submissionId: string) => void;
}

const REVIEWABLE: ReadonlySet<SubmissionStatus> = new Set([
  "READY",
  "NEEDS_REVIEW",
]);

function getStatusBadgeClass(status: SubmissionStatus): string {
  switch (status) {
    case "READY":
      return "badge badge--success";
    case "NEEDS_REVIEW":
      return "badge badge--warning";
    case "FAILED":
      return "badge badge--danger";
    case "QUEUED":
    case "OCR_RUNNING":
    case "EXTRACTING":
    case "ENRICHING":
    case "GENERATING_SUMMARY":
      return "badge badge--processing";
    case "UPLOADED":
    default:
      return "badge badge--neutral";
  }
}

function formatDate(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function formatStatusLabel(status: SubmissionStatus): string {
  return status.replace(/_/g, " ");
}

function SkeletonRows() {
  return (
    <div className="skeleton-list" aria-label="Loading submissions">
      {[1, 2, 3].map((i) => (
        <div key={i} className="skeleton-row">
          <span className="skeleton-block skeleton-block--name" />
          <span className="skeleton-block skeleton-block--badge" />
          <span className="skeleton-block skeleton-block--date" />
        </div>
      ))}
    </div>
  );
}

export function RecentSubmissions({
  submissions = [],
  loading = false,
  loadingMore = false,
  error = null,
  hasMore = false,
  onLoadMore,
  onSelect,
}: RecentSubmissionsProps) {
  return (
    <section
      className="recent-submissions"
      aria-labelledby="recent-heading"
    >
      <h2 id="recent-heading" className="panel-heading">
        Recent Submissions
      </h2>

      {loading && <SkeletonRows />}

      {!loading && error && (
        <p className="submissions-error" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && submissions.length === 0 && (
        <p className="empty-state">No submissions yet</p>
      )}

      {!loading && !error && submissions.length > 0 && (
        <>
          <div className="table-wrapper">
            <table className="submissions-table">
              <thead>
                <tr>
                  <th scope="col">File Name</th>
                  <th scope="col">Status</th>
                  <th scope="col">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => {
                  const reviewable = onSelect && REVIEWABLE.has(sub.status);
                  return (
                    <tr
                      key={sub.submissionId}
                      className={reviewable ? "submissions-row--clickable" : undefined}
                      onClick={
                        reviewable ? () => onSelect(sub.submissionId) : undefined
                      }
                      tabIndex={reviewable ? 0 : undefined}
                      role={reviewable ? "button" : undefined}
                      aria-label={
                        reviewable ? `Open triage brief for ${sub.fileName}` : undefined
                      }
                      onKeyDown={
                        reviewable
                          ? (e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                onSelect(sub.submissionId);
                              }
                            }
                          : undefined
                      }
                    >
                      <td className="cell-filename" title={sub.fileName}>
                        {sub.fileName}
                      </td>
                      <td>
                        <span className={getStatusBadgeClass(sub.status)}>
                          {formatStatusLabel(sub.status)}
                        </span>
                      </td>
                      <td className="cell-date">{formatDate(sub.createdAt)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {hasMore && onLoadMore && (
            <div className="submissions-footer">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={onLoadMore}
                disabled={loadingMore}
              >
                {loadingMore ? "Loading..." : "Load more"}
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
