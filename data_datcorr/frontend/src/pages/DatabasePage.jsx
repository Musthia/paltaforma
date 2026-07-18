import { useState, useEffect, useCallback, useRef } from "react";
import {
    Box,
    Typography,
    TextField,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Tabs,
    Tab,
    IconButton,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import SearchIcon from "@mui/icons-material/Search";
import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { listarBases, consultarBase, buscarEnBase, eliminarRegistro } from "../services/databaseService";
import EditRecordModal from "../components/modals/EditRecordModal";
import { useTabs } from "../context/TabContext";

const COLORES_COLUMNAS = {
    n_lote: "#b400ff",
    "hh.cc": "#c819c8",
    expediente: "#c819c8",
    documento: "#00e696",
    denominacion: "#0014ff",
};

export default function DatabasePage() {
    const [bases, setBases] = useState([]);
    const [baseActual, setBaseActual] = useState("");
    const [criterio, setCriterio] = useState("");
    const [loading, setLoading] = useState(false);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [editData, setEditData] = useState(null);
    const [deleteDialog, setDeleteDialog] = useState({ open: false, base: "", idRegistro: null, claveTab: "", row: null });
    const { tabs, tabIndex, setTabIndex, agregarTab, cerrarTab, setTabs, actualizarFila } = useTabs();
    const tabsRef = useRef(tabs);

    useEffect(() => {
        tabsRef.current = tabs;
    }, [tabs]);

    useEffect(() => {
        listarBases().then(setBases).catch(console.error);
    }, []);

    const construirTab = useCallback((base, modo, columnas, registros, total, page, pageSize) => {
        const cols = columnas
            .filter((col) => !col.toLowerCase().startsWith("id_datcorr"))
            .map((col) => ({
                field: col,
                headerName: col,
                flex: 1,
                minWidth: 120,
                cellClassName: () => {
                    const color = COLORES_COLUMNAS[col.toLowerCase()];
                    if (!color) return "";
                    return `highlight-${col.toLowerCase().replace(/\s+/g, "-")}`;
                },
            }));

        const rows = registros.map((row, idx) => {
            const rowData = { id: idx };
            columnas.forEach((col, ci) => {
                rowData[col] = row[ci] != null ? String(row[ci]) : "";
            });
            rowData._raw = row;
            rowData._idValue = row[0];
            return rowData;
        });

        return { base, modo, columns: cols, rows, total, columnas, page, pageSize };
    }, []);

    const fetchPage = useCallback(async (tab, newPage, newPageSize) => {
        try {
            const params = { page: newPage + 1, limit: newPageSize };
            let data;
            if (tab.modo === "BUSQUEDA") {
                data = await buscarEnBase(tab.base, tab._criterio, params);
            } else {
                data = await consultarBase(tab.base, params);
            }
            const rebuilt = construirTab(tab.base, tab.modo, data.columnas, data.registros, data.total, newPage, newPageSize);
            rebuilt._criterio = tab._criterio;
            rebuilt.clave = tab.clave;
            return rebuilt;
        } catch (err) {
            console.error("Error fetching page:", err);
            return tab;
        }
    }, [construirTab]);

    const handleTabPagination = useCallback(async (newModel) => {
        const tab = tabs[tabIndex];
        if (!tab) return;
        const updated = await fetchPage(tab, newModel.page, newModel.pageSize);
        setTabs((prev) => prev.map((t, i) => (i === tabIndex ? updated : t)));
    }, [tabs, tabIndex, fetchPage, setTabs]);

    const encontrarOCrearTab = async (base, modo, criterio) => {
        setLoading(true);
        try {
            const params = { page: 1, limit: 50 };
            let data;
            if (modo === "BUSQUEDA") {
                data = await buscarEnBase(base, criterio, params);
            } else {
                data = await consultarBase(base, params);
            }
            const tab = construirTab(base, modo, data.columnas, data.registros, data.total, 0, 50);
            if (modo === "BUSQUEDA") tab._criterio = criterio;
            const current = tabsRef.current;
            const idx = current.findIndex((t) =>
                t.base === base && t.modo === modo && (modo !== "BUSQUEDA" || t._criterio === criterio)
            );
            if (idx >= 0) {
                setTabs((prev) => prev.map((t, i) => (i === idx ? { ...tab, clave: t.clave } : t)));
                setTabIndex(idx);
            } else {
                agregarTab(tab);
                setTabIndex(current.length);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleConsultar = async () => {
        if (!baseActual) return;
        await encontrarOCrearTab(baseActual, "CONSULTA");
    };

    const handleBuscar = async () => {
        if (!baseActual || !criterio.trim()) return;
        await encontrarOCrearTab(baseActual, "BUSQUEDA", criterio.trim());
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") handleBuscar();
    };

    const handleEditClick = (row) => {
        const tab = tabs[tabIndex];
        if (!tab) return;
        const valores = tab.columnas.map((col) => row[col]);
        setEditData({
            base: tab.base,
            idRegistro: row._idValue,
            columnas: tab.columnas,
            valores,
            claveTab: tab.clave,
        });
        setEditModalOpen(true);
    };

    const handleDeleteClick = (row) => {
        const tab = tabs[tabIndex];
        if (!tab) return;
        setDeleteDialog({
            open: true,
            base: tab.base,
            idRegistro: row._idValue,
            claveTab: tab.clave,
            row,
        });
    };

    const handleDeleteConfirm = async () => {
        const { base, idRegistro, claveTab } = deleteDialog;
        try {
            await eliminarRegistro(base, idRegistro);
            setDeleteDialog({ open: false, base: "", idRegistro: null, claveTab: "", row: null });
            const tab = tabs.find((t) => t.clave === claveTab);
            if (tab) {
                const updated = await fetchPage(tab, tab.page, tab.pageSize);
                setTabs((prev) =>
                    prev.map((t) => (t.clave === claveTab ? { ...updated, clave: claveTab } : t))
                );
            }
        } catch (err) {
            console.error("Error eliminando registro:", err);
        }
    };

    const handleDoubleClick = (params) => {
        handleEditClick(params.row);
    };

    const handleEditSaved = (datos) => {
        if (editData && datos) {
            actualizarFila(editData.claveTab, editData.idRegistro, datos);
        }
        setEditModalOpen(false);
        setEditData(null);
    };

    if (!bases.length) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography variant="h5">Consultar Bases</Typography>
                <Typography color="text.secondary">Cargando bases disponibles...</Typography>
            </Box>
        );
    }

    const tabActual = tabs[Math.min(tabIndex, tabs.length - 1)];

    return (
        <Box sx={{ p: 3, overflow: "hidden", maxWidth: "100%" }}>
            <Typography variant="h5" gutterBottom>
                Consultar Bases de Datos
            </Typography>

            <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2, flexWrap: "wrap" }}>
                <FormControl sx={{ minWidth: 250 }} size="small">
                    <InputLabel>Base de datos</InputLabel>
                    <Select
                        value={baseActual}
                        label="Base de datos"
                        onChange={(e) => setBaseActual(e.target.value)}
                    >
                        {bases.map((b) => (
                            <MenuItem key={`${b.nombre}_${b.tipo}`} value={b.nombre}>
                                {b.nombre}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <TextField
                    size="small"
                    placeholder="Buscar..."
                    value={criterio}
                    onChange={(e) => setCriterio(e.target.value)}
                    onKeyDown={handleKeyDown}
                    sx={{ minWidth: 300 }}
                />

                <Button variant="contained" onClick={handleBuscar} startIcon={<SearchIcon />}>
                    Buscar
                </Button>

                <Button variant="outlined" onClick={handleConsultar}>
                    Ver todo
                </Button>
            </Box>

            {tabs.length > 0 && (
                <>
                    <Tabs
                        value={Math.min(tabIndex, tabs.length - 1)}
                        onChange={(_, v) => setTabIndex(v)}
                        variant="scrollable"
                        scrollButtons="auto"
                    >
                        {tabs.map((tab, i) => (
                            <Tab
                                key={tab.clave}
                                label={
                                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                                        <Chip
                                            label={tab.modo}
                                            size="small"
                                            color={tab.modo === "BUSQUEDA" ? "warning" : "info"}
                                            sx={{ height: 20, fontSize: 11 }}
                                        />
                                        <span>{tab.base}</span>
                                        <span style={{ fontSize: 12, opacity: 0.7 }}>
                                            ({tab.total})
                                        </span>
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

                    <Box sx={{ height: 600, mt: 1, width: "100%", overflow: "hidden", maxWidth: "100%" }}>
                        <DataGrid
                            key={tabActual?.clave}
                            rows={tabActual?.rows || []}
                            columns={
                                tabActual
                                    ? [
                                          {
                                              field: "acciones",
                                              headerName: "",
                                              width: 80,
                                              sortable: false,
                                              renderCell: (params) => (
                                                  <Box>
                                                      <IconButton
                                                          size="small"
                                                          onClick={(e) => {
                                                              e.stopPropagation();
                                                              handleEditClick(params.row);
                                                          }}
                                                          title="Editar"
                                                      >
                                                          <EditIcon fontSize="small" />
                                                      </IconButton>
                                                      <IconButton
                                                          size="small"
                                                          onClick={(e) => {
                                                              e.stopPropagation();
                                                              handleDeleteClick(params.row);
                                                          }}
                                                          title="Eliminar"
                                                      >
                                                          <DeleteIcon fontSize="small" />
                                                      </IconButton>
                                                  </Box>
                                              ),
                                          },
                                          ...tabActual.columns,
                                      ]
                                    : []
                            }
                            loading={loading}
                            rowCount={tabActual?.total || 0}
                            paginationMode="server"
                            paginationModel={{ page: tabActual?.page ?? 0, pageSize: tabActual?.pageSize ?? 50 }}
                            onPaginationModelChange={handleTabPagination}
                            pageSizeOptions={[25, 50, 100]}
                            onRowDoubleClick={handleDoubleClick}
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
                </>
            )}

            {tabs.length === 0 && (
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        height: 300,
                        color: "text.secondary",
                    }}
                >
                    Seleccione una base y realice una búsqueda o consulta
                </Box>
            )}

            {editModalOpen && editData && (
                <EditRecordModal
                    open={editModalOpen}
                    onClose={() => {
                        setEditModalOpen(false);
                        setEditData(null);
                    }}
                    onSaved={handleEditSaved}
                    base={editData.base}
                    idRegistro={editData.idRegistro}
                    columnas={editData.columnas}
                    valores={editData.valores}
                />
            )}

            <Dialog
                open={deleteDialog.open}
                onClose={() => setDeleteDialog({ open: false, base: "", idRegistro: null, claveTab: "", row: null })}
                maxWidth="xs"
            >
                <DialogTitle>Confirmar eliminacion</DialogTitle>
                <DialogContent>
                    <Typography>
                        ¿Eliminar el registro <strong>#{deleteDialog.idRegistro}</strong>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Esta accion eliminara el registro de la base <strong>{deleteDialog.base}</strong> y quedara registrado en la auditoria.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={() =>
                            setDeleteDialog({ open: false, base: "", idRegistro: null, claveTab: "", row: null })
                        }
                    >
                        Cancelar
                    </Button>
                    <Button variant="contained" color="error" onClick={handleDeleteConfirm}>
                        Eliminar
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
