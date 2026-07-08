import { useEffect, useRef } from "react";
import { Button } from "../Button/Button";
import styles from "./JsonModal.module.css";

interface JsonModalProps {
  open: boolean;
  title: string;
  data: unknown;
  onClose: () => void;
}

export function JsonModal({ open, title, data, onClose }: JsonModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  const formatted = JSON.stringify(data, null, 2);

  return (
    <div
      className={styles.overlay}
      onClick={onClose}
      role="presentation"
    >
      <div
        ref={dialogRef}
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="json-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className={styles.header}>
          <h3 id="json-modal-title" className={styles.title}>{title}</h3>
          <button
            type="button"
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </header>
        <pre className={styles.code}>{formatted}</pre>
        <footer className={styles.footer}>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </footer>
      </div>
    </div>
  );
}
