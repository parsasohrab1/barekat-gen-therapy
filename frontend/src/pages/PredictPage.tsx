import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchModels, predictOutcome } from "../api/client";

export default function PredictPage() {
  const [age, setAge] = useState(45);
  const [gender, setGender] = useState("Male");
  const [severity, setSeverity] = useState(5);
  const [gene5, setGene5] = useState(false);
  const [gene12, setGene12] = useState(false);
  const [gene18Expr, setGene18Expr] = useState(5);

  const { data: models } = useQuery({ queryKey: ["models"], queryFn: fetchModels });
  const activeModel = models?.find((m) => m.is_active);

  const mutation = useMutation({
    mutationFn: () =>
      predictOutcome({
        age,
        gender,
        disease_severity: severity,
        gene_5_mutation: gene5,
        gene_12_mutation: gene12,
        gene_18_expression: gene18Expr,
      }),
  });

  return (
    <section>
      <h2>Treatment Outcome Prediction</h2>
      <p>
        Active model:{" "}
        {activeModel ? `CoxPH v${activeModel.version}` : "Not trained yet — generate synthetic data first"}
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
        style={{ display: "grid", gap: "0.75rem", maxWidth: "320px", marginTop: "1rem" }}
      >
        <label>
          Age
          <input type="number" value={age} min={10} max={80} onChange={(e) => setAge(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <label>
          Sex
          <select value={gender} onChange={(e) => setGender(e.target.value)} style={{ display: "block", width: "100%", marginTop: "4px" }}>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </label>
        <label>
          Disease severity (1–10)
          <input type="number" value={severity} min={1} max={10} step={0.1} onChange={(e) => setSeverity(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <label>
          <input type="checkbox" checked={gene5} onChange={(e) => setGene5(e.target.checked)} /> Gene_5 mutation
        </label>
        <label>
          <input type="checkbox" checked={gene12} onChange={(e) => setGene12(e.target.checked)} /> Gene_12 mutation
        </label>
        <label>
          Gene_18 expression
          <input type="number" value={gene18Expr} min={0} max={15} step={0.1} onChange={(e) => setGene18Expr(Number(e.target.value))} style={{ display: "block", width: "100%", marginTop: "4px" }} />
        </label>
        <button type="submit" disabled={mutation.isPending || !activeModel}>
          Predict
        </button>
      </form>

      {mutation.error && <p style={{ color: "crimson", marginTop: "1rem" }}>{mutation.error.message}</p>}

      {mutation.data && (
        <div style={{ marginTop: "1.5rem", padding: "1rem", border: "1px solid #ddd", borderRadius: "8px" }}>
          <p style={{ fontSize: "0.85rem", color: "#92400e", marginTop: 0 }}>
            ⚠ Research prediction — not for clinical diagnosis
            {mutation.data.is_research_prediction && " (is_research_prediction=true)"}
          </p>
          <h3>Prediction result</h3>
          <ul>
            <li>Time to recovery (median): {mutation.data.time_to_recovery_days} days</li>
            <li>Event probability (180 days): {(mutation.data.event_probability * 100).toFixed(1)}%</li>
            <li>Toxicity level: {mutation.data.toxicity_level}</li>
            <li>Partial hazard: {mutation.data.partial_hazard}</li>
            <li>Model: v{mutation.data.model_version}</li>
          </ul>
        </div>
      )}
    </section>
  );
}
