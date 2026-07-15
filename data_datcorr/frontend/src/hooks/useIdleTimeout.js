import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";
import api from "../api/axiosClient";

export function useIdleTimeout(timeout = 15 * 60 * 1000) {
    const timerRef = useRef(null);
    const navigate = useNavigate();
    const logout = useAuthStore((s) => s.logout);

    useEffect(() => {
        const reset = () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            timerRef.current = setTimeout(async () => {
                try {
                    await api.post("/auth/logout");
                } catch {
                    // ignore
                }
                logout();
                navigate("/login", { state: { msg: "Sesión expirada por inactividad" } });
            }, timeout);
        };

        const events = ["mousemove", "keydown", "click", "scroll", "touchstart"];
        events.forEach((e) => window.addEventListener(e, reset));
        reset();

        return () => {
            events.forEach((e) => window.removeEventListener(e, reset));
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [timeout, logout, navigate]);
}
