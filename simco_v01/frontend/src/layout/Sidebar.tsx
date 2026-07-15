import { useState, type CSSProperties } from "react";

import { menuItems } from "../auth/menu";
import { getUser } from "../auth/user";
import { useTabs } from "../tabs/TabContext";

const SIDEBAR_EXPANDED = 260;
const SIDEBAR_COLLAPSED = 60;

const icons: Record<string, string> = {
  dashboard: "▦",
  mensajes: "✉",
  solicitudes: "📄",
  respuestas: "💬",
  usuarios: "👥",
  auditoria: "🛡",
};

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const user = getUser();
  const { openTab, activeTab } = useTabs();

  if (!user) return null;

  const role = user.role;
  const showMensajes = menuItems.find((i) => i.path === "/mensajes")?.roles.includes(role) ?? false;
  const mainItems = menuItems.filter((item) => item.path !== "/mensajes" && item.roles.includes(role));

  const handleClick = (id: string, label: string) => {
    if (activeTab === id) return;
    openTab(id, label);
  };

  const isActive = (id: string) => activeTab === id;

  const w = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;

  return (
    <div
      style={{
        ...styles.sidebar,
        width: w,
        minWidth: w,
        transition: "width 0.25s ease, min-width 0.25s ease",
      }}
    >
      {/* Collapse toggle — top */}
      <div
        style={{
          ...styles.toggleArea,
          justifyContent: collapsed ? "center" : "flex-end",
          padding: collapsed ? "12px 0" : "12px 16px",
        }}
      >
        <button
          style={styles.toggleBtn}
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? "Expandir menú" : "Colapsar menú"}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              display: "block",
              transform: collapsed ? "scaleX(-1)" : "none",
              transition: "transform 0.25s ease",
            }}
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
      </div>

      {/* Logo */}
      <div
        style={{
          ...styles.logoArea,
          padding: collapsed ? "0 0 12px" : "0 24px 20px",
          textAlign: collapsed ? "center" : "left",
        }}
      >
        <div style={{ ...styles.logoIcon, fontSize: collapsed ? 18 : 26 }}>
          {collapsed ? "S" : "SiMCo"}
        </div>
        {!collapsed && (
          <div style={styles.logoSub}>Sistema de Manejo de Consultas</div>
        )}
      </div>

      {/* Main menu */}
      <nav style={{ ...styles.nav, padding: collapsed ? "4px 8px" : "4px 12px" }}>
        {mainItems.map((item) => {
          const id = item.path.replace("/", "");
          const active = isActive(id);
          return (
            <div
              key={item.path}
              style={{
                ...styles.menuItem,
                ...(active ? styles.menuItemActive : {}),
                justifyContent: collapsed ? "center" : "flex-start",
                padding: collapsed ? "10px 0" : "10px 14px",
              }}
              onClick={() => handleClick(id, item.label)}
              title={collapsed ? item.label : undefined}
            >
              <span style={styles.menuIcon}>{icons[id] || "○"}</span>
              {!collapsed && <span style={styles.menuLabel}>{item.label}</span>}
            </div>
          );
        })}
      </nav>

      {/* Divider */}
      <div style={{ ...styles.divider, margin: collapsed ? "8px 12px" : "8px 24px" }} />

      {/* Mensajes section (isolated) */}
      {showMensajes && (
        <div style={{ ...styles.section, padding: collapsed ? "4px 8px" : "4px 12px" }}>
          <div
            style={{
              ...styles.menuItem,
              ...(isActive("mensajes") ? styles.menuItemActive : {}),
              justifyContent: collapsed ? "center" : "flex-start",
              padding: collapsed ? "10px 0" : "10px 14px",
            }}
            onClick={() => handleClick("mensajes", "Mensajes")}
            title={collapsed ? "Mensajes" : undefined}
          >
            <span style={styles.menuIcon}>✉</span>
            {!collapsed && <span style={styles.menuLabel}>Mensajes</span>}
          </div>
        </div>
      )}

      {/* Divider */}
      <div style={{ ...styles.divider, margin: collapsed ? "8px 12px" : "8px 24px" }} />

      {/* Acerca de */}
      <div style={{ ...styles.bottom, padding: collapsed ? "8px 8px 20px" : "8px 12px 20px" }}>
        <div
          style={{
            ...styles.menuItem,
            ...(isActive("acerca") ? styles.menuItemActive : {}),
            justifyContent: collapsed ? "center" : "flex-start",
            padding: collapsed ? "10px 0" : "10px 14px",
          }}
          onClick={() => handleClick("acerca", "Acerca de SiMCo")}
          title={collapsed ? "Acerca de SiMCo" : undefined}
        >
          <span style={styles.menuIcon}>ℹ</span>
          {!collapsed && <span style={styles.menuLabel}>Acerca de SiMCo</span>}
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  sidebar: {
    background: "linear-gradient(180deg, #486f81 0%, #044464 100%)",
    display: "flex",
    flexDirection: "column",
    padding: "0",
    overflow: "hidden",
    userSelect: "none",
  },
  logoArea: {
    transition: "padding 0.25s ease",
  },
  logoIcon: {
    fontWeight: 700,
    color: "#fff",
    letterSpacing: "-0.5px",
    transition: "font-size 0.25s ease",
  },
  logoSub: {
    fontSize: 11,
    color: "rgba(255,255,255,0.5)",
    marginTop: 4,
    fontWeight: 400,
    lineHeight: 1.3,
  },
  nav: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: 2,
    transition: "padding 0.25s ease",
  },
  menuItem: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    borderRadius: 10,
    cursor: "pointer",
    color: "rgba(255,255,255,0.65)",
    fontSize: 14,
    fontWeight: 450,
    transition: "all 0.15s",
  },
  menuItemActive: {
    background: "rgba(255,255,255,0.1)",
    color: "#fff",
    fontWeight: 500,
  },
  menuIcon: {
    fontSize: 16,
    width: 20,
    textAlign: "center",
    flexShrink: 0,
  },
  menuLabel: {
    whiteSpace: "nowrap",
  },
  divider: {
    height: 1,
    background: "rgba(255,255,255,0.08)",
    transition: "margin 0.25s ease",
  },
  section: {
    display: "flex",
    flexDirection: "column",
    gap: 2,
    transition: "padding 0.25s ease",
  },
  bottom: {
    transition: "padding 0.25s ease",
  },
  toggleArea: {
    display: "flex",
    transition: "padding 0.25s ease",
  },
  toggleBtn: {
    background: "rgba(255,255,255,0.08)",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    color: "rgba(255,255,255,0.6)",
    width: 32,
    height: 32,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.15s, color 0.15s",
  },
};
