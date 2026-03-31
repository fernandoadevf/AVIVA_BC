"use client";

import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { LoadingScreen } from "@/components/LoadingScreen";

export function AppWrapper({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <>
      <AnimatePresence mode="wait">
        {isLoading && (
          <LoadingScreen
            key="app-loading-screen"
            onComplete={() => setIsLoading(false)}
          />
        )}
      </AnimatePresence>
      <div
        aria-hidden={isLoading}
        style={{
          opacity: isLoading ? 0 : 1,
          transition: "opacity 0.5s ease-out",
        }}
      >
        {children}
      </div>
    </>
  );
}
