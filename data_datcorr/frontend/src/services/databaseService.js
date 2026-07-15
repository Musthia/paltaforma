import api from "../api/axiosClient";

export const listarBases = async () => {
    const res = await api.get("/databases/");
    return res.data?.bases || [];
};

export const consultarBase = async (base, params = {}) => {
    const res = await api.get(`/databases/${encodeURIComponent(base)}/data`, { params });
    return res.data;
};

export const buscarEnBase = async (base, q, params = {}) => {
    const res = await api.get(`/databases/${encodeURIComponent(base)}/search`, {
        params: { q, ...params }
    });
    return res.data;
};

export const actualizarRegistro = async (base, recordId, data, params = {}) => {
    const res = await api.patch(`/databases/${encodeURIComponent(base)}/records/${recordId}`, { data }, { params });
    return res.data;
};

export const eliminarRegistro = async (base, recordId, params = {}) => {
    const res = await api.delete(`/databases/${encodeURIComponent(base)}/records/${recordId}`, { params });
    return res.data;
};
