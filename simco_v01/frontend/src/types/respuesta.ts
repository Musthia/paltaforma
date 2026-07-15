export interface Respuesta {
    id: number;
    solicitud_id: number;
    usuario_responde_id: number;
    estado_documento: string;
    observacion: string;
    archivo_nombre: string | null;
    detalle: string;
    fecha_respuesta: Date;
}