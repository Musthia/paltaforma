import api from "../api/axiosClient";

export const getConsultas = async () => {
    const res = await api.get("/reportes/consultas");
    return res.data.consultas;
};

export const ejecutarConsulta = async (consultaId, filtros = {}) => {
    const res = await api.get(`/reportes/ejecutar/${consultaId}`, { params: filtros });
    return res.data;
};

export const exportarConsulta = async (consultaId, formato, filtros = {}) => {
    const res = await api.get(`/reportes/exportar/${consultaId}`, {
        params: { formato, ...filtros },
        responseType: "blob",
    });
    return res;
};

export const getKpis = async () => {
    const res = await api.get("/reportes/kpis");
    return res.data;
};
