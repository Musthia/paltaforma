import { DataGrid } from "@mui/x-data-grid";
import { useUsuariosGrid } from "../../hooks/useUsuariosGrid";

import UsuarioModal from "../../components/modals/UsuarioModal";
import { useState } from "react";

import {
    Button,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Typography,
    Box,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { usePermissions } from "../../auth/usePermissions";
import { useAuthStore } from "../../auth/authStore";
import { eliminarUsuario } from "../../services/usuariosService";



export default function UsuariosPage() {

    const user = useAuthStore(s => s.user);
    const permissions = usePermissions();

    const [openModal, setOpenModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [deleteDialog, setDeleteDialog] = useState({ open: false, user: null });

    const {
        rows,
        loading,
        pagination,
        fetchData
    } = useUsuariosGrid();

    const columns = [
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
                            setSelectedUser(params.row);
                            setOpenModal(true);
                        }}
                        title="Editar"
                    >
                        <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                        size="small"
                        onClick={(e) => {
                            e.stopPropagation();
                            setDeleteDialog({ open: true, user: params.row });
                        }}
                        title="Eliminar"
                    >
                        <DeleteIcon fontSize="small" />
                    </IconButton>
                </Box>
            ),
        },
        { field: "id", headerName: "ID", width: 80 },
        { field: "usuario", headerName: "Usuario", flex: 1 },
        { field: "nombre", headerName: "Nombre", flex: 1 },
        { field: "apellido", headerName: "Apellido", flex: 1 },
        { field: "email", headerName: "Email", flex: 1 },

        ...(permissions.showRolColumn
            ? [{ field: "rol", headerName: "Rol", width: 150 }]
            : []),

        ...(permissions.showNivelColumn
            ? [{ field: "nivel_seguridad", headerName: "Nivel", width: 120 }]
            : [])
    ];

    const handleGuardar = async () => {
        await fetchData(pagination.page, pagination.pageSize);
    };

    const handleEliminar = async () => {
        try {
            await eliminarUsuario(deleteDialog.user.id);
            setDeleteDialog({ open: false, user: null });
            await fetchData(pagination.page, pagination.pageSize);
        } catch (err) {
            console.error("Error eliminando usuario:", err);
        }
    };

    if (!permissions.canViewUsers) {
        return <div>Sin permisos</div>;
    }

    return (
        <div style={{ padding: 20 }}>

            <h2>ERP Usuarios</h2>

            {permissions.canCreateUser && (
                <Button
                    variant="contained"
                    onClick={() => {
                        setSelectedUser(null);
                        setOpenModal(true);
                    }}
                >
                    Nuevo Usuario
                </Button>
            )}

            <DataGrid
                rows={rows}
                columns={columns}
                loading={loading}
                pageSizeOptions={[10, 20, 50]}
                paginationModel={{
                    page: pagination.page,
                    pageSize: pagination.pageSize
                }}
                rowCount={pagination.total}
                paginationMode="server"
                onPaginationModelChange={(model) => {
                    fetchData(model.page, model.pageSize);
                }}
                disableRowSelectionOnClick
                slotProps={{
                    basePagination: {
                        showFirstButton: true,
                        showLastButton: true,
                    },
                }}
                sx={{
                    "& .MuiDataGrid-cell:focus": { outline: "none" },
                    mt: 1,
                }}
            />

            <UsuarioModal
                open={openModal}
                onClose={() => {
                    setOpenModal(false);
                    setSelectedUser(null);
                }}
                usuario={selectedUser}
                onSave={handleGuardar}
            />

            <Dialog
                open={deleteDialog.open}
                onClose={() => setDeleteDialog({ open: false, user: null })}
                maxWidth="xs"
            >
                <DialogTitle>Confirmar eliminacion</DialogTitle>
                <DialogContent>
                    <Typography>
                        ¿Eliminar al usuario <strong>{deleteDialog.user?.usuario}</strong>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Esta accion no se puede deshacer.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialog({ open: false, user: null })}>
                        Cancelar
                    </Button>
                    <Button variant="contained" color="error" onClick={handleEliminar}>
                        Eliminar
                    </Button>
                </DialogActions>
            </Dialog>

        </div>
    );
}