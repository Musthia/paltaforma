export const menuItems: MenuItem[] = [
    {
        label: "Dashboard",
        path: "/dashboard",
        roles: ["admin", "oficina", "deposito", "consulta", "Administrador", "Supervisor", "Operador"],
    },
    {
        label: "Mensajes",
        path: "/mensajes",
        roles: ["admin", "oficina", "deposito", "Administrador", "Supervisor", "Operador"],
    },
    {
        label: "Solicitudes",
        path: "/solicitudes",
        roles: ["admin", "oficina", "deposito", "Administrador", "Supervisor", "Operador"],
    },
    {
        label: "Respuestas",
        path: "/respuestas",
        roles: ["admin", "oficina", "deposito", "Administrador", "Supervisor", "Operador"],
    },
    {
        label: "Auditoría SIMCO",
        path: "/auditoria",
        roles: ["admin", "Administrador"],
    },
];

export type Role = "admin" | "oficina" | "deposito" | "consulta" | "Administrador" | "Supervisor" | "Operador" | "Consulta";

export interface MenuItem {
    label: string;
    path: string;
    roles: Role[];
}
