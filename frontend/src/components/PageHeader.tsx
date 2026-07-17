import { ReactNode } from "react";

type Props = {
  title: string;
  subtitle?: string;
  children?: ReactNode;
};

export function PageHeader({ title, subtitle, children }: Props) {
  return (
    <div style={{ marginBottom: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
        <div>
          <h2 style={{ margin: 0 }}>{title}</h2>
          {subtitle && <p style={{ margin: "0.35rem 0 0", color: "#64748b" }}>{subtitle}</p>}
        </div>
        {children}
      </div>
    </div>
  );
}
