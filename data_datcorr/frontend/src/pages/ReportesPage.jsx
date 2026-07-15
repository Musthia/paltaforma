import { useState, useEffect, useCallback } from "react";
import {
    Box, Typography, Button, Select, MenuItem, FormControl, InputLabel,
    TextField, Grid, Card, CardContent, CircularProgress, Snackbar, Alert,
    FormGroup,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { getConsultas, ejecutarConsulta, exportarConsulta, getKpis } from "../services/reportesService";
import { usePermissions } from "../auth/usePermissions";

export default function ReportesPage() {
    const perms = usePermissions();

    const [consultas, setConsultas] = useState([]);
    const [consultaId, setConsultaId] = useState("");
    const [consultaMeta, setConsultaMeta] = useState(null);
    const [filtros, setFiltros] = useState({});
    const [rows, setRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [generated, setGenerated] = useState(false);
    const [kpis, setKpis] = useState(null);
    const [snack, setSnack] = useState({ open: false, msg: "", severity: "info" });

    useEffect(() => {
        getConsultas()
            .then(setConsultas)
            .catch(() => setSnack({ open: true, msg: "Error al cargar consultas", severity: "error" }));
        getKpis()
            .then(setKpis)
            .catch(() => {});
    }, []);

    const moduloActual = consultas.find((c) => c.id === consultaId);

    const handleSelectChange = (id) => {
        setConsultaId(id);
        setConsultaMeta(consultas.find((c) => c.id === id) || null);
        setRows([]);
        setColumns([]);
        setGenerated(false);
        setFiltros({});
    };

    const handleFiltroChange = (key, value) => {
        setFiltros((prev) => ({ ...prev, [key]: value }));
    };

    const handleGenerate = useCallback(async () => {
        if (!consultaId) return;
        setLoading(true);
        try {
            const result = await ejecutarConsulta(consultaId, filtros);
            setConsultaMeta({ nombre: result.nombre, descripcion: result.descripcion });
            const cols = (result.columnas || []).map((c, i) => ({
                field: c,
                headerName: c.charAt(0).toUpperCase() + c.slice(1).replace(/_/g, " "),
                flex: 1,
                minWidth: 120,
            }));
            setColumns(cols);
            const dataRows = (result.datos || []).map((r, i) => ({ id: i, ...r }));
            setRows(dataRows);
            setGenerated(true);
        } catch (err) {
            setSnack({ open: true, msg: "Error al generar reporte", severity: "error" });
        } finally {
            setLoading(false);
        }
    }, [consultaId, filtros]);

    const handleExport = useCallback(async (formato) => {
        if (!consultaId || rows.length === 0) return;
        try {
            const res = await exportarConsulta(consultaId, formato, filtros);
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", `reporte_${consultaId}.${formato}`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            setSnack({ open: true, msg: `Exportado como ${formato.toUpperCase()}`, severity: "success" });
        } catch (err) {
            setSnack({ open: true, msg: "Error al exportar", severity: "error" });
        }
    }, [consultaId, filtros, rows]);

    const renderFiltro = (f) => {
        if (f.tipo === "date") {
            return (
                <TextField
                    key={f.key}
                    label={f.label}
                    type="date"
                    size="small"
                    InputLabelProps={{ shrink: true }}
                    value={filtros[f.key] || ""}
                    onChange={(e) => handleFiltroChange(f.key, e.target.value)}
                    sx={{ minWidth: 180 }}
                />
            );
        }
        if (f.tipo === "select") {
            return (
                <FormControl key={f.key} size="small" sx={{ minWidth: 180 }}>
                    <InputLabel>{f.label}</InputLabel>
                    <Select
                        value={filtros[f.key] || f.default || ""}
                        label={f.label}
                        onChange={(e) => handleFiltroChange(f.key, e.target.value)}
                    >
                        {(f.opciones || []).map((o) => (
                            <MenuItem key={o.valor} value={o.valor}>{o.texto}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            );
        }
        if (f.tipo === "text") {
            return (
                <TextField
                    key={f.key}
                    label={f.label}
                    size="small"
                    value={filtros[f.key] || ""}
                    onChange={(e) => handleFiltroChange(f.key, e.target.value)}
                    sx={{ minWidth: 180 }}
                />
            );
        }
        return null;
    };

    return (
        <Box sx={{ p: 3, maxWidth: "100%" }}>
            <Typography variant="h5" gutterBottom>Reportes</Typography>

            {/* KPIs */}
            {kpis && (
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    {[
                        { label: "Total Registros", value: kpis.total_registros?.toLocaleString() },
                        { label: "Usuarios Activos", value: kpis.usuarios_activos },
                        { label: "Total Usuarios", value: kpis.total_usuarios },
                        { label: "Alertas Pendientes", value: kpis.alertas_pendientes, color: kpis.alertas_pendientes > 0 ? "error.main" : undefined },
                    ].map((kpi) => (
                        <Grid item xs={6} sm={3} key={kpi.label}>
                            <Card>
                                <CardContent sx={{ textAlign: "center", py: 2 }}>
                                    <Typography variant="h4" sx={{ color: kpi.color || "primary.main", fontWeight: 700 }}>
                                        {kpi.value}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {kpi.label}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Selector de reporte */}
            <FormControl size="small" sx={{ minWidth: 280, mb: 2 }}>
                <InputLabel>Seleccionar Reporte</InputLabel>
                <Select
                    value={consultaId}
                    label="Seleccionar Reporte"
                    onChange={(e) => handleSelectChange(e.target.value)}
                >
                    {consultas.map((c) => (
                        <MenuItem key={c.id} value={c.id}>{c.nombre} — {c.descripcion}</MenuItem>
                    ))}
                </Select>
            </FormControl>

            {moduloActual && moduloActual.filtros && moduloActual.filtros.length > 0 && (
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center", mb: 2 }}>
                    {moduloActual.filtros.map(renderFiltro)}
                </Box>
            )}

            {/* Botones */}
            <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                <Button variant="contained" onClick={handleGenerate} disabled={!consultaId || loading}>
                    {loading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                    Generar
                </Button>
                {generated && rows.length > 0 && (
                    <>
                        <Button variant="outlined" onClick={() => handleExport("csv")}>CSV</Button>
                        <Button variant="outlined" onClick={() => handleExport("xlsx")}>XLSX</Button>
                        <Button variant="outlined" onClick={() => handleExport("pdf")}>PDF</Button>
                    </>
                )}
            </Box>

            {/* Preview */}
            {generated && (
                <Box sx={{ height: "calc(100vh - 350px)", width: "100%", minHeight: 400 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {consultaMeta?.nombre} — {rows.length} registros
                    </Typography>
                    <DataGrid
                        rows={rows}
                        columns={columns}
                        disableRowSelectionOnClick
                        disableExtendRowFullWidth
                        pageSizeOptions={[25, 50, 100]}
                        initialState={{ pagination: { paginationModel: { pageSize: 50 } } }}
                        slotProps={{
                            basePagination: { showFirstButton: true, showLastButton: true },
                        }}
                        sx={{
                            "& .MuiDataGrid-virtualScroller": { overflow: "auto" },
                            "& .MuiDataGrid-cell:focus": { outline: "none" },
                        }}
                    />
                </Box>
            )}

            <Snackbar
                open={snack.open}
                autoHideDuration={4000}
                onClose={() => setSnack((s) => ({ ...s, open: false }))}
            >
                <Alert severity={snack.severity} onClose={() => setSnack((s) => ({ ...s, open: false }))}>
                    {snack.msg}
                </Alert>
            </Snackbar>
        </Box>
    );
}
