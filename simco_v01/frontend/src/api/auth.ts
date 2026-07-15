import { api } from "./client";

export const loginRequest = async (username: string, password: string) => {
  const res = await api.post("/auth/login", {
    username,
    password,
  });

  return res.data;
};

export const refreshTokenRequest = async (refreshToken: string) => {
  const res = await api.post("/auth/refresh", {
    refresh_token: refreshToken,
  });

  return res.data;
};