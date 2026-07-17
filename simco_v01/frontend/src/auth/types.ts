import type { JwtPayload } from "jwt-decode";

export type Role = "admin" | "oficina" | "deposito" | "consulta";

export interface UserToken extends JwtPayload {
    sub: string;
    user_id: number;
    role: Role;
    nivel: number;
    is_superuser: boolean;
    full_name: string;
}