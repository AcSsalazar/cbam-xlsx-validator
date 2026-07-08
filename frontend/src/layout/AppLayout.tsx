import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import styles from "./AppLayout.module.css";

export function AppLayout() {
  return (
    <div className={styles.app}>
      <Navbar />
      <main className={styles.main}>
        <div className={styles.container}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
