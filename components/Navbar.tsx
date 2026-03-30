"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/cn";

type NavTheme = "light" | "dark";

export function Navbar() {
  const [theme, setTheme] = useState<NavTheme>("dark");

  useEffect(() => {
    const update = (): void => {
      const triggerY = 100;
      const sections = document.querySelectorAll<HTMLElement>("[data-nav-theme]");
      let active: NavTheme = "light";
      sections.forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.top <= triggerY && r.bottom > triggerY) {
          const t = el.dataset.navTheme;
          if (t === "dark" || t === "light") active = t;
        }
      });
      setTheme(active);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 z-[10000] w-full transition-colors duration-300",
        theme === "dark" ? "text-white" : "text-brand-black",
      )}
    >
      <div className="container-fluid flex items-center justify-between px-3 py-4 md:px-6">
        <Link
          href="#"
          className={cn(
            "inline-flex items-center",
            theme === "dark"
              ? "[&_img]:drop-shadow-[0_1px_3px_rgba(0,0,0,0.35)]"
              : "",
          )}
          aria-label="AVIVA BC — início"
        >
          <Image
            src="/images/avaiva.png"
            alt=""
            width={1000}
            height={1000}
            priority
            className={cn(
              "h-6 w-auto md:h-7",
              theme === "light" ? "brightness-0" : "",
            )}
          />
        </Link>
        <a
          href="#"
          className="border-2 border-brand-orange bg-brand-black px-5 py-2 font-mono text-[11px] font-bold uppercase tracking-[0.25em] text-brand-orange"
        >
          MENU
        </a>
      </div>
    </header>
  );
}
