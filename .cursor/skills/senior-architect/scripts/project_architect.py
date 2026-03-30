#!/usr/bin/env python3
"""
Project Architect
Analyzes project structure and produces architecture recommendations.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


class ProjectAnalyzer:
    def __init__(self, project_path: str, verbose: bool = False):
        self.project_path = Path(project_path).resolve()
        self.verbose = verbose
        self.findings: list[dict] = []
        self.metrics: dict[str, Any] = {}
        self.recommendations: list[dict] = []

        self.skip_dirs = {
            "node_modules", ".git", "__pycache__", ".next", "dist", "build",
            ".cache", "coverage", ".nyc_output", "vendor", ".venv", "venv",
            "env", ".env", ".tox", ".mypy_cache", ".pytest_cache",
        }

    def analyze(self) -> dict:
        if not self.project_path.exists():
            print(f"Error: Path '{self.project_path}' does not exist.")
            sys.exit(1)

        self._collect_file_metrics()
        self._detect_architecture_pattern()
        self._analyze_project_structure()
        self._check_layer_separation()
        self._check_config_management()
        self._check_error_handling()
        self._check_testing()
        self._check_security_posture()
        self._check_api_design()
        self._generate_recommendations()

        return {
            "project": str(self.project_path),
            "metrics": self.metrics,
            "findings": self.findings,
            "recommendations": self.recommendations,
        }

    def _collect_file_metrics(self) -> None:
        extensions: dict[str, int] = {}
        total_files = 0
        total_dirs = 0
        total_lines = 0
        largest_files: list[tuple[str, int]] = []

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            total_dirs += len(dirs)

            for f in files:
                filepath = Path(root) / f
                total_files += 1
                ext = filepath.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1

                try:
                    line_count = sum(1 for _ in open(filepath, errors="ignore"))
                    total_lines += line_count
                    largest_files.append((str(filepath.relative_to(self.project_path)), line_count))
                except (OSError, UnicodeDecodeError):
                    pass

        largest_files.sort(key=lambda x: x[1], reverse=True)

        self.metrics = {
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_lines": total_lines,
            "file_extensions": dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:20]),
            "largest_files": [{"path": p, "lines": l} for p, l in largest_files[:10]],
            "avg_file_size": round(total_lines / max(total_files, 1), 1),
        }

        for path, lines in largest_files[:5]:
            if lines > 500:
                self.findings.append({
                    "type": "complexity",
                    "severity": "warning" if lines < 1000 else "critical",
                    "message": f"Large file detected: {path} ({lines} lines)",
                    "file": path,
                })

    def _detect_architecture_pattern(self) -> None:
        root = self.project_path
        pattern = "unknown"
        confidence = "low"

        has_packages = (root / "packages").is_dir() or (root / "apps").is_dir()
        has_services = (root / "services").is_dir() or (root / "microservices").is_dir()
        has_docker_compose = (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists()
        has_lerna = (root / "lerna.json").exists()
        has_nx = (root / "nx.json").exists()
        has_turborepo = (root / "turbo.json").exists()
        workspaces_file = root / "pnpm-workspace.yaml"
        has_workspaces = workspaces_file.exists() or has_lerna or has_nx or has_turborepo

        if has_services and has_docker_compose:
            pattern = "microservices"
            confidence = "high"
        elif has_packages or has_workspaces:
            if has_services:
                pattern = "modular_monolith"
                confidence = "high"
            else:
                pattern = "monorepo"
                confidence = "high"
        elif has_docker_compose:
            pattern = "multi_container"
            confidence = "medium"
        else:
            src_dirs = [d for d in root.iterdir() if d.is_dir() and d.name not in self.skip_dirs]
            if len(src_dirs) <= 5:
                pattern = "monolith"
                confidence = "medium"
            else:
                pattern = "monolith"
                confidence = "low"

        self.metrics["architecture_pattern"] = pattern
        self.metrics["pattern_confidence"] = confidence

        self.findings.append({
            "type": "architecture",
            "severity": "info",
            "message": f"Detected architecture pattern: {pattern} (confidence: {confidence})",
        })

    def _analyze_project_structure(self) -> None:
        root = self.project_path
        structure_score = 0
        max_score = 0

        checks = [
            (root / "src", "Source directory (src/)"),
            (root / "tests", "Tests directory (tests/)"),
            (root / "test", "Tests directory (test/)"),
            (root / "__tests__", "Tests directory (__tests__/)"),
            (root / "docs", "Documentation directory (docs/)"),
            (root / ".github", "GitHub config (.github/)"),
            (root / ".gitignore", ".gitignore file"),
            (root / "README.md", "README.md"),
        ]

        for path, description in checks:
            max_score += 1
            if path.exists():
                structure_score += 1
            elif self.verbose:
                self.findings.append({
                    "type": "structure",
                    "severity": "info",
                    "message": f"Missing: {description}",
                })

        has_tests = any((root / d).exists() for d in ["tests", "test", "__tests__", "spec"])
        if not has_tests:
            test_files = list(root.rglob("*.test.*")) + list(root.rglob("*.spec.*")) + list(root.rglob("test_*.py"))
            has_tests = len(test_files) > 0

        if not has_tests:
            self.findings.append({
                "type": "testing",
                "severity": "critical",
                "message": "No test files or test directories detected",
            })

        self.metrics["structure_score"] = f"{structure_score}/{max_score}"

    def _check_layer_separation(self) -> None:
        root = self.project_path
        layers_found = []

        layer_indicators = {
            "presentation": ["components", "pages", "views", "screens", "ui", "templates"],
            "business": ["services", "usecases", "domain", "logic", "handlers"],
            "data": ["repositories", "models", "entities", "db", "prisma", "migrations"],
            "infrastructure": ["config", "infra", "middleware", "utils", "helpers", "lib"],
        }

        for layer, dirs in layer_indicators.items():
            for d in dirs:
                matches = list(root.rglob(d))
                real_matches = [m for m in matches if m.is_dir() and not any(s in str(m) for s in self.skip_dirs)]
                if real_matches:
                    layers_found.append(layer)
                    break

        self.metrics["layers_detected"] = layers_found

        if len(layers_found) < 2:
            self.findings.append({
                "type": "architecture",
                "severity": "warning",
                "message": f"Poor layer separation: only {len(layers_found)} layer(s) detected ({', '.join(layers_found) or 'none'}). Consider separating presentation, business, and data layers.",
            })

    def _check_config_management(self) -> None:
        root = self.project_path

        env_file = root / ".env"
        env_example = root / ".env.example"
        env_local = root / ".env.local"
        gitignore = root / ".gitignore"

        if env_file.exists():
            gitignore_content = ""
            if gitignore.exists():
                gitignore_content = gitignore.read_text(errors="ignore")

            if ".env" not in gitignore_content:
                self.findings.append({
                    "type": "security",
                    "severity": "critical",
                    "message": ".env file exists but is NOT in .gitignore — secrets may be committed!",
                })

            if not env_example.exists() and not env_local.exists():
                self.findings.append({
                    "type": "config",
                    "severity": "warning",
                    "message": ".env exists but no .env.example found. New developers won't know required env vars.",
                })

    def _check_error_handling(self) -> None:
        error_patterns_found = 0
        files_checked = 0

        for ext in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.go"):
            for filepath in self.project_path.rglob(ext):
                if any(s in str(filepath) for s in self.skip_dirs):
                    continue
                files_checked += 1
                try:
                    content = filepath.read_text(errors="ignore")
                    if "try" in content or "catch" in content or "except" in content or "recover" in content:
                        error_patterns_found += 1
                except OSError:
                    pass

        if files_checked > 0:
            ratio = error_patterns_found / files_checked
            self.metrics["error_handling_ratio"] = round(ratio, 2)

            if ratio < 0.1:
                self.findings.append({
                    "type": "reliability",
                    "severity": "warning",
                    "message": f"Low error handling coverage: only {error_patterns_found}/{files_checked} files have error handling patterns.",
                })

    def _check_testing(self) -> None:
        test_files = 0
        source_files = 0

        for ext in ("*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.go"):
            for filepath in self.project_path.rglob(ext):
                if any(s in str(filepath) for s in self.skip_dirs):
                    continue
                name = filepath.name.lower()
                if any(p in name for p in (".test.", ".spec.", "test_", "_test.")):
                    test_files += 1
                else:
                    source_files += 1

        self.metrics["test_files"] = test_files
        self.metrics["source_files"] = source_files
        if source_files > 0:
            self.metrics["test_ratio"] = round(test_files / source_files, 2)

        if source_files > 10 and test_files == 0:
            self.findings.append({
                "type": "testing",
                "severity": "critical",
                "message": "No test files found in a project with significant source code.",
            })
        elif source_files > 0 and test_files / max(source_files, 1) < 0.2:
            self.findings.append({
                "type": "testing",
                "severity": "warning",
                "message": f"Low test coverage: {test_files} test files for {source_files} source files (ratio: {round(test_files/max(source_files,1), 2)})",
            })

    def _check_security_posture(self) -> None:
        root = self.project_path

        lockfiles = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Pipfile.lock", "poetry.lock", "go.sum"]
        has_lockfile = any((root / lf).exists() for lf in lockfiles)

        if not has_lockfile:
            pkg_managers = ["package.json", "Pipfile", "pyproject.toml", "go.mod"]
            has_pkg_manager = any((root / pm).exists() for pm in pkg_managers)
            if has_pkg_manager:
                self.findings.append({
                    "type": "security",
                    "severity": "warning",
                    "message": "No lockfile found. Dependency versions may be inconsistent across environments.",
                })

        for filepath in root.rglob("*"):
            if any(s in str(filepath) for s in self.skip_dirs):
                continue
            name = filepath.name.lower()
            if name in ("credentials.json", "service-account.json", "id_rsa", "id_ed25519", ".pem"):
                self.findings.append({
                    "type": "security",
                    "severity": "critical",
                    "message": f"Potential secret/credential file detected: {filepath.relative_to(root)}",
                })

    def _check_api_design(self) -> None:
        api_files = []
        for pattern in ("**/routes/**", "**/api/**", "**/controllers/**", "**/handlers/**"):
            for filepath in self.project_path.glob(pattern):
                if filepath.is_file() and not any(s in str(filepath) for s in self.skip_dirs):
                    api_files.append(filepath)

        self.metrics["api_files_detected"] = len(api_files)

        graphql_files = list(self.project_path.rglob("*.graphql")) + list(self.project_path.rglob("*.gql"))
        graphql_files = [f for f in graphql_files if not any(s in str(f) for s in self.skip_dirs)]

        rest_indicators = len(api_files)
        graphql_indicators = len(graphql_files)

        if rest_indicators > 0 and graphql_indicators > 0:
            self.findings.append({
                "type": "api",
                "severity": "info",
                "message": "Both REST and GraphQL patterns detected. Ensure clear API strategy.",
            })

        self.metrics["api_style"] = (
            "graphql" if graphql_indicators > rest_indicators
            else "rest" if rest_indicators > 0
            else "unknown"
        )

    def _generate_recommendations(self) -> None:
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        sorted_findings = sorted(self.findings, key=lambda f: severity_order.get(f["severity"], 3))

        for finding in sorted_findings:
            if finding["severity"] in ("critical", "warning"):
                rec = {
                    "priority": "high" if finding["severity"] == "critical" else "medium",
                    "area": finding["type"],
                    "finding": finding["message"],
                    "suggestion": self._get_suggestion(finding),
                }
                self.recommendations.append(rec)

    def _get_suggestion(self, finding: dict) -> str:
        suggestions = {
            "security": {
                ".env": "Add .env to .gitignore immediately. Create .env.example with placeholder values.",
                "secret": "Move credentials to a secrets manager (e.g., AWS Secrets Manager, Vault). Never commit secrets.",
                "lockfile": "Generate a lockfile: npm install, yarn install, or pip freeze > requirements.txt",
            },
            "testing": {
                "No test": "Set up a testing framework (Jest, pytest, Go testing) and add tests for critical paths first.",
                "Low test": "Increase test coverage. Focus on business logic and API endpoints first.",
            },
            "architecture": {
                "layer": "Reorganize code into clear layers: presentation/ (UI), domain/ (business logic), data/ (persistence).",
            },
            "reliability": {
                "error": "Add try/catch blocks around I/O operations, API calls, and database queries. Implement global error handlers.",
            },
            "complexity": {
                "Large file": "Break this file into smaller, focused modules. Each file should have a single responsibility.",
            },
            "config": {
                ".env.example": "Create .env.example listing all required environment variables with descriptions.",
            },
        }

        area_suggestions = suggestions.get(finding["type"], {})
        for key, suggestion in area_suggestions.items():
            if key.lower() in finding["message"].lower():
                return suggestion

        return "Review and address this finding based on your project's specific requirements."


def format_markdown(result: dict) -> str:
    lines = [f"# Architecture Analysis: {Path(result['project']).name}", ""]

    metrics = result["metrics"]
    lines.append("## Project Metrics")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Files | {metrics.get('total_files', 'N/A')} |")
    lines.append(f"| Total Directories | {metrics.get('total_directories', 'N/A')} |")
    lines.append(f"| Total Lines | {metrics.get('total_lines', 'N/A'):,} |")
    lines.append(f"| Avg File Size | {metrics.get('avg_file_size', 'N/A')} lines |")
    lines.append(f"| Architecture Pattern | {metrics.get('architecture_pattern', 'N/A')} ({metrics.get('pattern_confidence', 'N/A')}) |")
    lines.append(f"| API Style | {metrics.get('api_style', 'N/A')} |")
    lines.append(f"| Test Ratio | {metrics.get('test_ratio', 'N/A')} |")
    lines.append(f"| Structure Score | {metrics.get('structure_score', 'N/A')} |")
    lines.append(f"| Layers Detected | {', '.join(metrics.get('layers_detected', []))} |")
    lines.append("")

    if metrics.get("largest_files"):
        lines.append("### Largest Files")
        lines.append("")
        lines.append("| File | Lines |")
        lines.append("|------|-------|")
        for f in metrics["largest_files"][:5]:
            lines.append(f"| {f['path']} | {f['lines']:,} |")
        lines.append("")

    findings = result["findings"]
    if findings:
        lines.append("## Findings")
        lines.append("")
        for f in findings:
            icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(f["severity"], "⚪")
            lines.append(f"- {icon} **{f['severity'].upper()}** [{f['type']}]: {f['message']}")
        lines.append("")

    recs = result["recommendations"]
    if recs:
        lines.append("## Recommendations")
        lines.append("")
        for i, r in enumerate(recs, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["priority"], "⚪")
            lines.append(f"### {i}. {priority_icon} [{r['area'].upper()}] {r['finding']}")
            lines.append(f"")
            lines.append(f"**Suggestion:** {r['suggestion']}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Project Architect - Architecture Analyzer")
    parser.add_argument("project_path", help="Path to the project to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--format", choices=["json", "md"], default="md", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path (prints to stdout if not specified)")

    args = parser.parse_args()

    analyzer = ProjectAnalyzer(args.project_path, verbose=args.verbose)
    result = analyzer.analyze()

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
