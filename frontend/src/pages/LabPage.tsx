import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  dispatchSynthesis,
  importInvitro,
  retrainFromInvitro,
  searchMolecules,
  seedMoleculeLibrary,
  syncLims,
} from "../api/client";

const DEMO_SMILES = "CCCCCCCCCCCCCCCC(=O)OCC(COP(=O)(O)OCCN)OC(=O)CCCCCCCCCCCCCCC";

const DEMO_INVITRO = [
  { sample_external_id: "INV-UI-001", lipid_smiles: DEMO_SMILES, transfection_efficiency: 0.72, toxicity_score: 0.18, cell_line: "HEPG2" },
  { sample_external_id: "INV-UI-002", lipid_smiles: DEMO_SMILES, transfection_efficiency: 0.61, toxicity_score: 0.22, cell_line: "HEPG2" },
  { sample_external_id: "INV-UI-003", lipid_smiles: DEMO_SMILES, transfection_efficiency: 0.55, toxicity_score: 0.25, cell_line: "HEK293" },
  { sample_external_id: "INV-UI-004", lipid_smiles: DEMO_SMILES, transfection_efficiency: 0.48, toxicity_score: 0.3, cell_line: "HEPG2" },
  { sample_external_id: "INV-UI-005", lipid_smiles: DEMO_SMILES, transfection_efficiency: 0.8, toxicity_score: 0.15, cell_line: "HEPG2" },
];

function ResultBox({ title, data, error }: { title: string; data?: unknown; error?: Error | null }) {
  if (!data && !error) return null;
  return (
    <div style={{ marginTop: "1rem", padding: "0.75rem", background: error ? "#fef2f2" : "#f8fafc", borderRadius: 8 }}>
      <strong>{title}</strong>
      {error && <p style={{ color: "crimson", margin: "0.5rem 0 0" }}>{error.message}</p>}
      {data != null && (
        <pre style={{ margin: "0.5rem 0 0", overflow: "auto", fontSize: "0.85rem" }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function LabPage() {
  const [smiles, setSmiles] = useState(DEMO_SMILES);

  const syncLimsMutation = useMutation({ mutationFn: syncLims });
  const dispatchSynth = useMutation({
    mutationFn: () => dispatchSynthesis({ lipid_smiles: smiles, lipid_name: "lab-candidate" }),
  });
  const importDemo = useMutation({ mutationFn: () => importInvitro(DEMO_INVITRO) });
  const retrain = useMutation({ mutationFn: retrainFromInvitro });
  const seedLibrary = useMutation({ mutationFn: seedMoleculeLibrary });
  const search = useMutation({
    mutationFn: () => searchMolecules({ smiles, limit: 5, threshold: 0.5 }),
  });

  return (
    <section>
      <h2>Laboratory Integration</h2>
      <p>Closed loop: design → synthesis (MQTT) → in-vitro → retrain → prediction</p>
      <p style={{ fontSize: "0.85rem", color: "#64748b" }}>
        Sync LIMS reads from <code>LIMS_BASE_URL</code>; on error the mock demo is used.
      </p>

      <label style={{ display: "block", marginTop: "1rem", maxWidth: 560 }}>
        Reference SMILES
        <input
          value={smiles}
          onChange={(e) => setSmiles(e.target.value)}
          style={{ display: "block", width: "100%", marginTop: 4, fontFamily: "monospace", fontSize: "0.85rem" }}
        />
      </label>

      <div style={{ display: "grid", gap: "0.75rem", maxWidth: "480px", marginTop: "1rem" }}>
        <button onClick={() => syncLimsMutation.mutate()} disabled={syncLimsMutation.isPending}>
          Sync LIMS
        </button>
        <button onClick={() => dispatchSynth.mutate()} disabled={dispatchSynth.isPending}>
          Send to synthesis robot (MQTT)
        </button>
        <button onClick={() => importDemo.mutate()} disabled={importDemo.isPending}>
          Import in-vitro results (demo)
        </button>
        <button onClick={() => retrain.mutate()} disabled={retrain.isPending}>
          Retrain from in-vitro data
        </button>
        <button onClick={() => seedLibrary.mutate()} disabled={seedLibrary.isPending}>
          Index lipid library (Qdrant)
        </button>
        <button onClick={() => search.mutate()} disabled={search.isPending}>
          Search similar SMILES
        </button>
      </div>

      <ResultBox title="LIMS" data={syncLimsMutation.data} error={syncLimsMutation.error} />
      <ResultBox title="Synthesis" data={dispatchSynth.data} error={dispatchSynth.error} />
      <ResultBox title="Import" data={importDemo.data} error={importDemo.error} />
      <ResultBox title="Retrain" data={retrain.data} error={retrain.error} />
      <ResultBox title="Seed library" data={seedLibrary.data} error={seedLibrary.error} />
      <ResultBox title="Similarity search" data={search.data} error={search.error} />
    </section>
  );
}
