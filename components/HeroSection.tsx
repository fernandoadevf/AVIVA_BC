"use client";

import { useRef } from "react";
import { motion } from "framer-motion";
import { WhatsAppCtaButton } from "@/components/ui/button-with-icon";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

const stagger = 0.08;

/** Wireframe Figma 1440×1024 — cores em 0–1 → CSS */
const FIGMA = {
  bg: "#252525", // rgb(0.146, 0.146, 0.146)
  orange: "#ff4400", // rgb(1, 0.267, 0) ≈ fill principal
  tagline: "#ffccb8", // rgb(1, 0.797, 0.723) pêssego
  frameW: 1440,
  frameH: 1024,
} as const;

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const reduced = usePrefersReducedMotion();

  const block = reduced
    ? { initial: false, animate: {} }
    : {
        initial: { opacity: 0, y: 12 },
        animate: { opacity: 1, y: 0 },
      };

  return (
    <section
      ref={sectionRef}
      data-section="hero"
      data-nav-theme="dark"
      className="relative min-h-[min(84svh,740px)] overflow-hidden"
      style={{ backgroundColor: FIGMA.bg }}
    >
      <div
        id="hero-bg"
        className="pointer-events-none absolute inset-0 z-0"
        style={{ backgroundColor: FIGMA.bg }}
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 z-[1] bg-[url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27300%27 height=%27300%27%3E%3Cfilter id=%27n%27%3E%3CfeTurbulence type=%27fractalNoise%27 baseFrequency=%270.85%27 numOctaves=%274%27 stitchTiles=%27stitch%27/%3E%3C/filter%3E%3Crect width=%27100%25%27 height=%27100%25%27 filter=%27url(%23n)%27/%3E%3C/svg%3E')] opacity-[0.04]"
        aria-hidden
      />

      {/* Canvas 1440×1024 — posições em % iguais ao Figma */}
      <div className="relative z-[2] mx-auto min-h-[min(84svh,740px)] w-full max-w-[1440px]">
        {/* Tagline — mesma coluna x:379; y acima do wireframe (ref. y:174 → mais alto) */}
        <motion.p
          {...block}
          transition={{ duration: 0.4, delay: 0 }}
          className="absolute z-[15] max-w-[90%] font-mono text-[10px] uppercase leading-tight tracking-wide sm:text-[11px] md:text-xs"
          style={{
            left: 380,
            top: 70,
            width: `${(545 / FIGMA.frameW) * 100}%`,
            color: FIGMA.tagline,
            paddingTop: 25,
            paddingBottom: 25,
          }}
        >
          Deus está despertando uma geração!
        </motion.p>

        {/* [AVIVA — 1:3 x:320 y:174 */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 1 * stagger }}
          className="absolute z-[5] max-w-[95vw] font-fjalla text-[clamp(2.75rem,11.5vw,10.5rem)] uppercase leading-[0.82] tracking-tight"
          style={{
            left: `${(320 / FIGMA.frameW) * 100}%`,
            top: `${(174 / FIGMA.frameH) * 100}%`,
            width: `${(494 / FIGMA.frameW) * 100}%`,
            color: FIGMA.orange,
          }}
        >
          [AVIVA
        </motion.p>

        {/* BC&apos;26] — 1:4 x:711 y:238 (deslocado em relação ao primeiro) */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 2 * stagger }}
          className="absolute z-[5] max-w-[95vw] font-fjalla text-[clamp(2.75rem,11.5vw,10.5rem)] uppercase leading-[0.82] tracking-tight"
          style={{
            left: `${(711 / FIGMA.frameW) * 100}%`,
            top: `${(238 / FIGMA.frameH) * 100}%`,
            width: `${(489 / FIGMA.frameW) * 100}%`,
            color: FIGMA.orange,
          }}
        >
          BC&apos;26]
        </motion.p>

        {/* 25 DE ABRIL — 1:6 x:515 y:336 */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 3 * stagger }}
          className="absolute z-[5] whitespace-nowrap font-fjalla text-[clamp(1.35rem,4.5vw,4rem)] uppercase leading-none tracking-tight"
          style={{
            left: 575,
            top: 336,
            color: FIGMA.orange,
          }}
        >
          25 DE ABRIL
        </motion.p>

        <div className="absolute left-1/2 top-[507px] z-[6] -translate-x-1/2">
          <motion.div
            {...block}
            transition={{ duration: 0.45, delay: 3.4 * stagger }}
          >
            <WhatsAppCtaButton id="whatsapp-cta" href="#" />
          </motion.div>
        </div>

        {/* PRAIA BARRA NORTE vertical esquerda */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 4 * stagger }}
          className="absolute z-[5] origin-center font-fjalla uppercase tracking-[0.12em]"
          style={{
            left: -81,
            top: 117,
            fontSize: "clamp(0.65rem, 1.5vw, 1.05rem)",
            color: FIGMA.orange,
            writingMode: "vertical-rl",
            transform: "none",
          }}
        >
          PRAIA BARRA NORTE
        </motion.p>

        {/* PRAIA BARRA NORTE vertical direita */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 4.25 * stagger }}
          className="absolute z-[5] origin-center font-fjalla uppercase tracking-[0.12em]"
          style={{
            left: 1451,
            top: 480,
            fontSize: "clamp(0.65rem, 1.5vw, 1.05rem)",
            color: FIGMA.orange,
            writingMode: "vertical-rl",
            transform: "none",
          }}
        >
          PRAIA BARRA NORTE
        </motion.p>

        {/* AVIVA BC vertical direita */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 5 * stagger }}
          className="absolute z-[5] origin-center font-fjalla uppercase tracking-[0.18em]"
          style={{
            left: 1443,
            top: 150,
            fontSize: "clamp(0.55rem, 1.1vw, 0.85rem)",
            color: FIGMA.orange,
            writingMode: "vertical-rl",
            transform: "none",
          }}
        >
          AVIVA BC
        </motion.p>

        {/* AVIVA BC vertical esquerda baixo */}
        <motion.p
          {...block}
          transition={{ duration: 0.45, delay: 5.25 * stagger }}
          className="absolute z-[5] origin-center font-fjalla uppercase tracking-[0.18em]"
          style={{
            left: -79,
            top: 514,
            fontSize: "clamp(0.55rem, 1.1vw, 0.85rem)",
            color: FIGMA.orange,
            writingMode: "vertical-rl",
            transform: "none",
          }}
        >
          AVIVA BC
        </motion.p>
      </div>
    </section>
  );
}
