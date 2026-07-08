import type { ReactNode } from "react";
import styles from "./Card.module.css";

interface CardProps {
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
}

export function Card({ title, description, action, children }: CardProps) {
  return (
    <section className={styles.card}>
      {(title || description || action) && (
        <header className={styles.header}>
          <div className={styles.titleBlock}>
            {title && <h2 className={styles.title}>{title}</h2>}
            {description && (
              <p className={styles.description}>{description}</p>
            )}
          </div>
          {action && <div className={styles.action}>{action}</div>}
        </header>
      )}
      <div className={styles.body}>{children}</div>
    </section>
  );
}
