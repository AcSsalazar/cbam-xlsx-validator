import { NavLink } from "react-router-dom";
import { useHealth } from "../hooks/useHealth";
import styles from "./Navbar.module.css";

const HEALTH_LABEL: Record<string, string> = {
  online: "En linea",
  offline: "Fuera de linea",
  checking: "Verificando…",
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
          <div className={styles.logo} aria-hidden="true">
            <img src="/favicon.svg" alt="" className={styles.logoImg} />
          </div>
          <div className={styles.titleBlock}>
            <span className={styles.title}>Validador CBAM</span>
            <span className={styles.subtitle}>Recepcion de datos compartidos</span>
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
            Subir
          </NavLink>
          <NavLink
            to="/records"
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.linkActive : ""}`
            }
          >
            Registros
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
            Backend — {healthLabel(healthy)}
          </span>
        </div>
      </div>
    </header>
  );
}
