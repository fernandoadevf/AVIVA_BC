# Frontend Best Practices

Comprehensive guide covering security, accessibility, performance, testing, and maintainability.

## TypeScript Best Practices

### Strict Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Type Patterns

```tsx
// Discriminated unions for state machines
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function renderState<T>(state: AsyncState<T>, render: (data: T) => React.ReactNode) {
  switch (state.status) {
    case 'idle': return null;
    case 'loading': return <Spinner />;
    case 'success': return render(state.data);
    case 'error': return <ErrorDisplay error={state.error} />;
  }
}

// Branded types for type-safe IDs
type UserId = string & { readonly __brand: 'UserId' };
type PostId = string & { readonly __brand: 'PostId' };

function createUserId(id: string): UserId { return id as UserId; }
function getUser(id: UserId) { /* ... */ }

// Template literal types
type Route = `/${string}`;
type APIEndpoint = `/api/${string}`;
type EventName = `on${Capitalize<string>}`;

// Utility types
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

type NonNullableFields<T> = {
  [P in keyof T]: NonNullable<T[P]>;
};

// Extract component props
type ButtonProps = React.ComponentPropsWithoutRef<'button'>;
type InputProps = React.ComponentPropsWithRef<'input'>;
type DivProps = React.HTMLAttributes<HTMLDivElement>;
```

### Zod Schema Patterns

```tsx
import { z } from 'zod';

const userSchema = z.object({
  id: z.string().cuid(),
  email: z.string().email(),
  name: z.string().min(2).max(100),
  role: z.enum(['admin', 'user', 'moderator']),
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'system']).default('system'),
    notifications: z.boolean().default(true),
  }),
  createdAt: z.coerce.date(),
});

type User = z.infer<typeof userSchema>;

const apiResponseSchema = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema,
    meta: z.object({
      page: z.number(),
      total: z.number(),
    }).optional(),
  });

// Runtime validation
function parseAPIResponse<T extends z.ZodType>(schema: T, data: unknown): z.infer<T> {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error('Validation failed:', result.error.flatten());
    throw new Error('Invalid API response');
  }
  return result.data;
}
```

## Tailwind CSS Best Practices

### cn() Utility Setup

```tsx
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### Component Variants with CVA

```tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  }
);
```

### Responsive Design Patterns

```tsx
// Mobile-first approach
<div className="
  grid grid-cols-1 gap-4
  sm:grid-cols-2
  md:grid-cols-3
  lg:grid-cols-4
">

// Container queries (Tailwind v3.4+)
<div className="@container">
  <div className="grid grid-cols-1 @md:grid-cols-2 @lg:grid-cols-3">

// Responsive typography
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">

// Responsive spacing
<section className="px-4 py-8 sm:px-6 md:px-8 lg:py-16">
```

### Dark Mode

```tsx
// Tailwind config
darkMode: 'class',

// Toggle component
function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', theme === 'dark');
    }
  }, [theme]);
}

// Usage in components
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

## Security

### XSS Prevention

```tsx
// Never trust user input in dangerouslySetInnerHTML
import DOMPurify from 'dompurify';

function SafeHTML({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

// Validate URLs
function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}
```

### Content Security Policy

```tsx
// next.config.ts headers
headers: async () => [
  {
    source: '/(.*)',
    headers: [
      {
        key: 'Content-Security-Policy',
        value: [
          "default-src 'self'",
          "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
          "style-src 'self' 'unsafe-inline'",
          "img-src 'self' blob: data: https:",
          "font-src 'self'",
          "connect-src 'self' https://api.example.com",
          "frame-ancestors 'none'",
        ].join('; '),
      },
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
    ],
  },
],
```

### Environment Variables

```tsx
// Validate env at build time with t3-env
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    NEXTAUTH_SECRET: z.string().min(32),
    STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  },
  client: {
    NEXT_PUBLIC_APP_URL: z.string().url(),
    NEXT_PUBLIC_STRIPE_KEY: z.string().startsWith('pk_'),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
    NEXT_PUBLIC_STRIPE_KEY: process.env.NEXT_PUBLIC_STRIPE_KEY,
  },
});
```

## Accessibility (a11y)

### ARIA Patterns

```tsx
// Accessible modal
function Modal({ isOpen, onClose, title, children }: ModalProps) {
  return (
    <dialog
      open={isOpen}
      aria-labelledby="modal-title"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div role="document" className="rounded-lg bg-background p-6 shadow-xl">
        <h2 id="modal-title" className="text-lg font-semibold">{title}</h2>
        {children}
        <button onClick={onClose} aria-label="Close modal">×</button>
      </div>
    </dialog>
  );
}

// Accessible form
<form aria-labelledby="form-title">
  <h2 id="form-title">Contact Form</h2>
  <div>
    <label htmlFor="email">Email</label>
    <input
      id="email"
      type="email"
      aria-required="true"
      aria-invalid={!!errors.email}
      aria-describedby={errors.email ? 'email-error' : undefined}
    />
    {errors.email && <p id="email-error" role="alert">{errors.email}</p>}
  </div>
</form>

// Skip navigation
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4">
  Skip to main content
</a>
<main id="main-content">
```

### Focus Management

```tsx
function useAutoFocus<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  useEffect(() => { ref.current?.focus(); }, []);
  return ref;
}

function useTrapFocus(containerRef: RefObject<HTMLElement>) {
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const focusable = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== 'Tab') return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    }

    container.addEventListener('keydown', handleKeyDown);
    first?.focus();
    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [containerRef]);
}
```

## Testing Best Practices

### Component Testing with Testing Library

```tsx
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('UserForm', () => {
  it('validates and submits form data', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<UserForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'securepass123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'securepass123',
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<UserForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  });
});
```

### Testing Hooks

```tsx
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useUser', () => {
  it('fetches user data', async () => {
    const { result } = renderHook(() => useUser('123'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.name).toBe('John');
  });
});
```

### MSW for API Mocking

```tsx
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John', email: 'john@example.com' });
  }),
  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 'new-id', ...body }, { status: 201 });
  }),
];

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Error Handling

### Error Boundaries

```tsx
'use client';

import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center gap-4 p-8">
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })} className="rounded bg-primary px-4 py-2 text-primary-foreground">
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### API Error Handling

```tsx
class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(endpoint, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new APIError(
      body.message || `Request failed: ${res.status}`,
      res.status,
      body.code,
    );
  }

  return res.json();
}
```

## Troubleshooting

### Hydration Mismatches

**Symptoms:** "Text content does not match server-rendered HTML"

**Common causes:**
1. Using `Date.now()`, `Math.random()`, or browser APIs during render
2. Browser extensions modifying DOM
3. Different content based on `typeof window`

**Fix:**
```tsx
function ClientOnly({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  return <>{children}</>;
}
```

### "Cannot update a component while rendering"

Move state updates out of render phase into effects or event handlers.

### Bundle Size Issues

1. Run `ANALYZE=true npm run build` with `@next/bundle-analyzer`
2. Check for duplicate packages: `npx depcheck`
3. Look for barrel file imports pulling in unused code
4. Use `import()` for heavy libraries used in few places

### Slow Development Server

1. Exclude `node_modules` from file watchers
2. Use `turbo` mode: `next dev --turbo`
3. Check for circular dependencies: `npx madge --circular src/`
4. Reduce number of pages/routes in development

### Memory Leaks

1. Always clean up subscriptions in `useEffect` return
2. Cancel pending requests with `AbortController`
3. Remove event listeners on unmount
4. Use weak references for caches when appropriate

### CSS Not Applying

1. Check Tailwind content paths in config
2. Verify `globals.css` is imported in root layout
3. Check for CSS specificity conflicts
4. Use browser DevTools to inspect computed styles
5. Ensure `postcss.config.js` includes tailwindcss plugin
