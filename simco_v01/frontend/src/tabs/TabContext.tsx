import { createContext, useContext, useRef, useState, type ReactNode } from "react";

type TabParams = Record<string, string>;

export interface Tab {
  id: string;
  label: string;
  params: TabParams;
}

interface TabContextValue {
  tabs: Tab[];
  activeTab: string | null;
  openTab: (id: string, label: string, params?: TabParams) => void;
  closeTab: (id: string) => void;
  setActiveTab: (id: string) => void;
  isPermanent: (id: string) => boolean;
}

const PERMANENT = "dashboard";

const TabContext = createContext<TabContextValue | null>(null);

export function TabProvider({ children }: { children: ReactNode }) {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: PERMANENT, label: "Dashboard", params: {} },
  ]);
  const [activeTab, setActiveTab] = useState<string>(PERMANENT);
  const tabsRef = useRef(tabs);
  const activeTabRef = useRef(activeTab);
  tabsRef.current = tabs;
  activeTabRef.current = activeTab;

  const openTab = (id: string, label: string, params?: TabParams) => {
    setTabs((prev) => {
      const exists = prev.find((t) => t.id === id);
      if (exists) {
        return prev.map((t) =>
          t.id === id ? { ...t, params: params || {} } : t
        );
      }
      return [...prev, { id, label, params: params || {} }];
    });
    setActiveTab(id);
  };

  const closeTab = (id: string) => {
    if (id === PERMANENT) return;
    const prev = tabsRef.current;
    const idx = prev.findIndex((t) => t.id === id);
    const next = prev.filter((t) => t.id !== id);
    setTabs(next);
    if (activeTabRef.current === id && next.length > 0) {
      const newIdx = Math.min(idx, next.length - 1);
      setActiveTab(next[newIdx].id);
    }
  };

  const isPermanent = (id: string) => id === PERMANENT;

  return (
    <TabContext.Provider value={{ tabs, activeTab, openTab, closeTab, setActiveTab, isPermanent }}>
      {children}
    </TabContext.Provider>
  );
}

export function useTabs() {
  const ctx = useContext(TabContext);
  if (!ctx) throw new Error("useTabs deve usarse dentro de TabProvider");
  return ctx;
}
