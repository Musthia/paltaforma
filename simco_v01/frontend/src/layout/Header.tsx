import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { clearTokens } from "../auth/token";
import { getUser } from "../auth/user";
import { useTabs } from "../tabs/TabContext";
import { getAvailableUsers, sendMessage, getUnreadCount } from "../api/messages";

export default function Header() {
  const navigate = useNavigate();
  const user = getUser();
  //console.log(user);
  console.log("USER =", user);
  const { activeTab, tabs, openTab } = useTabs();
  const [showModal, setShowModal] = useState(false);
  const [users, setUsers] = useState<any[]>([]);
  const [receiverId, setReceiverId] = useState<number | "">("");
  const [msgContent, setMsgContent] = useState("");
  const [unread, setUnread] = useState(0);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getUnreadCount().then(setUnread).catch(() => {});
  }, []);

  useEffect(() => {
    getAvailableUsers()
      .then(setUsers)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!showModal) return;
    const handler = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        setShowModal(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [showModal]);

  const handleSend = async () => {
    if (!receiverId || !msgContent.trim()) return;
    try {
      await sendMessage({ receiver_id: Number(receiverId), content: msgContent.trim() });
      setMsgContent("");
      setReceiverId("");
      setShowModal(false);
    } catch {
      alert("Error al enviar mensaje");
    }
  };

  const logout = () => {
    clearTokens();
    navigate("/");
  };

  const currentTab = tabs.find((t) => t.id === activeTab);
  const title = currentTab?.label || "Dashboard";
  const role = user?.role;
  const showMessages = role !== "consulta";

  console.log("USER =", user);
  
  return (
    <header style={styles.header}>
      <div style={styles.left}>
        <h1 style={styles.title}>{title}</h1>
      </div>

      <div style={styles.right}>
        {showMessages && unread > 0 && (
          <button
            style={styles.msgBadge}
            onClick={() => openTab("mensajes", "Mensajes")}
            title={`${unread} mensaje(s) no leído(s)`}
          >
            ✉ {unread}
          </button>
        )}

        <div style={styles.userMeta}>
            <span style={styles.userName}>
                {user?.full_name || user?.sub}
            </span>
            <span style={styles.userRole}>
                {user?.role}
            </span>
        </div>
        <div style={styles.avatar}>
            {(user?.full_name || user?.sub)?.charAt(0).toUpperCase() || "U"}
        </div>
        <button style={styles.logoutBtn} onClick={logout}>
            Cerrar sesión
        </button>
      </div>

      {showModal && showMessages && (
        <div style={styles.overlay}>
          <div ref={modalRef} style={styles.modal}>
            <h3 style={styles.modalTitle}>Enviar mensaje privado</h3>
            <select
              style={styles.modalSelect}
              value={receiverId}
              onChange={(e) => setReceiverId(e.target.value ? Number(e.target.value) : "")}
            >
              <option value="">Seleccionar usuario</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name || u.username} ({u.role})
                </option>
              ))}
            </select>
            <textarea
              style={styles.modalTextarea}
              placeholder="Escribir mensaje..."
              value={msgContent}
              onChange={(e) => setMsgContent(e.target.value)}
              rows={3}
            />
            <div style={styles.modalButtons}>
              <button style={styles.modalSendBtn} onClick={handleSend} disabled={!receiverId || !msgContent.trim()}>
                Enviar
              </button>
              <button style={styles.modalCancelBtn} onClick={() => setShowModal(false)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    height: "var(--header-h)",
    background: "#fff",
    borderBottom: "1px solid var(--border-color)",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 24px",
    flexShrink: 0,
  },
  left: {
    display: "flex",
    alignItems: "center",
    gap: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 600,
    color: "var(--text-primary)",
    margin: 0,
    letterSpacing: "-0.3px",
  },
  right: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: "50%",
    background: "#e2e8f0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 14,
    fontWeight: 600,
    color: "var(--text-secondary)",
    flexShrink: 0,
  },
  userMeta: {
    display: "flex",
    flexDirection: "column",
    lineHeight: 1.3,
  },
  userName: {
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-primary)",
  },
  userRole: {
    fontSize: 11,
    color: "var(--text-muted)",
    display: "flex",
    alignItems: "center",
    gap: 4,
  },
  roleDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    display: "inline-block",
  },
  logoutBtn: {
    padding: "6px 14px",
    border: "1px solid #e2e8f0",
    borderRadius: 8,
    background: "transparent",
    color: "#dc2626",
    fontSize: 12,
    fontWeight: 500,
    cursor: "pointer",
    transition: "all 0.15s",
  },
  avatarWrapper: {
    cursor: "pointer",
    lineHeight: 0,
  },
  msgBadge: {
    background: "#0ea5e9",
    color: "#fff",
    border: "none",
    borderRadius: 20,
    padding: "4px 12px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 4,
  },
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    background: "var(--bg-card)",
    borderRadius: 12,
    padding: 24,
    width: "90%",
    maxWidth: 440,
    boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
    border: "1px solid var(--border-color)",
  },
  modalTitle: {
    margin: "0 0 16px",
    fontSize: 16,
    fontWeight: 600,
    color: "var(--text-primary)",
  },
  modalSelect: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid var(--border-color)",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: 14,
    marginBottom: 12,
  },
  modalTextarea: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid var(--border-color)",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: 14,
    resize: "vertical",
    minHeight: 60,
    marginBottom: 12,
    boxSizing: "border-box",
  },
  modalButtons: {
    display: "flex",
    gap: 10,
    justifyContent: "flex-end",
  },
  modalSendBtn: {
    padding: "8px 20px",
    border: "none",
    borderRadius: 8,
    background: "#0ea5e9",
    color: "#fff",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
  modalCancelBtn: {
    padding: "8px 20px",
    border: "1px solid var(--border-color)",
    borderRadius: 8,
    background: "transparent",
    color: "var(--text-secondary)",
    fontSize: 14,
    cursor: "pointer",
  },
};
