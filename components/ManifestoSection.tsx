"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Annotation } from "@/components/Annotation";
import { ParallaxRise } from "@/components/ParallaxRise";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const leftLines = [
  "O AVIVA BC",
  "NÃO É UM     CULTO_",
  "— É UM",
  "MOVIMENTO.",
] as const;

const rightCopy = [
  "Uma convocação para uma geração que decidiu não se misturar.",
  "[A REVOLUÇÃO JÁ COMEÇOU.]",
  "Nas praias. Nas escolas. Nas ruas.",
  "500 pessoas se levantaram às 5H da manhã. O próximo é maior.",
  "Homens e mulheres que sabem a quem pertencem.",
  "Fé não é fuga — é posicionamento.",
] as const;

export function ManifestoSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const leftRefs = useRef<(HTMLParagraphElement | null)[]>([]);
  const rightRefs = useRef<(HTMLParagraphElement | null)[]>([]);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const ctx = gsap.context(() => {
      const leftEls = leftRefs.current.filter(Boolean);
      const rightEls = rightRefs.current.filter(Boolean);

      if (reduced) {
        gsap.set([...leftEls, ...rightEls], { opacity: 1, x: 0, y: 0 });
        return;
      }

      gsap.set(leftEls, { opacity: 0, x: -90 });
      gsap.set(rightEls, { opacity: 0, y: 48 });

      ScrollTrigger.batch(leftEls, {
        start: "top 88%",
        onEnter: (batch) => {
          gsap.to(batch, {
            opacity: 1,
            x: 0,
            duration: 0.85,
            stagger: 0.14,
            ease: "power3.out",
          });
        },
      });

      ScrollTrigger.batch(rightEls, {
        start: "top 90%",
        onEnter: (batch) => {
          gsap.to(batch, {
            opacity: 1,
            y: 0,
            duration: 0.7,
            stagger: 0.09,
            ease: "power2.out",
          });
        },
      });
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      data-section="manifesto"
      data-nav-theme="light"
      className="relative overflow-hidden bg-brand-light pt-20 pb-6 md:pt-24 md:pb-8"
    >
      <Annotation
        text="//HAGIOS"
        className="right-8 top-24 text-brand-black/60 md:right-16"
      />
      <Annotation
        text="[*]"
        className="bottom-32 left-10 text-brand-black/50"
      />
      <ParallaxRise
        triggerRef={sectionRef}
        strength={100}
        scrub={0.72}
        className="container-fluid px-3 md:px-6"
      >
        <div className="row g-5 align-items-start">
          <div className="col-lg-7">
            <div className="space-y-2 md:space-y-4">
              {leftLines.map((line, i) => (
                <p
                  key={line}
                  ref={(el) => {
                    leftRefs.current[i] = el;
                  }}
                  className="font-fjalla text-[clamp(2.5rem,8vw,7rem)] leading-[0.95] text-brand-black"
                  style={{
                    paddingLeft: i === 1 ? "0.15em" : i === 3 ? "2rem" : 0,
                    transform: i === 2 ? "translateX(8%)" : undefined,
                  }}
                >
                  {line}
                </p>
              ))}
            </div>
          </div>
          <div className="col-lg-5">
            <div className="space-y-6 pt-4 md:pt-12">
              {rightCopy.map((text, i) => (
                <p
                  key={text}
                  ref={(el) => {
                    rightRefs.current[i] = el;
                  }}
                  className="font-mono text-sm leading-relaxed text-brand-black/90 md:text-[14px]"
                  style={{ textAlign: "justify" }}
                >
                  {text}
                </p>
              ))}
            </div>
          </div>
        </div>
      </ParallaxRise>
    </section>
  );
}
