import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "../api/client";

const STATUS_COLOR: Record<string, string> = {
  queued: "#6b7280",
  running: "#2563eb",
  completed: "#16a34a",
  failed: "#dc2626",
};

export default function JobsPage() {
  const { data: jobs, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => fetchJobs(),
    refetchInterval: 3000,
  });

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>وضعیت Jobها</h2>
        <button onClick={() => refetch()}>بروزرسانی</button>
      </div>

      {isLoading && <p>در حال بارگذاری...</p>}
      {isError && <p style={{ color: "crimson" }}>{(error as Error).message}</p>}

      {jobs && jobs.length === 0 && <p>هنوز jobی ثبت نشده است.</p>}

      {jobs && jobs.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <thead>
            <tr style={{ textAlign: "right", borderBottom: "2px solid #ddd" }}>
              <th style={{ padding: "8px" }}>نوع</th>
              <th style={{ padding: "8px" }}>وضعیت</th>
              <th style={{ padding: "8px" }}>ایجاد</th>
              <th style={{ padding: "8px" }}>جزئیات</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.job_id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "8px" }}>{job.job_type}</td>
                <td style={{ padding: "8px", color: STATUS_COLOR[job.status] ?? "#000" }}>
                  {job.status}
                </td>
                <td style={{ padding: "8px" }}>{new Date(job.created_at).toLocaleString("fa-IR")}</td>
                <td style={{ padding: "8px", fontSize: "0.85rem" }}>
                  {job.error_message && <span style={{ color: "crimson" }}>{job.error_message}</span>}
                  {job.result && (
                    <span>
                      {job.job_type === "synthetic" && job.result.c_index != null
                        ? `C-index: ${Number(job.result.c_index).toFixed(3)}`
                        : job.job_type === "design"
                          ? `${(job.result.candidates as unknown[])?.length ?? 0} کاندیدا`
                          : "تکمیل شد"}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
