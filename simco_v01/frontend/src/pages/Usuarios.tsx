import { useEffect, useMemo, useState } from "react";
import {
  getUsuarios,
  createUsuario,
  updateUsuario,
  deleteUsuario,
  type Usuario,
} from "../api/usuarios";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

type FormMode = "crear" | "editar";

interface FormData {
  username: string;
  full_name: string;
  password: string;
  role: string;
}

const emptyForm: FormData = {
  username: "",
  full_name: "",
  password: "",
  role: "oficina",
};

export default function Usuarios() {
  const [data, setData] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const [modalOpen, setModalOpen] = useState(false);
  const [mode, setMode] = useState<FormMode>("crear");
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormData>(emptyForm);

  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  useEffect(() => {
    load();
  }, []);

  const totalPages = Math.max(1, Math.ceil(data.length / PAGE_SIZE));
  const pageData = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return data.slice(start, start + PAGE_SIZE);
  }, [data, page]);

  const load = async () => {
    setLoading(true);
    try {
      const res = await getUsuarios();
      setData(res);
      setPage(1);
    } catch {
      alert("Error al cargar usuarios");
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setMode("crear");
    setEditId(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (u: Usuario) => {
    setMode("editar");
    setEditId(u.id);
    setForm({
      username: u.username,
      full_name: u.full_name,
      password: "",
      role: u.role,
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.username || !form.full_name || !form.role) {
      alert("Completa todos los campos obligatorios");
      return;
    }
    if (mode === "crear" && !form.password) {
      alert("La contraseña es obligatoria");
      return;
    }
    try {
      if (mode === "crear") {
        await createUsuario(form);
      } else if (editId !== null) {
        const payload: Record<string, string> = {};
        if (form.full_name) payload.full_name = form.full_name;
        if (form.password) payload.password = form.password;
        if (form.role) payload.role = form.role;
        await updateUsuario(editId, payload);
      }
      setModalOpen(false);
      load();
    } catch {
      alert("Error al guardar usuario");
    }
  };

  const handleDelete = async () => {
    if (confirmDelete === null) return;
    try {
      await deleteUsuario(confirmDelete);
      setConfirmDelete(null);
      load();
    } catch {
      alert("Error al eliminar usuario");
    }
  };

  return (
    <div>
      <h1>Usuarios</h1>

      {loading && <p>Cargando...</p>}

      <button onClick={load}>Refrescar</button>
      <button onClick={openCreate}>Nuevo Usuario</button>

      <table className="pro-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Nombre Completo</th>
            <th>Rol</th>
            <th>Activo</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {pageData.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.full_name}</td>
              <td>{u.role}</td>
              <td>{u.is_active ? "Sí" : "No"}</td>
              <td>
                <button onClick={() => openEdit(u)}>Editar</button>
                <button onClick={() => setConfirmDelete(u.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />

      {modalOpen && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <h3>{mode === "crear" ? "Nuevo Usuario" : "Editar Usuario"}</h3>

            <label style={styles.label}>
              Usuario *
              <input
                style={styles.input}
                value={form.username}
                disabled={mode === "editar"}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
              />
            </label>

            <label style={styles.label}>
              Nombre Completo *
              <input
                style={styles.input}
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
            </label>

            <label style={styles.label}>
              Contraseña {mode === "editar" && "(dejar vacío para no cambiar)"}
              <input
                style={styles.input}
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </label>

            <label style={styles.label}>
              Rol *
              <select
                style={styles.input}
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option value="admin">admin</option>
                <option value="oficina">oficina</option>
                <option value="deposito">deposito</option>
                <option value="consulta">consulta</option>
              </select>
            </label>

            <div style={styles.buttons}>
              <button onClick={handleSave}>Guardar</button>
              <button onClick={() => setModalOpen(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}

      {confirmDelete !== null && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <p>¿Eliminar usuario ID {confirmDelete}?</p>
            <div style={styles.buttons}>
              <button onClick={handleDelete}>Eliminar</button>
              <button onClick={() => setConfirmDelete(null)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    inset: 0,
    backgroundColor: "rgba(0,0,0,0.4)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  modal: {
    background: "#fff",
    padding: 24,
    borderRadius: 8,
    minWidth: 360,
    maxWidth: 480,
    boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
  },
  label: {
    display: "block",
    marginBottom: 10,
    fontSize: 14,
    fontWeight: 500,
  },
  input: {
    display: "block",
    width: "100%",
    marginTop: 4,
    padding: "6px 8px",
    fontSize: 14,
    border: "1px solid #ccc",
    borderRadius: 4,
    boxSizing: "border-box",
  },
  buttons: {
    display: "flex",
    gap: 8,
    marginTop: 16,
    justifyContent: "flex-end",
  },
};
