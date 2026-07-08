import { NavLink } from "react-router-dom";
import { useHealth } from "../hooks/useHealth";
import styles from "./Navbar.module.css";

const HEALTH_LABEL: Record<string, string> = {
  online: "Online",
  offline: "Offline",
  checking: "Checking…",
};

function healthLabel(state: boolean | null): string {
  if (state === null) return HEALTH_LABEL.checking;
  return state ? HEALTH_LABEL.online : HEALTH_LABEL.offline;
}

export function Navbar() {
  const healthy = useHealth();

  return (
    <header className={styles.navbar}>
      <div className={styles.inner}>
        <div className={styles.brand}>
          <div className={styles.logo} aria-hidden="true">C</div>
          <div className={styles.titleBlock}>
            <span className={styles.title}>CBAM Validator</span>
            <span className={styles.subtitle}>Shared Data Intake</span>
          </div>
        </div>

        <nav className={styles.nav} aria-label="Main">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.linkActive : ""}`
            }
          >
            Upload
          </NavLink>
          <NavLink
            to="/records"
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.linkActive : ""}`
            }
          >
            Records
          </NavLink>
        </nav>

        <div className={styles.health} aria-live="polite">
          <span
            className={`${styles.dot} ${
              healthy === null
                ? styles.dotChecking
                : healthy
                  ? styles.dotOnline
                  : styles.dotOffline
            }`}
            aria-hidden="true"
          />
          <span className={styles.healthLabel}>
            Backend · {healthLabel(healthy)}
          </span>
        </div>
      </div>
    </header>
  );
}
