# System Design Workflows

## Workflow 1: Greenfield System Design

### Step 1: Requirements Gathering

**Functional Requirements Checklist:**
- [ ] Core user stories / use cases
- [ ] Data entities and relationships
- [ ] API contracts (who calls what)
- [ ] Authentication / authorization model
- [ ] Third-party integrations

**Non-Functional Requirements:**
- [ ] Expected users (DAU/MAU)
- [ ] Latency requirements (p50, p95, p99)
- [ ] Throughput (requests/sec, events/sec)
- [ ] Availability target (99.9%, 99.99%)
- [ ] Data retention and compliance (GDPR, HIPAA)
- [ ] Budget constraints

### Step 2: Capacity Planning

**Traffic Estimation Template:**
```
Users:
  - DAU: ___
  - Peak concurrent: ___
  - Avg session duration: ___ min

Requests:
  - Avg requests/user/session: ___
  - Peak RPS = (DAU × requests/session) / (seconds in peak hours)
  - Example: 100K DAU × 20 req/session / (8h × 3600s) = ~69 RPS

Storage:
  - Avg record size: ___ KB
  - New records/day: ___
  - Storage growth/month: ___ GB
  - Retention period: ___ months
  - Total storage needed: ___ GB

Bandwidth:
  - Avg response size: ___ KB
  - Peak bandwidth = Peak RPS × avg response size
```

**Database Sizing:**
| Scale | Users | DB Choice | Notes |
|-------|-------|-----------|-------|
| Small | <10K DAU | Single PostgreSQL | Vertical scaling sufficient |
| Medium | 10K-100K DAU | PostgreSQL + Read replicas | Add connection pooling (PgBouncer) |
| Large | 100K-1M DAU | PostgreSQL cluster + Redis cache | Consider sharding strategy |
| Massive | >1M DAU | Distributed DB + CDN + Multi-region | Evaluate CockroachDB, Vitess |

### Step 3: High-Level Architecture

**Decision tree for architecture pattern:**

```
Is the team < 5 people?
├── Yes → Monolith or Modular Monolith
└── No
    ├── Are there clear domain boundaries with independent scaling needs?
    │   ├── Yes → Microservices
    │   └── No → Modular Monolith
    └── Is traffic sporadic/event-driven?
        ├── Yes → Serverless + Event-Driven
        └── No → Container-based deployment
```

### Step 4: Data Model Design

**Process:**
1. Identify core entities from requirements
2. Define relationships (1:1, 1:N, N:M)
3. Normalize to 3NF for write-heavy, denormalize for read-heavy
4. Define indexes based on query patterns
5. Plan for migrations from day one

**PostgreSQL Schema Template:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
```

### Step 5: API Design

**REST API Design Checklist:**
- [ ] Use nouns for resources (`/users`, not `/getUsers`)
- [ ] Use HTTP methods correctly (GET, POST, PUT, PATCH, DELETE)
- [ ] Version the API (`/v1/users`)
- [ ] Use consistent error format
- [ ] Implement pagination for list endpoints
- [ ] Add rate limiting
- [ ] Document with OpenAPI/Swagger

**GraphQL API Design Checklist:**
- [ ] Define clear type boundaries
- [ ] Implement DataLoader for N+1 prevention
- [ ] Add query depth/complexity limits
- [ ] Use input types for mutations
- [ ] Implement proper error handling with extensions
- [ ] Consider persisted queries for production

**Error Response Standard:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "email", "message": "Must be a valid email address" }
    ],
    "requestId": "req_abc123"
  }
}
```

### Step 6: Authentication & Authorization

**Decision Matrix:**
| Method | Best For | Avoid When |
|--------|----------|------------|
| JWT + Refresh Token | SPAs, mobile apps, microservices | Need instant revocation |
| Session Cookies | Server-rendered apps, simple auth | Distributed systems |
| OAuth 2.0 / OIDC | Third-party login, enterprise SSO | Simple internal tools |
| API Keys | Server-to-server, public APIs | User-facing auth |

**JWT Architecture:**
```
Client → Login → Auth Service → Issue JWT (short-lived, 15min)
                              → Issue Refresh Token (long-lived, 7d, stored in httpOnly cookie)

Client → API Request → API Gateway → Verify JWT → Forward to service
Client → Token Expired → Refresh Endpoint → Verify Refresh Token → Issue new JWT
```

### Step 7: Deployment Strategy

**Environment Progression:**
```
Local Dev → CI/CD → Staging → Production
    │          │        │          │
    │          │        │          ├── Blue/Green or Canary
    │          │        ├── Mirror of production
    │          ├── Automated tests + build
    └── Docker Compose
```

**Docker Compose (Development):**
```yaml
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
      - REDIS_URL=redis://cache:6379
    depends_on: [db, cache]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: ["5432:5432"]

  cache:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

**Kubernetes (Production):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    spec:
      containers:
        - name: api
          image: registry/api:latest
          ports: [{ containerPort: 3000 }]
          resources:
            requests: { cpu: "250m", memory: "256Mi" }
            limits: { cpu: "500m", memory: "512Mi" }
          livenessProbe:
            httpGet: { path: /health, port: 3000 }
            initialDelaySeconds: 10
          readinessProbe:
            httpGet: { path: /ready, port: 3000 }
            initialDelaySeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: db-secret, key: url }
```

---

## Workflow 2: Scaling an Existing System

### Step 1: Identify Bottlenecks

**Metrics to collect:**
- Response time percentiles (p50, p95, p99)
- Error rate
- CPU/Memory utilization
- Database query times (slow query log)
- Queue depth / processing lag

**Tools:**
| Category | Tools |
|----------|-------|
| APM | Datadog, New Relic, Grafana + Tempo |
| Metrics | Prometheus + Grafana |
| Logging | ELK Stack, Loki |
| Profiling | Node.js: clinic.js, Go: pprof, Python: py-spy |

### Step 2: Optimize Database

**Common optimizations (in order of effort):**

1. **Add indexes** — Check `EXPLAIN ANALYZE` for sequential scans
2. **Connection pooling** — PgBouncer or built-in pool (Prisma, TypeORM)
3. **Query optimization** — Avoid N+1, use JOINs or DataLoader
4. **Read replicas** — Route reads to replicas
5. **Caching** — Redis for hot data, HTTP cache headers
6. **Partitioning** — Time-based partitions for large tables
7. **Sharding** — Last resort, adds significant complexity

**PostgreSQL Performance Checklist:**
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Find missing indexes
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY seq_scan DESC;

-- Check table bloat
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Step 3: Implement Caching

**Caching Strategy Decision:**

| Layer | Tool | TTL | Use Case |
|-------|------|-----|----------|
| Browser | Cache-Control headers | Varies | Static assets, API responses |
| CDN | CloudFront, Cloudflare | 1h-24h | Static files, images |
| Application | Redis | 5min-1h | Session, computed data |
| Database | Query cache | Auto | Repeated queries |
| ORM | DataLoader | Per-request | N+1 prevention |

**Redis Caching Pattern:**
```typescript
async function getCachedUser(id: string): Promise<User> {
  const cacheKey = `user:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUnique({ where: { id } });
  if (user) {
    await redis.setex(cacheKey, 300, JSON.stringify(user)); // 5 min TTL
  }
  return user;
}

async function invalidateUserCache(id: string) {
  await redis.del(`user:${id}`);
}
```

### Step 4: Horizontal Scaling

**Stateless Application Checklist:**
- [ ] No in-memory sessions (use Redis/DB)
- [ ] No local file storage (use S3/GCS)
- [ ] No in-memory caches that can't be lost (use Redis)
- [ ] Health check endpoint returns quickly
- [ ] Graceful shutdown handles in-flight requests

**Auto-scaling Configuration (Kubernetes HPA):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## Workflow 3: Migration Strategy

### Strangler Fig Pattern

Gradually replace parts of a legacy system:

```
Phase 1: Proxy
  Client → API Gateway → Legacy System

Phase 2: Parallel
  Client → API Gateway ─┬→ New Service (feature X)
                        └→ Legacy System (everything else)

Phase 3: Complete
  Client → API Gateway → New Services (all features)
                        Legacy System (decommissioned)
```

### Database Migration Strategy

**Zero-downtime migration steps:**
1. Add new column/table (backward compatible)
2. Deploy code that writes to both old and new
3. Backfill existing data
4. Deploy code that reads from new
5. Deploy code that only writes to new
6. Remove old column/table

### Feature Flags for Safe Rollout

```typescript
interface FeatureFlags {
  'new-checkout-flow': boolean;
  'graphql-api': boolean;
  'redis-cache': boolean;
}

function isEnabled(flag: keyof FeatureFlags, userId?: string): boolean {
  const config = getFeatureConfig(flag);
  if (!config.enabled) return false;
  if (config.percentage === 100) return true;
  if (userId && config.allowlist?.includes(userId)) return true;
  if (config.percentage > 0) {
    return hashUserId(userId) % 100 < config.percentage;
  }
  return false;
}
```

---

## Workflow 4: Observability Setup

### Three Pillars

**1. Logging**
```typescript
// Structured logging with correlation
const logger = createLogger({
  format: json(),
  defaultMeta: { service: 'order-service' },
});

function logRequest(req: Request, res: Response, duration: number) {
  logger.info('request completed', {
    method: req.method,
    path: req.path,
    statusCode: res.statusCode,
    duration,
    requestId: req.headers['x-request-id'],
    userId: req.user?.id,
  });
}
```

**2. Metrics**
```typescript
// Key metrics to track
const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
});

const activeConnections = new Gauge({
  name: 'active_connections',
  help: 'Number of active connections',
});

const ordersCreated = new Counter({
  name: 'orders_created_total',
  help: 'Total orders created',
  labelNames: ['status'],
});
```

**3. Distributed Tracing**
```typescript
// OpenTelemetry setup
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('order-service');

async function createOrder(data: CreateOrderDTO) {
  return tracer.startActiveSpan('createOrder', async (span) => {
    span.setAttribute('user.id', data.userId);
    try {
      const order = await orderRepo.create(data);
      span.setAttribute('order.id', order.id);
      return order;
    } catch (error) {
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Error Rate | error_rate > 1% for 5min | Critical |
| High Latency | p99 > 2s for 10min | Warning |
| High CPU | cpu > 80% for 15min | Warning |
| Disk Space | disk > 85% | Critical |
| DB Connections | connections > 80% pool | Warning |
| Queue Backlog | queue_depth > 1000 for 5min | Warning |
