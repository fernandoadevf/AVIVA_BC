"use client";

import { useSyncExternalStore } from "react";

/** True quando o dispositivo tem ponteiro preciso (ex.: mouse), não apenas toque. */
export function usePointerFine(): boolean {
  return useSyncExternalStore(
    (onStoreChange) => {
      const mq = window.matchMedia("(pointer: fine)");
      mq.addEventListener("change", onStoreChange);
      return () => mq.removeEventListener("change", onStoreChange);
    },
    () => window.matchMedia("(pointer: fine)").matches,
    () => false,
  );
}
