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
      setFileError("Solo se aceptan archivos .xlsx");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const result = await uploadFile(file);
      setReport(result);
      void Swal.fire({
        title: "Carga completa",
        text: `${result.valid_rows} de ${result.total_rows} filas importadas.`,
        icon: "success",
        confirmButtonColor: "#2563eb",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      void Swal.fire({
        title: "Error al subir",
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
        <h1>Subir</h1>
        <p className={styles.subtitle}>
          Importe un libro de Excel con formato CBAM y revise los resultados
          de validacion a continuacion.
        </p>
      </header>

      <div className={styles.stack}>
        <Card
          title="Archivo"
          description="Seleccione un archivo .xlsx para importar."
          action={
            <Button
              onClick={handleUpload}
              disabled={!canUpload}
              size="sm"
            >
              {uploading ? <Spinner size={14} /> : null}
              {uploading ? "Subiendo…" : "Subir"}
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
                Limpiar
              </Button>
            )}
          </div>
        </Card>

        {report && (
          <Card
            title="Resumen"
            description="Los conteos incluyen solo las filas presentes en el archivo subido."
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
            title="Errores de validacion"
            description={`${report.errors.length} error${
              report.errors.length === 1 ? "" : "es"
            } en ${countInvalidRows(report.errors)} fila${
              countInvalidRows(report.errors) === 1 ? "" : "s"
            }.`}
          >
            <ErrorTable errors={report.errors} />
          </Card>
        )}

        {report && !showErrors && (
          <Card title="Errores de validacion">
            <EmptyState
              title="Sin errores de validacion"
              description="Todas las filas del archivo pasaron todas las reglas."
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
