import { useMemo } from "react";
import { AppShell } from "./components/AppShell";
import { UploadPanel } from "./components/UploadPanel";
import { RecentSubmissions } from "./components/RecentSubmissions";
import { StatusArea } from "./components/StatusArea";
import type { ActiveProcessing, TerminalResult } from "./components/StatusArea";
import { useSubmissionUpload } from "./hooks/useSubmissionUpload";
import { useSubmissions } from "./hooks/useSubmissions";
import { TERMINAL_STATUSES } from "./api/types";

export function App() {
  const {
    submissions,
    loading: submissionsLoading,
    error: submissionsError,
    refresh: refreshSubmissions,
  } = useSubmissions();

  const { upload, state, progress, error, submission, reset } =
    useSubmissionUpload(refreshSubmissions);

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
          <StatusArea active={activeProcessing} result={terminalResult} />
        </div>
        <div className="workbench-right">
          <RecentSubmissions
            submissions={submissionRows}
            loading={submissionsLoading}
            error={submissionsError}
          />
        </div>
      </div>
    </AppShell>
  );
}
