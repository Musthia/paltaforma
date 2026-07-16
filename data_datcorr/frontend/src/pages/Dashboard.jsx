import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";
import api from "../api/axiosClient";
import { getDashboardStats } from "../services/dashboardService";

export default function Dashboard() {
    const navigate = useNavigate();
    const logout = useAuthStore((s) => s.logout);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        getDashboardStats()
            .then(setStats)
            .catch(console.error);
    }, []);

    const handleLogout = async () => {
        try {
            await api.post("/auth/logout");
        } catch (err) {
            console.error("Logout error:", err);
        }
        logout();
        navigate("/");
    };

    if (!stats) {
        return (
            <div style={loadingStyles.container}>
                <div style={loadingStyles.spinner} />
                <p style={{ marginTop: 12, color: "#64748b", fontSize: 14 }}>Cargando panel...</p>
            </div>
        );
    }

    return (
        <div>
            {/* ── Welcome Card ── */}
            <div style={welcomeStyles.card}>
                <div style={welcomeStyles.content}>
                    <h1 style={welcomeStyles.title}>Panel de control</h1>
                    <p style={welcomeStyles.desc}>
                        Gestione y supervise las bases de datos documentales del sistema DatCorr.
                    </p>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>

                    <div style={welcomeStyles.badge}>
                        <span style={welcomeStyles.badgeText}>v1.0</span>
                    </div>
                    <button onClick={handleLogout} style={logoutBtnStyles}>
                        Cerrar sesion
                    </button>
                </div>
            </div>

            {/* ── KPI Metrics ── */}
            <div style={kpiStyles.row}>
                <KpiCard
                    icon="B"
                    iconBg="#eff6ff"
                    iconColor="#0284c7"
                    label="Bases activas"
                    value={stats.total_bases}
                    sub="Total de Organismos"
                />
                <KpiCard
                    icon="R"
                    iconBg="#f0fdf4"
                    iconColor="#16a34a"
                    label="Registros totales"
                    value={stats.total_registros.toLocaleString()}
                    sub="Suma de todas las bases"
                />
                <KpiCard
                    icon="U"
                    iconBg="#faf5ff"
                    iconColor="#9333ea"
                    label="Usuarios activos"
                    value={stats.usuarios_activos}
                    sub={`De ${stats.total_usuarios} registrados`}
                />
                <KpiCard
                    icon="A"
                    iconBg="#fff7ed"
                    iconColor="#ea580c"
                    label="Actividad reciente"
                    value={stats.actividad.length}
                    sub="Últimas acciones"
                />
            </div>

            {/* ── Bottom: Bases table + Timeline ── */}
            <div style={bottomStyles.row}>
                <div style={bottomStyles.left}>
                    <div style={cardStyles.card}>
                        <h2 style={sectionTitle}>Registros por base</h2>
                        <table className="pro-table">
                            <thead>
                                <tr>
                                    <th style={thStyles}>Base</th>
                                    <th style={{ ...thStyles, textAlign: "right" }}>Registros</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats.bases.map((b) => (
                                    <tr key={b.nombre}>
                                        <td style={tdStyles}>{b.nombre.replace(/_/g, " ")}</td>
                                        <td style={{ ...tdStyles, textAlign: "right", fontWeight: 600 }}>
                                            {b.registros.toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td style={{ ...tdStyles, fontWeight: 700, borderTop: "2px solid var(--border-color)" }}>TOTAL</td>
                                    <td style={{ ...tdStyles, fontWeight: 700, textAlign: "right", borderTop: "2px solid var(--border-color)" }}>
                                        {stats.total_registros.toLocaleString()}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

                <div style={bottomStyles.right}>
                    <div style={cardStyles.card}>
                        <h2 style={sectionTitle}>Actividad reciente</h2>
                        <div style={{ marginTop: 8 }}>
                            {stats.actividad.length === 0 && (
                                <p style={{ fontSize: 13, color: "var(--text-muted)" }}>Sin actividad registrada</p>
                            )}
                            {stats.actividad.map((item, i) => (
                                <div key={i} style={tlStyles.row}>
                                    <div style={tlStyles.iconCol}>
                                        <div style={{
                                            ...tlStyles.icon,
                                            background: actionColor(item.accion),
                                        }}>
                                            {actionIcon(item.accion)}
                                        </div>
                                        {i < stats.actividad.length - 1 && <div style={tlStyles.line} />}
                                    </div>
                                    <div style={tlStyles.textCol}>
                                        <div style={tlStyles.label}>{formatAction(item)}</div>
                                        <div style={tlStyles.time}>
                                            {item.usuario} &middot; {formatDate(item.fecha)}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ── Helpers ── */

function actionColor(accion) {
    const map = {
        LOGIN_SUCCESS: "#16a34a",
        LOGIN_FAILED: "#dc2626",
        LOGOUT_SUCCESS: "#64748b",
        LOGOUT_FAILED: "#dc2626",
        CREATE: "#0284c7",
        UPDATE: "#ea580c",
        DELETE_LOGICO: "#dc2626",
        TOKEN_REUSE_DETECTED: "#9333ea",
        TOKEN_REVOKED_GLOBAL: "#9333ea",
    };
    return map[accion] || "#64748b";
}

function actionIcon(accion) {
    const map = {
        LOGIN_SUCCESS: "✓",
        LOGIN_FAILED: "✗",
        LOGOUT_SUCCESS: "◀",
        CREATE: "+",
        UPDATE: "~",
        DELETE_LOGICO: "×",
    };
    return map[accion] || "●";
}

function formatAction(item) {
    const labels = {
        LOGIN_SUCCESS: "Inicio de sesion",
        LOGIN_FAILED: "Inicio fallido",
        LOGOUT_SUCCESS: "Cierre de sesion",
        LOGOUT_FAILED: "Cierre fallido",
        CREATE: "Creacion",
        UPDATE: "Actualizacion",
        DELETE_LOGICO: "Eliminacion logica",
        TOKEN_REUSE_DETECTED: "Reuso de token detectado",
        TOKEN_REVOKED_GLOBAL: "Token revocado globalmente",
    };
    const label = labels[item.accion] || item.accion;
    return item.detalle || label;
}

function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    const now = new Date();
    const diffMs = now - d;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "Ahora";
    if (diffMin < 60) return `Hace ${diffMin} min`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `Hace ${diffHr} h`;
    const diffDays = Math.floor(diffHr / 24);
    if (diffDays < 7) return `Hace ${diffDays} d`;
    return d.toLocaleDateString("es-AR", { day: "numeric", month: "short" });
}

/* ── KPI Card ── */

function KpiCard({ icon, iconBg, iconColor, label, value, sub }) {
    return (
        <div style={kpiStyles.card}>
            <div style={{ ...kpiStyles.iconWrap, background: iconBg }}>
                <span style={{ fontSize: 16, fontWeight: 700, color: iconColor }}>{icon}</span>
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

const sectionTitle = {
    fontSize: 16,
    fontWeight: 600,
    margin: 0,
    marginBottom: 12,
    color: "var(--text-primary)",
};

const logoutBtnStyles = {
    padding: "8px 16px",
    background: "#dc2626",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
};

const loadingStyles = {
    container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 300,
    },
    spinner: {
        width: 32,
        height: 32,
        border: "3px solid #e2e8f0",
        borderTop: "3px solid #0284c7",
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
    },
};

const welcomeStyles = {
    card: {
        background: "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
        borderRadius: 12,
        padding: "24px 28px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 20,
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
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
    badge: {
        background: "#0284c7",
        borderRadius: 20,
        padding: "4px 14px",
        flexShrink: 0,
    },
    badgeText: {
        color: "#fff",
        fontSize: 12,
        fontWeight: 600,
    },
};

const kpiStyles = {
    row: {
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 16,
        marginBottom: 20,
    },
    card: {
        background: "var(--bg-card, #fff)",
        borderRadius: 12,
        padding: "18px 20px",
        display: "flex",
        alignItems: "center",
        gap: 16,
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        border: "1px solid var(--border-color, #e2e8f0)",
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
    label: { fontSize: 13, color: "var(--text-muted, #64748b)", fontWeight: 500 },
    value: { fontSize: 26, fontWeight: 700, color: "var(--text-primary, #0f172a)", lineHeight: 1.2 },
    sub: { fontSize: 12, color: "var(--text-secondary, #94a3b8)", marginTop: 2 },
};

const cardStyles = {
    card: {
        background: "var(--bg-card, #fff)",
        borderRadius: 12,
        padding: 20,
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        border: "1px solid var(--border-color, #e2e8f0)",
    },
};

const bottomStyles = {
    row: {
        display: "flex",
        gap: 20,
        marginBottom: 20,
    },
    left: { flex: "7", minWidth: 0 },
    right: { flex: "3", minWidth: 0 },
};

const thStyles = {
    padding: "10px 12px",
    textAlign: "left",
    fontSize: 12,
    fontWeight: 600,
    color: "var(--text-muted, #64748b)",
    borderBottom: "2px solid var(--border-color, #e2e8f0)",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
};

const tdStyles = {
    padding: "10px 12px",
    fontSize: 13,
    borderBottom: "1px solid var(--border-color, #e2e8f0)",
    color: "var(--text-primary, #0f172a)",
};

const tlStyles = {
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
    textCol: { paddingBottom: 16 },
    label: { fontSize: 13, fontWeight: 500, color: "var(--text-primary, #0f172a)" },
    time: { fontSize: 11, color: "var(--text-muted, #64748b)", marginTop: 2 },
};
