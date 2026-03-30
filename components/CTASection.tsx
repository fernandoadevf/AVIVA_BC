"use client";

import { useLayoutEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ParallaxRise } from "@/components/ParallaxRise";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);

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
      className="cta-section flex min-h-screen flex-col justify-center overflow-hidden bg-brand-orange px-3 py-24 md:px-8"
    >
      <ParallaxRise
        triggerRef={sectionRef}
        strength={72}
        scrub={0.8}
        className="container-fluid mx-auto max-w-5xl"
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
          className="mt-6 inline-block bg-brand-black px-10 py-5 font-fjalla text-xl uppercase tracking-wide text-brand-cream md:text-2xl"
        >
          ENTRAR NO GRUPO DO WHATSAPP &gt;
        </Link>

        <p className="mt-8 font-mono text-xs text-brand-black/90">
          {"// +500 JÁ ESTÃO DENTRO"}
        </p>
      </ParallaxRise>
    </section>
  );
}
