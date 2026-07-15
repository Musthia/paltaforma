import type { JwtPayload } from "jwt-decode";

export interface UserToken extends JwtPayload {
    sub: string;
    id: number;
    role: "admin" | "oficina" | "deposito" | "consulta";
    username: string;
    full_name: string;
}