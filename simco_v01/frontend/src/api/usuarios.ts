import { api } from "./client";

export interface Usuario {
  id: number;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export const getUsuarios = async (): Promise<Usuario[]> => {
  const res = await api.get("/users/");
  return res.data;
};

export const getUsuario = async (id: number): Promise<Usuario> => {
  const res = await api.get(`/users/${id}`);
  return res.data;
};

export const createUsuario = async (data: {
  username: string;
  full_name: string;
  password: string;
  role: string;
}): Promise<Usuario> => {
  const res = await api.post("/users/", data);
  return res.data;
};

export const updateUsuario = async (
  id: number,
  data: {
    full_name?: string;
    password?: string;
    role?: string;
    is_active?: boolean;
  }
): Promise<Usuario> => {
  const res = await api.put(`/users/${id}`, data);
  return res.data;
};

export const deleteUsuario = async (id: number): Promise<void> => {
  await api.delete(`/users/${id}`);
};
