import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  deletePatient,
  fetchAuditTrail,
  fetchGmpTrace,
  pseudonymizePatient,
  recordGmpStep,
} from "../api/client";

export default function CompliancePage() {
  const [patientId, setPatientId] = useState("GT_0001");
  const [batchId, setBatchId] = useState("BATCH-DEMO-001");
  const [gmpStep, setGmpStep] = useState("formulation");
  const [operator, setOperator] = useState("qa_operator");
  const [message, setMessage] = useState<string | null>(null);

  const auditQuery = useQuery({
    queryKey: ["audit"],
    queryFn: () => fetchAuditTrail(30),
    refetchInterval: 10000,
  });

  const pseudo = useMutation({
    mutationFn: () => pseudonymizePatient(patientId),
    onSuccess: (data) => setMessage(JSON.stringify(data, null, 2)),
    onError: (err: Error) => setMessage(err.message),
  });

  const erase = useMutation({
    mutationFn: () => deletePatient(patientId),
    onSuccess: (data) => setMessage(JSON.stringify(data, null, 2)),
    onError: (err: Error) => setMessage(err.message),
  });

  const gmpRecord = useMutation({
    mutationFn: () =>
      recordGmpStep({
        batch_id: batchId,
        step: gmpStep,
        operator,
        equipment_id: "LNP-MIXER-01",
        parameters: { volume_ml: 50 },
      }),
    onSuccess: (data) => {
      setMessage(JSON.stringify(data, null, 2));
      auditQuery.refetch();
    },
    onError: (err: Error) => setMessage(err.message),
  });

  const gmpTrace = useMutation({
    mutationFn: () => fetchGmpTrace(batchId),
    onSuccess: (data) => setMessage(JSON.stringify(data, null, 2)),
    onError: (err: Error) => setMessage(err.message),
  });

  return (
    <section>
      <h2>انطباق و ممیزی</h2>
      <p>HIPAA/GDPR pseudonymization، حق فراموشی، ردیابی GMP، و audit trail مطابق 21 CFR Part 11</p>
      <p style={{ fontSize: "0.85rem", color: "#92400e" }}>
        عملیات حساس (حذف / audit) نیاز به نقش admin دارد — با <code>admin / admin123</code> وارد شوید.
      </p>

      <div style={{ display: "grid", gap: "1.25rem", marginTop: "1.25rem" }}>
        <fieldset style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: "1rem" }}>
          <legend>حریم خصوصی بیمار</legend>
          <label>
            Patient ID
            <input
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, maxWidth: 280 }}
            />
          </label>
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <button onClick={() => pseudo.mutate()} disabled={pseudo.isPending}>
              Pseudonymize
            </button>
            <button
              onClick={() => {
                if (confirm("حذف GDPR غیرقابل بازگشت است. ادامه؟")) erase.mutate();
              }}
              disabled={erase.isPending}
              style={{ color: "#b91c1c" }}
            >
              GDPR Delete
            </button>
          </div>
        </fieldset>

        <fieldset style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: "1rem" }}>
          <legend>ردیابی GMP</legend>
          <label>
            Batch ID
            <input
              value={batchId}
              onChange={(e) => setBatchId(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, maxWidth: 280 }}
            />
          </label>
          <label style={{ display: "block", marginTop: 8 }}>
            Step
            <input
              value={gmpStep}
              onChange={(e) => setGmpStep(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, maxWidth: 280 }}
            />
          </label>
          <label style={{ display: "block", marginTop: 8 }}>
            Operator
            <input
              value={operator}
              onChange={(e) => setOperator(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, maxWidth: 280 }}
            />
          </label>
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <button onClick={() => gmpRecord.mutate()} disabled={gmpRecord.isPending}>
              ثبت مرحله GMP
            </button>
            <button onClick={() => gmpTrace.mutate()} disabled={gmpTrace.isPending}>
              مشاهده Trace
            </button>
          </div>
        </fieldset>
      </div>

      {message && (
        <pre style={{ marginTop: "1rem", background: "#f1f5f9", padding: "1rem", borderRadius: 8, overflow: "auto" }}>
          {message}
        </pre>
      )}

      <h3 style={{ marginTop: "1.5rem" }}>Audit Trail</h3>
      {auditQuery.isError && <p style={{ color: "crimson" }}>دسترسی audit فقط برای admin</p>}
      {auditQuery.data && auditQuery.data.length === 0 && <p>هنوز رویدادی ثبت نشده.</p>}
      {auditQuery.data && auditQuery.data.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem", fontSize: "0.9rem" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #ddd", textAlign: "right" }}>
              <th style={{ padding: 8 }}>زمان</th>
              <th style={{ padding: 8 }}>عمل</th>
              <th style={{ padding: 8 }}>مدل</th>
            </tr>
          </thead>
          <tbody>
            {auditQuery.data.map((row) => (
              <tr key={row.id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: 8 }}>{new Date(row.created_at).toLocaleString("fa-IR")}</td>
                <td style={{ padding: 8 }}>{row.action}</td>
                <td style={{ padding: 8 }}>{row.model_version ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
