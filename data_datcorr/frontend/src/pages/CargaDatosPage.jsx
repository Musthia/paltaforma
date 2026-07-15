import { useState, useEffect, useCallback, useRef } from "react";
import {
    Box,
    Typography,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Paper,
    Alert,
    Snackbar,
    CircularProgress,
    Grid,
    Tabs,
    Tab,
    IconButton,
    Chip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { listarBases, actualizarRegistro, eliminarRegistro } from "../services/databaseService";
import api from "../api/axiosClient";

const STORAGE_KEY = "datcorr_carga_tabs";
const CAMPOS_EXCLUIDOS = new Set([
    "id_datcorr_database",
    "id_Datcorr_database",
    "registro",
]);
const CAMPOS_NO_EDITABLES = new Set(["id_datcorr_database", "id_Datcorr_database", "registro"]);

function loadTabs() {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveTabs(tabs) {
    try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(tabs));
    } catch { /* ignore */ }
}

export default function CargaDatosPage() {
    const [bases, setBases] = useState([]);
    const [tabs, setTabs] = useState(() => loadTabs());
    const [tabIndex, setTabIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

    const [editDialog, setEditDialog] = useState({ open: false, registro: null, idx: null });
    const [editForm, setEditForm] = useState({});
    const [deleteDialog, setDeleteDialog] = useState({ open: false, registro: null, idx: null });

    useEffect(() => {
        listarBases().then(setBases).catch(console.error);
    }, []);

    const actualizarTabs = useCallback((fn) => {
        setTabs((prev) => {
            const next = fn(prev);
            saveTabs(next);
            return next;
        });
    }, []);

    const abrirTab = useCallback(async (base) => {
        const existente = tabs.find((t) => t.base === base);
        if (existente) {
            setTabIndex(tabs.indexOf(existente));
            return;
        }

        setLoading(true);
        try {
            const res = await api.get(`/databases/${encodeURIComponent(base)}/columns`);
            const cols = (res.data?.columnas || []).filter(
                (c) => !CAMPOS_EXCLUIDOS.has(c.nombre.toLowerCase())
            );
            const initial = {};
            cols.forEach((c) => { initial[c.nombre] = ""; });

            const tab = {
                clave: `carga_${base}_${Date.now()}`,
                base,
                columnas: cols,
                formValues: initial,
                registrosCreados: [],
            };

            actualizarTabs((prev) => {
                const idx = prev.findIndex((t) => t.base === base);
                if (idx >= 0) {
                    setTabIndex(idx);
                    return prev;
                }
                setTabIndex(prev.length);
                return [...prev, tab];
            });
        } catch (err) {
            console.error("Error cargando columnas:", err);
        } finally {
            setLoading(false);
        }
    }, [tabs, actualizarTabs]);

    const cerrarTab = useCallback((idx) => {
        actualizarTabs((prev) => prev.filter((_, i) => i !== idx));
        setTabIndex((prev) => (prev >= idx && prev > 0 ? prev - 1 : prev));
    }, [actualizarTabs]);

    const handleChange = useCallback((e) => {
        const { name, value } = e.target;
        actualizarTabs((prev) =>
            prev.map((t, i) => {
                if (i !== tabIndex) return t;
                return { ...t, formValues: { ...t.formValues, [name]: value } };
            })
        );
    }, [tabIndex, actualizarTabs]);

    const tabActual = tabs[tabIndex] || null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!tabActual) return;
        setSaving(true);
        try {
            const data = {};
            tabActual.columnas.forEach((c) => {
                data[c.nombre] = tabActual.formValues[c.nombre] || "";
            });
            const res = await api.post(`/databases/${encodeURIComponent(tabActual.base)}/records`, { data });
            const registroId = res.data?.registro_id;
            const resumen = { ...tabActual.formValues };
            const todasLasCols = tabActual.columnas.map((c) => c.nombre);
            setSnackbar({ open: true, message: "Registro creado correctamente", severity: "success" });
            const initial = {};
            tabActual.columnas.forEach((c) => { initial[c.nombre] = ""; });
            actualizarTabs((prev) =>
                prev.map((t, i) => {
                    if (i !== tabIndex) return t;
                    return {
                        ...t,
                        formValues: initial,
                        registrosCreados: [
                            { id: registroId, timestamp: new Date().toLocaleString("es-AR"), datos: resumen, todasLasCols },
                            ...t.registrosCreados,
                        ],
                    };
                })
            );
        } catch (err) {
            console.error("Error creando registro:", err);
            setSnackbar({ open: true, message: "Error al crear registro", severity: "error" });
        } finally {
            setSaving(false);
        }
    };

    const abrirEditar = (registro, idx) => {
        setEditForm({ ...registro.datos });
        setEditDialog({ open: true, registro, idx });
    };

    const cerrarEditar = () => {
        setEditDialog({ open: false, registro: null, idx: null });
        setEditForm({});
    };

    const guardarEdicion = async () => {
        const { registro, idx } = editDialog;
        if (!tabActual || !registro) return;
        try {
            const data = {};
            tabActual.columnas.forEach((c) => {
                if (!CAMPOS_NO_EDITABLES.has(c.nombre.toLowerCase())) {
                    data[c.nombre] = editForm[c.nombre] || "";
                }
            });
            await actualizarRegistro(tabActual.base, registro.id, data);
            setSnackbar({ open: true, message: "Registro actualizado correctamente", severity: "success" });
            actualizarTabs((prev) =>
                prev.map((t, i) => {
                    if (i !== tabIndex) return t;
                    const updated = [...t.registrosCreados];
                    if (updated[idx]) {
                        updated[idx] = { ...updated[idx], datos: { ...updated[idx].datos, ...data } };
                    }
                    return { ...t, registrosCreados: updated };
                })
            );
            cerrarEditar();
        } catch (err) {
            console.error("Error actualizando registro:", err);
            setSnackbar({ open: true, message: "Error al actualizar registro", severity: "error" });
        }
    };

    const abrirConfirmarEliminar = (registro, idx) => {
        setDeleteDialog({ open: true, registro, idx });
    };

    const cerrarConfirmarEliminar = () => {
        setDeleteDialog({ open: false, registro: null, idx: null });
    };

    const confirmarEliminar = async () => {
        const { registro, idx } = deleteDialog;
        if (!tabActual || !registro) return;
        try {
            await eliminarRegistro(tabActual.base, registro.id);
            setSnackbar({ open: true, message: "Registro eliminado correctamente", severity: "success" });
            actualizarTabs((prev) =>
                prev.map((t, i) => {
                    if (i !== tabIndex) return t;
                    return {
                        ...t,
                        registrosCreados: t.registrosCreados.filter((_, ri) => ri !== idx),
                    };
                })
            );
            cerrarConfirmarEliminar();
        } catch (err) {
            console.error("Error eliminando registro:", err);
            setSnackbar({ open: true, message: "Error al eliminar registro", severity: "error" });
        }
    };

    const colEditables = tabActual?.columnas.filter(
        (c) => !CAMPOS_NO_EDITABLES.has(c.nombre.toLowerCase())
    ) || [];

    return (
        <Box sx={{ p: 3, overflow: "hidden", maxWidth: "100%" }}>
            <Typography variant="h5" gutterBottom>
                Carga de Datos
            </Typography>

            <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2, flexWrap: "wrap" }}>
                <FormControl sx={{ minWidth: 250 }} size="small">
                    <InputLabel>Base de datos</InputLabel>
                    <Select
                        value=""
                        label="Base de datos"
                        onChange={(e) => abrirTab(e.target.value)}
                    >
                        {bases.map((b) => (
                            <MenuItem key={`${b.nombre}_${b.tipo}`} value={b.nombre}>
                                {b.nombre}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Box>

            {tabs.length > 0 && (
                <Tabs
                    value={Math.min(tabIndex, tabs.length - 1)}
                    onChange={(_, v) => setTabIndex(v)}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{ mb: 2 }}
                >
                    {tabs.map((tab, i) => (
                        <Tab
                            key={tab.clave}
                            label={
                                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                                    <Chip
                                        label="CARGA"
                                        size="small"
                                        color="success"
                                        sx={{ height: 20, fontSize: 11 }}
                                    />
                                    <span>{tab.base}</span>
                                    <IconButton
                                        size="small"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            cerrarTab(i);
                                        }}
                                        sx={{ ml: 0.5 }}
                                    >
                                        <CloseIcon fontSize="small" />
                                    </IconButton>
                                </Box>
                            }
                        />
                    ))}
                </Tabs>
            )}

            {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {!loading && tabActual && (
                <Paper sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        Nuevo registro en: <strong>{tabActual.base}</strong>
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Complete los campos para agregar un nuevo registro
                    </Typography>

                    <Box component="form" onSubmit={handleSubmit}>
                        <Grid container spacing={2} sx={{ mb: 3 }}>
                            {tabActual.columnas.map((col) => (
                                <Grid item xs={12} sm={6} md={4} key={col.nombre}>
                                    <TextField
                                        fullWidth
                                        size="small"
                                        label={col.nombre}
                                        name={col.nombre}
                                        value={tabActual.formValues[col.nombre] || ""}
                                        onChange={handleChange}
                                    />
                                </Grid>
                            ))}
                        </Grid>

                        <Button
                            type="submit"
                            variant="contained"
                            disabled={saving}
                            startIcon={saving ? <CircularProgress size={20} /> : null}
                        >
                            {saving ? "Guardando..." : "Guardar registro"}
                        </Button>
                    </Box>
                </Paper>
            )}

            {tabActual && tabActual.registrosCreados?.length > 0 && (
                <Paper sx={{ p: 2, mt: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                        <Typography variant="subtitle2">
                            Registros creados en esta sesion — {tabActual.base}
                        </Typography>
                    </Box>
                    <TableContainer sx={{ maxHeight: 400, overflow: "auto" }}>
                        <Table size="small" stickyHeader>
                            <TableHead>
                                <TableRow>
                                    <TableCell sx={{ fontWeight: 600, fontSize: 12, whiteSpace: "nowrap" }}>#</TableCell>
                                    <TableCell sx={{ fontWeight: 600, fontSize: 12, whiteSpace: "nowrap" }}>Hora</TableCell>
                                    <TableCell sx={{ fontWeight: 600, fontSize: 12, whiteSpace: "nowrap" }}>Acciones</TableCell>
                                    {tabActual.registrosCreados[0]?.todasLasCols?.map((col) => (
                                        <TableCell key={col} sx={{ fontWeight: 600, fontSize: 12, whiteSpace: "nowrap" }}>
                                            {col}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {tabActual.registrosCreados.map((r, i) => (
                                    <TableRow key={r.id || i}>
                                        <TableCell sx={{ fontSize: 12 }}>{r.id || "-"}</TableCell>
                                        <TableCell sx={{ fontSize: 12, whiteSpace: "nowrap" }}>{r.timestamp}</TableCell>
                                        <TableCell>
                                            <IconButton size="small" onClick={() => abrirEditar(r, i)} title="Editar">
                                                <EditIcon fontSize="small" />
                                            </IconButton>
                                            <IconButton size="small" onClick={() => abrirConfirmarEliminar(r, i)} title="Eliminar">
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </TableCell>
                                        {r.todasLasCols.map((col) => (
                                            <TableCell key={col} sx={{ fontSize: 12, maxWidth: 250, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                                {r.datos[col] || ""}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            )}

            {!loading && !tabActual && tabs.length === 0 && (
                <Typography color="text.secondary">
                    Seleccione una base de datos del menu de arriba para comenzar
                </Typography>
            )}

            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
            >
                <Alert severity={snackbar.severity} variant="filled">
                    {snackbar.message}
                </Alert>
            </Snackbar>

            {/* Edit Dialog */}
            <Dialog open={editDialog.open} onClose={cerrarEditar} maxWidth="md" fullWidth>
                <DialogTitle>
                    Editar Registro #{editDialog.registro?.id}
                    <IconButton onClick={cerrarEditar} sx={{ position: "absolute", right: 8, top: 8 }}>
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 0.5 }}>
                        {colEditables.map((col) => (
                            <Grid item xs={12} sm={6} key={col.nombre}>
                                <TextField
                                    fullWidth
                                    size="small"
                                    label={col.nombre}
                                    name={col.nombre}
                                    value={editForm[col.nombre] || ""}
                                    onChange={(e) =>
                                        setEditForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
                                    }
                                />
                            </Grid>
                        ))}
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={cerrarEditar}>Cancelar</Button>
                    <Button variant="contained" onClick={guardarEdicion}>Guardar cambios</Button>
                </DialogActions>
            </Dialog>

            {/* Delete Confirmation */}
            <Dialog open={deleteDialog.open} onClose={cerrarConfirmarEliminar} maxWidth="xs">
                <DialogTitle>Confirmar eliminacion</DialogTitle>
                <DialogContent>
                    <Typography>
                        ¿Eliminar el registro #{deleteDialog.registro?.id} de <strong>{tabActual?.base}</strong>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Esta accion no se puede deshacer. Se eliminara de la base de datos y de la lista.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={cerrarConfirmarEliminar}>Cancelar</Button>
                    <Button variant="contained" color="error" onClick={confirmarEliminar}>Eliminar</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
