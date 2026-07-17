import { useCallback, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { fetchSyntheticJob, startSyntheticJob } from "../api/client";
import { RecoveryHistogram } from "../components/RecoveryHistogram";
import { useJobPolling } from "../hooks/useJobPolling";

export default function SyntheticPage() {
  const [nPatients, setNPatients] = useState(300);
  const [seed, setSeed] = useState(42);
  const [nClusters, setNClusters] = useState(5);
  const [useCk4gen, setUseCk4gen] = useState(true);
  const [jobId, setJobId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      startSyntheticJob({
        n_patients: nPatients,
        n_genes: 25,
        seed,
        use_ck4gen: useCk4gen,
        n_clusters: nClusters,
      }),
    onSuccess: (data) => setJobId(data.job_id),
  });

  const fetchJob = useCallback((id: string) => fetchSyntheticJob(id), []);
  const { job, error } = useJobPolling(jobId, fetchJob);
  const histogram = job?.result?.histogram as { bins: number[]; counts: number[] } | undefined;
  const validation = job?.result?.validation as Record<string, unknown> | undefined;
  const checks = validation?.checks as Record<string, boolean> | undefined;

  return (
    <section>
      <h2>تولید داده سنتتیک (CK4Gen)</h2>
      <p>CoxPH → Hazard Ratios → خوشه‌بندی ریسک → SynthNet → اعتبارسنجی KS/C-index</p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
        style={{ display: "grid", gap: "0.75rem", maxWidth: "360px", marginTop: "1rem" }}
      >
        <label>
          تعداد بیماران
          <input type="number" value={nPatients} min={10} max={10000} onChange={(e) => setNPatients(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <label>
          تعداد خوشه‌های ریسک
          <input type="number" value={nClusters} min={2} max={20} onChange={(e) => setNClusters(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <label>
          Seed
          <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <label>
          <input type="checkbox" checked={useCk4gen} onChange={(e) => setUseCk4gen(e.target.checked)} /> استفاده از خط لوله CK4Gen
        </label>
        <button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "در حال ارسال..." : "شروع تولید"}
        </button>
      </form>

      {jobId && (
        <div style={{ marginTop: "1.5rem" }}>
          <p>
            <strong>Job:</strong> {jobId} — <strong>وضعیت:</strong> {job?.status ?? "..."}
          </p>
          {error && <p style={{ color: "crimson" }}>{error}</p>}
          {job?.status === "completed" && job.result && (
            <div style={{ marginTop: "1rem" }}>
              <ul>
                <li>Pipeline: {String(job.result.pipeline ?? "ck4gen")}</li>
                <li>نمونه‌ها: {String(job.result.n_samples)}</li>
                <li>C-index: {Number(job.result.c_index).toFixed(3)}</li>
                {validation && (
                  <>
                    <li>KS p-value: {Number(validation.ks_pvalue).toFixed(4)}</li>
                    <li>C-index gap: {Number(validation.c_index_gap).toFixed(3)}</li>
                    <li>پذیرش: {validation.accepted ? "✓ قبول" : "⚠ نیاز به بازتولید"}</li>
                  </>
                )}
              </ul>
              {checks && (
                <div style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
                  {Object.entries(checks).map(([k, v]) => (
                    <div key={k}>{v ? "✓" : "✗"} {k}</div>
                  ))}
                </div>
              )}
              {histogram && <RecoveryHistogram histogram={histogram} />}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
