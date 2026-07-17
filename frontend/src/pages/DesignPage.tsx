import { useCallback, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { fetchDesignJob, rankDesignJob, startDesignJob } from "../api/client";
import { useJobPolling } from "../hooks/useJobPolling";

export default function DesignPage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [weights, setWeights] = useState({ efficacy: 0.4, safety: 0.3, synthesizability: 0.2, cost: 0.1 });
  const [ranked, setRanked] = useState<Record<string, unknown>[]>([]);

  const fetchJob = useCallback((id: string) => fetchDesignJob(id), []);
  const { job, error: pollError } = useJobPolling(jobId, fetchJob);

  const startMutation = useMutation({
    mutationFn: () =>
      startDesignJob({
        target_tissue: "spleen",
        cargo_type: "mRNA",
        n_candidates: 10,
        constraints: { max_molecular_weight: 1200, min_logP: 2, max_logP: 10, lipid_class: "ionizable" },
      }),
    onSuccess: (data) => {
      setJobId(data.job_id);
      setRanked([]);
    },
  });

  const rankMutation = useMutation({
    mutationFn: () => rankDesignJob(jobId!, weights),
    onSuccess: (data) => setRanked(data.ranked_candidates),
  });

  const candidates =
    ranked.length > 0
      ? ranked
      : job?.status === "completed" && Array.isArray(job.result?.candidates)
        ? (job.result.candidates as Record<string, unknown>[])
        : [];

  return (
    <section>
      <h2>طراحی و رتبه‌بندی لیپید</h2>
      <p>فیلتر RDKit (SMILES، logP، MW) + رتبه‌بندی چندمعیاره + حذف تکراری با Qdrant</p>

      <button onClick={() => startMutation.mutate()} disabled={startMutation.isPending} style={{ marginTop: "1rem" }}>
        {startMutation.isPending ? "در حال شروع..." : "شروع job طراحی"}
      </button>
      {startMutation.error && <p style={{ color: "crimson" }}>{startMutation.error.message}</p>}

      {jobId && (
        <p style={{ marginTop: "0.5rem" }}>
          Job: <code>{jobId}</code>
          {job && (
            <span style={{ marginRight: "0.75rem" }}>
              — وضعیت: <strong>{job.status}</strong>
            </span>
          )}
        </p>
      )}
      {pollError && <p style={{ color: "crimson" }}>{pollError}</p>}
      {job?.status === "failed" && (
        <p style={{ color: "crimson" }}>{job.error_message || "Job failed"}</p>
      )}

      <div style={{ marginTop: "1.5rem", display: "grid", gap: "0.5rem", maxWidth: "360px" }}>
        <h3>وزن‌های رتبه‌بندی</h3>
        {(["efficacy", "safety", "synthesizability", "cost"] as const).map((key) => (
          <label key={key}>
            {key}: {weights[key].toFixed(2)}
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={weights[key]}
              onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
              style={{ display: "block", width: "100%" }}
            />
          </label>
        ))}
        <button
          onClick={() => rankMutation.mutate()}
          disabled={!jobId || job?.status !== "completed" || rankMutation.isPending}
        >
          {rankMutation.isPending ? "رتبه‌بندی..." : "اعمال رتبه‌بندی"}
        </button>
        {rankMutation.error && <p style={{ color: "crimson" }}>{rankMutation.error.message}</p>}
      </div>

      {candidates.length > 0 && (
        <table style={{ width: "100%", marginTop: "1.5rem", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #ddd", textAlign: "right" }}>
              <th style={{ padding: 8 }}>رتبه</th>
              <th style={{ padding: 8 }}>نام</th>
              <th style={{ padding: 8 }}>امتیاز نهایی</th>
              <th style={{ padding: 8 }}>logP</th>
              <th style={{ padding: 8 }}>MW</th>
              <th style={{ padding: 8 }}>قابل سنتز</th>
              <th style={{ padding: 8 }}>تکراری</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c, idx) => (
              <tr key={String(c.name ?? idx)} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: 8 }}>{String(c.rank ?? idx + 1)}</td>
                <td style={{ padding: 8 }}>{String(c.name)}</td>
                <td style={{ padding: 8 }}>
                  {c.final_score != null ? Number(c.final_score).toFixed(3) : "—"}
                </td>
                <td style={{ padding: 8 }}>{c.log_p != null ? Number(c.log_p).toFixed(2) : "—"}</td>
                <td style={{ padding: 8 }}>
                  {c.molecular_weight != null ? Number(c.molecular_weight).toFixed(0) : "—"}
                </td>
                <td style={{ padding: 8 }}>{c.synthesizable ? "✓" : "✗"}</td>
                <td style={{ padding: 8 }}>{c.is_duplicate ? "بله" : "خیر"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
