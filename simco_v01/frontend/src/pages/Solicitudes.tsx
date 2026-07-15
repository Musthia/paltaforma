import { useEffect, useMemo, useState } from "react";

import { createSolicitud, getSolicitudes, destacarSolicitud, verificarSolicitud, getArchivoSolicitudUrl, getArchivoSolicitudDownloadUrl } from "../api/solicitudes";

import { formatDateTime } from "../utils/date";
import { useTabs } from "../tabs/TabContext";
import { useTabParams } from "../tabs/TabParamsContext";
import { getUser } from "../auth/user";
import { useRefreshOnNotification } from "../ws/useRefreshOnNotification";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

export default function Solicitudes() {
    const { openTab } = useTabs();
    const params = useTabParams();
    const highlightParam = params.highlight;
    const user = getUser();
    const role = user?.role;
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [selectedSolicitud, setSelectedSolicitud] = useState<any | null>(null);

    const totalPages = Math.max(1, Math.ceil(data.length / PAGE_SIZE));
    const pageData = useMemo(() => {
        const start = (page - 1) * PAGE_SIZE;
        return data.slice(start, start + PAGE_SIZE);
    }, [data, page]);

    const load = async () => {
        try {
            setLoading(true);
            setError(null);
            const res = await getSolicitudes();
            setData(res.reverse());
        } catch (err) {
            setError("Error al cargar solicitudes");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    useRefreshOnNotification("pendiente", load);

    type SolicitudForm = {
        tipo_documento: string;
        identificador_documento: string;
        detalle: string;
        prioridad: "baja" | "media" | "alta";
    };

    const [open, setOpen] = useState(false);
    const [archivo, setArchivo] = useState<File | null>(null);

    const [form, setForm] = useState<SolicitudForm>({
        tipo_documento: "",
        identificador_documento: "",
        detalle: "",
        prioridad: "media"
    });

    const handleCreate = async () => {
        const fd = new FormData();
        fd.append("tipo_documento", form.tipo_documento);
        fd.append("identificador_documento", form.identificador_documento);
        fd.append("detalle", form.detalle);
        fd.append("prioridad", form.prioridad);
        if (archivo) fd.append("archivo", archivo);
        await createSolicitud(fd);
        setOpen(false);
        setArchivo(null);
        load();
    };

    const handleDestacar = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        try {
            await destacarSolicitud(id);
        } catch (err: any) {
            const msg = err?.response?.data?.detail || "Error al destacar";
            window.alert(msg);
        }
        load();
    };

    const handleVerificar = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        try {
            await verificarSolicitud(id);
        } catch (err: any) {
            const msg = err?.response?.data?.detail || "Error al verificar";
            window.alert(msg);
        }
        load();
    };

    const rowBackground = (s: any): string => {
        if (role === "consulta") return "transparent";
        if (s.estado === "respondida") return "#697e8a";
        if (s.destacado) return "#f80519";
        if (s.verificado) return "#20943b";
        return "transparent";
    };

    return (
        <div>
            <h1>Solicitudes</h1>

            {loading && <p>Cargando...</p>}

            {error && <p style={{ color: "red" }}>{error}</p>}

            <button onClick={load}>
                Refrescar
            </button>

            {role !== "deposito" && role !== "consulta" && (
                <button onClick={() => setOpen(true)}>
                    Nueva Solicitud
                </button>
            )}

            {open && (
            <div style={stylesForm.card}>
                <h3 style={stylesForm.title}>Nueva Solicitud</h3>
                    
                <input
                    style={stylesForm.input}
                    placeholder="Tipo documento"
                    onChange={(e) =>
                        setForm({ ...form, tipo_documento: e.target.value })
                    }
                />
        
                <input
                    style={stylesForm.input}
                    placeholder="Area"
                    onChange={(e) =>
                        setForm({ ...form, identificador_documento: e.target.value })
                    }
                />
        
                <textarea
                    style={{ ...stylesForm.input, minHeight: 70, resize: "vertical" }}
                    placeholder="Detalle"
                    onChange={(e) =>
                        setForm({ ...form, detalle: e.target.value })
                    }
                />
        
                <input
                    style={stylesForm.fileInput}
                    type="file"
                    onChange={(e) => setArchivo(e.target.files?.[0] || null)}
                />
                
                <select
                    style={stylesForm.input}
                    value={form.prioridad}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            prioridad: e.target.value as "baja" | "media" | "alta"
                        })
                    }
                >
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                </select>
                
                <div style={stylesForm.buttons}>
                    <button style={stylesForm.btnPrimary} onClick={handleCreate}>
                        Solicitar
                    </button>
                    <button style={stylesForm.btnSecondary} onClick={() => setOpen(false)}>
                        Cancelar
                    </button>
                </div>
            </div>
        )}

            <table className="pro-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Codigo</th>
                        <th>Tipo de Archivo</th>
                        <th>Area</th>
                        <th>Detalle</th>
                        <th>Estado</th>
                        <th>Prioridad</th>
                        <th>Solicitante</th>
                        <th>Fecha de Solicitud</th>
                        <th>Archivo</th>
                        <th>Acción</th>
                    </tr>
                </thead>

                <tbody>
                    {pageData.map((s) => {
                        const clickable = s.estado === "pendiente";
                        return (
                        <tr
                            key={s.id}
                            style={{
                                backgroundColor: highlightParam && String(s.id) === highlightParam ? "var(--bg-card)3cd" : rowBackground(s),
                                outline: highlightParam && String(s.id) === highlightParam ? "2px solid #ffc107" : undefined,
                                cursor: clickable ? "pointer" : "default",
                            }}
                            onClick={clickable ? () => openTab("respuestas", "Respuestas", { solicitud_id: String(s.id), codigo: s.codigo, highlight: String(s.id) }) : undefined}
                            onDoubleClick={() => setSelectedSolicitud(s)}
                        >
                            <td>{s.id}</td>
                            <td>{s.codigo}</td>
                            <td>{s.tipo_documento}</td>
                            <td>{s.identificador_documento}</td>
                            <td>{s.detalle}</td>
                            <td>{s.estado}</td>
                            <td>{s.prioridad}</td>
                            <td>{s.creado_por_nombre || s.creado_por_usuario_id}</td>
                            <td>{formatDateTime(s.fecha_creacion)}</td>
                            <td>{s.archivo_nombre && <ArchivoLink nombre={s.archivo_nombre} url={getArchivoSolicitudUrl(s.id)} downloadUrl={getArchivoSolicitudDownloadUrl(s.id)} />}</td>
                            <td>
                                {s.estado === "pendiente" ? (
                                    <>
                                        {(role === "admin" || role === "deposito") && (
                                            <button onClick={(e) => handleVerificar(e, s.id)}>
                                                {s.verificado ? "✓ Verificado" : "Verificando"}
                                            </button>
                                        )}
                                        {(role === "admin" || role === "oficina") && (
                                            <button onClick={(e) => handleDestacar(e, s.id)}>
                                                {s.destacado ? "★ Destacado" : "Destacar"}
                                            </button>
                                        )}
                                    </>
                                ) : (
                                    <span style={{ color: "#206994" }}>{s.estado}</span>
                                )}
                            </td>
                        </tr>
                    );
                    })}
                </tbody>
            </table>

            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />

            {/* ── Modal detalle solicitud respondida ── */}
            {selectedSolicitud && (
                <div style={modalStyles.overlay} onClick={() => setSelectedSolicitud(null)}>
                    <div style={modalStyles.panel} onClick={(e) => e.stopPropagation()}>
                        <div style={modalStyles.header}>
                            <h2 style={{ margin: 0, fontSize: 16 }}>Solicitud #{selectedSolicitud.id} <span style={{ fontSize: 12, fontWeight: 400, color: "var(--text-muted)" }}>({selectedSolicitud.estado})</span></h2>
                            <button style={modalStyles.closeBtn} onClick={() => setSelectedSolicitud(null)}>×</button>
                        </div>

                        <div style={modalStyles.body}>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Código</span>
                                <span>{selectedSolicitud.codigo}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Tipo de documento</span>
                                <span>{selectedSolicitud.tipo_documento}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Área</span>
                                <span>{selectedSolicitud.identificador_documento}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Detalle</span>
                                <span>{selectedSolicitud.detalle}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Prioridad</span>
                                <span>{selectedSolicitud.prioridad}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Estado</span>
                                <span style={{ color: "#206994", fontWeight: 600 }}>{selectedSolicitud.estado}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Destacado</span>
                                <span>{selectedSolicitud.destacado ? "✓ Sí" : "✗ No"}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Verificado</span>
                                <span>{selectedSolicitud.verificado ? "✓ Sí" : "✗ No"}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Solicitante</span>
                                <span>{selectedSolicitud.creado_por_nombre || selectedSolicitud.creado_por_usuario_id}</span>
                            </div>
                            <div style={modalStyles.fieldRow}>
                                <span style={modalStyles.label}>Fecha</span>
                                <span>{formatDateTime(selectedSolicitud.fecha_creacion)}</span>
                            </div>
                            {selectedSolicitud.archivo_nombre && (
                                <div style={modalStyles.fieldRow}>
                                    <span style={modalStyles.label}>Archivo</span>
                                    <span>
                                        <ArchivoLink
                                            nombre={selectedSolicitud.archivo_nombre}
                                            url={getArchivoSolicitudUrl(selectedSolicitud.id)}
                                            downloadUrl={getArchivoSolicitudDownloadUrl(selectedSolicitud.id)}
                                        />
                                    </span>
                                </div>
                            )}
                        </div>

                        <div style={modalStyles.footer}>
                            {selectedSolicitud.estado === "pendiente" && (role === "admin" || role === "deposito") && (
                                <button
                                    style={modalStyles.btnPrimary}
                                    onClick={() => {
                                        setSelectedSolicitud(null);
                                        openTab("respuestas", "Respuestas", { solicitud_id: String(selectedSolicitud.id), codigo: selectedSolicitud.codigo });
                                    }}
                                >
                                    Responder
                                </button>
                            )}
                            <button style={modalStyles.btnSecondary} onClick={() => setSelectedSolicitud(null)}>
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}
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
                <a href={downloadUrl} style={{ marginLeft: 8, fontSize: "0.75em", color: "#418051" }} title="Descargar">
                    ⬇
                </a>
            </div>
        </div>
    );
}

const stylesForm: Record<string, React.CSSProperties> = {
    card: {
        background: "linear-gradient(135deg, #a3b7c2, #011429)",
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
        backgroundColor: "var(--bg-card)fff00",
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
        backgroundColor: "#0ea5e9",
        color: "var(--bg-card)",
        fontSize: 14,
        fontWeight: 600,
        cursor: "pointer",
        transition: "background-color 0.2s",
    },
    btnSecondary: {
        padding: "10px 24px",
        border: "1px solid #d1d5db",
        borderRadius: 6,
        backgroundColor: "var(--bg-card)",
        color: "#555",
        fontSize: 14,
        cursor: "pointer",
        transition: "background-color 0.2s",
    },
};

const modalStyles: Record<string, React.CSSProperties> = {
    overlay: {
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 10000,
    },
    panel: {
        background: "var(--bg-card)",
        borderRadius: 16,
        width: 520,
        maxWidth: "90vw",
        maxHeight: "85vh",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
    },
    header: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "18px 24px",
        borderBottom: "1px solid var(--border-color)",
    },
    closeBtn: {
        border: "none",
        background: "none",
        fontSize: 22,
        cursor: "pointer",
        color: "var(--text-muted)",
        lineHeight: 1,
    },
    body: {
        padding: "20px 24px",
        overflowY: "auto",
        flex: 1,
        display: "flex",
        flexDirection: "column",
        gap: 10,
    },
    fieldRow: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        gap: 16,
        fontSize: 13,
    },
    label: {
        fontWeight: 600,
        color: "var(--text-secondary)",
        minWidth: 120,
        flexShrink: 0,
    },
    footer: {
        display: "flex",
        justifyContent: "flex-end",
        gap: 10,
        padding: "14px 24px",
        borderTop: "1px solid var(--border-color)",
    },
    btnPrimary: {
        padding: "9px 22px",
        border: "none",
        borderRadius: 8,
        backgroundColor: "#085375",
        color: "var(--bg-card)",
        fontSize: 13,
        fontWeight: 600,
        cursor: "pointer",
    },
    btnSecondary: {
        padding: "9px 22px",
        border: "1px solid #d1d5db",
        borderRadius: 8,
        backgroundColor: "var(--bg-card)",
        color: "var(--text-secondary)",
        fontSize: 13,
        cursor: "pointer",
    },
};