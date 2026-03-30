"use client";

import { useRef } from "react";
import { motion } from "framer-motion";
import { Annotation } from "@/components/Annotation";
import { ParallaxRise } from "@/components/ParallaxRise";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

const cards = [
  {
    title: "05H DA MANHÃ",
    body: "Quando o sol ainda não nasceu. Quando a cidade dorme. Quando só os que foram chamados aparecem.",
    icon: (
      <svg
        viewBox="0 0 64 64"
        className="h-10 w-10 text-brand-cream"
        aria-hidden
      >
        <circle
          cx="32"
          cy="32"
          r="14"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M32 10v6M32 48v6M54 32h-6M16 32h-6"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M22 44c12 8 24-4 20-16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
    ),
  },
  {
    title: "TODO MÊS",
    body: "Uma vez por mês. Sem desculpas. Sem adiamentos.",
    icon: (
      <svg
        viewBox="0 0 64 64"
        className="h-10 w-10 text-brand-cream"
        aria-hidden
      >
        <rect
          x="10"
          y="14"
          width="44"
          height="40"
          rx="2"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path d="M10 24h44" stroke="currentColor" strokeWidth="2" />
        <path d="M22 10v8M42 10v8" stroke="currentColor" strokeWidth="2" />
        <rect x="18" y="32" width="8" height="8" fill="currentColor" />
      </svg>
    ),
  },
  {
    title: "PRAIA BARRA NORTE",
    body: "Em frente à Roda Gigante. Balneário Camboriú, SC.",
    icon: (
      <svg
        viewBox="0 0 64 64"
        className="h-10 w-10 text-brand-cream"
        aria-hidden
      >
        <path
          d="M32 8c-10 0-18 8-18 18 0 14 18 30 18 30s18-16 18-30c0-10-8-18-18-18z"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
        <circle cx="32" cy="26" r="4" fill="currentColor" />
      </svg>
    ),
  },
] as const;

export function HowItWorksSection() {
  const reduced = usePrefersReducedMotion();
  const sectionRef = useRef<HTMLElement>(null);

  return (
    <section
      ref={sectionRef}
      data-section="como-funciona"
      data-nav-theme="dark"
      className="relative overflow-hidden bg-brand-dark py-24 md:py-32"
    >
      <Annotation
        text="//ESTER 494"
        className="right-6 top-10 text-brand-cream/80 md:right-12"
      />
      <ParallaxRise
        triggerRef={sectionRef}
        strength={92}
        scrub={0.7}
        className="container-fluid px-3 md:px-6"
      >
        <h2 className="font-fjalla text-[clamp(2.5rem,6vw,5rem)] leading-none text-brand-cream">
          <span className="text-brand-orange">&lt;</span>
          COMO FUNCIONA
          <span className="text-brand-orange">&gt;</span>
        </h2>

        <div className="row g-4 mt-10 md:mt-14">
          {cards.map((card, index) => (
            <div key={card.title} className="col-md-4">
              <motion.article
                initial={reduced ? false : { opacity: 0, y: 56 }}
                whileInView={reduced ? undefined : { opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.25 }}
                transition={{
                  duration: 0.65,
                  delay: reduced ? 0 : index * 0.12,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="group h-full border border-brand-orange/30 bg-[#111111] p-6 transition-[border-color,box-shadow] duration-300 hover:border-brand-orange hover:shadow-[0_0_28px_rgba(255,85,0,0.18)]"
              >
                <div className="mb-5">{card.icon}</div>
                <h3 className="font-fjalla text-[clamp(2rem,4vw,3rem)] leading-none text-brand-cream">
                  {card.title}
                </h3>
                <p className="mt-4 font-mono text-[13px] leading-relaxed text-white/65">
                  {card.body}
                </p>
              </motion.article>
            </div>
          ))}
        </div>
      </ParallaxRise>
    </section>
  );
}
