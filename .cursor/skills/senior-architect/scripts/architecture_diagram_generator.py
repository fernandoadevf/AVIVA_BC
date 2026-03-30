#!/usr/bin/env python3
"""
Architecture Diagram Generator
Generates Mermaid and PlantUML diagrams from project analysis or YAML specs.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


DIAGRAM_TYPES = ["context", "container", "component", "sequence", "erd", "deployment"]


def parse_spec(spec_path: str) -> dict:
    if yaml is None:
        print("Error: pyyaml is required. Install with: pip install pyyaml")
        sys.exit(1)
    with open(spec_path) as f:
        return yaml.safe_load(f)


def scan_project(project_path: str) -> dict:
    """Scan a project directory and infer architecture components."""
    path = Path(project_path)
    if not path.exists():
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)

    spec: dict[str, Any] = {
        "system": path.name,
        "actors": [{"name": "User", "type": "external"}],
        "containers": [],
        "relationships": [],
    }

    indicators = {
        "next.config": ("Web App", "Next.js"),
        "vite.config": ("Web App", "React + Vite"),
        "angular.json": ("Web App", "Angular"),
        "package.json": None,
        "Podfile": ("iOS App", "Swift"),
        "build.gradle": ("Android App", "Kotlin"),
        "pubspec.yaml": ("Mobile App", "Flutter"),
        "go.mod": ("API Service", "Go"),
        "requirements.txt": ("API Service", "Python"),
        "Pipfile": ("API Service", "Python"),
        "pyproject.toml": ("API Service", "Python"),
        "Cargo.toml": ("Service", "Rust"),
        "docker-compose": ("Infrastructure", "Docker"),
        "Dockerfile": ("Container", "Docker"),
        "schema.prisma": ("Database", "PostgreSQL + Prisma"),
        "schema.graphql": ("API Layer", "GraphQL"),
        ".graphql": ("API Layer", "GraphQL"),
    }

    found_containers = set()

    for item in path.rglob("*"):
        if item.is_dir() and item.name in ("node_modules", ".git", "__pycache__", ".next", "dist", "build"):
            continue
        if not item.is_file():
            continue

        name = item.name
        for indicator_key, container_info in indicators.items():
            if indicator_key in name and container_info and container_info[0] not in found_containers:
                found_containers.add(container_info[0])
                spec["containers"].append({
                    "name": container_info[0],
                    "tech": container_info[1],
                    "description": f"Detected from {name}",
                })

    dirs_of_interest = {
        "api": ("API Gateway", "Express/Node.js"),
        "server": ("Backend Server", "Node.js"),
        "backend": ("Backend Service", "Node.js"),
        "frontend": ("Frontend App", "React"),
        "web": ("Web Client", "React"),
        "mobile": ("Mobile App", "React Native"),
        "services": ("Microservices", "Various"),
        "graphql": ("GraphQL API", "GraphQL"),
        "prisma": ("Database Layer", "Prisma + PostgreSQL"),
        "db": ("Database", "PostgreSQL"),
        "infra": ("Infrastructure", "IaC"),
        "terraform": ("Infrastructure", "Terraform"),
        "k8s": ("Orchestration", "Kubernetes"),
        "kubernetes": ("Orchestration", "Kubernetes"),
    }

    for child in path.iterdir():
        if child.is_dir() and child.name.lower() in dirs_of_interest:
            info = dirs_of_interest[child.name.lower()]
            if info[0] not in found_containers:
                found_containers.add(info[0])
                spec["containers"].append({
                    "name": info[0],
                    "tech": info[1],
                    "description": f"Detected from directory '{child.name}'",
                })

    if not spec["containers"]:
        spec["containers"].append({
            "name": "Application",
            "tech": "Unknown",
            "description": "No specific framework detected",
        })

    _infer_relationships(spec)
    return spec


def _infer_relationships(spec: dict) -> None:
    containers = [c["name"] for c in spec["containers"]]
    actors = [a["name"] for a in spec["actors"]]

    frontend_keywords = ("web", "frontend", "app", "client", "mobile", "ios", "android")
    backend_keywords = ("api", "server", "backend", "service", "gateway")
    db_keywords = ("database", "db", "prisma", "data")
    infra_keywords = ("infrastructure", "orchestration", "container")

    frontends = [c for c in containers if any(k in c.lower() for k in frontend_keywords)]
    backends = [c for c in containers if any(k in c.lower() for k in backend_keywords)]
    databases = [c for c in containers if any(k in c.lower() for k in db_keywords)]

    for actor in actors:
        for fe in frontends:
            spec["relationships"].append({"from": actor, "to": fe, "label": "HTTPS"})

    if not frontends and backends:
        for actor in actors:
            spec["relationships"].append({"from": actor, "to": backends[0], "label": "HTTPS"})

    for fe in frontends:
        for be in backends:
            graphql_containers = [c for c in containers if "graphql" in c.lower()]
            if graphql_containers:
                spec["relationships"].append({"from": fe, "to": graphql_containers[0], "label": "GraphQL"})
            else:
                spec["relationships"].append({"from": fe, "to": be, "label": "REST/GraphQL"})

    for be in backends:
        for db in databases:
            spec["relationships"].append({"from": be, "to": db, "label": "SQL/ORM"})


def generate_mermaid_context(spec: dict) -> str:
    lines = ["graph TB"]
    title = spec.get("system", "System")

    for actor in spec.get("actors", []):
        aid = _sanitize_id(actor["name"])
        lines.append(f'    {aid}["{actor["name"]}"]:::actor')

    lines.append(f'    system["{title}"]:::system')

    for actor in spec.get("actors", []):
        aid = _sanitize_id(actor["name"])
        lines.append(f'    {aid} --> system')

    lines.append("")
    lines.append("    classDef actor fill:#08427B,color:#fff,stroke:#073B6F")
    lines.append("    classDef system fill:#1168BD,color:#fff,stroke:#0E5CA6")

    return "\n".join(lines)


def generate_mermaid_container(spec: dict) -> str:
    lines = ["graph TB"]
    title = spec.get("system", "System")

    for actor in spec.get("actors", []):
        aid = _sanitize_id(actor["name"])
        lines.append(f'    {aid}("{actor["name"]}"):::actor')

    lines.append(f"    subgraph {_sanitize_id(title)}[\"{title}\"]")
    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        tech = container.get("tech", "")
        desc = container.get("description", "")
        label = f"{container['name']}"
        if tech:
            label += f"\\n[{tech}]"
        if desc:
            label += f"\\n{desc}"
        lines.append(f'        {cid}["{label}"]:::container')
    lines.append("    end")

    for rel in spec.get("relationships", []):
        fid = _sanitize_id(rel["from"])
        tid = _sanitize_id(rel["to"])
        label = rel.get("label", "")
        if label:
            lines.append(f'    {fid} -->|"{label}"| {tid}')
        else:
            lines.append(f"    {fid} --> {tid}")

    lines.append("")
    lines.append("    classDef actor fill:#08427B,color:#fff,stroke:#073B6F")
    lines.append("    classDef container fill:#438DD5,color:#fff,stroke:#3C7FC0")

    return "\n".join(lines)


def generate_mermaid_component(spec: dict) -> str:
    lines = ["graph LR"]

    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        lines.append(f"    subgraph {cid}[\"{container['name']}\"]")
        lines.append(f'        {cid}_ctrl["Controller"]:::component')
        lines.append(f'        {cid}_svc["Service"]:::component')
        lines.append(f'        {cid}_repo["Repository"]:::component')
        lines.append(f"        {cid}_ctrl --> {cid}_svc --> {cid}_repo")
        lines.append("    end")

    lines.append("")
    lines.append("    classDef component fill:#85BBF0,color:#000,stroke:#78A8D8")

    return "\n".join(lines)


def generate_mermaid_sequence(spec: dict) -> str:
    lines = ["sequenceDiagram"]

    actors = [a["name"] for a in spec.get("actors", [])]
    containers = [c["name"] for c in spec.get("containers", [])]

    all_participants = actors + containers
    for p in all_participants:
        lines.append(f"    participant {_sanitize_id(p)} as {p}")

    for rel in spec.get("relationships", []):
        fid = _sanitize_id(rel["from"])
        tid = _sanitize_id(rel["to"])
        label = rel.get("label", "request")
        lines.append(f"    {fid}->>+{tid}: {label}")
        lines.append(f"    {tid}-->>-{fid}: response")

    return "\n".join(lines)


def generate_mermaid_erd(spec: dict) -> str:
    lines = ["erDiagram"]

    containers = spec.get("containers", [])
    db_containers = [c for c in containers if any(k in c["name"].lower() for k in ("database", "db", "prisma", "data"))]

    entities = []
    for c in containers:
        if c not in db_containers:
            name = _sanitize_id(c["name"]).replace(" ", "")
            entities.append(name)
            lines.append(f"    {name} {{")
            lines.append(f"        uuid id PK")
            lines.append(f'        string name "required"')
            lines.append(f"        timestamp created_at")
            lines.append(f"        timestamp updated_at")
            lines.append("    }")

    for i in range(len(entities) - 1):
        lines.append(f"    {entities[i]} ||--o{{ {entities[i+1]} : references")

    return "\n".join(lines)


def generate_mermaid_deployment(spec: dict) -> str:
    lines = ["graph TB"]

    lines.append('    subgraph cloud["Cloud Provider"]')
    lines.append('        subgraph lb["Load Balancer"]')
    lines.append('            nginx["Nginx/ALB"]:::infra')
    lines.append("        end")

    lines.append('        subgraph compute["Compute"]')
    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        tech = container.get("tech", "")
        lines.append(f'            {cid}["{container["name"]}\\n[{tech}]"]:::container')
    lines.append("        end")

    lines.append('        subgraph storage["Storage"]')
    lines.append('            db["PostgreSQL"]:::database')
    lines.append('            cache["Redis"]:::database')
    lines.append("        end")
    lines.append("    end")

    lines.append("    nginx --> compute")
    lines.append("    compute --> storage")

    lines.append("")
    lines.append("    classDef infra fill:#999,color:#fff,stroke:#888")
    lines.append("    classDef container fill:#438DD5,color:#fff,stroke:#3C7FC0")
    lines.append("    classDef database fill:#F5A623,color:#000,stroke:#D4911E")

    return "\n".join(lines)


def generate_plantuml_context(spec: dict) -> str:
    lines = ["@startuml", f'title System Context - {spec.get("system", "System")}', ""]

    for actor in spec.get("actors", []):
        lines.append(f'actor "{actor["name"]}" as {_sanitize_id(actor["name"])}')

    lines.append(f'package "{spec.get("system", "System")}" {{')
    lines.append(f'  [System] as system')
    lines.append("}")

    for actor in spec.get("actors", []):
        aid = _sanitize_id(actor["name"])
        lines.append(f"{aid} --> system")

    lines.append("@enduml")
    return "\n".join(lines)


def generate_plantuml_container(spec: dict) -> str:
    title = spec.get("system", "System")
    lines = ["@startuml", f"title Container Diagram - {title}", ""]

    for actor in spec.get("actors", []):
        lines.append(f'actor "{actor["name"]}" as {_sanitize_id(actor["name"])}')

    lines.append("")
    lines.append(f'package "{title}" {{')
    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        tech = container.get("tech", "")
        desc = container.get("description", "")
        stereotype = f" <<{tech}>>" if tech else ""
        lines.append(f'  [{container["name"]}]{stereotype} as {cid}')
    lines.append("}")

    lines.append("")
    for rel in spec.get("relationships", []):
        fid = _sanitize_id(rel["from"])
        tid = _sanitize_id(rel["to"])
        label = rel.get("label", "")
        if label:
            lines.append(f'{fid} --> {tid} : "{label}"')
        else:
            lines.append(f"{fid} --> {tid}")

    lines.append("@enduml")
    return "\n".join(lines)


def generate_plantuml_component(spec: dict) -> str:
    lines = ["@startuml", f'title Component Diagram - {spec.get("system", "System")}', ""]

    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        lines.append(f'package "{container["name"]}" {{')
        lines.append(f"  [{cid}_Controller] as {cid}_ctrl")
        lines.append(f"  [{cid}_Service] as {cid}_svc")
        lines.append(f"  [{cid}_Repository] as {cid}_repo")
        lines.append(f"  {cid}_ctrl --> {cid}_svc")
        lines.append(f"  {cid}_svc --> {cid}_repo")
        lines.append("}")
        lines.append("")

    lines.append("@enduml")
    return "\n".join(lines)


def generate_plantuml_sequence(spec: dict) -> str:
    lines = ["@startuml", f'title Sequence Diagram - {spec.get("system", "System")}', ""]

    for actor in spec.get("actors", []):
        lines.append(f'actor "{actor["name"]}" as {_sanitize_id(actor["name"])}')
    for container in spec.get("containers", []):
        lines.append(f'participant "{container["name"]}" as {_sanitize_id(container["name"])}')

    lines.append("")
    for rel in spec.get("relationships", []):
        fid = _sanitize_id(rel["from"])
        tid = _sanitize_id(rel["to"])
        label = rel.get("label", "request")
        lines.append(f"{fid} -> {tid} : {label}")
        lines.append(f"{tid} --> {fid} : response")

    lines.append("@enduml")
    return "\n".join(lines)


def generate_plantuml_erd(spec: dict) -> str:
    lines = ["@startuml", f'title ERD - {spec.get("system", "System")}', ""]

    containers = spec.get("containers", [])
    db_containers = [c for c in containers if any(k in c["name"].lower() for k in ("database", "db", "prisma"))]
    entities = []

    for c in containers:
        if c not in db_containers:
            name = _sanitize_id(c["name"]).replace(" ", "")
            entities.append(name)
            lines.append(f"entity {name} {{")
            lines.append(f"  * id : UUID <<PK>>")
            lines.append(f"  --")
            lines.append(f"  * name : VARCHAR(255)")
            lines.append(f"  created_at : TIMESTAMP")
            lines.append(f"  updated_at : TIMESTAMP")
            lines.append("}")
            lines.append("")

    for i in range(len(entities) - 1):
        lines.append(f"{entities[i]} ||--o{{ {entities[i+1]}")

    lines.append("@enduml")
    return "\n".join(lines)


def generate_plantuml_deployment(spec: dict) -> str:
    lines = ["@startuml", f'title Deployment Diagram - {spec.get("system", "System")}', ""]

    lines.append('cloud "Cloud Provider" {')
    lines.append('  node "Load Balancer" {')
    lines.append("    [Nginx/ALB] as lb")
    lines.append("  }")
    lines.append('  node "Compute" {')
    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        tech = container.get("tech", "")
        lines.append(f'    [{container["name"]}] as {cid} <<{tech}>>')
    lines.append("  }")
    lines.append('  database "Storage" {')
    lines.append("    [PostgreSQL] as db")
    lines.append("    [Redis] as cache")
    lines.append("  }")
    lines.append("}")

    lines.append("")
    lines.append("lb --> compute")

    for container in spec.get("containers", []):
        cid = _sanitize_id(container["name"])
        lines.append(f"{cid} --> db")

    lines.append("@enduml")
    return "\n".join(lines)


MERMAID_GENERATORS = {
    "context": generate_mermaid_context,
    "container": generate_mermaid_container,
    "component": generate_mermaid_component,
    "sequence": generate_mermaid_sequence,
    "erd": generate_mermaid_erd,
    "deployment": generate_mermaid_deployment,
}

PLANTUML_GENERATORS = {
    "context": generate_plantuml_context,
    "container": generate_plantuml_container,
    "component": generate_plantuml_component,
    "sequence": generate_plantuml_sequence,
    "erd": generate_plantuml_erd,
    "deployment": generate_plantuml_deployment,
}


def _sanitize_id(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")


def write_output(content: str, output_path: str, filename: str) -> str:
    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Architecture Diagram Generator")
    parser.add_argument("--type", choices=DIAGRAM_TYPES, default="container", help="Diagram type to generate")
    parser.add_argument("--project-path", help="Path to project to analyze")
    parser.add_argument("--from-spec", help="Path to YAML spec file")
    parser.add_argument("--output", default="./docs/architecture", help="Output directory")
    parser.add_argument("--format", choices=["mermaid", "plantuml", "both"], default="both", help="Output format")
    parser.add_argument("--title", help="Override system title")
    parser.add_argument("--all-types", action="store_true", help="Generate all diagram types")

    args = parser.parse_args()

    if args.from_spec:
        spec = parse_spec(args.from_spec)
    elif args.project_path:
        spec = scan_project(args.project_path)
    else:
        print("Error: Provide either --project-path or --from-spec")
        sys.exit(1)

    if args.title:
        spec["system"] = args.title

    types_to_generate = DIAGRAM_TYPES if args.all_types else [args.type]
    generated_files = []

    for diagram_type in types_to_generate:
        if args.format in ("mermaid", "both"):
            generator = MERMAID_GENERATORS[diagram_type]
            content = generator(spec)
            filepath = write_output(content, args.output, f"{diagram_type}_diagram.mmd")
            generated_files.append(filepath)
            print(f"  Mermaid {diagram_type}: {filepath}")

        if args.format in ("plantuml", "both"):
            generator = PLANTUML_GENERATORS[diagram_type]
            content = generator(spec)
            filepath = write_output(content, args.output, f"{diagram_type}_diagram.puml")
            generated_files.append(filepath)
            print(f"  PlantUML {diagram_type}: {filepath}")

    print(f"\nGenerated {len(generated_files)} diagram(s) in {args.output}")


if __name__ == "__main__":
    main()
