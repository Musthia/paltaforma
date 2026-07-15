import { jwtDecode } from "jwt-decode";

export const decodeToken = (token) => {
    if (!token) return null;

    try {
        return jwtDecode(token);
    } catch (err) {
        return null;
    }
};