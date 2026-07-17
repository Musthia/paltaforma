import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";
import { usePermissions } from "../auth/usePermissions";
import api from "../api/axiosClient";
import { useState } from "react";

export default function Sidebar() {

    const navigate = useNavigate();
    const location = useLocation();
    const [simcoOpen, setSimcoOpen] = useState(false);

    const user = useAuthStore((s) => s.user);
    const accessToken = useAuthStore((s) => s.accessToken);
    const logout = useAuthStore((s) => s.logout);
    const perms = usePermissions();

    const menu = [
        { label: "Dashboard", path: "/dashboard", external: false },
        ...(perms.canViewUsers ? [{ label: "Usuarios", path: "/usuarios", external: false }] : []),
        { label: "Consultar Bases", path: "/database", external: false },
        { label: "Carga de Datos", path: "/carga-datos", external: false },
        ...(perms.canViewAuditoria ? [{ label: "Auditoria DATCORR", path: "/auditoria", external: false }] : []),
        ...(perms.canViewReportes ? [{ label: "Reportes", path: "/reportes", external: false }] : []),
    ];

    const openSimco = () => {
        const params = new URLSearchParams();
        if (accessToken) params.set("token", accessToken);
        window.open("http://localhost:8000/simco/?" + params.toString(), "_blank");
    };

    const handleNav = (item) => {
        if (item.external) {
            window.open(item.path, "_blank");
        } else {
            navigate(item.path);
        }
    };

    const handleLogout = async () => {
        try {
            await api.post("/auth/logout");
        } catch (err) {
            console.error("Logout error:", err);
        }
        logout();
        navigate("/");
    };

    const nombre = user?.full_name || user?.sub || "Usuario";
    const inicial = nombre.charAt(0).toUpperCase();
    const rol = user?.role || "";
    const nivel = user?.nivel !== null && user?.nivel !== undefined ? `Nivel ${user.nivel}` : "";

    const isActive = (path) => location.pathname === path;

    return (
        <aside style={{
            width: "240px",
            height: "100vh",
            background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)",
            color: "#e2e8f0",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            borderRight: "1px solid #334155",
        }}>
            {/* ── Brand Header ── */}
            <div style={{
                padding: "20px 16px 16px",
                borderBottom: "1px solid #334155",
            }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{
                        width: 36,
                        height: 36,
                        borderRadius: 10,
                        background: "linear-gradient(135deg, #3b82f6, #6366f1)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 16,
                        fontWeight: 800,
                        color: "#fff",
                        flexShrink: 0,
                    }}>D</div>
                    <div>
                        <div style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9", letterSpacing: "0.3px" }}>
                            DATCORR
                        </div>
                        <div style={{ fontSize: 10, color: "#64748b", letterSpacing: "1px", textTransform: "uppercase" }}>
                            Plataforma Documental
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Navigation ── */}
            <div style={{
                flex: 1,
                overflowY: "auto",
                padding: "12px 10px",
            }}>
                <div style={{ fontSize: 10, fontWeight: 600, color: "#64748b", padding: "0 12px 8px", textTransform: "uppercase", letterSpacing: "1px" }}>
                    Navegación
                </div>

                {menu.map(item => (
                    <div
                        key={item.path}
                        onClick={() => handleNav(item)}
                        style={{
                            padding: "10px 12px",
                            cursor: "pointer",
                            borderRadius: 8,
                            marginBottom: 2,
                            fontSize: 14,
                            fontWeight: isActive(item.path) ? 600 : 400,
                            background: isActive(item.path) ? "rgba(59, 130, 246, 0.15)" : "transparent",
                            color: isActive(item.path) ? "#60a5fa" : "#cbd5e1",
                            transition: "all 0.15s",
                        }}
                        onMouseEnter={(e) => {
                            if (!isActive(item.path)) e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                        }}
                        onMouseLeave={(e) => {
                            if (!isActive(item.path)) e.currentTarget.style.background = "transparent";
                        }}
                    >
                        {item.label}
                    </div>
                ))}

                {perms.canAccessSimco && (
                    <>
                        <div style={{ fontSize: 10, fontWeight: 600, color: "#64748b", padding: "16px 12px 8px", textTransform: "uppercase", letterSpacing: "1px" }}>
                            Módulos
                        </div>
                        <div
                            onClick={openSimco}
                            style={{
                                padding: "10px 12px",
                                cursor: "pointer",
                                borderRadius: 8,
                                marginBottom: 2,
                                fontSize: 14,
                                fontWeight: 500,
                                background: "linear-gradient(135deg, #0284c7, #0e7490)",
                                color: "#fff",
                                transition: "opacity 0.15s",
                                display: "flex",
                                alignItems: "center",
                                gap: 8,
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.opacity = "0.9"}
                            onMouseLeave={(e) => e.currentTarget.style.opacity = "1"}
                        >
                            <span style={{ fontSize: 16 }}>↗</span>
                            <span>SIMCO</span>
                        </div>
                    </>
                )}
            </div>

            {/* ── User Profile ── */}
            <div style={{
                borderTop: "1px solid #334155",
                padding: "12px 10px",
            }}>
                <div style={{
                    padding: "12px",
                    background: "rgba(255,255,255,0.04)",
                    borderRadius: 10,
                    border: "1px solid rgba(255,255,255,0.06)",
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{
                            width: 40,
                            height: 40,
                            borderRadius: "50%",
                            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 16,
                            fontWeight: 700,
                            color: "#fff",
                            flexShrink: 0,
                            boxShadow: "0 2px 8px rgba(99, 102, 241, 0.3)",
                        }}>
                            {inicial}
                        </div>
                        <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{
                                fontSize: 14,
                                fontWeight: 600,
                                color: "#f1f5f9",
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                            }}>
                                {nombre}
                            </div>
                            <div style={{
                                fontSize: 11,
                                color: "#94a3b8",
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                marginTop: 1,
                            }}>
                                {[rol, nivel].filter(Boolean).join(" · ") || "Usuario"}
                            </div>
                        </div>
                    </div>
                </div>

                <div
                    onClick={handleLogout}
                    style={{
                        padding: "10px 12px",
                        cursor: "pointer",
                        borderRadius: 8,
                        color: "#f87171",
                        fontSize: 13,
                        fontWeight: 500,
                        marginTop: 6,
                        transition: "background 0.15s",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = "rgba(248, 113, 113, 0.1)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                >
                    <span style={{ fontSize: 14 }}>⏻</span>
                    <span>Cerrar sesión</span>
                </div>
            </div>
        </aside>
    );
}
