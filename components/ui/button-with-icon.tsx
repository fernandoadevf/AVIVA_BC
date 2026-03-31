"use client";

import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ArrowUpRight } from "lucide-react";

export type WhatsAppCtaButtonProps = {
  href: string;
  id?: string;
  className?: string;
  children?: ReactNode;
};

/**
 * CTA estilo “pill” com ícone que desliza no hover (hero AVIVA).
 * Cores alinhadas ao wireframe: creme + laranja marca.
 */
export function WhatsAppCtaButton({
  href,
  id,
  className,
  children = "ENTRAR NO GRUPO DO WHATSAPP",
}: WhatsAppCtaButtonProps) {
  return (
    <Button
      asChild
      variant="outline"
      className={cn(
        "group relative h-12 w-fit min-w-[min(100%,288px)] !justify-start overflow-hidden rounded-full border-2 border-brand-orange bg-brand-cream p-1 ps-7 pe-[5.25rem] font-fjalla text-xs uppercase tracking-wide text-brand-orange shadow-none transition-all duration-500 hover:bg-brand-cream hover:ps-14 hover:pe-9 hover:text-brand-orange md:min-w-[300px] md:ps-8 md:pe-[5.5rem] md:text-sm",
        className,
      )}
    >
      <a
        id={id}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="relative inline-flex items-center justify-start"
      >
        <span className="relative z-10 ml-11 text-left transition-all duration-500 md:ml-12">
          {children}
        </span>
        <div className="absolute right-1 flex h-10 w-10 items-center justify-center rounded-full bg-brand-orange text-black transition-all duration-500 group-hover:right-[calc(100%-44px)] group-hover:rotate-45">
          <ArrowUpRight size={16} aria-hidden />
        </div>
      </a>
    </Button>
  );
}

/** Variante demo genérica (texto placeholder). */
export function ButtonWithIconDemo() {
  return (
    <Button className="group relative h-12 w-fit cursor-pointer overflow-hidden rounded-full p-1 ps-6 pe-14 text-sm font-medium transition-all duration-500 hover:ps-14 hover:pe-6">
      <span className="relative z-10 transition-all duration-500">
        Let&apos;s Collaborate
      </span>
      <div className="absolute right-1 flex h-10 w-10 items-center justify-center rounded-full bg-background text-foreground transition-all duration-500 group-hover:right-[calc(100%-44px)] group-hover:rotate-45">
        <ArrowUpRight size={16} aria-hidden />
      </div>
    </Button>
  );
}
