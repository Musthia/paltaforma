import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "../auth/token";

// Desarrollo: usa VITE_API_URL del .env.development (ej: http://192.168.109.116:8000)
// Producción: usa window.location.origin (mismo servidor que sirve la página)
//const API_BASE = import.meta.env.VITE_API_URL || window.location.origin;

export const api = axios.create({
  baseURL:  "/api",
});

let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

function getNewToken(): Promise<string> {
  return new Promise((resolve, reject) => {
    const refresh = getRefreshToken();
    if (!refresh) {
      clearTokens();
      reject(new Error("No refresh token"));
      return;
    }
    api
      .post("/auth/refresh", { refresh_token: refresh })
      .then((res) => {
        const data = res.data;
        setTokens(data.access_token, data.refresh_token);
        resolve(data.access_token);
      })
      .catch((err) => {
        clearTokens();
        reject(err);
      });
  });
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }
    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingRequests.push((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }
    originalRequest._retry = true;
    isRefreshing = true;
    try {
      const token = await getNewToken();
      pendingRequests.forEach((cb) => cb(token));
      pendingRequests = [];
      originalRequest.headers.Authorization = `Bearer ${token}`;
      return api(originalRequest);
    } catch {
      pendingRequests = [];
      window.location.href = "/";
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);