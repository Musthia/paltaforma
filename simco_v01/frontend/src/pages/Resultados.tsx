import { useEffect, useMemo, useState } from "react";
import { getSolicitudes } from "../api/solicitudes";
import { getRespuestas } from "../api/respuestas";
import { buscarEnArchivos } from "../api/buscar";
import type { ArchivoResult } from "../api/buscar";
import { formatDateTime } from "../utils/date";
import { useTabParams } from "../tabs/TabParamsContext";
import { getUser } from "../auth/user";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

type FileResult = ArchivoResult & { tipo_archivo: string };

export default function Resultados() {
    const params = useTabParams();
    const query = (params.q || "").toLowerCase();
    const user = getUser();
    const role = user?.role;
    const [loading, setLoading] = useState(true);
    const [solicitudes, setSolicitudes] = useState<any[]>([]);
    const [respuestas, setRespuestas] = useState<any[]>([]);
    const [archivos, setArchivos] = useState<FileResult[]>([]);
    const [solPage, setSolPage] = useState(1);
    const [resPage, setResPage] = useState(1);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [sols, resps, archs] = await Promise.all([
                    getSolicitudes(),
                    (role === "admin" || role === "oficina" || role === "deposito") ? getRespuestas() : Promise.resolve([]),
                    buscarEnArchivos(query).catch(() => []),
                ]);
                const q = query;
                setSolicitudes(sols.filter((s: any) => Object.values(s).join(" ").toLowerCase().includes(q)));
                setRespuestas(resps.filter((r: any) => Object.values(r).join(" ").toLowerCase().includes(q)));
                const enriched: FileResult[] = archs.map((a) => {
                    const ext = a.archivo_original.includes(".") ? a.archivo_original.split(".").pop()!.toUpperCase() : "DESCONOCIDO";
                    return { ...a, tipo_archivo: ext };
                });
                setArchivos(enriched);
            } catch {
                setSolicitudes([]);
                setRespuestas([]);
                setArchivos([]);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [query, role]);

    const solTotalPages = Math.max(1, Math.ceil(solicitudes.length / PAGE_SIZE));
    const solPageData = useMemo(() => {
        const start = (solPage - 1) * PAGE_SIZE;
        return solicitudes.slice(start, start + PAGE_SIZE);
    }, [solicitudes, solPage]);

    const resTotalPages = Math.max(1, Math.ceil(respuestas.length / PAGE_SIZE));
    const resPageData = useMemo(() => {
        const start = (resPage - 1) * PAGE_SIZE;
        return respuestas.slice(start, start + PAGE_SIZE);
    }, [respuestas, resPage]);

    /* group file results by extension */
    const archivosPorTipo = useMemo(() => {
        const map = new Map<string, FileResult[]>();
        for (const a of archivos) {
            const ext = a.tipo_archivo;
            if (!map.has(ext)) map.set(ext, []);
            map.get(ext)!.push(a);
        }
        return map;
    }, [archivos]);

    const totalCoinc = solicitudes.length + respuestas.length + archivos.length;

    return (
        <div>
            <h1>Resultados de búsqueda</h1>
            <p style={{ marginBottom: 16, color: "#000000" }}>
                {loading ? "Buscando..." : `${totalCoinc} coincidencia(s) para "${query}"`}
            </p>

            {loading ? <p>Cargando...</p> : (
                <>
                    {/* Mensajes de solicitudes */}
                    {solicitudes.length > 0 && (
                        <section style={{ marginBottom: 32 }}>
                            <h2 style={{ marginBottom: 8 }}>En mensajes de solicitudes ({solicitudes.length})</h2>
                            <table className="pro-table">
                                <thead>
                                    <tr>
                                        <th>Código</th>
                                        <th>Tipo</th>
                                        <th>Área</th>
                                        <th>Detalle</th>
                                        <th>Solicitante</th>
                                        <th>Estado</th>
                                        <th>Archivo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {solPageData.map((s) => (
                                        <tr key={s.id}>
                                            <td>{s.codigo}</td>
                                            <td>{s.tipo_documento}</td>
                                            <td>{s.identificador_documento}</td>
                                            <td>{s.detalle}</td>
                                            <td>{s.creado_por_nombre || s.creado_por_usuario_id}</td>
                                            <td>{s.estado}</td>
                                            <td>{s.archivo_nombre || "—"}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <Pagination currentPage={solPage} totalPages={solTotalPages} onPageChange={setSolPage} />
                        </section>
                    )}

                    {/* Mensajes de respuestas */}
                    {respuestas.length > 0 && (
                        <section style={{ marginBottom: 32 }}>
                            <h2 style={{ marginBottom: 8 }}>En mensajes de respuestas ({respuestas.length})</h2>
                            <table className="pro-table">
                                <thead>
                                    <tr>
                                        <th>Usuario</th>
                                        <th>Estado Doc.</th>
                                        <th>Observación</th>
                                        <th>Detalle</th>
                                        <th>Archivo</th>
                                        <th>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {resPageData.map((r) => (
                                        <tr key={r.id}>
                                            <td>{r.usuario_responde_nombre || r.usuario_responde_id}</td>
                                            <td>{r.estado_documento}</td>
                                            <td>{r.observacion}</td>
                                            <td>{r.detalle}</td>
                                            <td>{r.archivo_nombre || "—"}</td>
                                            <td>{formatDateTime(r.fecha_respuesta)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <Pagination currentPage={resPage} totalPages={resTotalPages} onPageChange={setResPage} />
                        </section>
                    )}

                    {/* Resultados dentro de archivos adjuntos — separados por tipo */}
                    {archivosPorTipo.size > 0 && (
                        <section style={{ marginBottom: 32 }}>
                            <h2 style={{ marginBottom: 12 }}>Dentro de archivos adjuntos ({archivos.length})</h2>
                            {Array.from(archivosPorTipo.entries()).map(([ext, items]) => (
                                <div key={ext} style={{ marginBottom: 20 }}>
                                    <h3 style={{ marginBottom: 6, color: "#065174", fontSize: 14 }}>{ext} ({items.length})</h3>
                                    <table className="pro-table">
                                        <thead>
                                            <tr>
                                                <th>Entidad</th>
                                                <th>Archivo</th>
                                                <th>Origen</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {items.map((item, i) => (
                                                <tr key={`${item.tipo}-${item.id}-${i}`}>
                                                    <td>{item.entidad_titulo}</td>
                                                    <td>{item.archivo_original}</td>
                                                    <td>{item.tipo === "solicitud" ? "Solicitud" : "Respuesta"}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ))}
                        </section>
                    )}

                    {totalCoinc === 0 && (
                        <p style={{ color: "#000000" }}>Sin resultados</p>
                    )}
                </>
            )}
        </div>
    );
}
