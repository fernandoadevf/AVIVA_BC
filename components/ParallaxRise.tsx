"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { cn } from "@/lib/cn";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export type ParallaxRiseProps = {
  triggerRef: React.RefObject<HTMLElement | null>;
  children: ReactNode;
  /** Deslocamento total em px: o bloco vai de +strength/2 a −strength/2 ao atravessar a viewport */
  strength?: number;
  scrub?: number | boolean;
  className?: string;
};

export function ParallaxRise({
  triggerRef,
  children,
  strength = 88,
  scrub = 0.75,
  className,
}: ParallaxRiseProps) {
  const innerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const inner = innerRef.current;
    const trigger = triggerRef.current;
    if (!inner || !trigger) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const half = strength * 0.5;
    const tween = gsap.fromTo(
      inner,
      { y: half },
      {
        y: -half,
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
    <div
      ref={innerRef}
      className={cn("will-change-transform", className)}
    >
      {children}
    </div>
  );
}
