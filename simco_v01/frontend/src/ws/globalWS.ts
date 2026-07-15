// En desarrollo usa la URL del env; en producción usa ws/wss del mismo host
const WS_BASE = import.meta.env.VITE_WS_URL || `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;

type Listener = (data: Record<string, unknown>) => void;

class GlobalWS {
  private ws: WebSocket | null = null;
  private listeners = new Map<string, Set<Listener>>();
  private retryTimer: ReturnType<typeof setTimeout> | null = null;
  private destroyed = false;
  private started = false;

  start() {
    if (this.started) return;
    this.started = true;
    this.connect();
  }

  private connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(`${WS_BASE}/ws/notificaciones`);

    this.ws.onopen = () => {
      this.ws?.send(JSON.stringify({ token: "" }));
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const tipo = data.tipo as string;
        if (tipo) {
          this.listeners.get(tipo)?.forEach((fn) => fn(data));
          this.listeners.get("*")?.forEach((fn) => fn(data));
        }
      } catch {
        // ignore
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
      if (!this.destroyed) {
        this.retryTimer = setTimeout(() => this.connect(), 5000);
      }
    };

    this.ws.onerror = () => this.ws?.close();
  }

  on(tipo: string, listener: Listener) {
  if (!this.listeners.has(tipo)) {
    this.listeners.set(tipo, new Set());
  }

  this.listeners.get(tipo)!.add(listener);

  return () => {
    this.listeners.get(tipo)?.delete(listener);
  };
}

  stop() {
    this.destroyed = true;
    if (this.retryTimer) clearTimeout(this.retryTimer);
    this.ws?.close();
    this.ws = null;
    this.listeners.clear();
    this.started = false;
  }
}

export const globalWS = new GlobalWS();
