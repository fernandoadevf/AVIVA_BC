"use client";

import { useRef } from "react";
import { ParallaxRise } from "@/components/ParallaxRise";

export function Footer() {
  const sectionRef = useRef<HTMLElement>(null);

  return (
    <footer
      ref={sectionRef}
      data-section="footer"
      data-nav-theme="dark"
      className="overflow-hidden border-t border-[#222] bg-brand-dark px-3 py-12 md:px-8"
    >
      <ParallaxRise
        triggerRef={sectionRef}
        strength={56}
        scrub={0.85}
        className="container-fluid"
      >
        <div className="row align-items-center gy-8">
          <div className="col-md-4 text-center text-md-start">
            <p className="font-fjalla text-3xl text-brand-cream md:text-4xl">
              [AVIVA BC]
            </p>
          </div>
          <div className="col-md-4 text-center">
            <p className="font-mono text-xs text-white/45">
              Balneário Camboriú — SC — 2026
            </p>
          </div>
          <div className="col-md-4 text-center text-md-end">
            <div className="inline-flex items-center gap-6">
              <a
                href="#"
                aria-label="Instagram"
                className="text-brand-cream transition-opacity hover:opacity-80"
              >
                <svg
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden
                >
                  <path
                    d="M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="3.25"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <circle cx="17" cy="7" r="1.2" fill="currentColor" />
                </svg>
              </a>
              <a
                href="#"
                aria-label="WhatsApp"
                className="text-brand-cream transition-opacity hover:opacity-80"
              >
                <svg
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden
                >
                  <path
                    d="M12 3a8.5 8.5 0 00-7.3 13L4 21l5.2-1.4A8.5 8.5 0 1012 3z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M8.7 9.8c.2-.6 1-.9 1.6-.7.5.2 1.1.9 1.3 1.4.3.7.3 1.3-.1 1.8-.3.4-.3.4-.1.9.2.4 1 1.7 2 2.4 1 .8 1.4.9 1.9.9.4 0 1.1-.5 1.3-.9.2-.5.2-.6.5-.5.3 0 1.9.9 2.2 1.1.3.2.5.3.6.6.1.3 0 1.7-.8 3.3-.8 1.6-2.9 1.7-4 1.4-1.2-.3-4-1.6-6.3-3.9C8 14.1 6.4 11.4 6 10.3c-.4-1.1-.9-2.6.1-3.7.4-.5.6-.8.6-.8z"
                    fill="currentColor"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
        <p className="mt-10 text-center font-mono text-[10px] text-white/35">
          {"// Um movimento. Uma geração. Uma praia."}
        </p>
      </ParallaxRise>
    </footer>
  );
}
