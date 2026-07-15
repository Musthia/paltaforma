import { api } from "./client";

export interface NuevasNotificacionesResponse {
    count: number;
    max_id: number;
    items: any[];
}

export const getNuevasNotificaciones = async (tipo: "pendiente" | "respondida", desdeId: number): Promise<NuevasNotificacionesResponse> => {
    const res = await api.get("/notificaciones/nuevas", { params: { tipo, desde_id: desdeId } });
    return res.data;
};
