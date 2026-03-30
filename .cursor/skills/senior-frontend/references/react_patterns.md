# React Patterns & Anti-Patterns

Comprehensive guide to modern React patterns for production applications.

## Component Patterns

### Compound Components

Use when building complex UI components with shared implicit state (Tabs, Accordion, Select).

```tsx
interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('Tab components must be used within <Tabs>');
  return ctx;
}

function Tabs({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div role="tablist">{children}</div>
    </TabsContext.Provider>
  );
}

function TabTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useTabsContext();
  return (
    <button
      role="tab"
      aria-selected={activeTab === value}
      onClick={() => setActiveTab(value)}
      className={cn('px-4 py-2', activeTab === value && 'border-b-2 border-primary')}
    >
      {children}
    </button>
  );
}

function TabContent({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab } = useTabsContext();
  if (activeTab !== value) return null;
  return <div role="tabpanel">{children}</div>;
}

Tabs.Trigger = TabTrigger;
Tabs.Content = TabContent;

// Usage:
<Tabs defaultValue="tab1">
  <Tabs.Trigger value="tab1">Tab 1</Tabs.Trigger>
  <Tabs.Trigger value="tab2">Tab 2</Tabs.Trigger>
  <Tabs.Content value="tab1">Content 1</Tabs.Content>
  <Tabs.Content value="tab2">Content 2</Tabs.Content>
</Tabs>
```

### Render Props / Headless Components

Use when you need to share behavior while letting consumers control rendering.

```tsx
interface UseDisclosureReturn {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

function useDisclosure(initial = false): UseDisclosureReturn {
  const [isOpen, setIsOpen] = useState(initial);
  return {
    isOpen,
    open: useCallback(() => setIsOpen(true), []),
    close: useCallback(() => setIsOpen(false), []),
    toggle: useCallback(() => setIsOpen(prev => !prev), []),
  };
}
```

### Polymorphic Components

Components that can render as different HTML elements.

```tsx
type PolymorphicProps<E extends React.ElementType> = {
  as?: E;
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<E>, 'as' | 'children'>;

function Box<E extends React.ElementType = 'div'>({ as, children, ...props }: PolymorphicProps<E>) {
  const Component = as || 'div';
  return <Component {...props}>{children}</Component>;
}

// Usage:
<Box as="section" className="p-4">Section content</Box>
<Box as="article">Article content</Box>
<Box as={Link} href="/about">Link content</Box>
```

### Controlled vs Uncontrolled Pattern

Support both modes for maximum flexibility.

```tsx
interface InputProps {
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
}

function Input({ value: controlledValue, defaultValue = '', onChange }: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (!isControlled) setInternalValue(newValue);
    onChange?.(newValue);
  };

  return <input value={value} onChange={handleChange} />;
}
```

## Hook Patterns

### Custom Hook Composition

Build complex hooks from simpler ones.

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

function useDebouncedSearch(query: string) {
  const debouncedQuery = useDebounce(query, 300);

  return useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchAPI(debouncedQuery),
    enabled: debouncedQuery.length > 2,
  });
}
```

### useReducer for Complex State

Prefer `useReducer` when state transitions are interdependent.

```tsx
type FormState = {
  values: Record<string, string>;
  errors: Record<string, string>;
  isSubmitting: boolean;
  isDirty: boolean;
};

type FormAction =
  | { type: 'SET_FIELD'; field: string; value: string }
  | { type: 'SET_ERROR'; field: string; error: string }
  | { type: 'SUBMIT_START' }
  | { type: 'SUBMIT_SUCCESS' }
  | { type: 'SUBMIT_ERROR'; errors: Record<string, string> }
  | { type: 'RESET' };

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET_FIELD':
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
        errors: { ...state.errors, [action.field]: '' },
        isDirty: true,
      };
    case 'SET_ERROR':
      return { ...state, errors: { ...state.errors, [action.field]: action.error } };
    case 'SUBMIT_START':
      return { ...state, isSubmitting: true };
    case 'SUBMIT_SUCCESS':
      return { ...state, isSubmitting: false, isDirty: false };
    case 'SUBMIT_ERROR':
      return { ...state, isSubmitting: false, errors: action.errors };
    case 'RESET':
      return { values: {}, errors: {}, isSubmitting: false, isDirty: false };
  }
}
```

### Ref Patterns

```tsx
function useMergedRefs<T>(...refs: (React.Ref<T> | undefined)[]) {
  return useCallback((node: T | null) => {
    refs.forEach(ref => {
      if (typeof ref === 'function') ref(node);
      else if (ref) (ref as React.MutableRefObject<T | null>).current = node;
    });
  }, refs);
}

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T | undefined>(undefined);
  useEffect(() => { ref.current = value; });
  return ref.current;
}

function useEventCallback<T extends (...args: any[]) => any>(fn: T): T {
  const ref = useRef(fn);
  useLayoutEffect(() => { ref.current = fn; });
  return useCallback((...args: any[]) => ref.current(...args), []) as T;
}
```

## Data Fetching Patterns

### TanStack Query Patterns

```tsx
const queryKeys = {
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters: UserFilters) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
};

function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60 * 1000,
  });
}

function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateUser,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.users.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.users.lists() });
    },
  });
}
```

### Optimistic Updates

```tsx
function useToggleFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleFavoriteAPI,
    onMutate: async (itemId) => {
      await queryClient.cancelQueries({ queryKey: ['items', itemId] });
      const previous = queryClient.getQueryData(['items', itemId]);
      queryClient.setQueryData(['items', itemId], (old: Item) => ({
        ...old,
        isFavorite: !old.isFavorite,
      }));
      return { previous };
    },
    onError: (_err, itemId, context) => {
      queryClient.setQueryData(['items', itemId], context?.previous);
    },
    onSettled: (_data, _err, itemId) => {
      queryClient.invalidateQueries({ queryKey: ['items', itemId] });
    },
  });
}
```

## Form Patterns

### React Hook Form + Zod

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const signupSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'At least 8 characters'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords must match',
  path: ['confirmPassword'],
});

type SignupForm = z.infer<typeof signupSchema>;

function SignupForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupForm) => {
    await signupAPI(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <input {...register('email')} placeholder="Email" className="w-full rounded border px-3 py-2" />
        {errors.email && <p className="mt-1 text-sm text-destructive">{errors.email.message}</p>}
      </div>
      <div>
        <input {...register('password')} type="password" placeholder="Password" className="w-full rounded border px-3 py-2" />
        {errors.password && <p className="mt-1 text-sm text-destructive">{errors.password.message}</p>}
      </div>
      <div>
        <input {...register('confirmPassword')} type="password" placeholder="Confirm" className="w-full rounded border px-3 py-2" />
        {errors.confirmPassword && <p className="mt-1 text-sm text-destructive">{errors.confirmPassword.message}</p>}
      </div>
      <button type="submit" disabled={isSubmitting} className="w-full rounded bg-primary px-4 py-2 text-primary-foreground">
        {isSubmitting ? 'Signing up...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

## Anti-Patterns to Avoid

### 1. Prop Drilling

**Bad:**
```tsx
<App user={user}>
  <Layout user={user}>
    <Sidebar user={user}>
      <UserMenu user={user} />
    </Sidebar>
  </Layout>
</App>
```

**Good:** Use context or state management.

### 2. Unnecessary Effects

**Bad:**
```tsx
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);
```

**Good:** Derive state directly.
```tsx
const fullName = `${firstName} ${lastName}`;
```

### 3. Object/Array as Dependency

**Bad:**
```tsx
useEffect(() => { fetchData(filters); }, [filters]); // new object every render
```

**Good:**
```tsx
const serialized = JSON.stringify(filters);
useEffect(() => { fetchData(filters); }, [serialized]);
// Or use individual primitive values
useEffect(() => { fetchData(filters); }, [filters.status, filters.page]);
```

### 4. State for Derived Data

**Bad:**
```tsx
const [items, setItems] = useState([]);
const [filteredItems, setFilteredItems] = useState([]);
useEffect(() => { setFilteredItems(items.filter(predicate)); }, [items]);
```

**Good:**
```tsx
const [items, setItems] = useState([]);
const filteredItems = useMemo(() => items.filter(predicate), [items, predicate]);
```

### 5. Fetching in useEffect Without Cleanup

**Bad:**
```tsx
useEffect(() => {
  fetch(`/api/user/${id}`).then(r => r.json()).then(setUser);
}, [id]);
```

**Good:** Use TanStack Query or handle cleanup:
```tsx
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/user/${id}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setUser)
    .catch(e => { if (e.name !== 'AbortError') throw e; });
  return () => controller.abort();
}, [id]);
```

### 6. Misusing Keys

**Bad:** Using array index as key for dynamic lists.
```tsx
{items.map((item, i) => <Item key={i} {...item} />)}
```

**Good:** Use stable unique identifiers.
```tsx
{items.map(item => <Item key={item.id} {...item} />)}
```

## Performance Patterns

### React.memo — When to Use

Only memoize when:
- Component re-renders frequently with same props
- Component is expensive to render (large trees, complex calculations)
- Profiler confirms it's a bottleneck

```tsx
const ExpensiveList = memo(function ExpensiveList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{/* complex rendering */}</li>
      ))}
    </ul>
  );
});
```

### Virtualization for Long Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualRow.start}px)`,
              height: virtualRow.size,
              width: '100%',
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Code Splitting

```tsx
const HeavyChart = lazy(() => import('./HeavyChart'));
const AdminPanel = lazy(() => import('./AdminPanel'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <HeavyChart data={data} />
    </Suspense>
  );
}
```
