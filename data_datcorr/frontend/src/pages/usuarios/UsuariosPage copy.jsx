import { DataGrid } from "@mui/x-data-grid";
import { useUsuariosGrid } from "../../hooks/useUsuariosGrid";

export default function UsuariosPage() {

    const {
        rows,
        loading,
        pagination,
        fetchData
    } = useUsuariosGrid();

    const columns = [
        { field: "id", headerName: "ID", width: 80 },
        { field: "usuario", headerName: "Usuario", flex: 1 },
        { field: "nombre", headerName: "Nombre", flex: 1 },
        { field: "apellido", headerName: "Apellido", flex: 1 },
        { field: "rol", headerName: "Rol", width: 150 },
        { field: "nivel", headerName: "Nivel", width: 120 }
    ];

    return (
        <div style={{ height: 600, width: "100%" }}>

            <h2>Usuarios ERP</h2>

            <DataGrid
                rows={rows}
                columns={columns}
                loading={loading}
                pagination
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
            />

        </div>
    );
}