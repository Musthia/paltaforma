import { jwtDecode } from "jwt-decode";
import { getAccessToken } from "./token";

import type { UserToken } from "./types";

export const getUser = (): UserToken | null => {
    const token = getAccessToken();

    if (!token) return null;

    try {
        return jwtDecode<UserToken>(token);
    } catch {
        return null;
    }
};