import { useCallback, useEffect, useState } from "react";
import Swal from "sweetalert2";
import { Card } from "../components/Card/Card";
import { Table, type Column } from "../components/Table/Table";
import { Pagination } from "../components/Pagination/Pagination";
import { Spinner } from "../components/Spinner/Spinner";
import { EmptyState } from "../components/EmptyState/EmptyState";
import { Button } from "../components/Button/Button";
import { JsonModal } from "../components/JsonModal/JsonModal";
import { listRecords } from "../services/records";
import type { PaginatedRecords, RecordItem } from "../types/api";
import styles from "./RecordsPage.module.css";

const PAGE_SIZE = 20;
const PREVIEW_KEYS = [
  "EORI Number",
  "CN Code",
  "Import Volume",
  "Date of importation",
  "Country of Origin",
  "Supplier Name",
] as const;

interface PreviewItem extends RecordItem {
  preview: Record<string, string>;
}

function buildPreview(payload: Record<string, string>): Record<string, string> {
  const result: Record<string, string> = {};
  for (const key of PREVIEW_KEYS) {
    if (key in payload) {
      result[key] = payload[key] ?? "";
    }
  }
  if (Object.keys(result).length === 0) {
    const first = Object.entries(payload)[0];
    if (first) {
      result[first[0]] = first[1] ?? "";
    }
  }
  return result;
}

export function RecordsPage() {
  const [data, setData] = useState<PaginatedRecords | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<RecordItem | null>(null);

  const load = useCallback(async (target: number) => {
    setLoading(true);
    try {
      const result = await listRecords(target, PAGE_SIZE);
      setData(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load records";
      void Swal.fire({
        title: "Server error",
        text: message,
        icon: "error",
        confirmButtonColor: "#2563eb",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(page);
  }, [load, page]);

  const handlePageChange = (next: number) => {
    setPage(next);
  };

  const handleOpenJson = (item: RecordItem) => {
    setSelected(item);
  };

  const handleCloseJson = () => {
    setSelected(null);
  };

  const rows: PreviewItem[] =
    data?.items.map((item) => ({
      ...item,
      preview: buildPreview(item.payload),
    })) ?? [];

  const columns: Column<PreviewItem>[] = [
    {
      key: "row_number",
      header: "Row",
      width: "64px",
      render: (row) => <span className={styles.numericCell}>{row.row_number}</span>,
    },
    {
      key: "preview",
      header: "Preview",
      render: (row) => (
        <div className={styles.preview}>
          {Object.entries(row.preview).map(([key, value]) => (
            <div key={key} className={styles.previewRow}>
              <span className={styles.previewKey}>{key}</span>
              <span className={styles.previewValue}>{value || "—"}</span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: "created_at",
      header: "Created",
      width: "180px",
      render: (row) => (
        <span className={styles.mutedCell}>{formatDate(row.created_at)}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      width: "140px",
      align: "right",
      render: (row) => (
        <Button
          size="sm"
          variant="secondary"
          onClick={() => handleOpenJson(row)}
        >
          View JSON
        </Button>
      ),
    },
  ];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Records</h1>
        <p className={styles.subtitle}>
          Valid rows persisted from previous uploads.
        </p>
      </header>

      <Card>
        {loading && !data ? (
          <div className={styles.loading}>
            <Spinner size={20} label="Loading records" />
          </div>
        ) : data && data.items.length === 0 ? (
          <EmptyState
            title="No records yet"
            description="Upload a workbook to see its valid rows here."
          />
        ) : (
          <>
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
            />
            <Pagination
              page={data?.page ?? 1}
              pageSize={data?.page_size ?? PAGE_SIZE}
              total={data?.total ?? 0}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </Card>

      <JsonModal
        open={!!selected}
        title={selected ? `Record #${selected.id} (row ${selected.row_number})` : ""}
        data={selected?.payload ?? {}}
        onClose={handleCloseJson}
      />
    </div>
  );
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
