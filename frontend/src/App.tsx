import { useCallback, useEffect, useMemo, useState } from "react";
import { AppShell } from "./components/AppShell";
import { UploadPanel } from "./components/UploadPanel";
import { RecentSubmissions } from "./components/RecentSubmissions";
import { StatusArea } from "./components/StatusArea";
import type { ActiveProcessing, TerminalResult } from "./components/StatusArea";
import { SummaryPanel } from "./components/SummaryPanel";
import { useSubmissionUpload } from "./hooks/useSubmissionUpload";
import { useSubmissions } from "./hooks/useSubmissions";
import { useSubmissionSummary } from "./hooks/useSubmissionSummary";
import { TERMINAL_STATUSES } from "./api/types";
import { installCognitoAuth } from "./auth/cognito";

export function App() {
  useEffect(() => {
    void installCognitoAuth();
  }, []);

  const {
    submissions,
    loading: submissionsLoading,
    loadingMore: submissionsLoadingMore,
    error: submissionsError,
    hasMore: submissionsHasMore,
    refresh: refreshSubmissions,
    loadMore: loadMoreSubmissions,
  } = useSubmissions();

  const { upload, state, progress, error, submission, reset } =
    useSubmissionUpload(refreshSubmissions);

  const [selectedSummaryId, setSelectedSummaryId] = useState<string | null>(
    null,
  );
  const {
    summary,
    loading: summaryLoading,
    error: summaryError,
    reload: reloadSummary,
  } = useSubmissionSummary(selectedSummaryId);

  const handleViewSummary = useCallback((submissionId: string) => {
    setSelectedSummaryId(submissionId);
  }, []);

  const handleCloseSummary = useCallback(() => {
    setSelectedSummaryId(null);
  }, []);

  const handleRetry = useCallback(() => {
    setSelectedSummaryId(null);
    reset();
  }, [reset]);

  // Derive active processing state for the StatusArea progress bar
  const activeProcessing: ActiveProcessing | null = useMemo(() => {
    if (state === "polling" && progress && submission) {
      return {
        submissionId: submission.submissionId,
        fileName: submission.file.fileName,
        currentStep: progress.currentStep,
        percent: progress.percent,
      };
    }
    if (
      (state === "requesting_url" ||
        state === "uploading" ||
        state === "starting") &&
      progress
    ) {
      return {
        submissionId: "",
        fileName: "",
        currentStep: progress.currentStep,
        percent: progress.percent,
      };
    }
    return null;
  }, [state, progress, submission]);

  // Derive terminal result state
  const terminalResult: TerminalResult | null = useMemo(() => {
    if (state === "complete" && submission && TERMINAL_STATUSES.has(submission.status)) {
      return {
        submissionId: submission.submissionId,
        fileName: submission.file.fileName,
        status: submission.status,
        error: submission.error,
      };
    }
    return null;
  }, [state, submission]);

  // Map API list items to the row format expected by RecentSubmissions
  const submissionRows = useMemo(
    () =>
      submissions.map((item) => ({
        submissionId: item.submissionId,
        fileName: item.fileName,
        status: item.status,
        createdAt: item.createdAt,
      })),
    [submissions],
  );

  return (
    <AppShell>
      <div className="workbench">
        <div className="workbench-left">
          <UploadPanel
            onUpload={upload}
            uploadState={state}
            uploadError={error}
            onReset={reset}
          />
          <StatusArea
            active={activeProcessing}
            result={terminalResult}
            onViewSummary={handleViewSummary}
            onRetry={handleRetry}
          />
          {selectedSummaryId && (
            <SummaryPanel
              summary={summary}
              loading={summaryLoading}
              error={summaryError}
              onRetry={reloadSummary}
              onClose={handleCloseSummary}
            />
          )}
        </div>
        <div className="workbench-right">
          <RecentSubmissions
            submissions={submissionRows}
            loading={submissionsLoading}
            loadingMore={submissionsLoadingMore}
            error={submissionsError}
            hasMore={submissionsHasMore}
            onLoadMore={loadMoreSubmissions}
            onSelect={handleViewSummary}
          />
        </div>
      </div>
    </AppShell>
  );
}
