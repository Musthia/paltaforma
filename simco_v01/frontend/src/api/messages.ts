import { api } from "./client";

export interface MessageOut {
  id: number;
  sender_id: number;
  sender_name: string | null;
  receiver_id: number | null;
  receiver_name: string | null;
  content: string;
  is_general: boolean;
  created_at: string;
  read_at: string | null;
}

export const getGeneralMessages = async (): Promise<MessageOut[]> => {
  const res = await api.get("/messages/general");
  return res.data;
};

export const getPrivateMessages = async (otherId?: number): Promise<MessageOut[]> => {
  const params = otherId ? { other_id: otherId } : {};
  const res = await api.get("/messages/privados", { params });
  return res.data;
};

export const sendMessage = async (data: {
  receiver_id?: number | null;
  content: string;
  is_general?: boolean;
}): Promise<MessageOut> => {
  const res = await api.post("/messages/", data);
  return res.data;
};

export const getUnreadCount = async (): Promise<number> => {
  const res = await api.get("/messages/no-leidos");
  return res.data.total;
};

export const markAsRead = async (messageId: number): Promise<void> => {
  await api.post(`/messages/${messageId}/leer`);
};

export const getAvailableUsers = async (): Promise<{ id: number; username: string; full_name: string; role: string }[]> => {
  const res = await api.get("/messages/usuarios-disponibles");
  return res.data;
};
