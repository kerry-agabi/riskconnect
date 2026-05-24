import type {
  UploadUrlRequest,
  UploadUrlResponse,
  StartProcessingRequest,
  StartProcessingResponse,
  SubmissionStatusResponse,
  SubmissionListResponse,
  ListSubmissionsParams,
  ApiErrorResponse,
} from "./types";
import { ApiError } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
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
  const response = await fetch(`${BASE_URL}/submissions/upload-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return handleResponse<UploadUrlResponse>(response);
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
  const response = await fetch(
    `${BASE_URL}/submissions/${submissionId}/start`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
  return handleResponse<StartProcessingResponse>(response);
}

/**
 * Get the current status of a submission.
 */
export async function getSubmissionStatus(
  submissionId: string,
): Promise<SubmissionStatusResponse> {
  const response = await fetch(
    `${BASE_URL}/submissions/${submissionId}`,
    { method: "GET" },
  );
  return handleResponse<SubmissionStatusResponse>(response);
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
  const url = `${BASE_URL}/submissions${query ? `?${query}` : ""}`;
  const response = await fetch(url, { method: "GET" });
  return handleResponse<SubmissionListResponse>(response);
}
