import { api } from "./client";

export const getActivity = async () => {
    const res = await api.get("/dashboard/activity");
    return res.data;
};