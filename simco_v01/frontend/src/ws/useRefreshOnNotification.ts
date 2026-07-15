import { useEffect, useRef } from "react";
import { globalWS } from "./globalWS";

export function useRefreshOnNotification(tipo: string, callback: () => void) {
  const cbRef = useRef(callback);
  cbRef.current = callback;

  useEffect(() => {
    globalWS.start();
    return globalWS.on(tipo, () => cbRef.current());
  }, [tipo]);
}
