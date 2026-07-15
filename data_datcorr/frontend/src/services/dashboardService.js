import api from "../api/axiosClient";

export const getDashboardStats = async () => {
    const res = await api.get("/dashboard/stats");
    return res.data;
};

export const getAuditoria = async (page = 1, limit = 50) => {
    const res = await api.get("/auditoria", { params: { page, limit } });
    return res.data;
};
