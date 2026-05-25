// API Types matching the documented contract at docs/api-contract.md

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

export const TERMINAL_STATUSES: ReadonlySet<SubmissionStatus> = new Set([
  "READY",
  "NEEDS_REVIEW",
  "FAILED",
]);

export const PROCESSING_STATUSES: ReadonlySet<SubmissionStatus> = new Set([
  "QUEUED",
  "OCR_RUNNING",
  "EXTRACTING",
  "ENRICHING",
  "GENERATING_SUMMARY",
]);

// POST /api/submissions/upload-url
export interface UploadUrlRequest {
  fileName: string;
  contentType: string;
  fileSizeBytes: number;
}

export interface UploadUrlResponse {
  submissionId: string;
  uploadUrl: string;
  objectKey: string;
  expiresInSeconds: number;
  maxFileSizeBytes: number;
}

// POST /api/submissions/{submissionId}/start
export interface StartProcessingRequest {
  objectKey: string;
}

export interface StartProcessingResponse {
  submissionId: string;
  status: "QUEUED";
}

// GET /api/submissions/{submissionId}
export interface SubmissionProgress {
  currentStep: string;
  percent: number;
}

export interface SubmissionFile {
  fileName: string;
  contentType: string;
}

export interface SubmissionStatusResponse {
  submissionId: string;
  status: SubmissionStatus;
  createdAt: string;
  updatedAt: string;
  progress: SubmissionProgress | null;
  file: SubmissionFile;
  error: string | null;
}

// GET /api/submissions/{submissionId}/summary
// Only available for READY or NEEDS_REVIEW.
export interface ExtractedAddress {
  line1?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  countyFips?: string;
}

export interface ExtractedLimits {
  building?: number;
  businessPersonalProperty?: number;
  [key: string]: number | undefined;
}

export interface ExtractedFacts {
  insuredName?: string;
  address?: ExtractedAddress;
  industry?: string;
  requestedCoverage?: string;
  limits?: ExtractedLimits;
  missingFields: string[];
}

export interface HazardData {
  femaRiskRating?: string;
  topHazards: string[];
  recentDisasterDeclarations?: number;
  stormEventCounts10Yr?: Record<string, number>;
}

export type AiBriefConfidence = "low" | "medium" | "high";

export interface AiBrief {
  executiveSummary: string;
  riskFlags: string[];
  questionsForBroker: string[];
  confidence: AiBriefConfidence;
}

export interface SourceLink {
  name: string;
  url: string;
}

export interface SubmissionSummaryResponse {
  submissionId: string;
  status: Extract<SubmissionStatus, "READY" | "NEEDS_REVIEW">;
  extracted: ExtractedFacts;
  hazards: HazardData;
  aiBrief: AiBrief;
  sources: SourceLink[];
}

// GET /api/submissions
export interface SubmissionListItem {
  submissionId: string;
  status: SubmissionStatus;
  createdAt: string;
  fileName: string;
}

export interface SubmissionListResponse {
  items: SubmissionListItem[];
  nextToken: string | null;
}

export interface ListSubmissionsParams {
  status?: SubmissionStatus;
  limit?: number;
  nextToken?: string;
}

// Error response shape
export interface ApiErrorResponse {
  message: string;
  code?: string;
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly code: string | undefined;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}
