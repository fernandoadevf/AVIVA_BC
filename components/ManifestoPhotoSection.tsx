"use client";

import { useRef } from "react";
import { ParallaxBackground } from "@/components/ParallaxBackground";

/**
 * Faixa abaixo do manifesto — imagem inteira (object-contain) + parallax.
 * Usa <img> para evitar wrapper/layout do next/image quebrando o fluxo.
 */
export function ManifestoPhotoSection() {
  const sectionRef = useRef<HTMLElement>(null);

  return (
    <section
      ref={sectionRef}
      data-section="foto-manifesto"
      data-nav-theme="light"
      className="relative z-0 -mt-6 w-full overflow-hidden bg-brand-light md:-mt-10"
    >
      <div className="relative w-full max-w-[100vw]">
        <ParallaxBackground
          triggerRef={sectionRef}
          strength={36}
          scrub={0.9}
          className="relative block w-full max-w-full"
        >
          {/* eslint-disable-next-line @next/next/no-img-element -- controle total de proporção sem wrapper do optimizer */}
          <img
            src="/images/foto1.png"
            alt="Jovens em adoração no AVIVA BC — Balneário Camboriú"
            width={1920}
            height={1080}
            decoding="async"
            className="mx-auto block h-auto w-full max-w-full object-contain object-center"
          />
        </ParallaxBackground>

        <div
          className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-b from-transparent via-transparent to-brand-dark/35"
          aria-hidden
        />

        <div
          className="pointer-events-none absolute inset-0 z-[2] bg-[url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27300%27 height=%27300%27%3E%3Cfilter id=%27n%27%3E%3CfeTurbulence type=%27fractalNoise%27 baseFrequency=%270.85%27 numOctaves=%274%27 stitchTiles=%27stitch%27/%3E%3C/filter%3E%3Crect width=%27100%25%27 height=%27100%25%27 filter=%27url(%23n)%27/%3E%3C/svg%3E')] opacity-[0.06]"
          aria-hidden
        />
      </div>
    </section>
  );
}
