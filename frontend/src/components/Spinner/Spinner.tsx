import styles from "./Spinner.module.css";

interface SpinnerProps {
  size?: number;
  label?: string;
}

export function Spinner({ size = 16, label }: SpinnerProps) {
  const style = { width: size, height: size };
  const accessibleLabel = label ?? "Cargando";
  return (
    <span
      className={styles.wrapper}
      role="status"
      aria-label={accessibleLabel}
    >
      <span className={styles.spinner} style={style} aria-hidden="true" />
      {label && <span className={styles.label}>{label}</span>}
    </span>
  );
}
