import { useEffect, useMemo, useState } from "react";

import { getSolicitudes } from "../api/solicitudes";
import { getRespuestas } from "../api/respuestas";
import { getActividadHoy } from "../api/dashboard";

import { formatDateTime, timeAgo } from "../utils/date";
import { useTabs } from "../tabs/TabContext";
import { getUser } from "../auth/user";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 5;

export default function Dashboard() {
  const { openTab } = useTabs();
  const user = getUser();
  const [solicitudes, setSolicitudes] = useState<any[]>([]);
  const [respuestas, setRespuestas] = useState<any[]>([]);
  const [recientes, setRecientes] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    Promise.all([
      getSolicitudes(),
      getRespuestas().catch(() => []),
      getActividadHoy().catch(() => []),
    ]).then(([sols, resps, hoy]) => {
      setSolicitudes(sols);
      setRespuestas(resps);
      setRecientes(hoy.slice(0, 5));
    });
  }, []);

  const handleSearch = () => {
    const q = searchQuery.trim();
    if (!q) return;
    openTab("resultados", "Resultados", { q });
  };

  const totalSols = solicitudes.length;
  const pendientes = solicitudes.filter((s) => s.estado === "pendiente").length;
  const respondidas = solicitudes.filter((s) => s.estado === "respondida").length;
  const totalResps = respuestas.length;
  const totalUsers = 4; // placeholder — we can improve later

  const totalPages = Math.max(1, Math.ceil(solicitudes.length / PAGE_SIZE));
  const pageData = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return solicitudes.slice(start, start + PAGE_SIZE);
  }, [solicitudes, page]);

  /* ── activity timeline from recent solicitudes ── */
  const timeline = useMemo(() => {
    const items: { label: string; time: string; icon: string; color: string }[] = [];
    for (const s of recientes.slice(0, 6)) {
      items.push({
        label: s.estado === "respondida" ? "Solicitud respondida" : "Nueva solicitud creada",
        time: timeAgo(s.fecha_creacion),
        icon: s.estado === "respondida" ? "✓" : "●",
        color: s.estado === "respondida" ? "#16a34a" : "#0ea5e9",
      });
    }
    for (const r of respuestas.slice(0, 3)) {
      items.push({
        label: "Respuesta enviada",
        time: timeAgo(r.fecha_respuesta),
        icon: "↩",
        color: "#8b5cf6",
      });
    }
    return items.slice(0, 6);
  }, [recientes, respuestas]);

  return (
    <div>
      {/* ── Welcome Card ── */}
      <div style={welcomeStyles.card}>
        <div style={welcomeStyles.content}>
          <h1 style={welcomeStyles.title}>Panel de administración</h1>
          <p style={welcomeStyles.desc}>
            Gestione y supervise las solicitudes documentales del sistema SiMCo de forma eficiente.
          </p>
          <div style={{ marginTop: 16 }}>
            <div style={searchStyles.row}>
              <input
                style={searchStyles.input}
                placeholder="Buscar en solicitudes y respuestas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <button style={searchStyles.btn} onClick={handleSearch}>
                Buscar
              </button>
            </div>
          </div>
        </div>
        <div style={welcomeStyles.illustration}>
          <svg width="140" height="120" viewBox="0 0 140 120" fill="none">
            <rect x="20" y="30" width="100" height="70" rx="8" fill="#bfdbfe" />
            <rect x="28" y="42" width="50" height="6" rx="3" fill="#60a5fa" />
            <rect x="28" y="54" width="70" height="4" rx="2" fill="#93c5fd" />
            <rect x="28" y="64" width="40" height="4" rx="2" fill="#93c5fd" />
            <rect x="28" y="74" width="60" height="4" rx="2" fill="#93c5fd" />
            <path d="M82 88l14-14 4 4-14 14z" fill="#0ea5e9" />
            <path d="M76 94l-6-6 4-4 6 6z" fill="#0ea5e9" />
            <circle cx="90" cy="80" r="16" stroke="#0ea5e9" strokeWidth="2" fill="none" />
            <path d="M20 30l-4-8h1c12 0 16-4 20-10l2 10z" fill="#93c5fd" />
            <path d="M20 30l-4-8h1c12 0 16-4 20-10l2 10z" fill="#bfdbfe" opacity="0.6" />
          </svg>
        </div>
      </div>

      {/* ── KPI Metrics ── */}
      <div style={kpiStyles.row}>
        <KpiCard
          icon="📄"
          iconBg="#eff6ff"
          label="Solicitudes"
          value={totalSols}
          sub={`Pendientes: ${pendientes}`}
        />
        <KpiCard
          icon="💬"
          iconBg="#f0fdf4"
          label="Respuestas"
          value={totalResps}
          sub={`Respondidas: ${respondidas}`}
        />
        <KpiCard
          icon="👥"
          iconBg="#faf5ff"
          label="Usuarios"
          value={totalUsers}
          sub={`Activos: ${totalUsers}`}
        />
        {user?.role === "admin" && (
          <KpiCard
            icon="🛡"
            iconBg="#fff7ed"
            label="Auditorías"
            value={solicitudes.length + respuestas.length}
            sub={`Hoy: ${recientes.length}`}
          />
        )}
      </div>

      {/* ── Bottom: Table + Timeline ── */}
      <div style={bottomStyles.row}>
        {/* Recent solicitudes */}
        <div style={bottomStyles.left}>
          <div style={cardStyles.card}>
            <h2>Solicitudes recientes</h2>
            <table className="pro-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Detalle</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Prioridad</th>
                  <th>Solicitante</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {pageData.map((s) => (
                  <tr key={s.id}>
                    <td>{s.codigo}</td>
                    <td style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.detalle}</td>
                    <td>{s.tipo_documento}</td>
                    <td>{s.estado}</td>
                    <td>{s.prioridad}</td>
                    <td>{s.creado_por_nombre || s.creado_por_usuario_id}</td>
                    <td>{formatDateTime(s.fecha_creacion)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
          </div>
        </div>

        {/* Activity timeline */}
        <div style={bottomStyles.right}>
          <div style={cardStyles.card}>
            <h2>Actividad reciente</h2>
            <div style={{ marginTop: 8 }}>
              {timeline.map((item, i) => (
                <div key={i} style={tlStyles.row}>
                  <div style={tlStyles.iconCol}>
                    <div style={{ ...tlStyles.icon, background: item.color }}>{item.icon}</div>
                    {i < timeline.length - 1 && <div style={tlStyles.line} />}
                  </div>
                  <div style={tlStyles.textCol}>
                    <div style={tlStyles.label}>{item.label}</div>
                    <div style={tlStyles.time}>{item.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Info Footer ── */}
      <div style={infoStyles.card}>
        <span style={infoStyles.icon}>ℹ</span>
        <span style={infoStyles.text}>
          SiMCo es un sistema adaptable, derivada de: 🏛️ La Arquitectura de Datcorr S.A. Los tipos de solicitudes, 
          campos y flujos pueden variar según la estructura y 
          necesidades de cada organismo.
        </span>
      </div>
    </div>
  );
}

/* ── KPI Card Component ── */
function KpiCard({ icon, iconBg, label, value, sub }: {
  icon: string; iconBg: string;
  label: string; value: number; sub: string;
}) {
  return (
    <div style={kpiStyles.card}>
      <div style={{ ...kpiStyles.iconWrap, background: iconBg }}>
        <span style={{ fontSize: 20 }}>{icon}</span>
      </div>
      <div>
        <div style={kpiStyles.label}>{label}</div>
        <div style={kpiStyles.value}>{value}</div>
        <div style={kpiStyles.sub}>{sub}</div>
      </div>
    </div>
  );
}

/* ── Styles ── */

const welcomeStyles: Record<string, React.CSSProperties> = {
  card: {
    background: "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
    borderRadius: "var(--radius-lg)",
    padding: "24px 28px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    boxShadow: "var(--shadow-sm)",
  },
  content: { flex: 1 },
  title: {
    fontSize: 20,
    fontWeight: 700,
    color: "#0284c7",
    margin: 0,
    letterSpacing: "-0.4px",
  },
  desc: {
    fontSize: 13,
    color: "#38bdf8",
    marginTop: 6,
    maxWidth: 420,
  },
  illustration: {
    flexShrink: 0,
    marginLeft: 20,
    opacity: 0.9,
  },
};

const searchStyles: Record<string, React.CSSProperties> = {
  row: { display: "flex", gap: 8, maxWidth: 440 },
  input: {
    flex: 1,
    padding: "9px 14px",
    border: "1px solid #bfdbfe",
    borderRadius: 8,
    fontSize: 13,
    outline: "none",
    background: "#fff",
  },
  btn: {
    padding: "9px 20px",
    border: "none",
    borderRadius: 8,
    backgroundColor: "#085a80",
    color: "#fff",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
  },
};

const kpiStyles: Record<string, React.CSSProperties> = {
  row: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 16,
    marginBottom: 20,
  },
  card: {
    background: "var(--bg-card)",
    borderRadius: "var(--radius-lg)",
    padding: "18px 20px",
    display: "flex",
    alignItems: "center",
    gap: 16,
    boxShadow: "var(--shadow-sm)",
    border: "1px solid var(--border-color)",
  },
  iconWrap: {
    width: 48,
    height: 48,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  label: { fontSize: 13, color: "var(--text-muted)", fontWeight: 500 },
  value: { fontSize: 26, fontWeight: 700, color: "var(--text-primary)", lineHeight: 1.2 },
  sub: { fontSize: 12, color: "var(--text-secondary)", marginTop: 2 },
};

const cardStyles: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--bg-card)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
    boxShadow: "var(--shadow-sm)",
    border: "1px solid var(--border-color)",
  },
};

const bottomStyles: Record<string, React.CSSProperties> = {
  row: {
    display: "flex",
    gap: 20,
    marginBottom: 20,
  },
  left: { flex: "7", minWidth: 0 },
  right: { flex: "3", minWidth: 0 },
};

const tlStyles: Record<string, React.CSSProperties> = {
  row: { display: "flex", gap: 12, marginBottom: 0 },
  iconCol: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: 28,
    flexShrink: 0,
  },
  icon: {
    width: 24,
    height: 24,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 10,
    color: "#fff",
    fontWeight: 700,
    flexShrink: 0,
  },
  line: {
    width: 1,
    flex: 1,
    background: "#e2e8f0",
    minHeight: 28,
  },
  textCol: { paddingBottom: 20 },
  label: { fontSize: 13, fontWeight: 500, color: "var(--text-primary)" },
  time: { fontSize: 11, color: "var(--text-muted)", marginTop: 2 },
};

const infoStyles: Record<string, React.CSSProperties> = {
  card: {
    display: "flex",
    alignItems: "flex-start",
    gap: 12,
    background: "#f0f9ff",
    borderRadius: "var(--radius-md)",
    padding: "14px 18px",
    border: "1px solid #bae6fd",
  },
  icon: {
    fontSize: 16,
    color: "#0ea5e9",
    flexShrink: 0,
    marginTop: 1,
  },
  text: {
    fontSize: 13,
    color: "#0369a1",
    lineHeight: 1.5,
  },
};
