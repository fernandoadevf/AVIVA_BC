#!/usr/bin/env python3
"""
Database Migration Tool — Schema analysis, migration generation, and query optimization.

Analyzes PostgreSQL schemas for anti-patterns, generates migration files,
and provides query optimization recommendations.

Usage:
    python database_migration_tool.py <project-path> --analyze
    python database_migration_tool.py <project-path> --generate --name add_user_roles
    python database_migration_tool.py <project-path> --optimize --verbose
"""

import argparse
import os
import sys
import re
import json
import datetime
from pathlib import Path
from textwrap import dedent


ANTI_PATTERNS = [
    {
        "name": "Missing Foreign Key Index",
        "severity": "HIGH",
        "pattern": r"REFERENCES\s+\w+\s*\(\s*\w+\s*\)",
        "check": "fk_without_index",
        "fix": "CREATE INDEX on the foreign key column",
    },
    {
        "name": "SELECT * Usage",
        "severity": "MEDIUM",
        "pattern": r"SELECT\s+\*\s+FROM",
        "check": "select_star",
        "fix": "Specify only needed columns",
    },
    {
        "name": "Missing WHERE on UPDATE/DELETE",
        "severity": "CRITICAL",
        "pattern": r"(UPDATE|DELETE\s+FROM)\s+\w+\s*(?!.*WHERE)",
        "check": "missing_where",
        "fix": "Always include a WHERE clause on UPDATE/DELETE",
    },
    {
        "name": "String Concatenation in Query",
        "severity": "CRITICAL",
        "pattern": r"(\+\s*['\"]|['\"\s]\s*\+|\$\{|f['\"].*\{)",
        "check": "sql_injection_risk",
        "fix": "Use parameterized queries ($1, $2) instead of string interpolation",
    },
    {
        "name": "No Pagination on List Query",
        "severity": "MEDIUM",
        "pattern": r"findMany\s*\(\s*\{(?!.*take)(?!.*limit)",
        "check": "missing_pagination",
        "fix": "Add LIMIT/OFFSET or cursor-based pagination",
    },
]

MIGRATION_TEMPLATE_SQL = dedent("""\
    -- Migration: {name}
    -- Created: {timestamp}

    -- UP
    BEGIN;

    -- Add your migration SQL here
    -- Example:
    -- ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
    -- CREATE INDEX CONCURRENTLY idx_users_role ON users(role);

    COMMIT;

    -- DOWN
    -- BEGIN;
    -- ALTER TABLE users DROP COLUMN role;
    -- COMMIT;
""")

MIGRATION_TEMPLATE_PRISMA = dedent("""\
    // Migration: {name}
    // Created: {timestamp}
    //
    // After editing your schema.prisma, run:
    //   npx prisma migrate dev --name {name}
    //
    // Example schema changes:
    //
    // model User {{
    //   id    String @id @default(cuid())
    //   email String @unique
    //   role  String @default("user")  // <- new field
    //   @@index([role])                 // <- new index
    // }}
""")


def find_project_files(project_path: Path, extensions: list[str]) -> list[Path]:
    files = []
    exclude_dirs = {"node_modules", ".git", "dist", "build", "__pycache__", ".next", "venv"}
    for ext in extensions:
        for f in project_path.rglob(f"*{ext}"):
            if not any(part in exclude_dirs for part in f.parts):
                files.append(f)
    return files


def analyze_schema(project_path: Path, verbose: bool = False):
    print("\n🔍 Analyzing project for database anti-patterns...\n")

    files = find_project_files(project_path, [".ts", ".js", ".py", ".sql", ".prisma"])
    if not files:
        print("  ⚠ No source files found to analyze.")
        return

    issues = []
    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for ap in ANTI_PATTERNS:
            matches = list(re.finditer(ap["pattern"], content, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                issues.append({
                    "file": str(filepath.relative_to(project_path)),
                    "line": line_num,
                    "name": ap["name"],
                    "severity": ap["severity"],
                    "fix": ap["fix"],
                    "snippet": content[max(0, match.start() - 20):match.end() + 20].strip(),
                })

    if not issues:
        print("  ✅ No anti-patterns detected!\n")
        return

    by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
    for issue in issues:
        by_severity.get(issue["severity"], []).append(issue)

    total = len(issues)
    print(f"  Found {total} issue(s):\n")

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = by_severity[severity]
        if not items:
            continue
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}[severity]
        print(f"  {icon} {severity} ({len(items)})")
        for item in items:
            print(f"     {item['file']}:{item['line']} — {item['name']}")
            print(f"       Fix: {item['fix']}")
            if verbose:
                print(f"       Context: ...{item['snippet']}...")
            print()

    print(f"\n  Summary: {len(by_severity['CRITICAL'])} critical, {len(by_severity['HIGH'])} high, "
          f"{len(by_severity['MEDIUM'])} medium, {len(by_severity['LOW'])} low\n")


def generate_migration(project_path: Path, name: str, orm: str):
    print(f"\n📝 Generating migration: {name}\n")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = re.sub(r"[^a-z0-9_]", "_", name.lower())

    if orm == "prisma":
        migrations_dir = project_path / "prisma" / "migrations" / f"{timestamp}_{safe_name}"
        migrations_dir.mkdir(parents=True, exist_ok=True)
        filepath = migrations_dir / "migration.sql"
        content = MIGRATION_TEMPLATE_SQL.format(name=safe_name, timestamp=timestamp)
        filepath.write_text(content)
        print(f"  ✓ Created {filepath.relative_to(project_path)}")

        hint_path = migrations_dir / "README.md"
        hint_path.write_text(MIGRATION_TEMPLATE_PRISMA.format(name=safe_name, timestamp=timestamp))
        print(f"  ✓ Created {hint_path.relative_to(project_path)}")
    else:
        migrations_dir = project_path / "migrations"
        migrations_dir.mkdir(parents=True, exist_ok=True)
        filepath = migrations_dir / f"{timestamp}_{safe_name}.sql"
        content = MIGRATION_TEMPLATE_SQL.format(name=safe_name, timestamp=timestamp)
        filepath.write_text(content)
        print(f"  ✓ Created {filepath.relative_to(project_path)}")

    print(f"\n✅ Migration '{safe_name}' generated.\n")


def optimize_queries(project_path: Path, verbose: bool = False):
    print("\n⚡ Analyzing queries for optimization opportunities...\n")

    files = find_project_files(project_path, [".ts", ".js", ".py", ".sql"])
    recommendations = []

    optimization_checks = [
        {
            "pattern": r"findMany\s*\(\s*\)",
            "issue": "findMany() without filters or limits",
            "recommendation": "Add where, take/skip, or select to avoid loading entire tables",
        },
        {
            "pattern": r"include:\s*\{[^}]*include:",
            "issue": "Deeply nested includes (potential N+1)",
            "recommendation": "Limit include depth to 2 levels; use separate queries or DataLoader for deeper relations",
        },
        {
            "pattern": r"for\s*\(.*\)\s*\{[^}]*await\s+.*\.(find|query|select|update|delete)",
            "issue": "Database query inside a loop (N+1 pattern)",
            "recommendation": "Batch queries using WHERE IN, Promise.all, or DataLoader",
        },
        {
            "pattern": r"ORDER\s+BY\s+\w+(?!.*INDEX)",
            "issue": "ORDER BY without apparent index",
            "recommendation": "Ensure an index exists on the ORDER BY column(s)",
        },
        {
            "pattern": r"LIKE\s+['\"]%",
            "issue": "Leading wildcard LIKE query (cannot use B-tree index)",
            "recommendation": "Use full-text search (tsvector/GIN) or trigram index (pg_trgm) instead",
        },
    ]

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for check in optimization_checks:
            matches = list(re.finditer(check["pattern"], content, re.IGNORECASE | re.DOTALL))
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                recommendations.append({
                    "file": str(filepath.relative_to(project_path)),
                    "line": line_num,
                    "issue": check["issue"],
                    "recommendation": check["recommendation"],
                })

    if not recommendations:
        print("  ✅ No obvious optimization issues found!\n")
        return

    print(f"  Found {len(recommendations)} optimization opportunity(ies):\n")
    for rec in recommendations:
        print(f"  📌 {rec['file']}:{rec['line']}")
        print(f"     Issue: {rec['issue']}")
        print(f"     Fix: {rec['recommendation']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Database Migration Tool — Analyze, generate, optimize")
    parser.add_argument("project_path", help="Path to the project root")
    parser.add_argument("--analyze", action="store_true", help="Analyze schema for anti-patterns")
    parser.add_argument("--generate", action="store_true", help="Generate a new migration file")
    parser.add_argument("--optimize", action="store_true", help="Analyze queries for optimization")
    parser.add_argument("--name", help="Migration name (used with --generate)")
    parser.add_argument("--orm", choices=["prisma", "knex", "raw"], default="prisma", help="ORM/migration tool")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)

    if not any([args.analyze, args.generate, args.optimize]):
        print("Error: Specify at least one action: --analyze, --generate, or --optimize")
        sys.exit(1)

    if args.analyze:
        analyze_schema(project_path, args.verbose)

    if args.generate:
        if not args.name:
            print("Error: --name is required with --generate")
            sys.exit(1)
        generate_migration(project_path, args.name, args.orm)

    if args.optimize:
        optimize_queries(project_path, args.verbose)


if __name__ == "__main__":
    main()
