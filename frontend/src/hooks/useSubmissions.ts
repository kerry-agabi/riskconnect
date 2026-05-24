import { useCallback, useEffect, useState } from "react";
import { listSubmissions } from "../api/client";
import type { SubmissionListItem } from "../api/types";

interface UseSubmissionsReturn {
  submissions: SubmissionListItem[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useSubmissions(): UseSubmissionsReturn {
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubmissions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listSubmissions({ limit: 25 });
      setSubmissions(response.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load submissions",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  return {
    submissions,
    loading,
    error,
    refresh: fetchSubmissions,
  };
}
