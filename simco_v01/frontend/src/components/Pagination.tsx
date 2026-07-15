import type { CSSProperties } from "react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const go = (p: number) => onPageChange(Math.max(1, Math.min(p, totalPages)));

  return (
    <div style={styles.wrapper}>
      <button style={styles.btn} disabled={currentPage <= 1} onClick={() => go(1)}>
        ⏮
      </button>
      <button style={styles.btn} disabled={currentPage <= 1} onClick={() => go(currentPage - 1)}>
        ◀
      </button>

      <span style={styles.info}>
        Pág.{" "}
        <input
          style={styles.input}
          type="number"
          min={1}
          max={totalPages}
          value={currentPage}
          onChange={(e) => {
            const v = parseInt(e.target.value, 10);
            if (v >= 1 && v <= totalPages) go(v);
          }}
        />{" "}
        de {totalPages}
      </span>

      <button style={styles.btn} disabled={currentPage >= totalPages} onClick={() => go(currentPage + 1)}>
        ▶
      </button>
      <button style={styles.btn} disabled={currentPage >= totalPages} onClick={() => go(totalPages)}>
        ⏭
      </button>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  wrapper: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    marginTop: 12,
    flexWrap: "wrap",
  },
  btn: {
    border: "1px solid var(--border-color)",
    borderRadius: 4,
    padding: "4px 10px",
    cursor: "pointer",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: 14,
  },
  info: {
    fontSize: 14,
    display: "flex",
    alignItems: "center",
    gap: 4,
    color: "var(--text-primary)",
  },
  input: {
    width: 50,
    textAlign: "center",
    border: "1px solid var(--border-color)",
    borderRadius: 4,
    padding: "2px 4px",
    fontSize: 14,
    background: "var(--bg-card)",
    color: "var(--text-primary)",
  },
};
