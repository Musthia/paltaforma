import { useEffect, useMemo, useState } from "react";

import { getActivity } from "../api/auditoria";

import { formatDateTime } from "../utils/date";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 10;

export default function Auditoria() {
    const [logs, setLogs] = useState<any[]>([]);
    const [page, setPage] = useState(1);

    useEffect(() => {
        load();
    }, []);

    const totalPages = Math.max(1, Math.ceil(logs.length / PAGE_SIZE));
    const pageData = useMemo(() => {
        const start = (page - 1) * PAGE_SIZE;
        return logs.slice(start, start + PAGE_SIZE);
    }, [logs, page]);

    const load = async () => {
        const auditoria = await getActivity();
        setLogs(auditoria);
        setPage(1);
    };

    return (
        <div>
            <h1>Auditoria SiMCo</h1>

            <button onClick={load}>Refrescar</button>

            <h2>Actividad del Sistema</h2>

            <table className="pro-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Acción</th>
                        <th>Codigo</th>
                        <th>Entidad</th>
                        <th>ID Entidad</th>
                        <th>Detalle</th>
                        <th>Fecha</th>
                    </tr>
                </thead>

                <tbody>
                    {pageData.map((log) => (
                        <tr key={log.id}>
                            <td>{log.id}</td>
                            <td>{log.usuario_id}</td>
                            <td>{log.accion}</td>
                            <td>{log.codigo}</td>
                            <td>{log.entidad}</td>
                            <td>{log.entidad_id}</td>
                            <td>{log.detalle}</td>
                            <td>{formatDateTime(log.fecha)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
    );
}
