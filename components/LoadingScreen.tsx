"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { motion, AnimatePresence } from "framer-motion";

const WORDS = ["Deus", "está despertando", "uma geração!"] as const;

/** Theme (spec): --bg, --text, --stroke */
const loaderStyle = {
  "--bg": "#0a0a0a",
  "--text": "#f5f5f5",
  "--stroke": "#1f1f1f",
} as CSSProperties;

export type LoadingScreenProps = {
  onComplete: () => void;
};

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const onCompleteRef = useRef(onComplete);
  const completedRef = useRef(false);
  onCompleteRef.current = onComplete;

  const [wordIndex, setWordIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setWordIndex(1), 900);
    const t2 = setTimeout(() => setWordIndex(2), 1800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    const start = performance.now();
    let rafId = 0;
    let doneTimeout: ReturnType<typeof setTimeout>;

    const finish = () => {
      if (completedRef.current) return;
      completedRef.current = true;
      setProgress(100);
      doneTimeout = setTimeout(() => {
        onCompleteRef.current();
      }, 400);
    };

    const tick = (now: number) => {
      const elapsed = now - start;
      if (elapsed >= 2700) {
        finish();
        return;
      }
      setProgress((elapsed / 2700) * 100);
      rafId = requestAnimationFrame(tick);
    };

    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      clearTimeout(doneTimeout);
    };
  }, []);

  const display = Math.round(progress).toString().padStart(3, "0");
  const scaleX = Math.min(1, progress / 100);

  return (
    <motion.div
      className="fixed inset-0 z-[9999]"
      style={{ ...loaderStyle, backgroundColor: "var(--bg)" }}
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
    >
      <div className="absolute inset-0 flex items-center justify-center px-4">
        <AnimatePresence mode="wait">
          <motion.span
            key={wordIndex}
            className="max-w-[min(92vw,36rem)] text-center font-display text-3xl italic leading-tight text-[color:color-mix(in_srgb,var(--text)_80%,transparent)] sm:text-4xl md:text-5xl lg:text-6xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          >
            {WORDS[wordIndex]}
          </motion.span>
        </AnimatePresence>
      </div>

      <motion.div
        className="absolute bottom-8 right-8 font-display tabular-nums not-italic md:bottom-12 md:right-12"
        style={{ color: "var(--text)" }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <span className="text-6xl md:text-8xl lg:text-9xl">{display}</span>
      </motion.div>

      <div
        className="absolute bottom-0 left-0 right-0 h-[3px] bg-[color:color-mix(in_srgb,var(--stroke)_50%,transparent)]"
        aria-hidden
      >
        <motion.div
          className="h-full origin-left"
          style={{
            background: "linear-gradient(90deg, #89AACC 0%, #4E85BF 100%)",
            boxShadow: "0 0 8px rgba(137, 170, 204, 0.35)",
          }}
          initial={{ scaleX: 0 }}
          animate={{ scaleX }}
          transition={{ duration: 0.1, ease: "linear" }}
        />
      </div>
    </motion.div>
  );
}
