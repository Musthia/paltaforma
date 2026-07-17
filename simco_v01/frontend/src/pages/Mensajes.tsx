import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import { getUser } from "../auth/user";
import { getGeneralMessages, getPrivateMessages, sendMessage, getAvailableUsers, markAsRead } from "../api/messages";
import type { MessageOut } from "../api/messages";
import { formatDateTime } from "../utils/date";

type TabView = "general" | "privados";

export default function Mensajes() {
  const user = getUser();
  const role = user?.role;
  const [view, setView] = useState<TabView>("general");
  const [general, setGeneral] = useState<MessageOut[]>([]);
  const [privados, setPrivados] = useState<MessageOut[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [selectedUser, setSelectedUser] = useState<number | undefined>();
  const [content, setContent] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getGeneralMessages().then(setGeneral).catch(() => {});
    getAvailableUsers()
      .then(setUsers)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (view === "privados") {
      getPrivateMessages(selectedUser).then(setPrivados).catch(() => {});
    }
  }, [view, selectedUser]);

  const handleSend = async () => {
    if (!content.trim()) return;
    setSending(true);
    try {
      if (view === "general") {
        await sendMessage({ content: content.trim(), is_general: true });
        setContent("");
        const msgs = await getGeneralMessages();
        setGeneral(msgs);
      } else {
        await sendMessage({ receiver_id: selectedUser, content: content.trim() });
        setContent("");
        const msgs = await getPrivateMessages(selectedUser);
        setPrivados(msgs);
      }
    } catch {
      alert("Error al enviar mensaje");
    } finally {
      setSending(false);
    }
  };

  const handleMarkRead = async (msg: MessageOut) => {
    if (msg.receiver_id === user?.user_id && !msg.read_at) {
      try {
        await markAsRead(msg.id);
        if (view === "general") {
          setGeneral((prev) => prev.map((m) => (m.id === msg.id ? { ...m, read_at: new Date().toISOString() } : m)));
        } else {
          setPrivados((prev) => prev.map((m) => (m.id === msg.id ? { ...m, read_at: new Date().toISOString() } : m)));
        }
      } catch {}
    }
  };

  const msgs = view === "general" ? general : privados;
  const otherUsers = users.filter((u) => u.id !== user?.user_id);

  return (
    <div style={styles.container}>
      <h1>Mensajes</h1>

      <div style={styles.tabs}>
        <button style={{ ...styles.tabBtn, ...(view === "general" ? styles.tabActive : {}) }} onClick={() => setView("general")}>
          Generales
        </button>
        <button style={{ ...styles.tabBtn, ...(view === "privados" ? styles.tabActive : {}) }} onClick={() => setView("privados")}>
          Privados
        </button>
        {role === "admin" && view === "privados" && (
          <select
            style={styles.userSelect}
            value={selectedUser ?? ""}
            onChange={(e) => setSelectedUser(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">Todos</option>
            {otherUsers.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name || u.username}</option>
            ))}
          </select>
        )}
        {role !== "admin" && view === "privados" && (
          <select
            style={styles.userSelect}
            value={selectedUser ?? ""}
            onChange={(e) => setSelectedUser(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">Seleccionar usuario</option>
            {otherUsers.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name || u.username}</option>
            ))}
          </select>
        )}
      </div>

      <div style={styles.messageList}>
        {msgs.map((msg) => (
          <div
            key={msg.id}
            style={{
              ...styles.messageCard,
              borderLeft: `4px solid ${msg.is_general ? "#0ea5e9" : msg.sender_id === user?.user_id ? "#059669" : "#d97706"}`,
              opacity: msg.receiver_id === user?.user_id && !msg.read_at ? 1 : 0.7,
              cursor: msg.receiver_id === user?.user_id && !msg.read_at ? "pointer" : "default",
            }}
            onClick={() => handleMarkRead(msg)}
          >
            <div style={styles.msgHeader}>
              <strong>{msg.sender_name || `Usuario #${msg.sender_id}`}</strong>
              {msg.receiver_name && <span style={{ color: "#6b7280" }}> → {msg.receiver_name}</span>}
              <span style={styles.msgDate}>{formatDateTime(msg.created_at)}</span>
              {msg.receiver_id === user?.user_id && !msg.read_at && <span style={styles.badge}>Nuevo</span>}
            </div>
            <div style={styles.msgContent}>{msg.content}</div>
          </div>
        ))}
        {msgs.length === 0 && <p style={{ color: "var(--text-muted)", padding: 20 }}>Sin mensajes</p>}
      </div>

      <div style={styles.sendArea}>
        <textarea
          style={styles.textarea}
          placeholder="Escribir mensaje..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={2}
        />
        <button style={styles.sendBtn} onClick={handleSend} disabled={sending || !content.trim()}>
          {sending ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  container: { maxWidth: 800, margin: "0 auto" },
  tabs: { display: "flex", gap: 8, marginBottom: 16, alignItems: "center", flexWrap: "wrap" },
  tabBtn: {
    padding: "8px 18px",
    border: "1px solid var(--border-color)",
    borderRadius: 6,
    cursor: "pointer",
    background: "var(--bg-card)",
    color: "var(--text-secondary)",
    fontSize: 13,
    fontWeight: 500,
  },
  tabActive: {
    background: "#0ea5e9",
    color: "#fff",
    borderColor: "#0ea5e9",
  },
  userSelect: {
    padding: "6px 10px",
    borderRadius: 6,
    border: "1px solid var(--border-color)",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: 13,
    marginLeft: "auto",
  },
  messageList: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    marginBottom: 16,
    maxHeight: "55vh",
    overflowY: "auto",
  },
  messageCard: {
    background: "var(--bg-card)",
    borderRadius: 8,
    padding: "12px 16px",
    boxShadow: "var(--shadow-sm)",
    border: "1px solid var(--border-color)",
    transition: "opacity 0.15s",
  },
  msgHeader: {
    display: "flex",
    gap: 8,
    alignItems: "center",
    fontSize: 12,
    marginBottom: 6,
    flexWrap: "wrap",
  },
  msgDate: {
    color: "var(--text-muted)",
    fontSize: 11,
    marginLeft: "auto",
  },
  badge: {
    background: "#dc2626",
    color: "#fff",
    fontSize: 10,
    fontWeight: 700,
    padding: "2px 8px",
    borderRadius: 10,
  },
  msgContent: {
    fontSize: 14,
    color: "var(--text-primary)",
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
  },
  sendArea: {
    display: "flex",
    gap: 10,
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid var(--border-color)",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: 14,
    resize: "vertical",
    minHeight: 50,
  },
  sendBtn: {
    padding: "10px 24px",
    border: "none",
    borderRadius: 8,
    background: "#074f70",
    color: "#fff",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    whiteSpace: "nowrap",
  },
};
