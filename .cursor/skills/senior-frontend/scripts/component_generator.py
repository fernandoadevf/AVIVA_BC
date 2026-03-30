#!/usr/bin/env python3
"""
Component Generator — Scaffolds React/Next.js components with TypeScript,
Tailwind CSS, tests, and Storybook stories.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

COMPONENT_TEMPLATE = '''import {{ cn }} from '@/lib/utils';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export function {name}({{ className, children }}: {name}Props) {{
  return (
    <div className={{cn('{tailwind_base}', className)}}>
      {{children}}
    </div>
  );
}}
'''

PAGE_TEMPLATE = '''import {{ Metadata }} from 'next';

export const metadata: Metadata = {{
  title: '{name}',
  description: '{name} page',
}};

export default function {name}Page() {{
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold tracking-tight">{name}</h1>
    </main>
  );
}}
'''

LAYOUT_TEMPLATE = '''interface {name}LayoutProps {{
  children: React.ReactNode;
}}

export default function {name}Layout({{ children }}: {name}LayoutProps) {{
  return (
    <div className="min-h-screen">
      {{children}}
    </div>
  );
}}
'''

HOOK_TEMPLATE = '''import {{ useState, useCallback }} from 'react';

interface Use{name}Options {{
  initialValue?: string;
}}

interface Use{name}Return {{
  value: string;
  setValue: (value: string) => void;
  reset: () => void;
}}

export function use{name}(options: Use{name}Options = {{}}): Use{name}Return {{
  const {{ initialValue = '' }} = options;
  const [value, setValueState] = useState(initialValue);

  const setValue = useCallback((newValue: string) => {{
    setValueState(newValue);
  }}, []);

  const reset = useCallback(() => {{
    setValueState(initialValue);
  }}, [initialValue]);

  return {{ value, setValue, reset }};
}}
'''

TEST_TEMPLATE = '''import {{ render, screen }} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {{ describe, it, expect }} from 'vitest';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('renders without crashing', () => {{
    render(<{name} />);
  }});

  it('renders children', () => {{
    render(<{name}>Test content</{name}>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  }});

  it('applies custom className', () => {{
    const {{ container }} = render(<{name} className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  }});
}});
'''

HOOK_TEST_TEMPLATE = '''import {{ renderHook, act }} from '@testing-library/react';
import {{ describe, it, expect }} from 'vitest';
import {{ use{name} }} from './use{name}';

describe('use{name}', () => {{
  it('returns initial value', () => {{
    const {{ result }} = renderHook(() => use{name}());
    expect(result.current.value).toBe('');
  }});

  it('updates value', () => {{
    const {{ result }} = renderHook(() => use{name}());
    act(() => {{
      result.current.setValue('new value');
    }});
    expect(result.current.value).toBe('new value');
  }});

  it('resets to initial value', () => {{
    const {{ result }} = renderHook(() => use{name}({{ initialValue: 'initial' }}));
    act(() => {{
      result.current.setValue('changed');
      result.current.reset();
    }});
    expect(result.current.value).toBe('initial');
  }});
}});
'''

STORY_TEMPLATE = '''import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {name} }} from './{name}';

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
  tags: ['autodocs'],
  argTypes: {{
    className: {{ control: 'text' }},
  }},
}};

export default meta;
type Story = StoryObj<typeof {name}>;

export const Default: Story = {{
  args: {{
    children: '{name} content',
  }},
}};

export const WithCustomClass: Story = {{
  args: {{
    children: 'Custom styled',
    className: 'bg-blue-100 p-4 rounded-lg',
  }},
}};
'''

LOADING_TEMPLATE = '''export default function {name}Loading() {{
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 w-48 rounded bg-muted" />
      <div className="h-4 w-full rounded bg-muted" />
      <div className="h-4 w-3/4 rounded bg-muted" />
    </div>
  );
}}
'''

ERROR_TEMPLATE = ''''use client';

interface {name}ErrorProps {{
  error: Error & {{ digest?: string }};
  reset: () => void;
}}

export default function {name}Error({{ error, reset }}: {name}ErrorProps) {{
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground">{{error.message}}</p>
      <button
        onClick={{reset}}
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
      >
        Try again
      </button>
    </div>
  );
}}
'''

INDEX_TEMPLATE = "export {{ {name} }} from './{name}';\n"
HOOK_INDEX_TEMPLATE = "export {{ use{name} }} from './use{name}';\n"


def to_kebab(name: str) -> str:
    result = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            result.append('-')
        result.append(ch.lower())
    return ''.join(result)


def generate_component(args):
    name = args.name
    comp_type = args.type
    base_path = Path(args.path)
    
    if comp_type == 'hook':
        folder = base_path / f"use{name}"
        folder.mkdir(parents=True, exist_ok=True)
        
        hook_file = folder / f"use{name}.ts"
        hook_file.write_text(HOOK_TEMPLATE.format(name=name))
        print(f"  Created: {hook_file}")
        
        index_file = folder / "index.ts"
        index_file.write_text(HOOK_INDEX_TEMPLATE.format(name=name))
        print(f"  Created: {index_file}")
        
        if args.with_test:
            test_file = folder / f"use{name}.test.ts"
            test_file.write_text(HOOK_TEST_TEMPLATE.format(name=name))
            print(f"  Created: {test_file}")
        
        return

    kebab = to_kebab(name)
    folder = base_path / name
    folder.mkdir(parents=True, exist_ok=True)

    templates = {
        'component': COMPONENT_TEMPLATE,
        'page': PAGE_TEMPLATE,
        'layout': LAYOUT_TEMPLATE,
    }

    ext = 'tsx'
    template = templates.get(comp_type, COMPONENT_TEMPLATE)
    tailwind_base = f"flex flex-col gap-4"
    
    main_file = folder / f"{name}.{ext}"
    main_file.write_text(template.format(name=name, tailwind_base=tailwind_base))
    print(f"  Created: {main_file}")

    index_file = folder / f"index.ts"
    index_file.write_text(INDEX_TEMPLATE.format(name=name))
    print(f"  Created: {index_file}")

    if args.with_test:
        test_file = folder / f"{name}.test.{ext}"
        test_file.write_text(TEST_TEMPLATE.format(name=name))
        print(f"  Created: {test_file}")

    if args.with_story:
        story_file = folder / f"{name}.stories.{ext}"
        story_file.write_text(STORY_TEMPLATE.format(name=name))
        print(f"  Created: {story_file}")

    if args.with_loading:
        loading_file = folder / f"loading.{ext}"
        loading_file.write_text(LOADING_TEMPLATE.format(name=name))
        print(f"  Created: {loading_file}")

    if args.with_error:
        error_file = folder / f"error.{ext}"
        error_file.write_text(ERROR_TEMPLATE.format(name=name))
        print(f"  Created: {error_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate React/Next.js components with TypeScript and Tailwind CSS'
    )
    parser.add_argument('--name', required=True, help='Component name (PascalCase)')
    parser.add_argument('--type', choices=['component', 'page', 'layout', 'hook'],
                        default='component', help='Type of component to generate')
    parser.add_argument('--path', default='src/components',
                        help='Base path for the component')
    parser.add_argument('--with-test', action='store_true',
                        help='Generate test file')
    parser.add_argument('--with-story', action='store_true',
                        help='Generate Storybook story')
    parser.add_argument('--with-loading', action='store_true',
                        help='Generate loading.tsx (Next.js)')
    parser.add_argument('--with-error', action='store_true',
                        help='Generate error.tsx (Next.js)')

    args = parser.parse_args()

    if not args.name[0].isupper():
        print(f"Error: Component name '{args.name}' should be PascalCase", file=sys.stderr)
        sys.exit(1)

    print(f"\nGenerating {args.type}: {args.name}")
    print(f"Path: {args.path}\n")

    generate_component(args)

    print(f"\nDone! {args.type.title()} '{args.name}' generated successfully.")


if __name__ == '__main__':
    main()
