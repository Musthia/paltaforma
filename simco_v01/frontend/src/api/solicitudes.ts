import { api } from "./client";
import type { Solicitud } from "../types/solicitud";

export const getSolicitudes = async (): Promise<Solicitud[]> => {
    const res = await api.get("/solicitudes/");
    return res.data;
};

export const createSolicitud = async (formData: FormData) => {
    const res = await api.post("/solicitudes/", formData);
    return res.data;
};

export const getSolicitudesByEstado = async (estado: string): Promise<Solicitud[]> => {
    const res = await api.get(`/solicitudes/estado/${estado}`);
    return res.data;
};

export const destacarSolicitud = async (id: number): Promise<Solicitud> => {
    const res = await api.patch(`/solicitudes/${id}/destacar`);
    return res.data;
};

export const verificarSolicitud = async (id: number): Promise<Solicitud> => {
    const res = await api.patch(`/solicitudes/${id}/verificando`);
    return res.data;
};

export const getArchivoSolicitudUrl = (id: number): string => {
    return `${window.location.origin}/solicitudes/${id}/archivo`;
};

export const getArchivoSolicitudDownloadUrl = (id: number): string => {
    return `${window.location.origin}/solicitudes/${id}/archivo/download`;
};