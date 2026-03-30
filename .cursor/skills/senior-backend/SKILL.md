---
name: senior-backend
description: Comprehensive backend development skill for building scalable backend systems using NodeJS, Express, Go, Python, Postgres, GraphQL, REST APIs. Includes API scaffolding, database optimization, security implementation, and performance tuning. Use when designing APIs, optimizing database queries, implementing business logic, handling authentication/authorization, or reviewing backend code.
---

# Senior Backend

Complete toolkit for senior backend development with modern tools and best practices.

## Quick Start

### Main Capabilities

Three core capabilities through automated scripts:

```bash
# API Scaffolder — generate REST/GraphQL endpoints with validation, auth, tests
python scripts/api_scaffolder.py [options]

# Database Migration Tool — analyze schemas, generate migrations, optimize queries
python scripts/database_migration_tool.py [options]

# API Load Tester — benchmark endpoints, detect bottlenecks, generate reports
python scripts/api_load_tester.py [options]
```

## Core Capabilities

### 1. API Scaffolder

Generates production-ready API endpoints with built-in best practices.

**Features:**
- REST & GraphQL endpoint generation with proper HTTP semantics
- Input validation (Zod/Joi for Node, Pydantic for Python)
- Auth middleware integration (JWT, API keys, OAuth)
- Auto-generated tests and OpenAPI/Swagger docs
- Supports Express, Fastify, Flask, Gin

**Usage:**
```bash
# Scaffold a REST CRUD resource
python scripts/api_scaffolder.py <project-path> --type rest --resource users --auth jwt

# Scaffold a GraphQL schema + resolvers
python scripts/api_scaffolder.py <project-path> --type graphql --schema users

# Generate with tests
python scripts/api_scaffolder.py <project-path> --type rest --resource orders --with-tests
```

### 2. Database Migration Tool

Schema analysis, migration generation, and query optimization.

**Features:**
- Analyze existing schemas for anti-patterns (missing indexes, N+1 risks)
- Generate Prisma/Knex/SQLAlchemy migrations from schema diffs
- Query performance analysis with EXPLAIN ANALYZE
- Index recommendations based on query patterns
- Data integrity checks and foreign key validation

**Usage:**
```bash
# Analyze current schema
python scripts/database_migration_tool.py <project-path> --analyze

# Generate migration from schema changes
python scripts/database_migration_tool.py <project-path> --generate --name add_user_roles

# Optimize slow queries
python scripts/database_migration_tool.py <project-path> --optimize --verbose
```

### 3. API Load Tester

Benchmark APIs, detect bottlenecks, and generate performance reports.

**Features:**
- Concurrent request simulation with configurable patterns
- Latency percentile tracking (p50, p95, p99)
- Throughput and error rate monitoring
- Connection pool and memory leak detection
- HTML/JSON report generation

**Usage:**
```bash
# Basic load test
python scripts/api_load_tester.py --url http://localhost:3000/api/users --concurrency 50 --duration 30

# Stress test with ramp-up
python scripts/api_load_tester.py --url http://localhost:3000/api/orders --ramp 10,50,100 --duration 60

# Generate report
python scripts/api_load_tester.py --url http://localhost:3000/api --suite endpoints.json --report html
```

## Reference Documentation

For detailed patterns and guides, read these files when needed:

- **API Design Patterns** → `references/api_design_patterns.md`
  REST conventions, GraphQL schema design, versioning, pagination, error handling
- **Database Optimization** → `references/database_optimization_guide.md`
  Indexing strategies, query optimization, connection pooling, Postgres-specific tuning
- **Security Practices** → `references/backend_security_practices.md`
  Auth flows, input sanitization, rate limiting, CORS, secrets management

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Languages | TypeScript, Python, Go |
| Backend | Node.js, Express, Fastify, GraphQL (Apollo/Yoga), Flask, Gin |
| Database | PostgreSQL, Prisma, Knex, SQLAlchemy, Redis |
| Infrastructure | Supabase, NeonDB, AWS (RDS, Lambda, ECS), GCP, Docker |
| DevOps | GitHub Actions, Docker Compose, Kubernetes, Terraform |
| Testing | Jest, Vitest, Pytest, k6, Artillery |

## Development Workflow

### 1. Project Setup
```bash
npm install          # or pip install -r requirements.txt
cp .env.example .env # configure DATABASE_URL, JWT_SECRET, etc.
```

### 2. Design & Scaffold
```bash
python scripts/api_scaffolder.py . --type rest --resource <name> --auth jwt --with-tests
```

### 3. Database
```bash
python scripts/database_migration_tool.py . --analyze
python scripts/database_migration_tool.py . --generate --name <migration_name>
npx prisma migrate dev  # or alembic upgrade head
```

### 4. Test & Benchmark
```bash
npm test                 # unit + integration
python scripts/api_load_tester.py --url http://localhost:3000/api --concurrency 50
```

### 5. Deploy
```bash
docker build -t app:latest .
docker-compose up -d     # or kubectl apply -f k8s/
```

## Best Practices Summary

### API Design
- Use proper HTTP methods and status codes
- Version APIs (`/v1/`, `/v2/`) from the start
- Implement cursor-based pagination for large datasets
- Return consistent error format: `{ error: { code, message, details } }`

### Database
- Always add indexes for foreign keys and frequent WHERE/ORDER BY columns
- Use connection pooling (PgBouncer or built-in pool)
- Prefer `SELECT` only needed columns, avoid `SELECT *`
- Use database transactions for multi-step writes

### Security
- Validate and sanitize all inputs at the boundary
- Use parameterized queries — never string interpolation for SQL
- Implement rate limiting per endpoint sensitivity
- Store secrets in environment variables, never in code
- Use short-lived JWTs with refresh token rotation

### Performance
- Measure first with load tests before optimizing
- Cache hot paths (Redis, in-memory, HTTP cache headers)
- Use database connection pooling appropriately
- Implement request timeouts and circuit breakers
- Monitor p95/p99 latency, not just averages

## Common Commands

```bash
# Dev
npm run dev && npm run build && npm test && npm run lint

# Database
npx prisma migrate dev && npx prisma studio
# or: alembic revision --autogenerate -m "msg" && alembic upgrade head

# Docker
docker build -t app:latest . && docker-compose up -d

# Kubernetes
kubectl apply -f k8s/ && kubectl get pods
```
