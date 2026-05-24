import { useRef, useState } from "react";
import type { UploadFlowState } from "../hooks/useSubmissionUpload";

const ACCEPTED_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "text/plain",
];
const ACCEPTED_EXTENSIONS = ".pdf,.png,.jpg,.jpeg,.txt";
const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1_000_000;

interface UploadPanelProps {
  onUpload?: (file: File) => void;
  uploadState?: UploadFlowState;
  uploadError?: string | null;
  onReset?: () => void;
}

function getUploadStateLabel(state: UploadFlowState): string | null {
  switch (state) {
    case "requesting_url":
      return "Requesting upload...";
    case "uploading":
      return "Uploading file...";
    case "starting":
      return "Starting processing...";
    case "polling":
      return "Processing submission...";
    default:
      return null;
  }
}

export function UploadPanel({
  onUpload,
  uploadState = "idle",
  uploadError = null,
  onReset,
}: UploadPanelProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const isUploading =
    uploadState === "requesting_url" ||
    uploadState === "uploading" ||
    uploadState === "starting" ||
    uploadState === "polling";

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return `Unsupported file type. Accepted: PDF, PNG, JPEG, TXT.`;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `File exceeds ${MAX_FILE_SIZE_MB} MB limit.`;
    }
    return null;
  };

  const handleFile = (file: File) => {
    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      setSelectedFile(null);
    } else {
      setValidationError(null);
      setSelectedFile(file);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleBrowseClick = () => {
    if (isUploading) return;
    inputRef.current?.click();
  };

  const handleSubmit = () => {
    if (!selectedFile || isUploading) return;
    onUpload?.(selectedFile);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setValidationError(null);
    if (inputRef.current) inputRef.current.value = "";
    onReset?.();
  };

  const displayError = validationError || uploadError;
  const stateLabel = getUploadStateLabel(uploadState);

  return (
    <section className="upload-panel" aria-labelledby="upload-heading">
      <h2 id="upload-heading" className="panel-heading">
        Upload Submission
      </h2>

      <div
        className={`upload-dropzone ${dragOver ? "upload-dropzone--active" : ""} ${isUploading ? "upload-dropzone--disabled" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        role="button"
        tabIndex={isUploading ? -1 : 0}
        aria-label="Drop file here or click to browse"
        aria-disabled={isUploading}
        onClick={handleBrowseClick}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleBrowseClick();
          }
        }}
      >
        <div className="upload-dropzone-content">
          <span className="upload-icon" aria-hidden="true">
            &#8593;
          </span>
          <p className="upload-dropzone-label">
            Drag and drop a file, or click to browse
          </p>
          <p className="upload-dropzone-hint">
            PDF, PNG, JPEG, or TXT — up to {MAX_FILE_SIZE_MB} MB
          </p>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS}
        onChange={handleInputChange}
        className="upload-input-hidden"
        aria-label="Select file"
        tabIndex={-1}
        disabled={isUploading}
      />

      {displayError && (
        <p className="upload-error" role="alert">
          {displayError}
        </p>
      )}

      {stateLabel && (
        <div className="upload-state-indicator" aria-live="polite">
          <span className="upload-spinner" aria-hidden="true" />
          <span className="upload-state-label">{stateLabel}</span>
        </div>
      )}

      {selectedFile && !stateLabel && (
        <div className="upload-file-info">
          <span className="upload-file-name" title={selectedFile.name}>
            {selectedFile.name}
          </span>
          <span className="upload-file-size">
            {(selectedFile.size / 1_000_000).toFixed(2)} MB
          </span>
          <div className="upload-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={isUploading}
            >
              Clear
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={isUploading}
            >
              Upload
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
