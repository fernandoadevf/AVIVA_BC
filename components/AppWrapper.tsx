"use client";

import { useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { LoadingScreen } from "@/components/LoadingScreen";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

function refreshScrollTriggers(): void {
  ScrollTrigger.refresh();
}

export function AppWrapper({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const onLoad = () => refreshScrollTriggers();
    window.addEventListener("load", onLoad);
    void document.fonts.ready.then(() => refreshScrollTriggers());

    let resizeTimer: ReturnType<typeof setTimeout>;
    const onResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => refreshScrollTriggers(), 120);
    };
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("load", onLoad);
      window.removeEventListener("resize", onResize);
      clearTimeout(resizeTimer);
    };
  }, []);

  useEffect(() => {
    if (isLoading) return;
    let cancelled = false;
    const timers: ReturnType<typeof setTimeout>[] = [];

    const run = () => {
      if (!cancelled) refreshScrollTriggers();
    };

    requestAnimationFrame(() => {
      requestAnimationFrame(run);
    });
    void document.fonts.ready.then(run);
    timers.push(setTimeout(run, 600));

    return () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    };
  }, [isLoading]);

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
