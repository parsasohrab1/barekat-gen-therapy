import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchHealth, getToken, login, setToken } from "../api/client";
import CompliancePage from "./CompliancePage";
import DesignPage from "./DesignPage";
import JobsPage from "./JobsPage";
import LabPage from "./LabPage";
import PredictPage from "./PredictPage";
import SyntheticPage from "./SyntheticPage";

type Page = "synthetic" | "predict" | "design" | "lab" | "compliance" | "jobs";

const NAV: { id: Page; label: string }[] = [
  { id: "synthetic", label: "داده سنتتیک" },
  { id: "predict", label: "پیش‌بینی پیامد" },
  { id: "design", label: "طراحی لیپید" },
  { id: "lab", label: "آزمایشگاه" },
  { id: "compliance", label: "انطباق" },
  { id: "jobs", label: "Jobها" },
];

const DEMO_USERS = [
  { username: "scientist", password: "scientist123", role: "scientist" },
  { username: "clinician", password: "clinician123", role: "clinician" },
  { username: "admin", password: "admin123", role: "admin" },
];

export default function App() {
  const [page, setPage] = useState<Page>("synthetic");
  const [username, setUsername] = useState("scientist");
  const [password, setPassword] = useState("scientist123");
  const [loggedIn, setLoggedIn] = useState(!!getToken());
  const [role, setRole] = useState<string | null>(localStorage.getItem("barekat_role"));

  const { data: health } = useQuery({ queryKey: ["health"], queryFn: fetchHealth, refetchInterval: 30000 });

  const loginMutation = useMutation({
    mutationFn: () => login(username, password),
    onSuccess: (data) => {
      setToken(data.access_token);
      localStorage.setItem("barekat_role", data.role);
      setRole(data.role);
      setLoggedIn(true);
    },
  });

  const logout = () => {
    setToken(null);
    localStorage.removeItem("barekat_role");
    setRole(null);
    setLoggedIn(false);
  };

  const healthOk = health?.status === "ok";
  const services = health?.services;

  return (
    <div style={{ fontFamily: "Tahoma, sans-serif", minHeight: "100vh", background: "#f8fafc" }}>
      <header style={{ background: "#0f172a", color: "#fff", padding: "1rem 2rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: "1.4rem" }}>Barekat Gen Therapy</h1>
            <p style={{ margin: "0.25rem 0 0", opacity: 0.8, fontSize: "0.9rem" }}>
              پلتفرم طراحی و بهینه‌سازی ناقل‌های ژنی
              {health && (
                <span style={{ marginRight: "1rem" }}>
                  — API: {healthOk ? "✓" : "⚠"} {health.status} v{health.version}
                  {health.auth_enabled && " — Auth ON"}
                  {role && ` — ${role}`}
                </span>
              )}
            </p>
            {services && (
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem", opacity: 0.7 }}>
                db:{services.database} · redis:{services.redis}
                {services.qdrant != null && ` · qdrant:${services.qdrant}`}
              </p>
            )}
          </div>
          {!loggedIn ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                loginMutation.mutate();
              }}
              style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}
            >
              <select
                value={username}
                onChange={(e) => {
                  const u = DEMO_USERS.find((d) => d.username === e.target.value);
                  setUsername(e.target.value);
                  if (u) setPassword(u.password);
                }}
                style={{ padding: "4px 8px" }}
              >
                {DEMO_USERS.map((u) => (
                  <option key={u.username} value={u.username}>
                    {u.username} ({u.role})
                  </option>
                ))}
              </select>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="pass"
                style={{ padding: "4px 8px" }}
              />
              <button type="submit" disabled={loginMutation.isPending}>
                ورود
              </button>
              {loginMutation.isError && (
                <span style={{ color: "#fca5a5", fontSize: "0.85rem" }}>{loginMutation.error.message}</span>
              )}
            </form>
          ) : (
            <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
              <span style={{ fontSize: "0.85rem", opacity: 0.85 }}>{role}</span>
              <button onClick={logout}>خروج</button>
            </div>
          )}
        </div>
      </header>

      <div style={{ background: "#fef3c7", color: "#92400e", padding: "0.5rem 2rem", fontSize: "0.85rem" }}>
        ⚠ داده‌های سنتتیک (<code>is_synthetic=true</code>) از داده واقعی بیمار جدا هستند. پیش‌بینی‌ها صرفاً برای تحقیق هستند.
      </div>

      <nav style={{ display: "flex", gap: "0.5rem", padding: "1rem 2rem", background: "#fff", borderBottom: "1px solid #e2e8f0", flexWrap: "wrap" }}>
        {NAV.map((item) => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            style={{
              padding: "0.5rem 1rem",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              background: page === item.id ? "#2563eb" : "#e2e8f0",
              color: page === item.id ? "#fff" : "#334155",
              fontWeight: page === item.id ? 600 : 400,
            }}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <main style={{ padding: "2rem", maxWidth: "960px", margin: "0 auto" }}>
        {page === "synthetic" && <SyntheticPage />}
        {page === "predict" && <PredictPage />}
        {page === "design" && <DesignPage />}
        {page === "lab" && <LabPage />}
        {page === "compliance" && <CompliancePage />}
        {page === "jobs" && <JobsPage />}
      </main>
    </div>
  );
}
