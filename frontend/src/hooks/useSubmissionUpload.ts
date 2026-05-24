import { useCallback, useEffect, useRef, useState } from "react";
import {
  requestUploadUrl,
  uploadFileToS3,
  startProcessing,
  getSubmissionStatus,
} from "../api/client";
import type { SubmissionStatusResponse } from "../api/types";
import { TERMINAL_STATUSES } from "../api/types";

export type UploadFlowState =
  | "idle"
  | "requesting_url"
  | "uploading"
  | "starting"
  | "polling"
  | "complete"
  | "error";

interface UploadFlowProgress {
  currentStep: string;
  percent: number;
}

interface UseSubmissionUploadReturn {
  upload: (file: File) => void;
  state: UploadFlowState;
  progress: UploadFlowProgress | null;
  error: string | null;
  submission: SubmissionStatusResponse | null;
  reset: () => void;
}

const POLL_INTERVAL_MS = 3000;

export function useSubmissionUpload(
  onComplete?: () => void,
): UseSubmissionUploadReturn {
  const [state, setState] = useState<UploadFlowState>("idle");
  const [progress, setProgress] = useState<UploadFlowProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submission, setSubmission] =
    useState<SubmissionStatusResponse | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const abortRef = useRef(false);

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      abortRef.current = true;
      stopPolling();
    };
  }, [stopPolling]);

  const startPolling = useCallback(
    (submissionId: string) => {
      stopPolling();

      const poll = async () => {
        if (abortRef.current) {
          stopPolling();
          return;
        }
        try {
          const status = await getSubmissionStatus(submissionId);
          setSubmission(status);

          if (status.progress) {
            setProgress({
              currentStep: status.progress.currentStep,
              percent: status.progress.percent,
            });
          }

          if (TERMINAL_STATUSES.has(status.status)) {
            stopPolling();
            setState("complete");
            setProgress(null);
            onComplete?.();
          }
        } catch (err) {
          // On poll error, stop polling and report error
          stopPolling();
          setState("error");
          setError(
            err instanceof Error
              ? err.message
              : "Failed to check processing status",
          );
        }
      };

      // Run immediately then set interval
      poll();
      pollRef.current = setInterval(poll, POLL_INTERVAL_MS);
    },
    [stopPolling, onComplete],
  );

  const upload = useCallback(
    async (file: File) => {
      abortRef.current = false;
      setError(null);
      setSubmission(null);
      setProgress(null);

      try {
        // Step 1: Request upload URL
        setState("requesting_url");
        const urlResponse = await requestUploadUrl({
          fileName: file.name,
          contentType: file.type,
          fileSizeBytes: file.size,
        });

        if (abortRef.current) return;

        // Step 2: Upload file to S3
        setState("uploading");
        setProgress({ currentStep: "Uploading file...", percent: 0 });
        await uploadFileToS3(urlResponse.uploadUrl, file, file.type);

        if (abortRef.current) return;

        // Step 3: Start processing
        setState("starting");
        setProgress({ currentStep: "Starting processing...", percent: 0 });
        await startProcessing(urlResponse.submissionId, {
          objectKey: urlResponse.objectKey,
        });

        if (abortRef.current) return;

        // Step 4: Begin polling
        setState("polling");
        setProgress({ currentStep: "Queued for processing", percent: 5 });
        startPolling(urlResponse.submissionId);
      } catch (err) {
        if (abortRef.current) return;
        setState("error");
        setProgress(null);
        setError(
          err instanceof Error ? err.message : "Upload failed unexpectedly",
        );
      }
    },
    [startPolling],
  );

  const reset = useCallback(() => {
    abortRef.current = true;
    stopPolling();
    setState("idle");
    setProgress(null);
    setError(null);
    setSubmission(null);
  }, [stopPolling]);

  return { upload, state, progress, error, submission, reset };
}
