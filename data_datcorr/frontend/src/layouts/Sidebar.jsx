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

    const nombre = user?.nombre || user?.usuario || "Usuario";
    const inicial = nombre.charAt(0).toUpperCase();
    const rol = user?.rol || "";
    const nivel = user?.nivel !== null && user?.nivel !== undefined ? `Nivel ${user.nivel}` : "";

    return (
        <aside style={{
            width: "220px",
            height: "100vh",
            background: "#1e1e2f",
            color: "white",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
        }}>
            <div style={{
                flex: 1,
                overflowY: "auto",
                padding: "10px 10px 0 10px",
            }}>
                <h3 style={{ margin: "0 0 16px 0", fontSize: 16, letterSpacing: "0.5px" }}>DATCORR ERP</h3>

                {menu.map(item => (
                    <div
                        key={item.path}
                        onClick={() => handleNav(item)}
                        style={{
                            padding: "10px 12px",
                            cursor: "pointer",
                            borderRadius: "6px",
                            marginBottom: "2px",
                            fontSize: 14,
                            background: location.pathname === item.path ? "#3f51b5" : "transparent",
                            transition: "background 0.15s",
                        }}
                    >
                        {item.label}
                    </div>
                ))}

                {perms.canAccessSimco && (
                    <div
                        onClick={openSimco}
                        style={{
                            padding: "10px 12px",
                            cursor: "pointer",
                            borderRadius: "6px",
                            marginBottom: "2px",
                            marginTop: "8px",
                            fontSize: 14,
                            background: "#0284c7",
                            transition: "background 0.15s",
                        }}
                    >
                        <span>SIMCO</span>
                    </div>
                )}
            </div>

            <div style={{
                flexShrink: 0,
                padding: "0 10px 10px 10px",
                borderTop: "1px solid #333",
            }}>
                <div style={{
                    padding: "12px",
                    background: "#2a2a3d",
                    borderRadius: 8,
                    marginTop: 8,
                    marginBottom: 8,
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{
                            width: 36,
                            height: 36,
                            borderRadius: "50%",
                            background: "#3f51b5",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 16,
                            fontWeight: 700,
                            flexShrink: 0,
                        }}>
                            {inicial}
                        </div>
                        <div style={{ minWidth: 0 }}>
                            <div style={{
                                fontSize: 13,
                                fontWeight: 600,
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
                        borderRadius: "6px",
                        color: "#ff6b6b",
                        fontSize: 14,
                        transition: "background 0.15s",
                    }}
                >
                    Cerrar sesion
                </div>
            </div>
        </aside>
    );
}
