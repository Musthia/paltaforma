import { createContext, useContext, useState, useCallback } from "react";

const TabContext = createContext();

const STORAGE_KEY = "datcorr_tabs";

function loadPersistedTabs() {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

export function TabProvider({ children }) {
    const [tabs, setTabs] = useState(() => loadPersistedTabs());
    const [tabIndex, setTabIndex] = useState(0);

    const persist = useCallback((next) => {
        setTabs(next);
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        } catch { /* quota exceeded, ignore */ }
    }, []);

    const agregarTab = useCallback((tab) => {
        setTabs((prev) => {
            const next = [...prev, { ...tab, clave: `${tab.base}_${tab.modo}_${Date.now()}` }];
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
            } catch { /* ignore */ }
            return next;
        });
    }, []);

    const cerrarTab = useCallback((idx) => {
        setTabs((prev) => {
            const next = prev.filter((_, i) => i !== idx);
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
            } catch { /* ignore */ }
            return next;
        });
        setTabIndex((prev) => (prev >= idx && prev > 0 ? prev - 1 : prev));
    }, []);

    const actualizarFila = useCallback((claveTab, idRegistro, datos) => {
        setTabs((prev) => {
            const next = prev.map((tab) => {
                if (tab.clave !== claveTab) return tab;
                const rows = tab.rows.map((row) => {
                    if (row._idValue !== idRegistro) return row;
                    const updated = { ...row };
                    Object.entries(datos).forEach(([col, val]) => {
                        updated[col] = String(val);
                    });
                    return updated;
                });
                return { ...tab, rows };
            });
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
            } catch { /* ignore */ }
            return next;
        });
    }, []);

    return (
        <TabContext.Provider value={{ tabs, tabIndex, setTabIndex, agregarTab, cerrarTab, actualizarFila, setTabs: persist }}>
            {children}
        </TabContext.Provider>
    );
}

export function useTabs() {
    const ctx = useContext(TabContext);
    if (!ctx) throw new Error("useTabs debe usarse dentro de TabProvider");
    return ctx;
}
