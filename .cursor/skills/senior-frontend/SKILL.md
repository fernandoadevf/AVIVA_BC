---
name: senior-frontend
description: Comprehensive frontend development skill for building modern, performant web applications using ReactJS, NextJS, TypeScript, Tailwind CSS. Includes component scaffolding, performance optimization, bundle analysis, and UI best practices. Use when developing frontend features, optimizing performance, implementing UI/UX designs, managing state, or reviewing frontend code.
---

# Senior Frontend

Complete toolkit for senior-level frontend development with modern tools and best practices.

## Quick Start

### Automated Scripts

```bash
# Generate React/Next.js components with TypeScript + Tailwind
python ~/.cursor/skills/senior-frontend/scripts/component_generator.py --name Button --type component --path src/components

# Analyze bundle size and get optimization recommendations
python ~/.cursor/skills/senior-frontend/scripts/bundle_analyzer.py <project-path> [--verbose]

# Scaffold a new frontend project (Next.js, React, etc.)
python ~/.cursor/skills/senior-frontend/scripts/frontend_scaffolder.py --template nextjs --name my-app --path .
```

## Core Principles

### TypeScript First

- Always use strict TypeScript (`strict: true` in tsconfig)
- Prefer `interface` for object shapes, `type` for unions/intersections
- Use generics for reusable components and hooks
- Never use `any` — use `unknown` with type guards instead
- Export types alongside components

### Component Architecture

```typescript
// Preferred component pattern
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', size = 'md', isLoading, children, onClick }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), isLoading && 'opacity-50 cursor-wait')}
      onClick={onClick}
      disabled={isLoading}
    >
      {isLoading ? <Spinner size={size} /> : children}
    </button>
  );
}
```

**Rules:**
- One component per file, named export matching filename
- Props interface defined above component, exported
- Default props via destructuring defaults
- Composition over configuration — prefer `children` and slots over prop drilling
- Use `forwardRef` when wrapping native elements

### Tailwind CSS Patterns

- Use `cn()` utility (clsx + tailwind-merge) for conditional classes
- Extract repeated patterns into component variants (CVA or manual)
- Use CSS variables for theme tokens, Tailwind for utility
- Mobile-first responsive: `base → sm → md → lg → xl`
- Avoid arbitrary values `[...]` when a design token exists

```typescript
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground',
        secondary: 'bg-secondary text-secondary-foreground',
        destructive: 'bg-destructive text-destructive-foreground',
        outline: 'border border-input bg-background',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);
```

### State Management Decision Tree

| Scenario | Solution |
|----------|----------|
| Local UI state | `useState` / `useReducer` |
| Shared between siblings | Lift state to parent |
| Form state | React Hook Form + Zod |
| Server state | TanStack Query (React Query) |
| Global client state | Zustand (simple) or Jotai (atomic) |
| URL state | `nuqs` or `useSearchParams` |
| Complex global state | Redux Toolkit (only when justified) |

### Performance Checklist

Before shipping any feature:

- [ ] Images use `next/image` with proper `sizes` and `priority`
- [ ] Lists > 50 items use virtualization (TanStack Virtual)
- [ ] Heavy computations wrapped in `useMemo` (with measured need)
- [ ] Event handlers stable via `useCallback` when passed as props
- [ ] Dynamic imports for routes and heavy components
- [ ] No layout shifts (CLS) — reserve space for async content
- [ ] Bundle analyzed — no duplicate dependencies
- [ ] Lighthouse score > 90 on all metrics

### Next.js Specifics

**App Router patterns:**
- Use Server Components by default, `'use client'` only when needed
- Colocate loading.tsx, error.tsx, not-found.tsx per route segment
- Use `generateMetadata` for dynamic SEO
- Prefer Server Actions for mutations over API routes
- Use `unstable_cache` or `revalidateTag` for data caching

**Data fetching hierarchy:**
1. Server Components with `fetch` (RSC)
2. Server Actions for mutations
3. Route Handlers for external API proxying
4. TanStack Query for client-side caching of server data

### Testing Strategy

| Layer | Tool | What to Test |
|-------|------|-------------|
| Unit | Vitest | Utils, hooks, pure functions |
| Component | Testing Library | Render, interaction, accessibility |
| Integration | Playwright | User flows, critical paths |
| Visual | Chromatic/Percy | UI regression |

### Folder Structure (Next.js App Router)

```
src/
├── app/                    # Routes and layouts
│   ├── (auth)/             # Route groups
│   ├── api/                # API routes
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                 # Primitives (Button, Input, etc.)
│   └── features/           # Domain components (UserCard, etc.)
├── hooks/                  # Custom hooks
├── lib/                    # Utilities, configs, clients
├── stores/                 # State management
├── types/                  # Shared TypeScript types
└── styles/                 # Global styles
```

### Accessibility (a11y)

- Every interactive element must be keyboard accessible
- Use semantic HTML (`button`, `nav`, `main`, `article`)
- ARIA attributes only when semantic HTML isn't sufficient
- Color contrast ratio ≥ 4.5:1 (AA) for text
- Focus indicators visible on all interactive elements
- Test with screen reader (VoiceOver/NVDA)

## Scripts Reference

### Component Generator

Generates React/Next.js components with TypeScript, Tailwind, tests, and stories.

```bash
python ~/.cursor/skills/senior-frontend/scripts/component_generator.py \
  --name UserProfile \
  --type component \
  --path src/components/features \
  --with-test \
  --with-story
```

Options: `--type` (component|page|layout|hook), `--with-test`, `--with-story`, `--with-loading`, `--with-error`

### Bundle Analyzer

Analyzes project dependencies, detects issues, and suggests optimizations.

```bash
python ~/.cursor/skills/senior-frontend/scripts/bundle_analyzer.py . --verbose
```

Checks: duplicate deps, oversized packages, tree-shaking opportunities, import analysis.

### Frontend Scaffolder

Scaffolds new projects with opinionated defaults.

```bash
python ~/.cursor/skills/senior-frontend/scripts/frontend_scaffolder.py \
  --template nextjs \
  --name my-app \
  --path . \
  --features auth,database,testing
```

Templates: `nextjs`, `react-vite`, `react-native`. Features: `auth`, `database`, `testing`, `ci`, `docker`.

## Reference Documentation

- React patterns and anti-patterns: [references/react_patterns.md](references/react_patterns.md)
- Next.js optimization strategies: [references/nextjs_optimization_guide.md](references/nextjs_optimization_guide.md)
- Frontend best practices and security: [references/frontend_best_practices.md](references/frontend_best_practices.md)

## Tech Stack

**Languages:** TypeScript, JavaScript, Python, Go, Swift, Kotlin
**Frontend:** React, Next.js, React Native, Flutter
**Backend:** Node.js, Express, GraphQL, REST APIs
**Database:** PostgreSQL, Prisma, NeonDB, Supabase
**DevOps:** Docker, Kubernetes, Terraform, GitHub Actions, CircleCI
**Cloud:** AWS, GCP, Azure

## Troubleshooting

For common issues and solutions, see [references/frontend_best_practices.md](references/frontend_best_practices.md#troubleshooting).
