import axios from "axios";
import { useAuthStore } from "../auth/authStore";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    withCredentials: true,
});

api.interceptors.request.use((config) => {

    const token = useAuthStore.getState().accessToken;

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

let isRefreshing = false;
let pendingRequests = [];

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes("/usuarios/refresh")) {
            if (isRefreshing) {
                return new Promise((resolve) => {
                    pendingRequests.push(() => resolve(api(originalRequest)));
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const response = await axios.post(
                    "http://127.0.0.1:8000/auth/refresh",
                    {},
                    { withCredentials: true }
                );

                const newToken = response.data.access_token;
                useAuthStore.getState().setTokens(newToken);

                pendingRequests.forEach((cb) => cb());
                pendingRequests = [];

                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return api(originalRequest);
            } catch {
                useAuthStore.getState().logout();
                window.location.href = "/login";
                return Promise.reject(error);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default api;
