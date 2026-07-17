import type { Histogram } from "../api/client";

export function RecoveryHistogram({ histogram }: { histogram: Histogram }) {
  const maxCount = Math.max(...histogram.counts, 1);

  return (
    <div style={{ marginTop: "1rem" }}>
      <h3>توزیع زمان بهبودی (روز)</h3>
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: "4px",
          height: "180px",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px",
          background: "#fafafa",
        }}
      >
        {histogram.counts.map((count, i) => (
          <div
            key={i}
            title={`${histogram.bins[i].toFixed(0)}–${histogram.bins[i + 1]?.toFixed(0) ?? ""} روز: ${count}`}
            style={{
              flex: 1,
              height: `${(count / maxCount) * 100}%`,
              background: "#2563eb",
              borderRadius: "4px 4px 0 0",
              minHeight: count > 0 ? "4px" : "0",
            }}
          />
        ))}
      </div>
    </div>
  );
}
