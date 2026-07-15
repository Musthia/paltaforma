const ACCESS_KEY = "sige_access";
const REFRESH_KEY = "sige_refresh";

export const setTokens = (access: string, refresh: string) => {
  sessionStorage.setItem(ACCESS_KEY, access);
  sessionStorage.setItem(REFRESH_KEY, refresh);
};

export const getAccessToken = () => {
  return sessionStorage.getItem(ACCESS_KEY);
};

export const getRefreshToken = () => {
  return sessionStorage.getItem(REFRESH_KEY);
};

export const clearTokens = () => {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
};

export const getUserRole = () => {
  const token = sessionStorage.getItem("sige_access");
  if (!token) return null;

  const payload = JSON.parse(atob(token.split(".")[1]));
  return payload.role;
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};