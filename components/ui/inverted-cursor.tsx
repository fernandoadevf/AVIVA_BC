"use client";

import React, { useEffect, useRef, useState } from "react";

export interface InvertedCursorProps {
  size?: number;
  /** Element that defines the coordinate system and receives pointer tracking (e.g. section ref). */
  containerRef: React.RefObject<HTMLElement | null>;
}

export function InvertedCursor({ size = 60, containerRef }: InvertedCursorProps) {
  const cursorRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number | undefined>(undefined);
  const previousPos = useRef({ x: -size, y: -size });
  const targetPos = useRef({ x: -size, y: -size });
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const animate = () => {
      const el = cursorRef.current;
      if (!el) {
        rafRef.current = requestAnimationFrame(animate);
        return;
      }

      const currentX = previousPos.current.x;
      const currentY = previousPos.current.y;
      const targetX = targetPos.current.x - size / 2;
      const targetY = targetPos.current.y - size / 2;

      const deltaX = (targetX - currentX) * 0.2;
      const deltaY = (targetY - currentY) * 0.2;

      const newX = currentX + deltaX;
      const newY = currentY + deltaY;

      previousPos.current = { x: newX, y: newY };
      el.style.transform = `translate(${newX}px, ${newY}px)`;

      rafRef.current = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      setVisible(true);
      targetPos.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    const handleMouseEnter = () => {
      setVisible(true);
    };

    const handleMouseLeave = () => {
      setVisible(false);
      targetPos.current = { x: -size, y: -size };
    };

    container.addEventListener("mousemove", handleMouseMove);
    container.addEventListener("mouseenter", handleMouseEnter);
    container.addEventListener("mouseleave", handleMouseLeave);

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      container.removeEventListener("mousemove", handleMouseMove);
      container.removeEventListener("mouseenter", handleMouseEnter);
      container.removeEventListener("mouseleave", handleMouseLeave);
      if (rafRef.current !== undefined) cancelAnimationFrame(rafRef.current);
    };
  }, [containerRef, size]);

  return (
    <div
      ref={cursorRef}
      className="pointer-events-none absolute left-0 top-0 z-[60] rounded-full border-2 border-brand-black bg-brand-cream/45 shadow-[0_6px_28px_rgba(10,10,10,0.18),inset_0_1px_0_rgba(255,255,255,0.35)] backdrop-blur-[3px] transition-opacity duration-300"
      style={{
        width: size,
        height: size,
        opacity: visible ? 1 : 0,
        willChange: "transform",
      }}
      aria-hidden
    />
  );
}

/** Alias — mesmo componente do snippet original */
export const Cursor = InvertedCursor;

export default InvertedCursor;
