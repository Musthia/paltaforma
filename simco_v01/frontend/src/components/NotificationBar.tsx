import { useCallback, useEffect, useRef, useState } from "react";
import { getNuevasNotificaciones } from "../api/notificaciones";
import { globalWS } from "../ws/globalWS";
import { useTabs } from "../tabs/TabContext";
import { getUser } from "../auth/user";

interface Notif {
  tipo: "pendiente" | "respondida";
  count: number;
  id: number;
  solicitudId?: number;
}

const LS_PENDIENTE = "notif_last_pendiente_id";
const LS_RESPONDIDA = "notif_last_respondida_id";

function lastSeen(tipo: "pendiente" | "respondida"): number {
  return Number(localStorage.getItem(tipo === "pendiente" ? LS_PENDIENTE : LS_RESPONDIDA)) || 0;
}
function setLastSeen(tipo: "pendiente" | "respondida", id: number) {
  localStorage.setItem(tipo === "pendiente" ? LS_PENDIENTE : LS_RESPONDIDA, String(id));
}

async function fetchMissed(tipo: "pendiente" | "respondida", sinceId: number) {
  try {
    return await getNuevasNotificaciones(tipo, sinceId);
  } catch {
    return { count: 0, max_id: 0, items: [] };
  }
}

export default function NotificationBar() {
  const { openTab } = useTabs();
  const user = getUser();
  const role = user?.role;
  const [notifs, setNotifs] = useState<Notif[]>([]);
  const pendAcked = useRef(false);
  const respAcked = useRef(false);

  const addNotif = useCallback((tipo: "pendiente" | "respondida", count: number, solicitudId?: number) => {
    setNotifs((prev) => [...prev, { tipo, count, id: Date.now() + Math.random(), solicitudId }]);
  }, []);

  useEffect(() => {
    if (!role) return;
    globalWS.start();

    /* ── role-based subscription filter ── */
    const subPendiente = role === "admin" || role === "deposito";
    const subRespondida = role === "admin" || role === "oficina" || role === "consulta";

    /* ── catch-up missed notifications from prev sessions ── */
    const catchUp = async () => {
      if (subPendiente && !pendAcked.current) {
        pendAcked.current = true;
        const since = lastSeen("pendiente");
        const data = await fetchMissed("pendiente", since);
        if (data.max_id > since) {
          addNotif("pendiente", data.count, data.items.length > 0 ? data.items[data.items.length - 1].id : undefined);
          setLastSeen("pendiente", data.max_id);
        }
      }
      if (subRespondida && !respAcked.current) {
        respAcked.current = true;
        const since = lastSeen("respondida");
        const data = await fetchMissed("respondida", since);
        if (data.max_id > since) {
          addNotif("respondida", data.count, data.items.length > 0 ? data.items[data.items.length - 1].id : undefined);
          setLastSeen("respondida", data.max_id);
        }
      }
    };
    catchUp();

    /* ── real-time WebSocket ── */
    const unsubPendiente = subPendiente
      ? globalWS.on("pendiente", (data) => {
          const maxId = (data.max_id as number) || 0;
          const prev = lastSeen("pendiente");
          if (maxId > prev) {
            addNotif("pendiente", maxId - prev, maxId);
            setLastSeen("pendiente", maxId);
          }
        })
      : () => {};

    const unsubRespondida = subRespondida
      ? globalWS.on("respondida", (data) => {
          const maxId = (data.max_id as number) || 0;
          const prev = lastSeen("respondida");
          if (maxId > prev) {
            addNotif("respondida", maxId - prev, maxId);
            setLastSeen("respondida", maxId);
          }
        })
      : () => {};

    return () => {
      unsubPendiente();
      unsubRespondida();
    };
  }, [role, addNotif]);

  const handleClick = (n: Notif) => {
    if (n.tipo === "pendiente") {
      openTab("solicitudes", "Solicitudes", n.solicitudId ? { highlight: String(n.solicitudId) } : {});
    } else {
      openTab("respuestas", "Respuestas", n.solicitudId ? { highlight: String(n.solicitudId) } : {});
    }
    setNotifs((prev) => prev.filter((x) => x.id !== n.id));
  };

  if (notifs.length === 0) return null;

  return (
    <div style={styles.container}>
      {notifs.map((n) => (
        <div
          key={n.id}
          className="notif-banner"
          style={{
            ...styles.banner,
            background: n.tipo === "pendiente"
              ? "linear-gradient(135deg, #fff3cd, #dabf70)"
              : "linear-gradient(135deg, #cce5ff, #5ba6f1)",
            borderLeft: `4px solid ${n.tipo === "pendiente" ? "#ffc107" : "#2196F3"}`,
            boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
            cursor: "pointer",
          }}
          onClick={() => handleClick(n)}
        >
          <span style={styles.link}>
            {n.count > 1 ? `${n.count} nuevas` : "1 nueva"}{" "}
            {n.tipo === "pendiente" ? "solicitud(es) pendiente(s)" : "solicitud(es) respondida(s)"}
            {" — Haz clic para ver"}
          </span>
        </div>
      ))}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    position: "fixed",
    top: 12,
    right: 20,
    zIndex: 9999,
    display: "flex",
    flexDirection: "column",
    gap: 8,
    maxWidth: 360,
  },
  banner: {
    padding: "10px 16px",
    borderRadius: 10,
    fontSize: 13,
    fontWeight: 500,
  },
  link: {
    color: "#333",
    textDecoration: "none",
  },
};
