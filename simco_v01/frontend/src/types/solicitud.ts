export interface Solicitud {
    id: number;
    codigo: string;
    tipo_documento: string;
    identificador_documento: string;
    detalle: string;
    prioridad: "baja" | "media" | "alta";
    estado: string;
    destacado: boolean;
    verificado: boolean;
    archivo_nombre: string | null;
}