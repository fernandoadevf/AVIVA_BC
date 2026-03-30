# Next.js Optimization Guide

Strategies and patterns for building performant Next.js applications with the App Router.

## Server Components vs Client Components

### Decision Framework

| Need | Use |
|------|-----|
| Fetch data | Server Component |
| Access backend resources | Server Component |
| Keep secrets server-side | Server Component |
| Reduce client JS | Server Component |
| Event listeners (onClick, onChange) | Client Component |
| State and lifecycle (useState, useEffect) | Client Component |
| Browser-only APIs | Client Component |
| Custom hooks with state | Client Component |

### Composition Pattern

Push `'use client'` boundary as low as possible in the tree.

```tsx
// app/dashboard/page.tsx — Server Component (default)
import { getMetrics } from '@/lib/data';
import { InteractiveChart } from './interactive-chart';

export default async function DashboardPage() {
  const metrics = await getMetrics();

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      {/* Static cards — Server Component, zero JS */}
      {metrics.map(metric => (
        <div key={metric.id} className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">{metric.label}</p>
          <p className="text-2xl font-bold">{metric.value}</p>
        </div>
      ))}

      {/* Only this part ships JS to the client */}
      <InteractiveChart data={metrics} />
    </div>
  );
}
```

```tsx
// app/dashboard/interactive-chart.tsx
'use client';

import { useState } from 'react';

export function InteractiveChart({ data }: { data: Metric[] }) {
  const [timeRange, setTimeRange] = useState('7d');
  // Interactive logic here
}
```

## Data Fetching

### Parallel Data Fetching

**Bad — sequential (waterfall):**
```tsx
export default async function Page() {
  const user = await getUser();
  const posts = await getPosts(); // waits for user to finish
  const comments = await getComments(); // waits for posts
}
```

**Good — parallel:**
```tsx
export default async function Page() {
  const [user, posts, comments] = await Promise.all([
    getUser(),
    getPosts(),
    getComments(),
  ]);
}
```

**Best — streaming with Suspense:**
```tsx
export default async function Page() {
  const userPromise = getUser();

  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile promise={userPromise} />
      </Suspense>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList />
      </Suspense>
    </div>
  );
}
```

### Caching Strategies

```tsx
// Per-request deduplication (automatic in fetch)
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`, {
    next: { revalidate: 3600 }, // ISR: revalidate every hour
  });
  return res.json();
}

// On-demand revalidation
import { revalidateTag, revalidatePath } from 'next/cache';

async function getProduct(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { tags: [`product-${id}`] },
  });
  return res.json();
}

// In a Server Action:
async function updateProduct(id: string, data: ProductData) {
  await db.product.update({ where: { id }, data });
  revalidateTag(`product-${id}`);
}
```

### unstable_cache for Non-Fetch Data

```tsx
import { unstable_cache } from 'next/cache';

const getCachedUser = unstable_cache(
  async (id: string) => db.user.findUnique({ where: { id } }),
  ['user'],
  { revalidate: 3600, tags: ['users'] }
);
```

## Server Actions

### Pattern: Form with Validation

```tsx
// actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

export async function createPost(formData: FormData) {
  const parsed = createPostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
    published: formData.get('published') === 'on',
  });

  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors };
  }

  await db.post.create({ data: parsed.data });
  revalidatePath('/posts');
  return { success: true };
}
```

```tsx
// form.tsx
'use client';

import { useActionState } from 'react';
import { createPost } from './actions';

export function CreatePostForm() {
  const [state, formAction, isPending] = useActionState(createPost, null);

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <input name="title" placeholder="Title" className="w-full rounded border px-3 py-2" />
        {state?.error?.title && <p className="text-sm text-destructive">{state.error.title}</p>}
      </div>
      <textarea name="content" placeholder="Content" className="w-full rounded border px-3 py-2" rows={5} />
      <button type="submit" disabled={isPending} className="rounded bg-primary px-4 py-2 text-primary-foreground">
        {isPending ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  );
}
```

## Image Optimization

### next/image Best Practices

```tsx
import Image from 'next/image';

// Static import (automatically optimized at build time)
import heroImage from '@/public/hero.jpg';

function Hero() {
  return (
    <Image
      src={heroImage}
      alt="Hero banner"
      priority // above the fold — preload
      placeholder="blur" // auto blur placeholder for static imports
      className="h-[400px] w-full object-cover"
      sizes="100vw"
    />
  );
}

// Dynamic/remote images
function Avatar({ src, name }: { src: string; name: string }) {
  return (
    <Image
      src={src}
      alt={`${name}'s avatar`}
      width={48}
      height={48}
      className="rounded-full"
      sizes="48px"
    />
  );
}
```

### Configure Remote Patterns

```ts
// next.config.ts
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.amazonaws.com' },
      { protocol: 'https', hostname: 'images.unsplash.com' },
    ],
    formats: ['image/avif', 'image/webp'],
  },
};
```

## Route Optimization

### Route Groups for Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx      # Marketing layout (no sidebar)
│   ├── page.tsx        # Home
│   └── about/page.tsx
├── (dashboard)/
│   ├── layout.tsx      # Dashboard layout (with sidebar)
│   ├── overview/page.tsx
│   └── settings/page.tsx
└── (auth)/
    ├── layout.tsx      # Minimal auth layout
    ├── login/page.tsx
    └── register/page.tsx
```

### Parallel Routes

```
app/
├── @modal/
│   ├── default.tsx
│   └── (.)photo/[id]/page.tsx  # Intercepted route
├── layout.tsx
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <>
      {children}
      {modal}
    </>
  );
}
```

### Dynamic Imports for Heavy Components

```tsx
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@/components/editor'), {
  loading: () => <div className="h-[400px] animate-pulse rounded bg-muted" />,
  ssr: false, // client-only component
});

const Map = dynamic(() => import('@/components/map'), {
  loading: () => <div className="h-[300px] animate-pulse rounded bg-muted" />,
  ssr: false,
});
```

## Metadata & SEO

### Dynamic Metadata

```tsx
import type { Metadata, ResolvingMetadata } from 'next';

interface PageProps {
  params: { slug: string };
}

export async function generateMetadata(
  { params }: PageProps,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const post = await getPost(params.slug);
  const previousImages = (await parent).openGraph?.images || [];

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage, ...previousImages],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}
```

### Sitemap & Robots

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await db.post.findMany({ where: { published: true } });

  return [
    { url: 'https://example.com', lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    ...posts.map(post => ({
      url: `https://example.com/blog/${post.slug}`,
      lastModified: post.updatedAt,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })),
  ];
}
```

## Middleware

### Auth + i18n Middleware

```tsx
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const protectedPaths = ['/dashboard', '/settings', '/api/private'];
const publicPaths = ['/login', '/register', '/api/auth'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('session-token');

  if (protectedPaths.some(p => pathname.startsWith(p)) && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (publicPaths.some(p => pathname.startsWith(p)) && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  const response = NextResponse.next();
  response.headers.set('x-pathname', pathname);
  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public/).*)'],
};
```

## Performance Monitoring

### Web Vitals

```tsx
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next';
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  );
}
```

### Custom Performance Tracking

```tsx
'use client';

import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals(metric => {
    const { name, value, rating } = metric;

    // Send to analytics
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, {
        value: Math.round(name === 'CLS' ? value * 1000 : value),
        event_label: rating,
        non_interaction: true,
      });
    }
  });

  return null;
}
```

## Build Optimization

### Bundle Analysis

```bash
# Install analyzer
npm install @next/bundle-analyzer

# next.config.ts
import withBundleAnalyzer from '@next/bundle-analyzer';

const config = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})({
  // your config
});

# Run analysis
ANALYZE=true npm run build
```

### Tree Shaking Tips

```tsx
// Bad — imports entire library
import { format } from 'date-fns';

// Good — imports only what's needed
import format from 'date-fns/format';

// Bad — barrel file imports
import { Button, Input, Select } from '@/components/ui';

// Good — direct imports (when barrel files are large)
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
```

### next.config.ts Production Settings

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      ],
    },
  ],
};

export default nextConfig;
```
