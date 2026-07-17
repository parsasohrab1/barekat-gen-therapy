export type HealthResponse = {
  status: string;
  version: string;
  auth_enabled?: boolean;
  services: { database: string; redis: string; qdrant?: string };
};

const TOKEN_KEY = "barekat_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export type Job = {
  job_id: string;
  job_type: string;
  status: string;
  input_payload: Record<string, unknown>;
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type SyntheticJob = {
  job_id: string;
  status: string;
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type PredictOutcome = {
  time_to_recovery_days: number;
  event_probability: number;
  toxicity_level: number;
  model_version: string | null;
  partial_hazard: number | null;
  is_research_prediction?: boolean;
};

export type Histogram = { bins: number[]; counts: number[] };

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...init?.headers,
    },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export function login(username: string, password: string): Promise<{
  access_token: string;
  role: string;
  username: string;
}> {
  return apiFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch("/api/v1/health");
}

export function fetchJobs(jobType?: string): Promise<Job[]> {
  const query = jobType ? `?job_type=${jobType}` : "";
  return apiFetch(`/api/v1/jobs${query}`);
}

export function startSyntheticJob(body: {
  n_patients: number;
  n_genes: number;
  seed: number;
  use_ck4gen?: boolean;
  n_clusters?: number;
}): Promise<{ job_id: string; status: string }> {
  return apiFetch("/api/v1/synthetic/generate", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function startDesignJob(body: {
  target_tissue: string;
  cargo_type: string;
  n_candidates: number;
  constraints: { max_molecular_weight: number; min_logP: number; max_logP: number; lipid_class: string };
}): Promise<{ job_id: string; status: string }> {
  return apiFetch("/api/v1/design/jobs", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function rankDesignJob(
  jobId: string,
  weights: { efficacy: number; safety: number; synthesizability: number; cost: number },
): Promise<{ job_id: string; ranked_candidates: Record<string, unknown>[]; weights_used: Record<string, number> }> {
  return apiFetch(`/api/v1/design/jobs/${jobId}/rank`, {
    method: "POST",
    body: JSON.stringify({ weights, only_synthesizable: true }),
  });
}

export function fetchDesignJob(jobId: string): Promise<{
  job_id: string;
  status: string;
  result: Record<string, unknown> | null;
  error_message?: string | null;
}> {
  return apiFetch(`/api/v1/design/jobs/${jobId}`);
}

export function fetchSyntheticJob(jobId: string): Promise<SyntheticJob> {
  return apiFetch(`/api/v1/synthetic/jobs/${jobId}`);
}

export function predictOutcome(body: {
  age: number;
  gender: string;
  disease_severity: number;
  gene_5_mutation: boolean;
  gene_12_mutation: boolean;
  gene_18_expression: number;
}): Promise<PredictOutcome> {
  return apiFetch("/api/v1/predict/outcome", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchModels(): Promise<
  Array<{ model_id: string; version: string; metrics: Record<string, unknown>; is_active: boolean; mlflow_run_id?: string }>
> {
  return apiFetch("/api/v1/models");
}

export function fetchActiveModel(): Promise<{
  model_id: string;
  version: string;
  mlflow_run_id: string | null;
  is_active: boolean;
}> {
  return apiFetch("/api/v1/models/active");
}

export function syncLims(): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/lab/lims/sync", { method: "POST" });
}

export function dispatchSynthesis(body: { lipid_smiles: string; lipid_name: string }): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/lab/synthesis/dispatch", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function retrainFromInvitro(): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/lab/retrain", { method: "POST" });
}

export function seedMoleculeLibrary(): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/molecules/seed-library", { method: "POST" });
}

export function searchMolecules(body: {
  smiles: string;
  limit?: number;
  threshold?: number;
}): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/molecules/search", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function importInvitro(results: Array<{
  lipid_smiles: string;
  transfection_efficiency: number;
  toxicity_score: number;
  cell_line?: string;
  sample_external_id?: string;
}>): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/lab/invitro/import", {
    method: "POST",
    body: JSON.stringify({ results }),
  });
}

export function pseudonymizePatient(patientId: string): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/compliance/patients/pseudonymize", {
    method: "POST",
    body: JSON.stringify({ patient_id: patientId }),
  });
}

export function deletePatient(patientId: string): Promise<Record<string, unknown>> {
  return apiFetch(`/api/v1/compliance/patients/${patientId}`, { method: "DELETE" });
}

export function recordGmpStep(body: {
  batch_id: string;
  step: string;
  operator: string;
  equipment_id?: string;
  parameters?: Record<string, unknown>;
}): Promise<Record<string, unknown>> {
  return apiFetch("/api/v1/compliance/gmp/record", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchGmpTrace(batchId: string): Promise<Array<Record<string, unknown>>> {
  return apiFetch(`/api/v1/compliance/gmp/trace/${batchId}`);
}

export function fetchAuditTrail(limit = 50): Promise<
  Array<{
    id: string;
    action: string;
    model_version: string | null;
    input_hash: string | null;
    details: Record<string, unknown>;
    created_at: string;
  }>
> {
  return apiFetch(`/api/v1/compliance/audit?limit=${limit}`);
}
