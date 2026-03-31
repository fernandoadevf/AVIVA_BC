"use client";

import { createContext, useContext, type ReactNode } from "react";

/** false enquanto o loading inicial está ativo — não inicializar GSAP ScrollTrigger antes disso */
const LoadingReadyContext = createContext(false);

export function LoadingReadyProvider({
  value,
  children,
}: {
  value: boolean;
  children: ReactNode;
}) {
  return (
    <LoadingReadyContext.Provider value={value}>
      {children}
    </LoadingReadyContext.Provider>
  );
}

export function useLoadingReady(): boolean {
  return useContext(LoadingReadyContext);
}
