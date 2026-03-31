import type { Metadata } from "next";
import { Fjalla_One, Instrument_Serif, Space_Mono } from "next/font/google";
import { AppWrapper } from "@/components/AppWrapper";
import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";

const fjallaOne = Fjalla_One({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-fjalla-one",
  display: "swap",
});

const spaceMono = Space_Mono({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-space-mono",
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-instrument-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AVIVA BC — Movimento de adoração ao alvorecer",
  description:
    "Movimento cristão de jovens em Balneário Camboriú. Adoração às 5h na Praia Barra Norte.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${fjallaOne.variable} ${spaceMono.variable} ${instrumentSerif.variable}`}
    >
      <body className="grain min-h-screen">
        <AppWrapper>{children}</AppWrapper>
      </body>
    </html>
  );
}
