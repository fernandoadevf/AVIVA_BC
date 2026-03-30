# API Design Patterns

## REST API Conventions

### Resource Naming
```
GET    /api/v1/users          # List users
POST   /api/v1/users          # Create user
GET    /api/v1/users/:id      # Get user
PATCH  /api/v1/users/:id      # Update user
DELETE /api/v1/users/:id      # Delete user
GET    /api/v1/users/:id/orders  # Nested resource
```

- Use plural nouns for resources
- Nest resources max 2 levels deep
- Use query params for filtering: `GET /users?status=active&role=admin`
- Use kebab-case for multi-word resources: `/api/v1/order-items`

### HTTP Status Codes

| Code | When to Use |
|------|-------------|
| 200 | Successful GET, PATCH, DELETE |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no content) |
| 400 | Invalid request body or params |
| 401 | Missing or invalid auth token |
| 403 | Valid auth but insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Validation error (semantic) |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error |

### Consistent Error Response

```typescript
interface ApiError {
  error: {
    code: string;        // Machine-readable: "VALIDATION_ERROR"
    message: string;     // Human-readable: "Email is required"
    details?: Record<string, string[]>; // Field-level errors
    requestId?: string;  // For debugging
  };
}

// Example
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": {
      "email": ["must be a valid email"],
      "age": ["must be at least 18"]
    },
    "requestId": "req_abc123"
  }
}
```

### Pagination

**Cursor-based (recommended for large/real-time datasets):**
```typescript
// Request
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTAwfQ

// Response
{
  "data": [...],
  "pagination": {
    "hasMore": true,
    "nextCursor": "eyJpZCI6MTIwfQ",
    "prevCursor": "eyJpZCI6MTAwfQ"
  }
}
```

**Offset-based (simpler, fine for small datasets):**
```typescript
GET /api/v1/users?page=2&limit=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### Filtering, Sorting, Field Selection

```
GET /api/v1/users?status=active&role=admin          # Filter
GET /api/v1/users?sort=-createdAt,name               # Sort (- = desc)
GET /api/v1/users?fields=id,name,email                # Sparse fields
GET /api/v1/users?search=john                         # Full-text search
```

### API Versioning

Prefer URL path versioning for simplicity:
```
/api/v1/users
/api/v2/users
```

Alternatives (use when URL versioning doesn't fit):
- Header: `Accept: application/vnd.api.v2+json`
- Query: `/api/users?version=2`

## GraphQL Patterns

### Schema Design

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  role: UserRole!
  orders(first: Int, after: String): OrderConnection!
  createdAt: DateTime!
}

enum UserRole {
  ADMIN
  USER
  MODERATOR
}

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}
```

### Query Complexity & Depth Limiting

```typescript
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer({
  schema,
  validationRules: [
    depthLimit(7),
    createComplexityLimitRule(1000),
  ],
});
```

### DataLoader for N+1 Prevention

```typescript
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (userIds: string[]) => {
  const users = await db.user.findMany({
    where: { id: { in: userIds } },
  });
  const userMap = new Map(users.map(u => [u.id, u]));
  return userIds.map(id => userMap.get(id) ?? null);
});

// In resolver
const resolvers = {
  Order: {
    user: (order) => userLoader.load(order.userId),
  },
};
```

## Request/Response Patterns

### Envelope Pattern

```typescript
// Success
{ "data": { ... }, "meta": { "requestId": "..." } }

// Error
{ "error": { "code": "...", "message": "..." } }

// List
{ "data": [...], "pagination": { ... }, "meta": { ... } }
```

### Idempotency

For non-idempotent operations (POST), use idempotency keys:

```typescript
app.post('/api/v1/payments', async (req, res) => {
  const idempotencyKey = req.headers['idempotency-key'];
  if (!idempotencyKey) return res.status(400).json({ error: { code: 'MISSING_IDEMPOTENCY_KEY' } });

  const existing = await cache.get(`idempotency:${idempotencyKey}`);
  if (existing) return res.status(200).json(JSON.parse(existing));

  const result = await processPayment(req.body);
  await cache.set(`idempotency:${idempotencyKey}`, JSON.stringify(result), 'EX', 86400);
  return res.status(201).json(result);
});
```

### Rate Limiting Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1672531200
Retry-After: 60
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Verbs in URLs (`/getUsers`) | Not RESTful | Use `GET /users` |
| Returning 200 for errors | Clients can't distinguish | Use proper status codes |
| Nested resources >2 levels | Complex, fragile URLs | Flatten or use query params |
| No pagination | Memory/performance issues | Always paginate list endpoints |
| Exposing internal IDs | Security risk | Use UUIDs or public IDs |
| No request validation | Injection, crashes | Validate at the boundary |
| Inconsistent naming | Confusing API | Pick a convention, enforce it |
| No versioning | Breaking changes | Version from day one |

## Express Middleware Stack (Recommended Order)

```typescript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { requestId } from './middleware/requestId';
import { logger } from './middleware/logger';
import { errorHandler } from './middleware/errorHandler';

const app = express();

// 1. Security headers
app.use(helmet());

// 2. CORS
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));

// 3. Request ID
app.use(requestId());

// 4. Logging
app.use(logger());

// 5. Rate limiting
app.use('/api/', rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// 6. Body parsing
app.use(express.json({ limit: '10mb' }));

// 7. Routes
app.use('/api/v1', routes);

// 8. Error handler (last)
app.use(errorHandler);
```
