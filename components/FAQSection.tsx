"use client";

import { useId, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ParallaxRise } from "@/components/ParallaxRise";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

const faqs = [
  {
    q: "QUANDO ACONTECE O AVIVA BC?",
    a: "Sempre no último sábado do mês, às 5h da manhã. Próximo: 25 de abril de 2026.",
  },
  {
    q: "ONDE EXATAMENTE É NA PRAIA?",
    a: "Praia Barra Norte, em frente à Roda Gigante de Balneário Camboriú. Coordenadas serão enviadas pelo grupo do WhatsApp.",
  },
  {
    q: "PRECISO ME INSCREVER?",
    a: "Não. O evento é aberto. Mas entre no grupo do WhatsApp para receber a confirmação e localização exata.",
  },
  {
    q: "QUAL O CUSTO?",
    a: "O AVIVA BC é completamente gratuito.",
  },
  {
    q: "POSSO LEVAR CRIANÇAS?",
    a: "Sim. O evento é para todos que queiram adorar.",
  },
  {
    q: "COMO FICO POR DENTRO DOS PRÓXIMOS?",
    a: "Entre no grupo do WhatsApp. É o único canal oficial.",
  },
] as const;

export function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);
  const reduced = usePrefersReducedMotion();
  const baseId = useId();
  const sectionRef = useRef<HTMLElement>(null);

  return (
    <section
      ref={sectionRef}
      data-section="faq"
      data-nav-theme="dark"
      className="overflow-hidden bg-brand-dark py-24 md:py-32"
    >
      <ParallaxRise
        triggerRef={sectionRef}
        strength={84}
        scrub={0.68}
        className="container-fluid px-3 md:px-6"
      >
        <p className="font-mono text-xs uppercase tracking-[0.35em] text-brand-orange">
          {"//FAQ"}
        </p>
        <h2 className="mt-4 font-fjalla text-[clamp(2.5rem,6vw,5rem)] leading-none text-brand-cream">
          <span className="text-brand-orange">&lt;</span>
          PERGUNTAS FREQUENTES
          <span className="text-brand-orange">&gt;</span>
        </h2>

        <div className="mt-12 max-w-4xl border-t border-transparent">
          {faqs.map((item, index) => {
            const isOpen = open === index;
            const panelId = `${baseId}-panel-${index}`;
            const headerId = `${baseId}-header-${index}`;
            return (
              <div
                key={item.q}
                className="border-b border-[#222]"
              >
                <button
                  type="button"
                  id={headerId}
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                  onClick={() => setOpen(isOpen ? null : index)}
                  className="flex w-full items-center justify-between gap-4 py-5 text-left"
                >
                  <span className="font-mono text-[13px] font-bold uppercase tracking-wide text-brand-orange md:text-[14px]">
                    {item.q}
                  </span>
                  <span
                    className="shrink-0 font-mono text-2xl text-brand-cream transition-transform duration-300"
                    style={{ transform: isOpen ? "rotate(45deg)" : "rotate(0deg)" }}
                    aria-hidden
                  >
                    +
                  </span>
                </button>
                <AnimatePresence initial={false}>
                  {isOpen ? (
                    <motion.div
                      id={panelId}
                      role="region"
                      aria-labelledby={headerId}
                      initial={reduced ? false : { height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={reduced ? undefined : { height: 0, opacity: 0 }}
                      transition={{ duration: reduced ? 0 : 0.35, ease: "easeInOut" }}
                      className="overflow-hidden"
                    >
                      <p className="pb-6 font-mono text-[13px] leading-relaxed text-brand-cream md:pr-8">
                        {item.a}
                      </p>
                    </motion.div>
                  ) : null}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </ParallaxRise>
    </section>
  );
}
