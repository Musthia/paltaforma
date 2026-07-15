import api from "../api/axiosClient";


// ===================================
// ERP USERS SERVICE (NORMALIZADO)
// ===================================

export const listarUsuarios = async (params = {}) => {
    const res = await api.get("/usuarios", { params });

    const data = res.data;

    return {
        usuarios: data?.usuarios || [],
        total: data?.total || 0,
        page: data?.page || 1,
        pages: data?.pages || 1
    };
};

export const crearUsuario = async (data) => {
    return api.post("/usuarios", data);
};

export const actualizarUsuario = async (id, data) => {
    return api.patch(`/usuarios/${id}`, data);
};

export const eliminarUsuario = async (id) => {
    return api.delete(`/usuarios/${id}`);
};
