#!/usr/bin/env python3
"""
Bundle Analyzer — Analyzes frontend project dependencies, detects issues,
and provides optimization recommendations.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

KNOWN_HEAVY_PACKAGES = {
    'moment': {'size': '290kb', 'alternative': 'date-fns or dayjs (2-7kb)'},
    'lodash': {'size': '72kb', 'alternative': 'lodash-es with tree-shaking or individual imports (lodash/get)'},
    'underscore': {'size': '30kb', 'alternative': 'Native ES6+ methods'},
    'jquery': {'size': '87kb', 'alternative': 'Native DOM APIs or React refs'},
    'axios': {'size': '13kb', 'alternative': 'Native fetch API (0kb) or ky (3kb)'},
    'classnames': {'size': '1kb', 'alternative': 'clsx (0.5kb)'},
    'node-fetch': {'size': '8kb', 'alternative': 'Native fetch (Node 18+)'},
    'uuid': {'size': '4kb', 'alternative': 'crypto.randomUUID() (native)'},
    'chalk': {'size': '12kb', 'alternative': 'picocolors (0.5kb)'},
    'request': {'size': '200kb+', 'alternative': 'Native fetch or undici'},
    'bluebird': {'size': '80kb', 'alternative': 'Native Promises'},
    'core-js': {'size': '150kb+', 'alternative': 'Target modern browsers, use browserslist'},
    'polished': {'size': '35kb', 'alternative': 'Tailwind CSS utilities'},
    'styled-components': {'size': '16kb', 'alternative': 'Tailwind CSS (0kb runtime)'},
    '@emotion/styled': {'size': '12kb', 'alternative': 'Tailwind CSS (0kb runtime)'},
    'animate.css': {'size': '80kb', 'alternative': 'Tailwind CSS animations or framer-motion'},
    'numeral': {'size': '17kb', 'alternative': 'Intl.NumberFormat (native)'},
    'validator': {'size': '55kb', 'alternative': 'Zod for schema validation'},
}

DUPLICATE_RISK_PACKAGES = {
    'react': 'Multiple React versions cause hooks to break',
    'react-dom': 'Must match react version exactly',
    'webpack': 'Multiple bundler instances cause build issues',
    'typescript': 'Version mismatches cause type errors',
    '@types/react': 'Must be compatible with react version',
}

SECURITY_CONCERN_PATTERNS = [
    ('eval(', 'Avoid eval() — use safer alternatives'),
    ('dangerouslySetInnerHTML', 'Sanitize HTML with DOMPurify before using dangerouslySetInnerHTML'),
    ('innerHTML', 'Use React rendering instead of innerHTML'),
    ('document.write', 'Never use document.write in modern apps'),
]


class BundleAnalyzer:
    def __init__(self, project_path: str, verbose: bool = False):
        self.project_path = Path(project_path).resolve()
        self.verbose = verbose
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.stats = {}

    def analyze(self):
        print(f"\n{'='*60}")
        print(f"  Bundle Analysis: {self.project_path.name}")
        print(f"{'='*60}\n")

        self._check_package_json()
        self._check_tsconfig()
        self._check_next_config()
        self._check_imports()
        self._check_images()
        self._check_env_files()
        self._print_report()

    def _check_package_json(self):
        pkg_path = self.project_path / 'package.json'
        if not pkg_path.exists():
            self.issues.append("No package.json found — is this a Node.js project?")
            return

        with open(pkg_path) as f:
            pkg = json.load(f)

        deps = pkg.get('dependencies', {})
        dev_deps = pkg.get('devDependencies', {})
        all_deps = {**deps, **dev_deps}

        self.stats['total_deps'] = len(deps)
        self.stats['total_dev_deps'] = len(dev_deps)

        print(f"  Dependencies: {len(deps)} production, {len(dev_deps)} dev\n")

        for name, info in KNOWN_HEAVY_PACKAGES.items():
            if name in deps:
                self.warnings.append(
                    f"Heavy package '{name}' (~{info['size']}) in production deps. "
                    f"Consider: {info['alternative']}"
                )

        for name, risk in DUPLICATE_RISK_PACKAGES.items():
            if name in deps and name in dev_deps:
                self.issues.append(
                    f"'{name}' in both dependencies and devDependencies. {risk}"
                )

        misplaced_dev = ['@types/', 'eslint', 'prettier', 'jest', 'vitest',
                         'storybook', '@storybook/', 'typescript', 'ts-node']
        for dep_name in deps:
            for pattern in misplaced_dev:
                if dep_name.startswith(pattern) or dep_name == pattern:
                    self.warnings.append(
                        f"'{dep_name}' should be in devDependencies, not dependencies"
                    )

        if 'react' in deps and 'next' not in deps:
            if '@vitejs/plugin-react' not in dev_deps and 'react-scripts' not in deps:
                self.suggestions.append(
                    "Consider using Vite for React projects (faster builds than CRA)"
                )

        scripts = pkg.get('scripts', {})
        if 'lint' not in scripts:
            self.suggestions.append("Add a 'lint' script (eslint .)")
        if 'typecheck' not in scripts and 'typescript' in all_deps:
            self.suggestions.append("Add a 'typecheck' script (tsc --noEmit)")
        if not any(k in scripts for k in ['test', 'test:unit']):
            self.suggestions.append("Add a 'test' script for running unit tests")

        if self.verbose:
            print("  Production dependencies:")
            for name, version in sorted(deps.items()):
                flag = " ⚠" if name in KNOWN_HEAVY_PACKAGES else ""
                print(f"    {name}@{version}{flag}")
            print()

    def _check_tsconfig(self):
        tsconfig_path = self.project_path / 'tsconfig.json'
        if not tsconfig_path.exists():
            self.suggestions.append("No tsconfig.json found — consider using TypeScript")
            return

        try:
            content = tsconfig_path.read_text()
            content = '\n'.join(
                line for line in content.split('\n')
                if not line.strip().startswith('//')
            )
            tsconfig = json.loads(content)
        except json.JSONDecodeError:
            self.warnings.append("tsconfig.json has invalid JSON (comments may need removal for analysis)")
            return

        compiler_opts = tsconfig.get('compilerOptions', {})

        if not compiler_opts.get('strict'):
            self.warnings.append("TypeScript strict mode is disabled — enable 'strict: true'")

        if not compiler_opts.get('noUncheckedIndexedAccess'):
            self.suggestions.append("Enable 'noUncheckedIndexedAccess' for safer array/object access")

        if compiler_opts.get('target', '').lower() in ('es5', 'es6', 'es2015', 'es2016'):
            self.suggestions.append(
                f"Target '{compiler_opts['target']}' is outdated — consider 'ES2022' or 'ESNext'"
            )

    def _check_next_config(self):
        for config_name in ['next.config.js', 'next.config.mjs', 'next.config.ts']:
            config_path = self.project_path / config_name
            if config_path.exists():
                content = config_path.read_text()

                if 'images' not in content:
                    self.suggestions.append(
                        "Configure 'images.remotePatterns' in next.config for external images"
                    )

                if 'experimental' in content and 'serverActions' in content:
                    self.suggestions.append(
                        "Server Actions are stable in Next.js 14+ — remove from experimental"
                    )

                if 'output' not in content:
                    self.suggestions.append(
                        "Consider 'output: standalone' in next.config for Docker deployments"
                    )
                return

    def _check_imports(self):
        src_dir = self.project_path / 'src'
        if not src_dir.exists():
            src_dir = self.project_path

        ts_files = list(src_dir.rglob('*.ts')) + list(src_dir.rglob('*.tsx'))
        js_files = list(src_dir.rglob('*.js')) + list(src_dir.rglob('*.jsx'))

        all_files = [f for f in ts_files + js_files
                     if 'node_modules' not in str(f) and '.next' not in str(f)]

        self.stats['source_files'] = len(all_files)

        barrel_imports = 0
        wildcard_imports = 0
        relative_deep_imports = 0
        console_logs = 0

        for filepath in all_files:
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue

            lines = content.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()

                if stripped.startswith('import ') and "from '.'" in stripped or "from '..'" in stripped:
                    if stripped.count('../') >= 3:
                        relative_deep_imports += 1

                if stripped.startswith('import * as'):
                    wildcard_imports += 1

                if 'console.log' in stripped and not stripped.startswith('//'):
                    console_logs += 1

                for pattern, msg in SECURITY_CONCERN_PATTERNS:
                    if pattern in stripped and not stripped.startswith('//'):
                        self.warnings.append(
                            f"Security: {msg} — {filepath.relative_to(self.project_path)}:{i+1}"
                        )

        if wildcard_imports > 5:
            self.warnings.append(
                f"Found {wildcard_imports} wildcard imports (import * as). "
                "These prevent tree-shaking — use named imports"
            )

        if relative_deep_imports > 5:
            self.suggestions.append(
                f"Found {relative_deep_imports} deep relative imports (../../../). "
                "Use path aliases (@/components/...)"
            )

        if console_logs > 10:
            self.warnings.append(
                f"Found {console_logs} console.log statements. "
                "Remove before production or use a logger"
            )

        if self.verbose:
            print(f"  Source files analyzed: {len(all_files)}")
            print(f"  Wildcard imports: {wildcard_imports}")
            print(f"  Deep relative imports: {relative_deep_imports}")
            print(f"  Console.log statements: {console_logs}\n")

    def _check_images(self):
        src_dir = self.project_path / 'src'
        public_dir = self.project_path / 'public'

        large_images = []
        for search_dir in [src_dir, public_dir]:
            if not search_dir.exists():
                continue
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']:
                for img in search_dir.rglob(ext):
                    size_kb = img.stat().st_size / 1024
                    if size_kb > 500:
                        large_images.append((img.relative_to(self.project_path), size_kb))

        if large_images:
            self.warnings.append(
                f"Found {len(large_images)} images > 500KB. Convert to WebP/AVIF:"
            )
            for img_path, size in large_images[:5]:
                self.warnings.append(f"  - {img_path} ({size:.0f}KB)")

    def _check_env_files(self):
        gitignore = self.project_path / '.gitignore'
        env_file = self.project_path / '.env'
        env_local = self.project_path / '.env.local'

        if env_file.exists() or env_local.exists():
            if gitignore.exists():
                gitignore_content = gitignore.read_text()
                if '.env' not in gitignore_content:
                    self.issues.append(
                        ".env files exist but are NOT in .gitignore — secrets may be exposed!"
                    )

        env_example = self.project_path / '.env.example'
        if (env_file.exists() or env_local.exists()) and not env_example.exists():
            self.suggestions.append(
                "Create .env.example with placeholder values for team onboarding"
            )

    def _print_report(self):
        print(f"\n{'='*60}")
        print("  ANALYSIS REPORT")
        print(f"{'='*60}\n")

        if self.stats:
            print("  Stats:")
            for key, val in self.stats.items():
                print(f"    {key.replace('_', ' ').title()}: {val}")
            print()

        if self.issues:
            print(f"  🔴 ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"    • {issue}")
            print()

        if self.warnings:
            print(f"  🟡 WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"    • {warning}")
            print()

        if self.suggestions:
            print(f"  🟢 SUGGESTIONS ({len(self.suggestions)}):")
            for suggestion in self.suggestions:
                print(f"    • {suggestion}")
            print()

        total = len(self.issues) + len(self.warnings) + len(self.suggestions)
        if total == 0:
            print("  ✅ No issues found! Project looks healthy.\n")
        else:
            score = max(0, 100 - (len(self.issues) * 15) - (len(self.warnings) * 5) - (len(self.suggestions) * 2))
            print(f"  Health Score: {score}/100")
            print(f"  ({len(self.issues)} issues, {len(self.warnings)} warnings, {len(self.suggestions)} suggestions)\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze frontend project bundle and dependencies'
    )
    parser.add_argument('path', help='Path to the project root')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed dependency listing')

    args = parser.parse_args()

    if not Path(args.path).exists():
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)

    analyzer = BundleAnalyzer(args.path, verbose=args.verbose)
    analyzer.analyze()


if __name__ == '__main__':
    main()
