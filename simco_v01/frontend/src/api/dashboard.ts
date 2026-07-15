import { api } from "./client";

export const getActividadHoy = async () => {
    const res = await api.get("/dashboard/hoy");
    return res.data;
};

