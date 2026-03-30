---
name: senior-architect
description: Comprehensive software architecture skill for designing scalable, maintainable systems using ReactJS, NextJS, NodeJS, Express, React Native, Swift, Kotlin, Flutter, Postgres, GraphQL, Go, Python. Includes architecture diagram generation, system design patterns, tech stack decision frameworks, and dependency analysis. Use when designing system architecture, making technical decisions, creating architecture diagrams, evaluating trade-offs, or defining integration patterns.
---

# Senior Architect

Complete toolkit for senior-level architecture decisions, system design, and technical leadership.

## Quick Start

### Core Scripts

```bash
# Generate architecture diagrams (Mermaid + PlantUML)
python scripts/architecture_diagram_generator.py --type <diagram-type> --output <path>

# Analyze project structure and recommend architecture improvements
python scripts/project_architect.py <project-path> [--verbose] [--format json|md]

# Analyze dependencies, detect cycles, and assess health
python scripts/dependency_analyzer.py <project-path> [--depth <n>] [--format json|md]
```

Install dependencies first:
```bash
pip install -r ~/.cursor/skills/senior-architect/requirements.txt
```

## Architecture Diagram Generator

Generates Mermaid and PlantUML diagrams from project analysis or specifications.

**Supported diagram types:**
| Type | Flag | Description |
|------|------|-------------|
| System Context | `--type context` | C4 Level 1 - system boundaries and actors |
| Container | `--type container` | C4 Level 2 - deployable units |
| Component | `--type component` | C4 Level 3 - internal components |
| Sequence | `--type sequence` | Request flow through services |
| ERD | `--type erd` | Database entity relationships |
| Deployment | `--type deployment` | Infrastructure and deployment topology |

**Options:**
```bash
python scripts/architecture_diagram_generator.py \
  --type container \
  --project-path ./my-app \
  --output ./docs/architecture \
  --format both          # mermaid | plantuml | both
  --title "My System"
```

**From spec file:**
```bash
python scripts/architecture_diagram_generator.py \
  --from-spec spec.yaml \
  --output ./docs
```

Spec YAML format:
```yaml
system: "E-Commerce Platform"
actors:
  - name: Customer
    type: external
containers:
  - name: Web App
    tech: Next.js
    description: Customer-facing SPA
  - name: API Gateway
    tech: Express + GraphQL
    description: Unified API layer
  - name: Order Service
    tech: Node.js
    description: Order processing
  - name: Database
    tech: PostgreSQL
    description: Primary data store
relationships:
  - from: Customer
    to: Web App
    label: "HTTPS"
  - from: Web App
    to: API Gateway
    label: "GraphQL"
  - from: API Gateway
    to: Order Service
    label: "gRPC"
  - from: Order Service
    to: Database
    label: "SQL"
```

## Project Architect

Analyzes a project and produces architecture recommendations.

**Analysis areas:**
- Project structure and organization patterns
- Layer separation (presentation, business, data)
- API design consistency
- Error handling patterns
- Configuration management
- Test coverage structure
- Security posture (env vars, secrets, auth patterns)

```bash
# Full analysis with markdown report
python scripts/project_architect.py ./my-project --verbose --format md

# JSON output for CI integration
python scripts/project_architect.py ./my-project --format json
```

**Output includes:**
- Architecture pattern detection (monolith, microservices, modular monolith)
- Layer violation warnings
- Recommended refactorings with priority
- Complexity hotspots
- Missing patterns (e.g., no error boundary, no retry logic)

## Dependency Analyzer

Deep analysis of project dependencies and their relationships.

```bash
# Analyze internal module dependencies
python scripts/dependency_analyzer.py ./my-project --depth 3

# Check for circular dependencies
python scripts/dependency_analyzer.py ./my-project --check-cycles

# Full health report
python scripts/dependency_analyzer.py ./my-project --health --format md
```

**Capabilities:**
- Internal import graph construction
- Circular dependency detection
- External dependency health (outdated, deprecated, vulnerable)
- Bundle size impact estimation (for JS/TS projects)
- Coupling metrics between modules

## Architecture Decision Framework

When making tech decisions, follow this structured approach:

### 1. Context Gathering
- What problem are we solving?
- What are the constraints (team size, timeline, budget)?
- What existing systems must we integrate with?
- What are the non-functional requirements (latency, throughput, availability)?

### 2. Options Evaluation Matrix

| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| Performance | 0-10 | ? | ? | ? |
| Developer Experience | 0-10 | ? | ? | ? |
| Scalability | 0-10 | ? | ? | ? |
| Maintenance Cost | 0-10 | ? | ? | ? |
| Team Expertise | 0-10 | ? | ? | ? |
| Ecosystem/Community | 0-10 | ? | ? | ? |

### 3. Decision Record (ADR)

```markdown
# ADR-NNN: [Title]

## Status: [Proposed | Accepted | Deprecated | Superseded]

## Context
[Why is this decision needed?]

## Decision
[What was decided and why]

## Consequences
### Positive
- [benefit]
### Negative
- [trade-off]
### Risks
- [risk and mitigation]
```

## Tech Stack Quick Reference

### Frontend Selection
| Need | Recommendation | When to avoid |
|------|---------------|---------------|
| SEO + SSR | Next.js | Pure SPA, no SEO needs |
| Complex SPA | React + Vite | Content-heavy sites |
| Mobile (cross-platform) | React Native or Flutter | Performance-critical native features |
| Mobile (iOS native) | Swift/SwiftUI | Cross-platform requirement |
| Mobile (Android native) | Kotlin/Jetpack Compose | Cross-platform requirement |

### Backend Selection
| Need | Recommendation | When to avoid |
|------|---------------|---------------|
| REST API (JS ecosystem) | Express/Fastify | CPU-intensive workloads |
| GraphQL API | Apollo Server / Yoga | Simple CRUD, internal APIs |
| High concurrency | Go | Rapid prototyping |
| ML/Data pipelines | Python (FastAPI) | Real-time low-latency |
| Microservices | Go or Node.js | Small team, simple domain |

### Database Selection
| Need | Recommendation | When to avoid |
|------|---------------|---------------|
| Relational + ACID | PostgreSQL | Massive write throughput |
| Managed Postgres | Supabase / NeonDB | Full DBA control needed |
| Document store | MongoDB | Complex joins needed |
| Cache layer | Redis | Persistence as primary |
| Search | Elasticsearch / Meilisearch | Simple queries |
| Time series | TimescaleDB | Non-temporal data |

## Common Architecture Patterns

### When to use each pattern:

| Pattern | Best for | Avoid when |
|---------|----------|------------|
| Monolith | Small team, early stage, <5 devs | Multiple teams, independent scaling |
| Modular Monolith | Growing team, clear domains | Need independent deployment |
| Microservices | Large org, independent teams | Small team, unclear boundaries |
| Event-Driven | Async workflows, decoupling | Simple CRUD, strong consistency |
| CQRS | Read/write asymmetry | Simple domains |
| Serverless | Sporadic traffic, event processing | Consistent low-latency |

## Reference Documentation

For detailed guides, the agent should read these files when needed:

- **Architecture Patterns**: [references/architecture_patterns.md](references/architecture_patterns.md) — detailed patterns with code examples, anti-patterns, and real-world scenarios
- **System Design Workflows**: [references/system_design_workflows.md](references/system_design_workflows.md) — step-by-step design processes, capacity planning, optimization strategies
- **Tech Decision Guide**: [references/tech_decision_guide.md](references/tech_decision_guide.md) — deep-dive on each technology, configuration examples, security considerations, scalability guidelines

## Workflow

### Designing a New System

```
Task Progress:
- [ ] Step 1: Gather requirements and constraints
- [ ] Step 2: Identify bounded contexts / domains
- [ ] Step 3: Choose architecture pattern
- [ ] Step 4: Select tech stack using decision matrix
- [ ] Step 5: Generate architecture diagrams
- [ ] Step 6: Write ADR for key decisions
- [ ] Step 7: Define API contracts
- [ ] Step 8: Plan data model
- [ ] Step 9: Define deployment strategy
- [ ] Step 10: Review with dependency analyzer
```

### Evaluating Existing Architecture

```
Task Progress:
- [ ] Step 1: Run project_architect.py for structural analysis
- [ ] Step 2: Run dependency_analyzer.py for coupling analysis
- [ ] Step 3: Generate current-state diagrams
- [ ] Step 4: Identify pain points and bottlenecks
- [ ] Step 5: Propose target architecture
- [ ] Step 6: Create migration roadmap
```
