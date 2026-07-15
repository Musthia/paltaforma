import { api } from "./client";
import type { Respuesta } from "../types/respuesta";

export const getRespuestas = async (): Promise<Respuesta[]> => {
    const res = await api.get("/respuestas/");
    return res.data;
};

export const createRespuesta = async (formData: FormData) => {
    const res = await api.post("/respuestas/", formData);
    return res.data;
};

export const getArchivoRespuestaUrl = (id: number): string => {
    return `${window.location.origin}/respuestas/${id}/archivo`;
};

export const getArchivoRespuestaDownloadUrl = (id: number): string => {
    return `${window.location.origin}/respuestas/${id}/archivo/download`;
};