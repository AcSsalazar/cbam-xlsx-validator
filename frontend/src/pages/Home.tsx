import { useState } from "react";
import Swal from "sweetalert2";
import { Card } from "../components/Card/Card";
import { Button } from "../components/Button/Button";
import { Spinner } from "../components/Spinner/Spinner";
import { FileUploader } from "../components/FileUploader/FileUploader";
import { UploadSummary } from "../components/UploadSummary/UploadSummary";
import { ErrorTable } from "../components/ErrorTable/ErrorTable";
import { EmptyState } from "../components/EmptyState/EmptyState";
import { uploadFile } from "../services/uploads";
import type { UploadReport } from "../types/api";
import styles from "./Home.module.css";

export function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [report, setReport] = useState<UploadReport | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (next: File | null) => {
    setFile(next);
    setFileError(null);
    if (next && !next.name.toLowerCase().endsWith(".xlsx")) {
      setFileError("Only .xlsx files are accepted");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const result = await uploadFile(file);
      setReport(result);
      void Swal.fire({
        title: "Upload complete",
        text: `${result.valid_rows} of ${result.total_rows} rows imported.`,
        icon: "success",
        confirmButtonColor: "#2563eb",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      void Swal.fire({
        title: "Upload failed",
        text: message,
        icon: "error",
        confirmButtonColor: "#2563eb",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setFileError(null);
    setReport(null);
  };

  const canUpload = !!file && !fileError && !uploading;
  const showErrors = report && report.errors.length > 0;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Upload</h1>
        <p className={styles.subtitle}>
          Import a CBAM-formatted Excel workbook and review the validation
          results below.
        </p>
      </header>

      <div className={styles.stack}>
        <Card
          title="File"
          description="Select a .xlsx workbook to import."
          action={
            <Button
              onClick={handleUpload}
              disabled={!canUpload}
              size="sm"
            >
              {uploading ? <Spinner size={14} /> : null}
              {uploading ? "Uploading…" : "Upload"}
            </Button>
          }
        >
          <div className={styles.uploaderRow}>
            <FileUploader
              file={file}
              onFileChange={handleFileChange}
              error={fileError}
              disabled={uploading}
            />
            {report && (
              <Button variant="ghost" size="sm" onClick={handleReset}>
                Clear
              </Button>
            )}
          </div>
        </Card>

        {report && (
          <Card
            title="Summary"
            description="Counts include only the rows present in the uploaded file."
          >
            <UploadSummary
              filename={report.filename}
              totalRows={report.total_rows}
              validRows={report.valid_rows}
              invalidRows={report.invalid_rows}
            />
          </Card>
        )}

        {showErrors && (
          <Card
            title="Validation errors"
            description={`${report.errors.length} error${
              report.errors.length === 1 ? "" : "s"
            } across ${countInvalidRows(report.errors)} row${
              countInvalidRows(report.errors) === 1 ? "" : "s"
            }.`}
          >
            <ErrorTable errors={report.errors} />
          </Card>
        )}

        {report && !showErrors && (
          <Card title="Validation errors">
            <EmptyState
              title="No validation errors"
              description="Every row in the file passed all rules."
            />
          </Card>
        )}
      </div>
    </div>
  );
}

function countInvalidRows(errors: ReadonlyArray<{ row: number }>): number {
  return new Set(errors.map((e) => e.row)).size;
}
