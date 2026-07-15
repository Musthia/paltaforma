import { createContext, useContext } from "react";

export const TabParamsContext = createContext<Record<string, string>>({});

export function useTabParams() {
  return useContext(TabParamsContext);
}
