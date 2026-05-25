import { useCallback, useEffect, useState } from "react";
import { listSubmissions } from "../api/client";
import { PROCESSING_STATUSES, type SubmissionListItem } from "../api/types";

interface UseSubmissionsReturn {
  submissions: SubmissionListItem[];
  loading: boolean;
  loadingMore: boolean;
  error: string | null;
  hasMore: boolean;
  refresh: () => void;
  loadMore: () => void;
  clear: () => void;
}

export function useSubmissions(authReady = true): UseSubmissionsReturn {
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([]);
  const [nextToken, setNextToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mergeUnique = useCallback(
    (existing: SubmissionListItem[], incoming: SubmissionListItem[]) => {
      const seen = new Set(existing.map((item) => item.submissionId));
      return [
        ...existing,
        ...incoming.filter((item) => !seen.has(item.submissionId)),
      ];
    },
    [],
  );

  const fetchSubmissions = useCallback(async (token?: string | null) => {
    if (token) setLoadingMore(true);
    else setLoading(true);
    setError(null);
    try {
      const response = await listSubmissions({ limit: 25, nextToken: token ?? undefined });
      setSubmissions((current) =>
        token ? mergeUnique(current, response.items) : response.items,
      );
      setNextToken(response.nextToken);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load submissions",
      );
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [mergeUnique]);

  useEffect(() => {
    // Do not fetch until auth has settled; otherwise the request races the
    // token exchange and goes out without an Authorization header -> 401.
    if (!authReady) return;
    fetchSubmissions();
  }, [authReady, fetchSubmissions]);

  useEffect(() => {
    if (!authReady) return;
    if (!submissions.some((item) => PROCESSING_STATUSES.has(item.status))) {
      return;
    }
    const interval = window.setInterval(() => {
      fetchSubmissions();
    }, 15_000);
    return () => window.clearInterval(interval);
  }, [authReady, fetchSubmissions, submissions]);

  return {
    submissions,
    loading,
    loadingMore,
    error,
    hasMore: nextToken !== null,
    refresh: () => fetchSubmissions(),
    loadMore: () => {
      if (nextToken && !loadingMore) fetchSubmissions(nextToken);
    },
    clear: () => {
      setSubmissions([]);
      setNextToken(null);
      setError(null);
      setLoading(false);
      setLoadingMore(false);
    },
  };
}
