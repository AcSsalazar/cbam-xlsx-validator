import type { FieldError } from "../../types/api";
import { Table, type Column } from "../Table/Table";
import styles from "./ErrorTable.module.css";

interface ErrorTableProps {
  errors: FieldError[];
}

type ErrorRow = FieldError & { renderedValue: string };

function renderValue(value: string): string {
  if (value === "") return "—";
  return value;
}

export function ErrorTable({ errors }: ErrorTableProps) {
  const rows: ErrorRow[] = errors.map((error) => ({
    ...error,
    renderedValue: renderValue(error.value),
  }));

  const columns: Column<ErrorRow>[] = [
    {
      key: "row",
      header: "Row",
      width: "80px",
      render: (row) => <span className={styles.rowCell}>{row.row}</span>,
    },
    {
      key: "field",
      header: "Field",
      width: "220px",
      render: (row) => <span className={styles.fieldCell}>{row.field}</span>,
    },
    {
      key: "value",
      header: "Value",
      render: (row) => <span className={styles.valueCell}>{row.renderedValue}</span>,
    },
    {
      key: "message",
      header: "Message",
      render: (row) => <span className={styles.messageCell}>{row.message}</span>,
    },
  ];

  return (
    <div className={styles.wrapper}>
      <Table
        columns={columns}
        rows={rows}
        getRowKey={(row) => `${row.row}-${row.field}`}
      />
    </div>
  );
}
