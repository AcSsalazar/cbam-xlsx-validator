import { useEffect, useState } from "react";
import { checkHealth } from "../services/health";

/** Polls GET /health on a fixed interval; null while the first check is in flight. */
export function useHealth(intervalMs = 30_000): boolean | null {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      const ok = await checkHealth();
      if (!cancelled) {
        setHealthy(ok);
      }
    };

    void check();
    const id = setInterval(check, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [intervalMs]);

  return healthy;
}
