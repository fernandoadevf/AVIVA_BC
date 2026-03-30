"use client";

import { useLayoutEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { MessageCircle } from "lucide-react";
import { ParallaxRise } from "@/components/ParallaxRise";
import { InvertedCursor } from "@/components/ui/inverted-cursor";
import { usePointerFine } from "@/lib/usePointerFine";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const reduced = usePrefersReducedMotion();
  const finePointer = usePointerFine();
  const useInvertedCursor = !reduced && finePointer;

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      const reduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
      const words = section.querySelectorAll<HTMLElement>(".cta-word");

      if (reduced) {
        gsap.set(words, { opacity: 1, x: 0, y: 0 });
        return;
      }

      gsap.from(words, {
        scrollTrigger: {
          trigger: section,
          start: "top 75%",
        },
        opacity: 0,
        x: () => gsap.utils.random(-110, 110),
        y: () => gsap.utils.random(-90, 90),
        duration: 0.9,
        stagger: 0.045,
        ease: "power3.out",
      });
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      data-section="cta"
      data-nav-theme="light"
      className={`cta-section relative flex min-h-screen flex-col justify-center overflow-hidden bg-brand-orange px-3 py-24 md:px-8 ${useInvertedCursor ? "cursor-none" : ""}`}
    >
      {useInvertedCursor && <InvertedCursor containerRef={sectionRef} size={64} />}
      <ParallaxRise
        triggerRef={sectionRef}
        strength={72}
        scrub={0.8}
        className="relative z-[1] container-fluid mx-auto max-w-5xl"
      >
        <div className="cta-headline space-y-2 md:space-y-4">
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2">
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              AGORA
            </span>
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              VOCÊ
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
            <span className="cta-word inline-flex items-center border-2 border-brand-black px-3 py-1 font-fjalla text-[clamp(2.2rem,8vw,5.5rem)] leading-none text-brand-black">
              [NÃO]
            </span>
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              PODE
            </span>
          </div>
          <div className="flex flex-wrap gap-x-6">
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              FICAR
            </span>
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              DE
            </span>
          </div>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              FORA
            </span>
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              ?/
            </span>
          </div>
        </div>

        <p className="mt-10 font-mono text-sm text-brand-black md:text-[14px]">
          &lt;ENTRE NO GRUPO ABAIXO&gt;
        </p>

        <Link
          id="whatsapp-btn"
          href="#"
          target="_blank"
          rel="noopener noreferrer"
          className="group mt-8 flex w-full max-w-lg items-center gap-3 border-2 border-brand-black px-4 py-3 font-fjalla text-[11px] uppercase leading-snug tracking-[0.22em] text-brand-black transition-[background-color,color,box-shadow] duration-300 hover:bg-brand-black hover:text-brand-cream focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-black focus-visible:ring-offset-2 focus-visible:ring-offset-brand-orange sm:gap-4 sm:px-5 sm:py-3.5 sm:text-xs md:mt-10 md:text-[13px]"
        >
          <MessageCircle
            className="h-[1.125rem] w-[1.125rem] shrink-0 stroke-[1.5] text-brand-black transition-colors duration-300 group-hover:text-brand-cream sm:h-5 sm:w-5"
            aria-hidden
          />
          <span className="min-w-0 flex-1 text-balance text-left">
            ENTRAR NO GRUPO DO WHATSAPP
          </span>
          <span
            className="shrink-0 font-mono text-sm text-brand-black/45 transition-colors duration-300 group-hover:text-brand-cream sm:text-base"
            aria-hidden
          >
            →
          </span>
        </Link>

        <p className="mt-8 font-mono text-xs text-brand-black/90">
          {"// +500 JÁ ESTÃO DENTRO"}
        </p>
      </ParallaxRise>
    </section>
  );
}
