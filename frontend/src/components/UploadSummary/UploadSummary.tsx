import styles from "./UploadSummary.module.css";

interface UploadSummaryProps {
  filename: string;
  totalRows: number;
  validRows: number;
  invalidRows: number;
}

export function UploadSummary({
  filename,
  totalRows,
  validRows,
  invalidRows,
}: UploadSummaryProps) {
  return (
    <div className={styles.summary}>
      <div className={styles.header}>
        <p className={styles.filename}>{filename}</p>
        <p className={styles.subtitle}>Upload completed</p>
      </div>
      <div className={styles.stats}>
        <Stat label="Total" value={totalRows} tone="neutral" />
        <Stat label="Valid" value={validRows} tone="success" />
        <Stat label="Invalid" value={invalidRows} tone="error" />
      </div>
    </div>
  );
}

interface StatProps {
  label: string;
  value: number;
  tone: "neutral" | "success" | "error";
}

function Stat({ label, value, tone }: StatProps) {
  return (
    <div className={styles.stat}>
      <span className={`${styles.dot} ${styles[tone]}`} aria-hidden="true" />
      <span className={styles.label}>{label}</span>
      <span className={`${styles.value} ${styles[tone]}`}>{value}</span>
    </div>
  );
}
