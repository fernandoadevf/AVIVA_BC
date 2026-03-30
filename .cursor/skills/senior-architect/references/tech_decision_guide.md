# Tech Decision Guide

## Frontend Technologies

### React + Next.js

**Best for:** SEO-critical apps, e-commerce, content platforms, dashboards

**Architecture:**
```
app/                          # App Router (Next.js 14+)
├── (auth)/                   # Route groups
│   ├── login/page.tsx
│   └── register/page.tsx
├── (dashboard)/
│   ├── layout.tsx            # Shared dashboard layout
│   ├── page.tsx
│   └── settings/page.tsx
├── api/                      # API routes
│   └── webhooks/route.ts
├── layout.tsx                # Root layout
└── globals.css
components/
├── ui/                       # Reusable UI primitives
├── forms/                    # Form components
└── layouts/                  # Layout components
lib/
├── actions/                  # Server Actions
├── queries/                  # Data fetching
├── utils/                    # Helpers
└── validations/              # Zod schemas
```

**Key Decisions:**
| Decision | Recommendation |
|----------|---------------|
| Rendering | Server Components by default; Client Components only for interactivity |
| Data fetching | Server Actions for mutations, `fetch` in Server Components for queries |
| State management | URL state (nuqs) + React Context for UI state; Zustand for complex client state |
| Styling | Tailwind CSS + shadcn/ui |
| Forms | React Hook Form + Zod |
| Auth | NextAuth.js / Clerk / Supabase Auth |

**Performance Checklist:**
- [ ] Use `<Image>` component for automatic optimization
- [ ] Implement `loading.tsx` for streaming
- [ ] Use `Suspense` boundaries for progressive loading
- [ ] Enable ISR for semi-static content
- [ ] Minimize client-side JavaScript bundle
- [ ] Use `dynamic()` for code splitting

### React Native

**Best for:** Cross-platform mobile apps sharing logic with web

**Architecture:**
```
src/
├── app/                      # Expo Router (file-based routing)
│   ├── (tabs)/
│   │   ├── _layout.tsx
│   │   ├── home.tsx
│   │   └── profile.tsx
│   ├── _layout.tsx
│   └── index.tsx
├── components/
│   ├── ui/                   # Platform-agnostic UI
│   └── screens/              # Screen-specific components
├── hooks/
├── services/                 # API clients
├── stores/                   # State management
└── utils/
```

**Key Decisions:**
| Decision | Recommendation |
|----------|---------------|
| Navigation | Expo Router (file-based) |
| State | Zustand + React Query |
| Styling | NativeWind (Tailwind for RN) or StyleSheet |
| Storage | MMKV for sync, AsyncStorage for legacy |
| Push notifications | Expo Notifications |

### Flutter

**Best for:** Pixel-perfect cross-platform UI, complex animations

**Architecture:**
```
lib/
├── core/
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── widgets/              # Shared widgets
├── features/
│   ├── auth/
│   │   ├── data/             # Repositories, data sources
│   │   ├── domain/           # Entities, use cases
│   │   └── presentation/     # Screens, widgets, bloc/cubit
│   └── home/
│       └── ...
├── l10n/                     # Localization
└── main.dart
```

**Key Decisions:**
| Decision | Recommendation |
|----------|---------------|
| State management | Riverpod (recommended) or BLoC |
| Navigation | GoRouter |
| DI | Riverpod or get_it |
| HTTP | Dio |
| Local storage | Hive or Isar |

---

## Backend Technologies

### Node.js + Express

**Best for:** REST APIs, real-time apps (WebSocket), rapid prototyping

**Production Configuration:**
```typescript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { pinoHttp } from 'pino-http';

const app = express();

app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));
app.use(express.json({ limit: '10mb' }));
app.use(pinoHttp());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

app.use('/api/v1/users', userRouter);
app.use('/api/v1/orders', orderRouter);

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error({ err, requestId: req.id }, 'Unhandled error');
  res.status(500).json({ error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' } });
});
```

**Security Checklist:**
- [ ] Use `helmet()` for security headers
- [ ] Implement rate limiting
- [ ] Validate all input (Zod, Joi)
- [ ] Use parameterized queries (never string concatenation)
- [ ] Set CORS properly
- [ ] Use HTTPS in production
- [ ] Implement request ID tracing
- [ ] Sanitize error messages (don't leak internals)

### GraphQL (Apollo Server / Yoga)

**Best for:** Complex data requirements, multiple clients with different needs

**Schema Design Principles:**
```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilter, pagination: PaginationInput): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}

type User {
  id: ID!
  email: String!
  name: String!
  orders(first: Int, after: String): OrderConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

input UserFilter {
  search: String
  status: UserStatus
  createdAfter: DateTime
}

type CreateUserPayload {
  user: User
  errors: [UserError!]
}
```

**Performance:**
- Use DataLoader for N+1 prevention (mandatory)
- Set query depth limit (max 10)
- Set query complexity limit
- Use persisted queries in production
- Implement field-level caching

### Go

**Best for:** High-concurrency services, CLI tools, infrastructure

**Project Layout:**
```
cmd/
├── api/main.go               # API server entry
└── worker/main.go             # Background worker entry
internal/
├── handler/                   # HTTP handlers
├── service/                   # Business logic
├── repository/                # Data access
├── model/                     # Domain types
├── middleware/                 # HTTP middleware
└── config/                    # Configuration
pkg/                           # Public packages (if any)
migrations/                    # SQL migrations
Makefile
go.mod
```

**Key Patterns:**
```go
// Dependency injection via constructor
type UserService struct {
    repo UserRepository
    cache Cache
}

func NewUserService(repo UserRepository, cache Cache) *UserService {
    return &UserService{repo: repo, cache: cache}
}

// Error handling with custom types
type AppError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Status  int    `json:"-"`
}

func (e *AppError) Error() string { return e.Message }

// Graceful shutdown
func main() {
    srv := &http.Server{Addr: ":8080", Handler: router}
    go func() { srv.ListenAndServe() }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}
```

### Python (FastAPI)

**Best for:** ML/AI services, data pipelines, rapid prototyping

**Project Structure:**
```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── users.py
│   │   │   └── orders.py
│   │   └── router.py
│   └── deps.py               # Dependency injection
├── core/
│   ├── config.py
│   └── security.py
├── models/                    # SQLAlchemy models
├── schemas/                   # Pydantic schemas
├── services/                  # Business logic
├── repositories/              # Data access
└── main.py
```

---

## Database Technologies

### PostgreSQL

**Configuration for Production:**
```sql
-- Connection settings
max_connections = 200
shared_buffers = '4GB'            -- 25% of RAM
effective_cache_size = '12GB'     -- 75% of RAM
work_mem = '64MB'
maintenance_work_mem = '512MB'

-- WAL settings
wal_buffers = '64MB'
checkpoint_completion_target = 0.9
max_wal_size = '4GB'

-- Query planner
random_page_cost = 1.1            -- For SSD
effective_io_concurrency = 200    -- For SSD
```

**Index Strategy:**
```sql
-- B-tree (default): equality and range queries
CREATE INDEX idx_users_email ON users(email);

-- Partial index: only index relevant rows
CREATE INDEX idx_orders_pending ON orders(created_at)
  WHERE status = 'pending';

-- Composite index: multi-column queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- GIN index: full-text search, JSONB
CREATE INDEX idx_products_search ON products
  USING GIN(to_tsvector('english', name || ' ' || description));

-- BRIN index: large tables with natural ordering
CREATE INDEX idx_events_created ON events USING BRIN(created_at);
```

**Connection Pooling:**
| Tool | Type | Best For |
|------|------|----------|
| PgBouncer | External | High connection count, serverless |
| Prisma Pool | Built-in | Prisma projects |
| pg-pool (node) | Application | Simple Node.js apps |

### Supabase

**Architecture:**
```
Supabase Project
├── PostgreSQL (database)
├── PostgREST (auto-generated REST API)
├── Realtime (WebSocket subscriptions)
├── Auth (JWT-based authentication)
├── Storage (S3-compatible file storage)
└── Edge Functions (Deno-based serverless)
```

**When to use vs raw PostgreSQL:**
| Use Supabase | Use Raw PostgreSQL |
|-------------|-------------------|
| Rapid prototyping | Full DBA control needed |
| Need auth + storage + realtime | Custom replication setup |
| Small-medium scale | Very high write throughput |
| Want managed service | On-premise requirement |

### NeonDB

**Best for:** Serverless PostgreSQL, branch-based development

**Key Features:**
- Autoscaling (scale to zero)
- Database branching (like git branches)
- Point-in-time restore
- Serverless driver (HTTP-based, no persistent connections)

```typescript
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);
const users = await sql`SELECT * FROM users WHERE id = ${userId}`;
```

---

## DevOps & Infrastructure

### CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm test
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push Docker image
        run: |
          docker build -t $REGISTRY/$IMAGE:${{ github.sha }} .
          docker push $REGISTRY/$IMAGE:${{ github.sha }}
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/api api=$REGISTRY/$IMAGE:${{ github.sha }}
          kubectl rollout status deployment/api
```

### Docker Best Practices

```dockerfile
# Multi-stage build for Node.js
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=builder --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:nodejs /app/package.json ./
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Terraform (Infrastructure as Code)

```hcl
# AWS ECS + RDS example
resource "aws_ecs_service" "api" {
  name            = "api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.api.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 3000
  }
}

resource "aws_db_instance" "postgres" {
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.t3.medium"
  allocated_storage    = 50
  storage_encrypted    = true
  multi_az             = true
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 7
  deletion_protection     = true
}
```

---

## Security Considerations

### OWASP Top 10 Checklist

| Risk | Mitigation |
|------|-----------|
| Injection | Parameterized queries, input validation |
| Broken Auth | MFA, secure session management, rate limiting |
| Sensitive Data Exposure | Encrypt at rest + transit, minimize data collection |
| XXE | Disable external entity processing |
| Broken Access Control | RBAC, deny by default, test authorization |
| Security Misconfiguration | Automated security scanning, minimal permissions |
| XSS | Content Security Policy, output encoding, sanitize HTML |
| Insecure Deserialization | Validate and sanitize all input, use allowlists |
| Vulnerable Components | Automated dependency scanning (Dependabot, Snyk) |
| Insufficient Logging | Structured logging, audit trails, alerting |

### Secrets Management

| Environment | Tool |
|-------------|------|
| Local dev | `.env` files (gitignored) |
| CI/CD | GitHub Secrets / GitLab CI Variables |
| Production | AWS Secrets Manager / HashiCorp Vault / GCP Secret Manager |
| Kubernetes | External Secrets Operator + Vault |

**Never:**
- Commit secrets to git
- Log secrets
- Pass secrets as CLI arguments (visible in process list)
- Store secrets in environment variables in Dockerfiles

---

## Scalability Guidelines

### Horizontal vs Vertical Scaling

| Approach | When | How |
|----------|------|-----|
| Vertical | Quick fix, single-instance DB | Bigger machine |
| Horizontal | Web servers, stateless services | More instances + load balancer |
| Database read scaling | Read-heavy workloads | Read replicas |
| Database write scaling | Write-heavy workloads | Sharding (complex) |
| Caching | Repeated reads | Redis/Memcached |
| CDN | Static assets, global users | CloudFront/Cloudflare |
| Queue | Async processing | RabbitMQ/SQS/Redis Streams |

### Load Testing

```bash
# k6 load test example
k6 run --vus 100 --duration 5m load-test.js
```

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```
