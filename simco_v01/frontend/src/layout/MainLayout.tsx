import Sidebar from "./Sidebar";
import Header from "./Header";

import { useTabs } from "../tabs/TabContext";
import { TabParamsContext } from "../tabs/TabParamsContext";

import Dashboard from "../pages/Dashboard";
import Solicitudes from "../pages/Solicitudes";
import Respuestas from "../pages/Respuestas";
import Usuarios from "../pages/Usuarios";
import Auditoria from "../pages/Auditoria";
import Resultados from "../pages/Resultados";
import Acerca from "../pages/Acerca";
import Mensajes from "../pages/Mensajes";
import NotificationBar from "../components/NotificationBar";

import type { CSSProperties, ReactNode } from "react";
import type { Tab } from "../tabs/TabContext";

function renderTabContent(tab: Tab): ReactNode {
  switch (tab.id) {
    case "dashboard":
      return <Dashboard />;
    case "solicitudes":
      return <Solicitudes />;
    case "respuestas":
      return <Respuestas />;
    case "usuarios":
      return <Usuarios />;
    case "auditoria":
      return <Auditoria />;
    case "resultados":
      return <Resultados />;
    case "mensajes":
      return <Mensajes />;
    case "acerca":
      return <Acerca />;
    default:
      return <p style={{ color: "var(--text-muted)", padding: 40 }}>Sección: {tab.label}</p>;
  }
}

export default function MainLayout() {
  const { tabs, activeTab, setActiveTab, closeTab, isPermanent } = useTabs();

  return (
    <div style={styles.container}>
      <Sidebar />

      <div style={styles.right}>
        <Header />

        <NotificationBar />

        {/* Tab bar */}
        <div style={styles.tabBar}>
          {tabs.map((tab) => (
            <div
              key={tab.id}
              style={{
                ...styles.tab,
                ...(activeTab === tab.id ? styles.activeTab : {}),
              }}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
              {!isPermanent(tab.id) && (
                <button
                  style={styles.tabClose}
                  onClick={(e) => {
                    e.stopPropagation();
                    closeTab(tab.id);
                  }}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>

        <div style={styles.content}>
          {tabs.map((tab) => (
            <div
              key={tab.id}
              style={{
                display: activeTab === tab.id ? "block" : "none",
                height: "100%",
              }}
            >
              <TabParamsContext.Provider value={tab.params}>
                <div style={tab.id === "dashboard" ? styles.panelDashboard : styles.panel}>
                  {renderTabContent(tab)}
                </div>
              </TabParamsContext.Provider>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  container: {
    display: "flex",
    height: "100vh",
    width: "100%",
  },
  right: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  tabBar: {
    display: "flex",
    backgroundColor: "var(--bg-page)",
    borderBottom: "1px solid var(--border-color)",
    minHeight: 34,
    alignItems: "stretch",
    flexShrink: 0,
    paddingLeft: 4,
    overflowX: "auto",
    overflowY: "hidden",
  },
  tab: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "5px 14px",
    cursor: "pointer",
    borderRight: "1px solid var(--border-color)",
    fontSize: 12,
    userSelect: "none",
    backgroundColor: "var(--bg-card)",
    color: "var(--text-secondary)",
    transition: "all 0.1s",
    whiteSpace: "nowrap",
    flexShrink: 0,
  },
  activeTab: {
    backgroundColor: "var(--bg-card)",
    borderBottom: "1px solid var(--bg-card)",
    marginBottom: -1,
    fontWeight: 600,
    color: "var(--text-primary)",
  },
  tabClose: {
    border: "none",
    background: "none",
    cursor: "pointer",
    fontSize: 13,
    lineHeight: 1,
    padding: "0 2px",
    color: "var(--text-muted)",
  },
  content: {
    flex: 1,
    padding: "24px",
    backgroundColor: "var(--bg-page)",
    overflowY: "auto",
    textAlign: "left",
  },
  panel: {
    background: "var(--bg-card)",
    borderRadius: 12,
    padding: "28px 32px",
    boxShadow: "var(--shadow-sm)",
    border: "1px solid var(--border-color)",
    minHeight: "100%",
  },
  panelDashboard: {
    minHeight: "100%",
  },
};
