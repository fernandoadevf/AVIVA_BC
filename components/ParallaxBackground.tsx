"use client";

import {
  useLayoutEffect,
  useRef,
  type ReactNode,
  type RefObject,
} from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { cn } from "@/lib/cn";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

type ParallaxBackgroundProps = {
  triggerRef: RefObject<HTMLElement | null>;
  /** Movimento vertical em px (metade para cima / metade para baixo no eixo do scroll) */
  strength?: number;
  scrub?: number | boolean;
  className?: string;
  children: ReactNode;
};

/**
 * Camada de fundo com parallax mais lento que o conteúdo (efeito de profundidade).
 */
export function ParallaxBackground({
  triggerRef,
  strength = 48,
  scrub = 1,
  className,
  children,
}: ParallaxBackgroundProps) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const el = ref.current;
    const trigger = triggerRef.current;
    if (!el || !trigger) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const h = strength * 0.5;
    const tween = gsap.fromTo(
      el,
      { y: h },
      {
        y: -h,
        ease: "none",
        scrollTrigger: {
          trigger,
          start: "top bottom",
          end: "bottom top",
          scrub,
        },
      },
    );

    return () => {
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, [triggerRef, strength, scrub]);

  return (
    <div ref={ref} className={cn("will-change-transform", className)}>
      {children}
    </div>
  );
}
