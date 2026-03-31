"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
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

type YTPlayerInstance = {
  mute: () => void;
  unMute: () => void;
  destroy: () => void;
};

const YT_VIDEO_ID = "8UQdcV-GkEw";

export function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const ytPlayerRef = useRef<YTPlayerInstance | null>(null);
  const [videoMuted, setVideoMuted] = useState(true);

  const toggleVideoMute = useCallback(() => {
    const p = ytPlayerRef.current;
    if (!p) return;
    if (videoMuted) {
      p.unMute();
      setVideoMuted(false);
    } else {
      p.mute();
      setVideoMuted(true);
    }
  }, [videoMuted]);

  useEffect(() => {
    let cancelled = false;

    const initPlayer = () => {
      if (cancelled) return;
      const w = window as unknown as {
        YT?: {
          Player: new (
            id: string,
            opts: {
              width: string;
              height: string;
              videoId: string;
              playerVars: Record<string, number | string>;
            },
          ) => YTPlayerInstance;
        };
      };
      if (!w.YT?.Player) return;

      const player = new w.YT.Player("cta-youtube-player", {
        width: "100%",
        height: "100%",
        videoId: YT_VIDEO_ID,
        playerVars: {
          autoplay: 1,
          mute: 1,
          loop: 1,
          playlist: YT_VIDEO_ID,
          controls: 0,
          modestbranding: 1,
          playsinline: 1,
          rel: 0,
        },
      });
      ytPlayerRef.current = player;
    };

    const win = window as unknown as {
      YT?: { Player: new (id: string, opts: object) => YTPlayerInstance };
      onYouTubeIframeAPIReady?: () => void;
    };

    if (win.YT?.Player) {
      initPlayer();
    } else {
      const previous = win.onYouTubeIframeAPIReady;
      win.onYouTubeIframeAPIReady = () => {
        previous?.();
        initPlayer();
      };
      if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        tag.async = true;
        document.body.appendChild(tag);
      }
    }

    return () => {
      cancelled = true;
      ytPlayerRef.current?.destroy();
      ytPlayerRef.current = null;
    };
  }, []);
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

      {/* iPhone 16 Mockup */}
      <div
        className="pointer-events-none absolute right-[8vw] top-1/2 z-[2] hidden -translate-y-1/2 md:block"
        style={{ width: "clamp(280px, 30vw, 400px)" }}
      >
        {/* aspect-ratio exato do PNG: 364×750 */}
        <div
          className="relative isolate w-full pointer-events-auto"
          style={{ aspectRatio: "364 / 750" }}
        >
          {/* Vídeo recortado por baixo; fundo preto evita halo nas bordas */}
          <div
            className="absolute z-0 overflow-hidden bg-black"
            style={{
              top: "1.8%",
              left: "2.4%",
              width: "95%",
              height: "96.5%",
              borderRadius: "9%",
              transform: "translateZ(0)",
              contain: "paint",
            }}
          >
            <div
              id="cta-youtube-player"
              className="absolute inset-0 h-full w-full overflow-hidden rounded-[inherit]"
            />
            <button
              type="button"
              className="absolute inset-0 z-[5] cursor-pointer border-0 bg-transparent p-0"
              aria-label={
                videoMuted
                  ? "Ativar som do vídeo"
                  : "Silenciar vídeo"
              }
              aria-pressed={!videoMuted}
              onClick={toggleVideoMute}
            />
          </div>

          {/* Mockup por cima do iframe (camada própria para não vazar borda do vídeo) */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/images/iphone16.png"
            alt=""
            className="pointer-events-none absolute inset-0 z-[30] h-full w-full"
            style={{
              mixBlendMode: "multiply",
              objectFit: "fill",
              transform: "translateZ(1px)",
              WebkitTransform: "translateZ(1px)",
            }}
          />
        </div>
      </div>

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
          <div className="flex flex-wrap items-end gap-4">
            <span className="cta-word font-fjalla text-[clamp(2.8rem,10vw,7rem)] leading-[0.95] text-brand-black">
              FORA
            </span>
          </div>
        </div>

        <Link
          id="whatsapp-btn"
          href="#"
          target="_blank"
          rel="noopener noreferrer"
          className="group mt-8 flex w-full max-w-lg items-center gap-3 border-2 border-brand-black px-4 py-3 font-fjalla text-[11px] uppercase leading-snug tracking-[0.22em] text-brand-black transition-[background-color,color,box-shadow] duration-300 hover:bg-brand-black hover:text-brand-cream focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-black focus-visible:ring-offset-2 focus-visible:ring-offset-brand-orange sm:gap-4 sm:px-5 sm:py-3.5 sm:text-xs md:mt-6 md:text-[13px]"
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
