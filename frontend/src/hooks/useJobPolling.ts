import { useEffect, useState } from "react";

type PollableJob = {
  job_id: string;
  status: string;
  result: Record<string, unknown> | null;
  error_message?: string | null;
};

export function useJobPolling<T extends PollableJob>(
  jobId: string | null,
  fetcher: (id: string) => Promise<T>,
  intervalMs = 2000,
) {
  const [job, setJob] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let active = true;
    const poll = async () => {
      try {
        const data = await fetcher(jobId);
        if (!active) return;
        setJob(data);
        setError(null);
        if (data.status === "completed" || data.status === "failed") return;
        setTimeout(poll, intervalMs);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Polling failed");
      }
    };

    poll();
    return () => {
      active = false;
    };
  }, [jobId, fetcher, intervalMs]);

  return { job, error };
}
