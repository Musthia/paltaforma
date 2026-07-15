import { api } from "./client";

export interface ArchivoResult {
    tipo: "solicitud" | "respuesta";
    id: number;
    codigo?: string;
    solicitud_id?: number;
    archivo_original: string;
    entidad_titulo: string;
}

export const buscarEnArchivos = async (q: string): Promise<ArchivoResult[]> => {
    const res = await api.get("/buscar/archivos", { params: { q } });
    return res.data;
};
