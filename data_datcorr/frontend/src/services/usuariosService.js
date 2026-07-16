import api from "../api/axiosClient";

export const listarUsuarios = async (params = {}) => {
    const res = await api.get("/users/", { params });
    const data = res.data;

    const usuarios = (data?.users || []).map(u => ({
        id: u.id,
        usuario: u.username,
        nombre: u.full_name || "",
        apellido: "",
        email: u.email || "",
        rol: u.role,
        nivel_seguridad: u.nivel_seguridad,
        is_active: u.is_active,
        is_superuser: u.is_superuser,
    }));

    return {
        usuarios,
        total: data?.total || 0,
        page: data?.page || 1,
        pages: data?.pages || 1,
    };
};

export const crearUsuario = async (data) => {
    const body = {
        username: data.usuario,
        password: data.password,
        full_name: [data.nombre, data.apellido].filter(Boolean).join(" "),
        email: data.email || null,
        role: data.rol,
        nivel_seguridad: data.nivel_seguridad || 1,
    };
    return api.post("/users/", body);
};

export const actualizarUsuario = async (id, data) => {
    const body = {};
    if (data.nombre || data.apellido)
        body.full_name = [data.nombre, data.apellido].filter(Boolean).join(" ");
    if (data.email !== undefined) body.email = data.email || null;
    if (data.rol) body.role = data.rol;
    if (data.nivel_seguridad !== undefined) body.nivel_seguridad = Number(data.nivel_seguridad);
    if (data.password) body.password = data.password;
    return api.put(`/users/${id}`, body);
};

export const eliminarUsuario = async (id) => {
    return api.delete(`/users/${id}`);
};
