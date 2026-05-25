import type {
  UploadUrlRequest,
  UploadUrlResponse,
  StartProcessingRequest,
  StartProcessingResponse,
  SubmissionStatusResponse,
  SubmissionSummaryResponse,
  SubmissionListResponse,
  ListSubmissionsParams,
  ApiErrorResponse,
} from "./types";
import { ApiError } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Auth-token seam. Deployed environments inject a Cognito JWT here so the
 * client sends `Authorization: Bearer <token>` on every backend request.
 * Local/dev leaves this unset and requests go out unauthenticated.
 */
type TokenProvider = () => string | null | undefined | Promise<string | null | undefined>;

let tokenProvider: TokenProvider | null = null;
let unauthorizedHandler: (() => void | Promise<void>) | null = null;

export function setAuthTokenProvider(provider: TokenProvider | null): void {
  tokenProvider = provider;
}

export function setUnauthorizedHandler(
  handler: (() => void | Promise<void>) | null,
): void {
  unauthorizedHandler = handler;
}

async function authHeaders(): Promise<Record<string, string>> {
  if (!tokenProvider) return {};
  const token = await tokenProvider();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * fetch wrapper for backend (`/api`) requests. Injects auth + JSON handling.
 * Not used for the direct S3 presigned PUT, which must not carry our headers.
 */
async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const auth = await authHeaders();
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { ...auth, ...(init?.headers ?? {}) },
  });
  return handleResponse<T>(response);
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401 && unauthorizedHandler) {
      await unauthorizedHandler();
    }
    let message = `Request failed with status ${response.status}`;
    let code: string | undefined;
    try {
      const body: ApiErrorResponse = await response.json();
      if (body.message) message = body.message;
      code = body.code;
    } catch {
      // Could not parse error body; use default message
    }
    throw new ApiError(message, response.status, code);
  }
  return response.json() as Promise<T>;
}

/**
 * Request a presigned upload URL for a new submission.
 */
export async function requestUploadUrl(
  request: UploadUrlRequest,
): Promise<UploadUrlResponse> {
  return apiFetch<UploadUrlResponse>("/submissions/upload-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

/**
 * Upload a file directly to S3 using the presigned URL.
 */
export async function uploadFileToS3(
  uploadUrl: string,
  file: File,
  contentType: string,
): Promise<void> {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers: { "Content-Type": contentType },
    body: file,
  });
  if (!response.ok) {
    throw new ApiError(
      `S3 upload failed with status ${response.status}`,
      response.status,
    );
  }
}

/**
 * Start processing a submitted file.
 */
export async function startProcessing(
  submissionId: string,
  request: StartProcessingRequest,
): Promise<StartProcessingResponse> {
  return apiFetch<StartProcessingResponse>(
    `/submissions/${submissionId}/start`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
}

/**
 * Get the current status of a submission.
 */
export async function getSubmissionStatus(
  submissionId: string,
): Promise<SubmissionStatusResponse> {
  return apiFetch<SubmissionStatusResponse>(`/submissions/${submissionId}`, {
    method: "GET",
  });
}

/**
 * Get the full triage summary for a submission.
 * Only valid once status is READY or NEEDS_REVIEW.
 */
export async function getSubmissionSummary(
  submissionId: string,
): Promise<SubmissionSummaryResponse> {
  return apiFetch<SubmissionSummaryResponse>(
    `/submissions/${submissionId}/summary`,
    { method: "GET" },
  );
}

/**
 * List submissions with optional filters.
 */
export async function listSubmissions(
  params?: ListSubmissionsParams,
): Promise<SubmissionListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.nextToken) searchParams.set("nextToken", params.nextToken);

  const query = searchParams.toString();
  return apiFetch<SubmissionListResponse>(
    `/submissions${query ? `?${query}` : ""}`,
    { method: "GET" },
  );
}
