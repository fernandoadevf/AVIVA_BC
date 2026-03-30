"use client";

import { cn } from "@/lib/cn";

export type AnnotationProps = {
  text: string;
  rotate?: number;
  className?: string;
};

export function Annotation({ text, rotate = 0, className }: AnnotationProps) {
  return (
    <span
      className={cn(
        "pointer-events-none absolute font-mono text-[10px] uppercase tracking-widest opacity-50",
        className,
      )}
      style={{ transform: rotate !== 0 ? `rotate(${rotate}deg)` : undefined }}
      aria-hidden
    >
      {text}
    </span>
  );
}
