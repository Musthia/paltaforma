import { useEffect, useRef, useState } from "react";
import { getUser } from "../auth/user";
import { globalWS } from "./globalWS";

interface Notif {
  tipo: "pendiente" | "respondida";
  count: number;
  id: number;
}

const ROLE_FILTER: Record<string, ("admin" | "deposito" | "oficina")[]> = {
  pendiente: ["admin", "deposito"],
  respondida: ["admin", "oficina"],
};

export function useNotifications() {
  const [notifs, setNotifs] = useState<Notif[]>([]);
  const roleRef = useRef(getUser()?.role);
  roleRef.current = getUser()?.role;

  useEffect(() => {
    globalWS.start();

    const unsubPendiente = globalWS.on("pendiente", (data) => {
      const role = roleRef.current;
      if (role && ROLE_FILTER.pendiente.includes(role as any)) {
        setNotifs((prev) => [
          ...prev,
          { tipo: "pendiente", count: data.count as number, id: Date.now() + Math.random() },
        ]);
      }
    });

    const unsubRespondida = globalWS.on("respondida", (data) => {
      const role = roleRef.current;
      if (role && ROLE_FILTER.respondida.includes(role as any)) {
        setNotifs((prev) => [
          ...prev,
          { tipo: "respondida", count: data.count as number, id: Date.now() + Math.random() },
        ]);
      }
    });

    return () => {
      unsubPendiente();
      unsubRespondida();
    };
  }, []);

  const dismiss = (id: number) => {
    setNotifs((prev) => prev.filter((n) => n.id !== id));
  };

  return { notifs, dismiss };
}
