import { useCallback, useEffect, useMemo, useState } from "react";

import { createRespuesta, getRespuestas, getArchivoRespuestaUrl, getArchivoRespuestaDownloadUrl } from "../api/respuestas";
import { getSolicitudes } from "../api/solicitudes";

import { formatDateTime } from "../utils/date";
import { useTabParams } from "../tabs/TabParamsContext";
import { getUser } from "../auth/user";
import { useRefreshOnNotification } from "../ws/useRefreshOnNotification";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

export default function Respuestas() {
    const params = useTabParams();
    const solicitudIdParam = params.solicitud_id;
    const highlightParam = params.highlight;
    const user = getUser();
    const role = user?.role;

    const [data, setLogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);

    const totalPages = Math.max(1, Math.ceil(data.length / PAGE_SIZE));
    const pageData = useMemo(() => {
        const start = (page - 1) * PAGE_SIZE;
        return data.slice(start, start + PAGE_SIZE);
    }, [data, page]);

    const load = async () => {
        try {
            setLoading(true);
            setError(null);
            const respuestas = await getRespuestas();
            setLogs(respuestas.reverse());
        } catch (err) {
            setError("Error al cargar respuestas");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    useRefreshOnNotification("respondida", load);

    type RespuestaForm = {
        solicitud_id: number;
        estado_documento: string;
        observacion: string;
        detalle: string;
    };

    const [open, setOpen] = useState(false);
    const [archivo, setArchivo] = useState<File | null>(null);
    const [pendientes, setPendientes] = useState<any[]>([]);

    const [form, setForm] = useState<RespuestaForm>({
        solicitud_id: solicitudIdParam ? Number(solicitudIdParam) : 0,
        estado_documento: "",
        observacion: "",
        detalle: ""
    });

    useEffect(() => {
        if (solicitudIdParam && role !== "oficina" && role !== "consulta") {
            setForm((prev) => ({ ...prev, solicitud_id: Number(solicitudIdParam) }));
            setOpen(true);
        }
    }, [solicitudIdParam]);

    /* ── load pending solicitudes for selector ── */
    const loadPendientes = useCallback(async () => {
        try {
            const sols = await getSolicitudes();
            const pend = sols
                .filter((s: any) => s.estado === "pendiente")
                .sort((a: any, b: any) => {
                    const pa = a.destacado ? 0 : a.verificado ? 1 : 2;
                    const pb = b.destacado ? 0 : b.verificado ? 1 : 2;
                    return pa - pb;
                });
            setPendientes(pend);
        } catch { /* ignore */ }
    }, []);

    useEffect(() => {
        loadPendientes();
    }, [loadPendientes]);

    const handleSelectSolicitud = (id: number) => {
        setForm((prev) => ({ ...prev, solicitud_id: id }));
        setOpen(true);
    };

    const handleCreate = async () => {
        const fd = new FormData();
        fd.append("solicitud_id", String(form.solicitud_id));
        fd.append("estado_documento", form.estado_documento);
        fd.append("observacion", form.observacion);
        fd.append("detalle", form.detalle);
        if (archivo) fd.append("archivo", archivo);
        await createRespuesta(fd);
        setOpen(false);
        setArchivo(null);
        setForm({ solicitud_id: form.solicitud_id, estado_documento: "", observacion: "", detalle: "" });
        load();
        loadPendientes();
    };

    return (
        <div>
            <h1>Respuestas SiMCo</h1>

            {loading && <p>Cargando...</p>}

            {error && <p style={{ color: "red" }}>{error}</p>}

            <button onClick={load}>
                Refrescar
            </button>

           

            {/* ── Selector de solicitudes pendientes ── */}
            {!open && role !== "oficina" && role !== "consulta" && pendientes.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                    <label style={{ display: "block", marginBottom: 6, fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>
                        Seleccionar solicitud pendiente:
                    </label>
                    <select
                        style={{
                            width: "100%",
                            maxWidth: 520,
                            padding: "10px 12px",
                            border: "1px solid #d1d5db",
                            borderRadius: 8,
                            fontSize: 14,
                            outline: "none",
                            background: "#fff",
                        }}
                        value={form.solicitud_id || ""}
                        onChange={(e) => {
                            const id = Number(e.target.value);
                            if (id) handleSelectSolicitud(id);
                        }}
                    >
                        <option value="">— Seleccione —</option>
                        {pendientes.map((s) => {
                            const dot = s.destacado ? "🔴" : s.verificado ? "🟢" : "⚪";
                            return (
                                <option key={s.id} value={s.id}>
                                    {dot} {s.identificador_documento} — {s.detalle?.slice(0, 60)}
                                </option>
                            );
                        })}
                    </select>
                </div>
            )}

            {open && role !== "oficina" && role !== "consulta" && (
            <div style={stylesForm.card}>
                <h3 style={stylesForm.title}>Responder Solicitud</h3>

                <label style={{ display: "block", marginBottom: 12, fontSize: 14, color: "#555" }}>
                    Solicitud: <strong style={{ color: "#2c3e50" }}>{form.solicitud_id > 0 ? `#${form.solicitud_id}` : "—"}</strong>
                    {(() => {
                        const sel = pendientes.find((s) => s.id === form.solicitud_id);
                        return sel ? (
                            <span style={{ marginLeft: 8, color: "#888", fontSize: "0.85em" }}>
                                {sel.identificador_documento} — {sel.detalle?.slice(0, 40)}
                            </span>
                        ) : null;
                    })()}
                </label>

                <input
                    style={stylesForm.input}
                    placeholder="Estado documento"
                    value={form.estado_documento}
                    onChange={(e) =>
                        setForm({ ...form, estado_documento: e.target.value })
                    }
                />

                <input
                    style={stylesForm.input}
                    placeholder="Area"
                    value={form.observacion}
                    onChange={(e) =>
                        setForm({ ...form, observacion: e.target.value })
                    }
                />
                <input
                    style={stylesForm.fileInput}
                    type="file"
                    onChange={(e) => setArchivo(e.target.files?.[0] || null)}
                />

                <textarea
                    style={{ ...stylesForm.input, minHeight: 70, resize: "vertical" }}
                    placeholder="Detalle"
                    value={form.detalle}
                    onChange={(e) =>
                        setForm({ ...form, detalle: e.target.value })
                    }
                />

                <div style={stylesForm.buttons}>
                    <button style={stylesForm.btnPrimary} onClick={handleCreate}>
                        Responder
                    </button>
                    <button style={stylesForm.btnSecondary} onClick={() => { setOpen(false); setForm((prev) => ({ ...prev, solicitud_id: 0 })); }}>
                        Cancelar
                    </button>
                </div>
            </div>
        )}

            <table className="pro-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Solicitud ID</th>
                        <th>Usuario</th>
                        <th>Estado</th>
                        <th>Area</th>
                        <th>Archivo</th>
                        <th>Detalle</th>
                        <th>Fecha</th>
                    </tr>
                </thead>

                <tbody>
                    {pageData.map((log) => {
                        const highlighted = highlightParam && String(log.solicitud_id) === highlightParam;
                        return (
                        <tr key={log.id} style={highlighted ? { backgroundColor: "#fff3cd", outline: "2px solid #ffc107" } : undefined}>
                            <td>{log.id}</td>
                            <td>{log.solicitud_id}</td>
                            <td>{log.usuario_responde_nombre || log.usuario_responde_id}</td>
                            <td>{log.estado_documento}</td>
                            <td>{log.observacion}</td>
                            <td>{log.archivo_nombre && <ArchivoLink nombre={log.archivo_nombre} url={getArchivoRespuestaUrl(log.id)} downloadUrl={getArchivoRespuestaDownloadUrl(log.id)} />}</td>
                            <td>{log.detalle}</td>
                            <td>{formatDateTime(log.fecha_respuesta)}</td>
                        </tr>
                    );
                    })}
                </tbody>
            </table>

            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
    );
}

function ArchivoLink({ nombre, url, downloadUrl }: { nombre: string; url: string; downloadUrl: string }) {
    const nombreOriginal = nombre.includes("::") ? nombre.split("::", 2)[1] : nombre;
    const esImagen = /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(nombreOriginal);

    return (
        <div>
            {esImagen && (
                <img src={url} alt={nombreOriginal} style={{ maxWidth: 60, maxHeight: 60, display: "block", marginBottom: 4, borderRadius: 4, border: "1px solid #555" }} />
            )}
            <div>
                <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: "#4da6ff", fontSize: "0.85em" }}>
                    {nombreOriginal}
                </a>
                <a href={downloadUrl} style={{ marginLeft: 8, fontSize: "0.75em", color: "#888" }} title="Descargar">
                    ⬇
                </a>
            </div>
        </div>
    );
}

const stylesForm: Record<string, React.CSSProperties> = {
    card: {
        background: "linear-gradient(135deg, #a5a5a5, #0c2033)",
        borderRadius: 10,
        padding: 24,
        marginBottom: 20,
        boxShadow: "0 4px 16px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.06)",
        border: "1px solid #e9ecef",
        maxWidth: 520,
    },
    title: {
        margin: "0 0 16px 0",
        fontSize: 18,
        fontWeight: 600,
        color: "#2c3e50",
    },
    input: {
        width: "100%",
        boxSizing: "border-box",
        padding: "10px 12px",
        marginBottom: 12,
        border: "1px solid #d1d5db",
        borderRadius: 6,
        fontSize: 14,
        backgroundColor: "#ffffff00",
        outline: "none",
        transition: "border-color 0.2s, box-shadow 0.2s",
    },
    fileInput: {
        marginBottom: 12,
        fontSize: 13,
        color: "#555",
    },
    buttons: {
        display: "flex",
        gap: 10,
        marginTop: 4,
    },
    btnPrimary: {
        padding: "10px 24px",
        border: "none",
        borderRadius: 6,
        backgroundColor: "#075477",
        color: "#fff",
        fontSize: 14,
        fontWeight: 600,
        cursor: "pointer",
        transition: "background-color 0.2s",
    },
    btnSecondary: {
        padding: "10px 24px",
        border: "1px solid #d1d5db",
        borderRadius: 6,
        backgroundColor: "#fff",
        color: "#555",
        fontSize: 14,
        cursor: "pointer",
        transition: "background-color 0.2s",
    },
};     
