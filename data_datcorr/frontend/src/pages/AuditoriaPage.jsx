import { useState, useEffect } from "react";
import { Box, Typography } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { getAuditoria } from "../services/dashboardService";
import { usePermissions } from "../auth/usePermissions";

const actionColor = (accion) => {
    const map = {
        LOGIN_SUCCESS: "#16a34a",
        LOGIN_FAILED: "#dc2626",
        LOGOUT_SUCCESS: "#64748b",
        CREATE: "#0284c7",
        UPDATE: "#ea580c",
        DELETE: "#dc2626",
        DELETE_LOGICO: "#dc2626",
        DELETE_LOGICO_ERROR: "#dc2626",
        CONSULTA: "#8b5cf6",
        BUSQUEDA: "#f59e0b",
    };
    return map[accion] || "#64748b";
};

const actionLabel = (accion, tabla) => {
    const map = {
        CREATE: tabla?.includes("usuarios") ? "Creacion de usuario" : "Creacion de registro",
        UPDATE: "Edicion de datos",
        DELETE: "Eliminacion de registro",
        DELETE_LOGICO: "Desactivacion de usuario",
        DELETE_LOGICO_ERROR: "Error al desactivar usuario",
        LOGIN_SUCCESS: "Inicio de sesion",
        LOGIN_FAILED: "Error de inicio de sesion",
        LOGOUT_SUCCESS: "Cierre de sesion",
        CONSULTA: "Consulta de datos",
        BUSQUEDA: "Busqueda de datos",
    };
    return map[accion] || accion;
};

export default function AuditoriaPage() {
    const permissions = usePermissions();

    if (!permissions.canViewAuditoria) {
        return <div>Sin permisos</div>;
    }

    const [rows, setRows] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 50 });

    useEffect(() => {
        setLoading(true);
        getAuditoria(paginationModel.page + 1, paginationModel.pageSize)
            .then((data) => {
                const mapped = (data.registros || []).map((r) => ({
                    id: r.id,
                    fecha: r.fecha ? new Date(r.fecha).toLocaleString("es-AR") : "",
                    usuario: r.usuario,
                    accion: r.accion,
                    tabla: r.tabla || "-",
                    detalle: r.detalle || "-",
                    ip: r.ip || r.ip_address || "-",
                }));
                setRows(mapped);
                setTotal(data.total || 0);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [paginationModel]);

    const columns = [
        { field: "fecha", headerName: "Fecha", width: 170 },
        { field: "usuario", headerName: "Usuario", width: 120 },
        {
            field: "accion",
            headerName: "Accion",
            width: 220,
            sortable: false,
            renderCell: (params) => (
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Box
                        sx={{
                            width: 10,
                            height: 10,
                            borderRadius: "50%",
                            bgcolor: actionColor(params.value),
                            flexShrink: 0,
                        }}
                    />
                    {actionLabel(params.value, params.row.tabla)}
                </Box>
            ),
        },
        { field: "tabla", headerName: "Tabla", width: 120 },
        { field: "detalle", headerName: "Detalle", flex: 1, minWidth: 200 },
        { field: "ip", headerName: "IP", width: 140 },
    ];

    return (
        <Box sx={{ p: 3, overflow: "hidden", maxWidth: "100%" }}>
            <Typography variant="h5" gutterBottom>
                Auditoria
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Registro de actividad del sistema ({total} eventos)
            </Typography>

            <Box sx={{ height: 600, width: "100%", overflow: "hidden", maxWidth: "100%" }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    loading={loading}
                    rowCount={total}
                    paginationMode="server"
                    paginationModel={paginationModel}
                    onPaginationModelChange={setPaginationModel}
                    pageSizeOptions={[25, 50, 100]}
                    disableRowSelectionOnClick
                    disableExtendRowFullWidth
                    slotProps={{
                        basePagination: {
                            showFirstButton: true,
                            showLastButton: true,
                        },
                    }}
                    sx={{
                        maxWidth: "100%",
                        overflow: "hidden",
                        "& .MuiDataGrid-main": { overflow: "hidden" },
                        "& .MuiDataGrid-virtualScroller": { overflow: "auto" },
                        "& .MuiDataGrid-cell:focus": { outline: "none" },
                    }}
                />
            </Box>
        </Box>
    );
}
