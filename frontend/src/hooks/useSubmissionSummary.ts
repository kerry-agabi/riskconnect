import { useCallback, useEffect, useRef, useState } from "react";
import { getSubmissionSummary } from "../api/client";
import type { SubmissionSummaryResponse } from "../api/types";

interface UseSubmissionSummaryReturn {
  summary: SubmissionSummaryResponse | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/**
 * Fetches the triage summary for a submission. Pass `null` to clear / skip.
 * Summary is only valid once status is READY or NEEDS_REVIEW; the caller is
 * responsible for only supplying an id in those states.
 */
export function useSubmissionSummary(
  submissionId: string | null,
): UseSubmissionSummaryReturn {
  const [summary, setSummary] = useState<SubmissionSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeId = useRef<string | null>(null);

  const fetchSummary = useCallback(async (id: string) => {
    activeId.current = id;
    setLoading(true);
    setError(null);
    try {
      const result = await getSubmissionSummary(id);
      // Ignore stale responses if the requested id changed mid-flight.
      if (activeId.current !== id) return;
      setSummary(result);
    } catch (err) {
      if (activeId.current !== id) return;
      setError(
        err instanceof Error ? err.message : "Failed to load triage summary",
      );
    } finally {
      if (activeId.current === id) setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!submissionId) {
      activeId.current = null;
      setSummary(null);
      setError(null);
      setLoading(false);
      return;
    }
    fetchSummary(submissionId);
  }, [submissionId, fetchSummary]);

  const reload = useCallback(() => {
    if (submissionId) fetchSummary(submissionId);
  }, [submissionId, fetchSummary]);

  return { summary, loading, error, reload };
}
