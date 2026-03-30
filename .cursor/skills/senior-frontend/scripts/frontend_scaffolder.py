#!/usr/bin/env python3
"""
Frontend Scaffolder — Scaffolds new frontend projects with opinionated
defaults for Next.js, React+Vite, and React Native.
"""

import argparse
import json
import os
import sys
from pathlib import Path

TEMPLATES = {
    'nextjs': {
        'description': 'Next.js 14+ App Router with TypeScript and Tailwind CSS',
        'dependencies': {
            'next': 'latest',
            'react': '^18',
            'react-dom': '^18',
            'tailwindcss': '^3',
            'autoprefixer': '^10',
            'postcss': '^8',
            'clsx': '^2',
            'tailwind-merge': '^2',
            'class-variance-authority': '^0.7',
        },
        'dev_dependencies': {
            'typescript': '^5',
            '@types/react': '^18',
            '@types/react-dom': '^18',
            '@types/node': '^20',
            'eslint': '^8',
            'eslint-config-next': 'latest',
            'prettier': '^3',
            'prettier-plugin-tailwindcss': '^0.5',
        },
    },
    'react-vite': {
        'description': 'React + Vite with TypeScript and Tailwind CSS',
        'dependencies': {
            'react': '^18',
            'react-dom': '^18',
            'react-router-dom': '^6',
            'tailwindcss': '^3',
            'autoprefixer': '^10',
            'postcss': '^8',
            'clsx': '^2',
            'tailwind-merge': '^2',
        },
        'dev_dependencies': {
            'typescript': '^5',
            '@types/react': '^18',
            '@types/react-dom': '^18',
            'vite': '^5',
            '@vitejs/plugin-react': '^4',
            'eslint': '^8',
            'prettier': '^3',
            'prettier-plugin-tailwindcss': '^0.5',
        },
    },
    'react-native': {
        'description': 'React Native with Expo, TypeScript, and NativeWind',
        'dependencies': {
            'expo': '~50',
            'react': '^18',
            'react-native': '^0.73',
            'nativewind': '^4',
            'expo-router': '~3',
            'react-native-safe-area-context': '^4',
            'react-native-screens': '~3',
        },
        'dev_dependencies': {
            'typescript': '^5',
            '@types/react': '^18',
            'tailwindcss': '^3',
        },
    },
}

FEATURE_MODULES = {
    'auth': {
        'deps': {'next-auth': '^4', 'bcryptjs': '^2', '@auth/prisma-adapter': '^1'},
        'dev_deps': {'@types/bcryptjs': '^2'},
        'files': {
            'src/lib/auth.ts': '''\
import NextAuth from 'next-auth';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [],
  // Configure providers and callbacks
});
''',
            'src/app/api/auth/[...nextauth]/route.ts': '''\
import { handlers } from '@/lib/auth';

export const { GET, POST } = handlers;
''',
        },
    },
    'database': {
        'deps': {'@prisma/client': '^5'},
        'dev_deps': {'prisma': '^5'},
        'files': {
            'prisma/schema.prisma': '''\
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
''',
            'src/lib/db.ts': '''\
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const db = globalForPrisma.prisma || new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db;
''',
        },
    },
    'testing': {
        'deps': {},
        'dev_deps': {
            'vitest': '^1',
            '@testing-library/react': '^14',
            '@testing-library/user-event': '^14',
            '@testing-library/jest-dom': '^6',
            '@vitejs/plugin-react': '^4',
            'jsdom': '^24',
            'playwright': '^1',
            '@playwright/test': '^1',
        },
        'files': {
            'vitest.config.ts': '''\
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
''',
            'src/test/setup.ts': '''\
import '@testing-library/jest-dom/vitest';
''',
            'playwright.config.ts': '''\
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
''',
        },
    },
    'ci': {
        'deps': {},
        'dev_deps': {},
        'files': {
            '.github/workflows/ci.yml': '''\
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test -- --run
      - run: npm run build
''',
        },
    },
    'docker': {
        'deps': {},
        'dev_deps': {},
        'files': {
            'Dockerfile': '''\
FROM node:20-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
''',
            'docker-compose.yml': '''\
version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    env_file:
      - .env.local
    depends_on:
      - db
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
''',
            '.dockerignore': '''\
node_modules
.next
.git
.env*.local
*.md
''',
        },
    },
}


def create_base_files(project_path: Path, template_name: str, project_name: str):
    """Create base project files common to all templates."""

    (project_path / 'src' / 'app').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'components' / 'ui').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'components' / 'features').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'hooks').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'lib').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'stores').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'types').mkdir(parents=True, exist_ok=True)
    (project_path / 'src' / 'styles').mkdir(parents=True, exist_ok=True)
    (project_path / 'public').mkdir(parents=True, exist_ok=True)

    template = TEMPLATES[template_name]
    pkg = {
        'name': project_name,
        'version': '0.1.0',
        'private': True,
        'scripts': {
            'dev': 'next dev' if template_name == 'nextjs' else 'vite',
            'build': 'next build' if template_name == 'nextjs' else 'tsc && vite build',
            'start': 'next start' if template_name == 'nextjs' else 'vite preview',
            'lint': 'next lint' if template_name == 'nextjs' else 'eslint src/',
            'typecheck': 'tsc --noEmit',
            'format': 'prettier --write "src/**/*.{ts,tsx,css}"',
        },
        'dependencies': template['dependencies'],
        'devDependencies': template['dev_dependencies'],
    }
    (project_path / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n')

    tsconfig = {
        'compilerOptions': {
            'target': 'ES2022',
            'lib': ['dom', 'dom.iterable', 'esnext'],
            'allowJs': True,
            'skipLibCheck': True,
            'strict': True,
            'noEmit': True,
            'esModuleInterop': True,
            'module': 'esnext',
            'moduleResolution': 'bundler',
            'resolveJsonModule': True,
            'isolatedModules': True,
            'jsx': 'preserve',
            'incremental': True,
            'noUncheckedIndexedAccess': True,
            'plugins': [{'name': 'next'}] if template_name == 'nextjs' else [],
            'paths': {'@/*': ['./src/*']},
        },
        'include': ['next-env.d.ts', '**/*.ts', '**/*.tsx', '.next/types/**/*.ts'] if template_name == 'nextjs' else ['src'],
        'exclude': ['node_modules'],
    }
    (project_path / 'tsconfig.json').write_text(json.dumps(tsconfig, indent=2) + '\n')

    tailwind_config = '''\
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
};

export default config;
'''
    (project_path / 'tailwind.config.ts').write_text(tailwind_config)

    postcss_config = '''\
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
'''
    (project_path / 'postcss.config.js').write_text(postcss_config)

    globals_css = '''\
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
'''
    (project_path / 'src' / 'styles' / 'globals.css').write_text(globals_css)

    cn_util = '''\
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
'''
    (project_path / 'src' / 'lib' / 'utils.ts').write_text(cn_util)

    if template_name == 'nextjs':
        layout = '''\
import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: '%s',
  description: 'Built with Next.js, TypeScript, and Tailwind CSS',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
''' % project_name
        (project_path / 'src' / 'app' / 'layout.tsx').write_text(layout)

        page = '''\
export default function HomePage() {
  return (
    <main className="container mx-auto flex min-h-screen flex-col items-center justify-center gap-6 px-4 py-16">
      <h1 className="text-4xl font-bold tracking-tight">%s</h1>
      <p className="text-lg text-muted-foreground">Ready to build something great.</p>
    </main>
  );
}
''' % project_name
        (project_path / 'src' / 'app' / 'page.tsx').write_text(page)

    gitignore = '''\
node_modules/
.next/
out/
dist/
build/
.env*.local
.env
*.tsbuildinfo
next-env.d.ts
.vercel
.DS_Store
coverage/
'''
    (project_path / '.gitignore').write_text(gitignore)

    env_example = '''\
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/app"

# Auth
NEXTAUTH_SECRET=""
NEXTAUTH_URL="http://localhost:3000"

# Add your environment variables here
'''
    (project_path / '.env.example').write_text(env_example)

    prettierrc = json.dumps({
        'semi': True,
        'singleQuote': True,
        'trailingComma': 'all',
        'tabWidth': 2,
        'printWidth': 100,
        'plugins': ['prettier-plugin-tailwindcss'],
    }, indent=2)
    (project_path / '.prettierrc').write_text(prettierrc + '\n')

    eslintrc = json.dumps({
        'extends': ['next/core-web-vitals'] if template_name == 'nextjs' else ['eslint:recommended'],
        'rules': {
            'no-unused-vars': 'off',
            '@typescript-eslint/no-unused-vars': ['warn', {'argsIgnorePattern': '^_'}],
        },
    }, indent=2)
    (project_path / '.eslintrc.json').write_text(eslintrc + '\n')


def add_features(project_path: Path, features: list[str], template_name: str):
    """Add optional feature modules to the project."""
    pkg_path = project_path / 'package.json'
    with open(pkg_path) as f:
        pkg = json.load(f)

    for feature in features:
        if feature not in FEATURE_MODULES:
            print(f"  ⚠ Unknown feature: {feature} (skipping)")
            continue

        module = FEATURE_MODULES[feature]
        print(f"  Adding feature: {feature}")

        pkg['dependencies'].update(module.get('deps', {}))
        pkg['devDependencies'].update(module.get('dev_deps', {}))

        for file_path, content in module.get('files', {}).items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"    Created: {file_path}")

    (project_path / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Scaffold a new frontend project with opinionated defaults'
    )
    parser.add_argument('--template', '-t', choices=list(TEMPLATES.keys()),
                        default='nextjs', help='Project template')
    parser.add_argument('--name', '-n', default=None, help='Project name')
    parser.add_argument('--path', '-p', default='.', help='Parent directory')
    parser.add_argument('--features', '-f', default='',
                        help='Comma-separated features: auth,database,testing,ci,docker')
    parser.add_argument('--list-templates', action='store_true',
                        help='List available templates')
    parser.add_argument('--list-features', action='store_true',
                        help='List available features')

    args = parser.parse_args()

    if args.list_templates:
        print("\nAvailable templates:\n")
        for name, info in TEMPLATES.items():
            print(f"  {name}: {info['description']}")
        print()
        return

    if args.list_features:
        print("\nAvailable features:\n")
        for name in FEATURE_MODULES:
            print(f"  {name}")
        print()
        return

    if not args.name:
        parser.error("--name/-n is required when scaffolding a project")

    project_path = Path(args.path).resolve() / args.name
    template = TEMPLATES[args.template]

    print(f"\n{'='*60}")
    print(f"  Scaffolding: {args.name}")
    print(f"  Template: {args.template} — {template['description']}")
    print(f"  Path: {project_path}")
    print(f"{'='*60}\n")

    if project_path.exists() and any(project_path.iterdir()):
        print(f"Error: Directory '{project_path}' already exists and is not empty", file=sys.stderr)
        sys.exit(1)

    project_path.mkdir(parents=True, exist_ok=True)

    print("  Creating base project structure...")
    create_base_files(project_path, args.template, args.name)

    features = [f.strip() for f in args.features.split(',') if f.strip()]
    if features:
        print(f"\n  Adding features: {', '.join(features)}")
        add_features(project_path, features, args.template)

    print(f"\n{'='*60}")
    print(f"  Project '{args.name}' created successfully!")
    print(f"{'='*60}")
    print(f"\n  Next steps:\n")
    print(f"    cd {args.name}")
    print(f"    npm install")
    print(f"    cp .env.example .env.local")
    print(f"    npm run dev\n")


if __name__ == '__main__':
    main()
