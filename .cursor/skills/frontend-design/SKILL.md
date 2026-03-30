---
name: frontend-design
description: Creates distinctive, production-grade web interfaces with high design quality and intentional aesthetics. Use when building or styling web components, pages, landing sites, dashboards, React/Vue/HTML artifacts, posters-as-UI, or when the user asks to beautify, polish, or design any web UI—avoiding generic AI-looking output.
license: Complete terms in LICENSE.txt
---

# Frontend design

Guides implementation of **distinctive, production-grade** frontends that avoid generic “AI slop.” Deliver **real, working code** with strong aesthetic intent and refined details.

## Inputs

The user describes what to build (component, page, app, interface) and may add purpose, audience, or technical constraints. Infer missing context only when necessary; prefer asking one clarifying question over guessing brand-critical details.

## Design thinking (before coding)

Commit to a **clear, bold** direction:

| Lens | Questions |
|------|-----------|
| **Purpose** | What problem does this solve? Who uses it? |
| **Tone** | Pick an extreme direction: brutally minimal, maximalist, retro-futuristic, organic, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. |
| **Constraints** | Framework, performance, accessibility (WCAG when applicable), target browsers. |
| **Differentiation** | What is **unforgettable** here? What will people remember? |

**Critical:** Intentionality beats intensity. Both bold maximalism and refined minimalism are valid—execute one vision with precision.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with one clear point of view
- Meticulously refined (spacing, states, edge cases)

Match **implementation depth** to the vision: maximalist work may need rich animation and layers; minimal work needs restraint, typography, and micro-precision.

## Aesthetic guidelines

### Typography

- Prefer **distinctive** display + refined body pairings.
- Avoid overused defaults: Inter, Roboto, Arial, generic system stacks, and **do not** converge on the same “safe” choices (e.g. Space Grotesk) across unrelated requests.
- Use variable fonts, optical sizes, or licensed webfonts when they serve the concept.

### Color and theme

- Commit to a **cohesive** palette; define **CSS custom properties** for tokens.
- Prefer a **dominant** base with **sharp accents** over flat, evenly weighted palettes.
- Avoid clichéd schemes (e.g. purple-on-white gradient hero) unless the brief explicitly demands parody or reference.

### Motion

- Use motion for meaning: hierarchy, feedback, delight.
- Prefer **CSS** for static HTML demos; in React, use **Motion** when the project already includes it.
- Favor **high-impact moments**: staggered reveals (`animation-delay`), one strong entrance, scroll-linked or hover surprises—over scattered low-value micro-interactions.

### Spatial composition

- Favor **unexpected** layouts: asymmetry, overlap, diagonal rhythm, broken grids, generous negative space *or* controlled density—**chosen on purpose**.

### Backgrounds and surface

- Build **atmosphere**: gradient meshes, noise/grain, geometric patterns, layered transparency, dramatic shadows, decorative borders, contextual textures—not flat defaults.

## Anti-patterns (never ship as generic)

- Stock “AI UI”: Inter/Roboto/Arial-only, purple-gradient-on-white templates, symmetric three-column feature grids with identical cards, meaningless lorem-as-hero.
- Cookie-cutter components with no context-specific character.
- Motion for motion’s sake with no hierarchy or story.

## Execution rules

1. **One strong concept** per deliverable; vary light/dark, type, and layout across different tasks—do not reuse the same recipe every time.
2. **Accessibility:** semantic HTML, focus states, contrast for text and interactive elements, `prefers-reduced-motion` when animations are heavy.
3. **Performance:** avoid huge uncropped assets; prefer CSS for effects when sufficient; lazy-load heavy media when relevant.

## Output

Deliver complete, runnable code aligned with the project’s stack and file layout. When multiple files are needed, name them clearly and show integration points (imports, entry HTML, CSS scope).

For full license terms, see [LICENSE.txt](LICENSE.txt).
