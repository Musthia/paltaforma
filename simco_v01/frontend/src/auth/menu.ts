export type Role = "admin" | "oficina" | "deposito" | "consulta";

export interface MenuItem {
    label: string;
    path: string;
    roles: Role[];
}

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
        label: "Usuarios",
        path: "/usuarios",
        roles: ["admin"],
    },
    {
        label: "Auditoría",
        path: "/auditoria",
        roles: ["admin"],
    },
];