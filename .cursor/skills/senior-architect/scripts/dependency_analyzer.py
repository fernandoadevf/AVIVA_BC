#!/usr/bin/env python3
"""
Dependency Analyzer
Analyzes project dependencies: internal import graphs, circular dependencies,
external dependency health, and coupling metrics.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class DependencyAnalyzer:
    def __init__(self, project_path: str, depth: int = 3):
        self.project_path = Path(project_path).resolve()
        self.depth = depth
        self.import_graph: dict[str, set[str]] = defaultdict(set)
        self.external_deps: dict[str, dict] = {}
        self.findings: list[dict] = []
        self.metrics: dict[str, Any] = {}

        self.skip_dirs = {
            "node_modules", ".git", "__pycache__", ".next", "dist", "build",
            ".cache", "coverage", "vendor", ".venv", "venv", "env",
        }

    def analyze(self) -> dict:
        if not self.project_path.exists():
            print(f"Error: Path '{self.project_path}' does not exist.")
            sys.exit(1)

        self._detect_project_type()
        self._build_import_graph()
        self._detect_cycles()
        self._calculate_coupling_metrics()
        self._analyze_external_deps()
        self._assess_health()

        return {
            "project": str(self.project_path),
            "project_type": self.metrics.get("project_type", "unknown"),
            "metrics": self.metrics,
            "import_graph": {k: list(v) for k, v in self.import_graph.items()},
            "external_dependencies": self.external_deps,
            "findings": self.findings,
        }

    def _detect_project_type(self) -> None:
        root = self.project_path
        if (root / "package.json").exists():
            self.metrics["project_type"] = "javascript/typescript"
        elif (root / "go.mod").exists():
            self.metrics["project_type"] = "go"
        elif (root / "requirements.txt").exists() or (root / "pyproject.toml").exists() or (root / "setup.py").exists():
            self.metrics["project_type"] = "python"
        elif (root / "Cargo.toml").exists():
            self.metrics["project_type"] = "rust"
        elif (root / "pubspec.yaml").exists():
            self.metrics["project_type"] = "flutter/dart"
        elif (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
            self.metrics["project_type"] = "kotlin/java"
        elif (root / "Package.swift").exists():
            self.metrics["project_type"] = "swift"
        else:
            self.metrics["project_type"] = "unknown"

    def _build_import_graph(self) -> None:
        project_type = self.metrics.get("project_type", "unknown")

        if "javascript" in project_type or "typescript" in project_type:
            self._parse_js_imports()
        elif project_type == "python":
            self._parse_python_imports()
        elif project_type == "go":
            self._parse_go_imports()
        else:
            self._parse_js_imports()
            self._parse_python_imports()

        self.metrics["total_modules"] = len(self.import_graph)
        self.metrics["total_imports"] = sum(len(v) for v in self.import_graph.values())

    def _parse_js_imports(self) -> None:
        import_patterns = [
            re.compile(r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'),
            re.compile(r'import\s*\([\'"](.+?)[\'"]\)'),
            re.compile(r'require\s*\([\'"](.+?)[\'"]\)'),
            re.compile(r'from\s+[\'"](.+?)[\'"]\s+import'),
        ]

        for ext in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs"):
            for filepath in self.project_path.rglob(ext):
                if any(s in str(filepath) for s in self.skip_dirs):
                    continue

                relative = str(filepath.relative_to(self.project_path))
                module_name = self._to_module_name(relative)

                try:
                    content = filepath.read_text(errors="ignore")
                except OSError:
                    continue

                for pattern in import_patterns:
                    for match in pattern.finditer(content):
                        imported = match.group(1)
                        if imported.startswith("."):
                            resolved = self._resolve_relative_import(filepath, imported)
                            if resolved:
                                self.import_graph[module_name].add(resolved)
                        else:
                            pkg_name = imported.split("/")[0]
                            if pkg_name.startswith("@"):
                                pkg_name = "/".join(imported.split("/")[:2])
                            self.external_deps.setdefault(pkg_name, {"type": "npm", "imported_by": []})
                            self.external_deps[pkg_name]["imported_by"].append(module_name)

    def _parse_python_imports(self) -> None:
        import_patterns = [
            re.compile(r'^import\s+([\w.]+)', re.MULTILINE),
            re.compile(r'^from\s+([\w.]+)\s+import', re.MULTILINE),
        ]

        for filepath in self.project_path.rglob("*.py"):
            if any(s in str(filepath) for s in self.skip_dirs):
                continue

            relative = str(filepath.relative_to(self.project_path))
            module_name = self._to_module_name(relative)

            try:
                content = filepath.read_text(errors="ignore")
            except OSError:
                continue

            for pattern in import_patterns:
                for match in pattern.finditer(content):
                    imported = match.group(1)
                    top_level = imported.split(".")[0]

                    internal_path = self.project_path / top_level
                    if internal_path.exists() or (self.project_path / f"{top_level}.py").exists():
                        self.import_graph[module_name].add(imported)
                    else:
                        self.external_deps.setdefault(top_level, {"type": "pip", "imported_by": []})
                        self.external_deps[top_level]["imported_by"].append(module_name)

    def _parse_go_imports(self) -> None:
        import_pattern = re.compile(r'"(.+?)"')

        go_mod = self.project_path / "go.mod"
        module_prefix = ""
        if go_mod.exists():
            content = go_mod.read_text(errors="ignore")
            match = re.search(r'^module\s+(.+)$', content, re.MULTILINE)
            if match:
                module_prefix = match.group(1).strip()

        for filepath in self.project_path.rglob("*.go"):
            if any(s in str(filepath) for s in self.skip_dirs):
                continue

            relative = str(filepath.relative_to(self.project_path))
            module_name = self._to_module_name(relative)

            try:
                content = filepath.read_text(errors="ignore")
            except OSError:
                continue

            in_import_block = False
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("import ("):
                    in_import_block = True
                    continue
                if in_import_block and stripped == ")":
                    in_import_block = False
                    continue

                if in_import_block or stripped.startswith("import "):
                    for match in import_pattern.finditer(stripped):
                        imported = match.group(1)
                        if module_prefix and imported.startswith(module_prefix):
                            local_path = imported[len(module_prefix):].lstrip("/")
                            self.import_graph[module_name].add(local_path)
                        else:
                            pkg_name = imported.split("/")[0]
                            if "." in pkg_name:
                                pkg_name = "/".join(imported.split("/")[:3])
                            self.external_deps.setdefault(pkg_name, {"type": "go", "imported_by": []})
                            self.external_deps[pkg_name]["imported_by"].append(module_name)

    def _to_module_name(self, relative_path: str) -> str:
        parts = relative_path.replace("\\", "/").split("/")
        if self.depth > 0 and len(parts) > self.depth:
            parts = parts[:self.depth]
        name = "/".join(parts)
        for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go"):
            if name.endswith(ext):
                name = name[:-len(ext)]
        if name.endswith("/index"):
            name = name[:-6]
        return name

    def _resolve_relative_import(self, from_file: Path, import_path: str) -> str | None:
        base_dir = from_file.parent
        resolved = (base_dir / import_path).resolve()

        try:
            relative = resolved.relative_to(self.project_path)
            return self._to_module_name(str(relative))
        except ValueError:
            return None

    def _detect_cycles(self) -> None:
        if HAS_NETWORKX:
            G = nx.DiGraph()
            for module, deps in self.import_graph.items():
                for dep in deps:
                    G.add_edge(module, dep)

            cycles = list(nx.simple_cycles(G))
            self.metrics["circular_dependencies"] = len(cycles)

            for cycle in cycles[:10]:
                cycle_str = " -> ".join(cycle) + f" -> {cycle[0]}"
                self.findings.append({
                    "type": "circular_dependency",
                    "severity": "critical" if len(cycle) <= 3 else "warning",
                    "message": f"Circular dependency: {cycle_str}",
                    "modules": cycle,
                })
        else:
            self._detect_cycles_simple()

    def _detect_cycles_simple(self) -> None:
        """Fallback cycle detection without networkx."""
        visited = set()
        rec_stack = set()
        cycles_found = []

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles_found.append(cycle[:])

            path.pop()
            rec_stack.discard(node)

        for module in self.import_graph:
            if module not in visited:
                dfs(module, [])

        self.metrics["circular_dependencies"] = len(cycles_found)

        for cycle in cycles_found[:10]:
            cycle_str = " -> ".join(cycle) + f" -> {cycle[0]}"
            self.findings.append({
                "type": "circular_dependency",
                "severity": "critical" if len(cycle) <= 3 else "warning",
                "message": f"Circular dependency: {cycle_str}",
                "modules": cycle,
            })

    def _calculate_coupling_metrics(self) -> None:
        afferent: dict[str, int] = defaultdict(int)
        efferent: dict[str, int] = defaultdict(int)

        for module, deps in self.import_graph.items():
            efferent[module] = len(deps)
            for dep in deps:
                afferent[dep] += 1

        all_modules = set(list(self.import_graph.keys()) + list(afferent.keys()))
        instability: dict[str, float] = {}

        for module in all_modules:
            ca = afferent.get(module, 0)
            ce = efferent.get(module, 0)
            total = ca + ce
            instability[module] = round(ce / total, 2) if total > 0 else 0.5

        most_depended = sorted(afferent.items(), key=lambda x: x[1], reverse=True)[:10]
        most_dependent = sorted(efferent.items(), key=lambda x: x[1], reverse=True)[:10]
        most_unstable = sorted(instability.items(), key=lambda x: x[1], reverse=True)[:10]

        self.metrics["coupling"] = {
            "most_depended_on": [{"module": m, "dependents": c} for m, c in most_depended],
            "most_dependencies": [{"module": m, "dependencies": c} for m, c in most_dependent],
            "most_unstable": [{"module": m, "instability": i} for m, i in most_unstable],
        }

        for module, deps_count in most_dependent:
            if deps_count > 15:
                self.findings.append({
                    "type": "coupling",
                    "severity": "warning",
                    "message": f"High efferent coupling: '{module}' depends on {deps_count} modules. Consider breaking it up.",
                })

        for module, dep_count in most_depended:
            if dep_count > 20:
                self.findings.append({
                    "type": "coupling",
                    "severity": "info",
                    "message": f"High afferent coupling: '{module}' is depended on by {dep_count} modules. Changes here have wide impact.",
                })

    def _analyze_external_deps(self) -> None:
        project_type = self.metrics.get("project_type", "unknown")

        if "javascript" in project_type or "typescript" in project_type:
            self._analyze_npm_deps()
        elif project_type == "python":
            self._analyze_python_deps()
        elif project_type == "go":
            self._analyze_go_deps()

    def _analyze_npm_deps(self) -> None:
        pkg_json = self.project_path / "package.json"
        if not pkg_json.exists():
            return

        try:
            pkg = json.loads(pkg_json.read_text())
        except (json.JSONDecodeError, OSError):
            return

        deps = pkg.get("dependencies", {})
        dev_deps = pkg.get("devDependencies", {})

        self.metrics["npm_dependencies"] = len(deps)
        self.metrics["npm_dev_dependencies"] = len(dev_deps)

        if len(deps) > 50:
            self.findings.append({
                "type": "dependencies",
                "severity": "warning",
                "message": f"High number of production dependencies ({len(deps)}). Consider auditing for unused packages.",
            })

        for name, version in deps.items():
            self.external_deps.setdefault(name, {"type": "npm", "imported_by": []})
            self.external_deps[name]["version"] = version
            self.external_deps[name]["is_dev"] = False

        for name, version in dev_deps.items():
            self.external_deps.setdefault(name, {"type": "npm", "imported_by": []})
            self.external_deps[name]["version"] = version
            self.external_deps[name]["is_dev"] = True

    def _analyze_python_deps(self) -> None:
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                lines = req_file.read_text().strip().split("\n")
                deps = [l.strip() for l in lines if l.strip() and not l.startswith("#") and not l.startswith("-")]
                self.metrics["python_dependencies"] = len(deps)

                for dep in deps:
                    name = re.split(r'[>=<!\[]', dep)[0].strip()
                    if name:
                        self.external_deps.setdefault(name, {"type": "pip", "imported_by": []})
                        self.external_deps[name]["version_spec"] = dep
            except OSError:
                pass

    def _analyze_go_deps(self) -> None:
        go_mod = self.project_path / "go.mod"
        if not go_mod.exists():
            return

        try:
            content = go_mod.read_text()
            require_pattern = re.compile(r'^\s+([\w./\-]+)\s+(v[\w.\-]+)', re.MULTILINE)
            deps = require_pattern.findall(content)
            self.metrics["go_dependencies"] = len(deps)

            for name, version in deps:
                self.external_deps.setdefault(name, {"type": "go", "imported_by": []})
                self.external_deps[name]["version"] = version
        except OSError:
            pass

    def _assess_health(self) -> None:
        health_score = 100

        cycles = self.metrics.get("circular_dependencies", 0)
        if cycles > 0:
            health_score -= min(cycles * 10, 30)

        total_modules = self.metrics.get("total_modules", 0)
        if total_modules > 100:
            health_score -= 5
        if total_modules > 200:
            health_score -= 10

        coupling = self.metrics.get("coupling", {})
        high_efferent = sum(1 for m in coupling.get("most_dependencies", []) if m["dependencies"] > 15)
        health_score -= min(high_efferent * 5, 20)

        total_external = len(self.external_deps)
        if total_external > 80:
            health_score -= 10
        elif total_external > 50:
            health_score -= 5

        health_score = max(0, min(100, health_score))
        self.metrics["health_score"] = health_score

        if health_score >= 80:
            grade = "A"
        elif health_score >= 60:
            grade = "B"
        elif health_score >= 40:
            grade = "C"
        elif health_score >= 20:
            grade = "D"
        else:
            grade = "F"

        self.metrics["health_grade"] = grade


def format_markdown(result: dict) -> str:
    lines = [f"# Dependency Analysis: {Path(result['project']).name}", ""]

    m = result["metrics"]
    lines.append("## Overview")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Project Type | {m.get('project_type', 'N/A')} |")
    lines.append(f"| Total Modules | {m.get('total_modules', 0)} |")
    lines.append(f"| Total Internal Imports | {m.get('total_imports', 0)} |")
    lines.append(f"| Circular Dependencies | {m.get('circular_dependencies', 0)} |")
    lines.append(f"| Health Score | {m.get('health_score', 'N/A')}/100 ({m.get('health_grade', 'N/A')}) |")
    lines.append("")

    if "npm_dependencies" in m:
        lines.append(f"| NPM Dependencies | {m['npm_dependencies']} prod + {m.get('npm_dev_dependencies', 0)} dev |")
    if "python_dependencies" in m:
        lines.append(f"| Python Dependencies | {m['python_dependencies']} |")
    if "go_dependencies" in m:
        lines.append(f"| Go Dependencies | {m['go_dependencies']} |")
    lines.append("")

    coupling = m.get("coupling", {})
    if coupling.get("most_depended_on"):
        lines.append("## Most Depended-On Modules (High Impact)")
        lines.append("")
        lines.append("| Module | Dependents |")
        lines.append("|--------|-----------|")
        for item in coupling["most_depended_on"][:5]:
            lines.append(f"| {item['module']} | {item['dependents']} |")
        lines.append("")

    if coupling.get("most_dependencies"):
        lines.append("## Modules with Most Dependencies (High Coupling)")
        lines.append("")
        lines.append("| Module | Dependencies |")
        lines.append("|--------|-------------|")
        for item in coupling["most_dependencies"][:5]:
            lines.append(f"| {item['module']} | {item['dependencies']} |")
        lines.append("")

    findings = result["findings"]
    if findings:
        lines.append("## Findings")
        lines.append("")
        for f in findings:
            icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(f["severity"], "⚪")
            lines.append(f"- {icon} **{f['severity'].upper()}** [{f['type']}]: {f['message']}")
        lines.append("")

    ext_deps = result.get("external_dependencies", {})
    if ext_deps:
        lines.append(f"## External Dependencies ({len(ext_deps)} total)")
        lines.append("")
        sorted_deps = sorted(ext_deps.items(), key=lambda x: len(x[1].get("imported_by", [])), reverse=True)
        lines.append("| Package | Type | Imported By |")
        lines.append("|---------|------|------------|")
        for name, info in sorted_deps[:20]:
            dep_type = info.get("type", "?")
            imported_count = len(info.get("imported_by", []))
            lines.append(f"| {name} | {dep_type} | {imported_count} modules |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dependency Analyzer")
    parser.add_argument("project_path", help="Path to the project to analyze")
    parser.add_argument("--depth", type=int, default=3, help="Module grouping depth")
    parser.add_argument("--check-cycles", action="store_true", help="Only check for circular dependencies")
    parser.add_argument("--health", action="store_true", help="Show health report")
    parser.add_argument("--format", choices=["json", "md"], default="md", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    analyzer = DependencyAnalyzer(args.project_path, depth=args.depth)
    result = analyzer.analyze()

    if args.check_cycles:
        cycles = [f for f in result["findings"] if f["type"] == "circular_dependency"]
        if cycles:
            print(f"Found {len(cycles)} circular dependency(ies):\n")
            for c in cycles:
                print(f"  {c['severity'].upper()}: {c['message']}")
            sys.exit(1)
        else:
            print("No circular dependencies found.")
            sys.exit(0)

    if args.format == "json":
        output = json.dumps(result, indent=2)
    else:
        output = format_markdown(result)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
