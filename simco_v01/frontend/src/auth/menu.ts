import type { Role } from "./types";

export const menuItems: MenuItem[] = [
    {
        label: "Dashboard",
        path: "/dashboard",
        roles: ["admin", "oficina", "deposito", "consulta"],
    },
    {
        label: "Mensajes",
        path: "/mensajes",
        roles: ["admin", "oficina", "deposito"],
    },
    {
        label: "Solicitudes",
        path: "/solicitudes",
        roles: ["admin", "oficina", "deposito"],
    },
    {
        label: "Respuestas",
        path: "/respuestas",
        roles: ["admin", "oficina", "deposito"],
    },
    {
        label: "Auditoría SIMCO",
        path: "/auditoria",
        roles: ["admin"],
    },
];

export interface MenuItem {
    label: string;
    path: string;
    roles: Role[];
}
