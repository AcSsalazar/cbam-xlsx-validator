import type { ChangeEvent } from "react";
import { useRef } from "react";
import styles from "./FileUploader.module.css";

interface FileUploaderProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  accept?: string;
  disabled?: boolean;
  error?: string | null;
}

const MAX_BYTES = 20 * 1024 * 1024; // 20 MB

export function FileUploader({
  file,
  onFileChange,
  accept = ".xlsx",
  disabled = false,
  error,
}: FileUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const next = event.target.files?.[0] ?? null;
    if (next && !next.name.toLowerCase().endsWith(".xlsx")) {
      onFileChange(null);
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    if (next && next.size > MAX_BYTES) {
      onFileChange(null);
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    onFileChange(next);
  };

  const handleClear = () => {
    onFileChange(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className={styles.wrapper}>
      <label
        className={`${styles.dropzone} ${disabled ? styles.disabled : ""} ${
          file ? styles.hasFile : ""
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          disabled={disabled}
          className={styles.input}
        />
        {!file && (
          <div className={styles.placeholder}>
              <p className={styles.placeholderTitle}>
                Selecciona un archivo .xlsx
              </p>
              <p className={styles.placeholderHint}>
                Tamaño maximo: 20 MB
              </p>
          </div>
        )}
        {file && (
          <div className={styles.fileInfo}>
            <div className={styles.fileMeta}>
              <p className={styles.fileName}>{file.name}</p>
              <p className={styles.fileSize}>{formatBytes(file.size)}</p>
            </div>
            <button
              type="button"
              className={styles.removeButton}
              onClick={(e) => {
                e.preventDefault();
                handleClear();
              }}
              disabled={disabled}
            >
              Remove
            </button>
          </div>
        )}
      </label>
      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
