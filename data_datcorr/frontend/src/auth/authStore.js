import { create } from "zustand";
import { decodeToken } from "./jwt";

const access = sessionStorage.getItem("access_token");

export const useAuthStore = create((set) => ({

    accessToken: access,

    // refresh_token vive en cookie HttpOnly — no se guarda en JS
    user: decodeToken(access),

    setTokens: (access) => {

        sessionStorage.setItem("access_token", access);

        set({
            accessToken: access,
            user: decodeToken(access)
        });
    },

    logout: () => {

        sessionStorage.removeItem("access_token");

        set({
            accessToken: null,
            user: null
        });
    }
}));