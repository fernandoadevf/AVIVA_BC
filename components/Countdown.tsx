"use client";

import { useEffect, useMemo, useState } from "react";
import { AVIVA_EVENT_ISO } from "@/lib/aviva-event";

export type CountdownProps = {
  /** ISO 8601 com offset (ex.: BRT). Padrão: próximo evento AVIVA BC. */
  targetDate?: string;
};

type Parts = {
  days: number;
  hours: number;
  minutes: number;
};

function parseTarget(iso: string): Date {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) {
    return new Date(AVIVA_EVENT_ISO);
  }
  return d;
}

/** Tempo restante até o instante alvo (mesmo relógio que `Date.now()` — contagem real). */
function remainingParts(target: Date): Parts | null {
  const ms = target.getTime() - Date.now();
  if (ms <= 0) return null;

  const totalMinutes = Math.floor(ms / 60_000);
  const totalHours = Math.floor(ms / 3_600_000);
  const days = Math.floor(ms / 86_400_000);
  const hours = totalHours - days * 24;
  const minutes = totalMinutes - days * 24 * 60 - hours * 60;

  return { days, hours, minutes };
}

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export function Countdown({ targetDate = AVIVA_EVENT_ISO }: CountdownProps) {
  const target = useMemo(() => parseTarget(targetDate), [targetDate]);
  const [parts, setParts] = useState<Parts | null>(() =>
    remainingParts(target),
  );

  useEffect(() => {
    const tick = (): void => {
      setParts(remainingParts(target));
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [target]);

  if (parts === null) {
    return (
      <p className="max-w-xs font-mono text-[10px] uppercase leading-snug tracking-[0.2em] text-brand-cream/75">
        {"// O AVIVA JÁ COMEÇOU"}
      </p>
    );
  }

  const units = [
    { value: String(parts.days), label: "dias" },
    { value: pad2(parts.hours), label: "h" },
    { value: pad2(parts.minutes), label: "min" },
  ] as const;

  return (
    <div
      className="inline-flex items-stretch gap-0 border border-brand-orange/35 bg-black/25 px-2.5 py-1.5 md:px-3 md:py-2"
      role="timer"
      aria-live="polite"
      aria-label={`Faltam ${parts.days} dias, ${parts.hours} horas e ${parts.minutes} minutos até o evento`}
    >
      {units.map((u, i) => (
        <div key={u.label} className="flex items-stretch">
          {i > 0 ? (
            <span
              className="mx-1.5 self-center font-mono text-[10px] text-brand-orange/45 md:mx-2"
              aria-hidden
            >
              :
            </span>
          ) : null}
          <div className="flex min-w-[2.25rem] flex-col items-center justify-center gap-0.5 md:min-w-[2.5rem]">
            <span className="font-mono text-sm tabular-nums leading-none text-brand-cream md:text-base">
              {u.value}
            </span>
            <span className="font-mono text-[7px] uppercase tracking-[0.12em] text-brand-cream/45 md:text-[8px]">
              {u.label}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
