<!-- AVIVA BC — landing institucional -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a1a,100:ff5500&height=140&section=header&text=AVIVA%20BC&fontSize=52&fontColor=f5f5f5&fontAlignY=35&desc=Movimento%20de%20adora%C3%A7%C3%A3o%20ao%20alvorecer&descAlignY=58&descSize=16&descAlign=50&animation=twinkling" alt="AVIVA BC — capa do repositório" width="100%" />

<br />

### Movimento de adoração ao alvorecer

**Balneário Camboriú** · Praia Barra Norte · encontros ao nascer do sol

<br />

[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-11-0055FF?style=for-the-badge&logo=framer&logoColor=white)](https://www.framer.com/motion/)
[![GSAP](https://img.shields.io/badge/GSAP-ScrollTrigger-88CE02?style=for-the-badge&logo=greensock&logoColor=white)](https://gsap.com/)

<br />

![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)

</div>

---

<br />

<table>
<tr>
<td width="50%" valign="top">

### Porque existe

Site institucional do **AVIVA BC**: um movimento cristão de jovens que se reúne **às 5h da manhã** para adorar na praia — experiência de fé, comunidade e presença, com identidade visual editorial (tipografia forte, laranja `#ff5500`, contraste claro/escuro).

</td>
<td width="50%" valign="top">

### O que tens aqui

Landing **one-page** com hero em vídeo, manifesto, FAQ, CTA para WhatsApp, mapa do local e microinterações (**Framer Motion**, **GSAP ScrollTrigger**, parallax). Pensado para carregar rápido e funcionar bem em mobile.

</td>
</tr>
</table>

<br />

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Framework | [Next.js](https://nextjs.org/) 14 (App Router) |
| UI | [React](https://react.dev/) 18 · [Tailwind CSS](https://tailwindcss.com/) · [Bootstrap](https://getbootstrap.com/) (grid/utilidades) |
| Motion | [Framer Motion](https://www.framer.com/motion/) · [GSAP](https://gsap.com/) + ScrollTrigger |
| Fontes | [next/font](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) (Fjalla One, Space Mono, Instrument Serif) |
| Ícones | [Lucide](https://lucide.dev/) |

---

## Scripts

```bash
npm install          # dependências
npm run dev          # dev com Turbopack
npm run build        # build de produção
npm start            # servidor após build
npm run lint         # ESLint
```

---

## Estrutura (resumo)

```
app/
  layout.tsx          # fontes globais + AppWrapper (loading)
  page.tsx            # landing (Navbar → Footer)
components/
  HeroSection, ManifestoSection, FAQSection, CTASection, …
  AppWrapper.tsx      # loading inicial + sincronização GSAP
public/
  images/             # assets otimizados para a UI
```

---

## Ambiente

- Node.js **18+** recomendado  
- Variáveis sensíveis: criar `.env.local` se no futuro houver API keys (não commitar)

---

<div align="center">

<br />

**AVIVA BC** · *Deus está despertando uma geração.*

<br />

<sub>Landing open-source do movimento · design e código para servir a mensagem, não o contrário.</sub>

</div>
