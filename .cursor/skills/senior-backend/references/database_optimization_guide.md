# Database Optimization Guide

## PostgreSQL Indexing Strategies

### When to Add Indexes

Always index:
- Primary keys (automatic)
- Foreign keys (NOT automatic in Postgres — always add manually)
- Columns in `WHERE` clauses used frequently
- Columns in `ORDER BY` on large tables
- Columns in `JOIN` conditions

### Index Types

```sql
-- B-tree (default, best for equality and range queries)
CREATE INDEX idx_users_email ON users(email);

-- Partial index (smaller, faster for filtered queries)
CREATE INDEX idx_users_active ON users(email) WHERE status = 'active';

-- Composite index (order matters: most selective first)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- GIN index (for JSONB, arrays, full-text search)
CREATE INDEX idx_users_metadata ON users USING gin(metadata);

-- Expression index
CREATE INDEX idx_users_lower_email ON users(lower(email));

-- Covering index (includes columns to avoid table lookup)
CREATE INDEX idx_orders_covering ON orders(user_id) INCLUDE (total, status);
```

### Index Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Index on every column | Slows writes, wastes space | Index based on query patterns |
| Missing FK indexes | Slow JOINs and cascading deletes | Always index foreign keys |
| Wrong column order in composite | Index not used | Put most selective column first |
| Unused indexes | Write overhead for no benefit | Monitor with `pg_stat_user_indexes` |

### Finding Unused Indexes

```sql
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Query Optimization

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.status = 'active'
GROUP BY u.id;
```

Key things to look for:
- **Seq Scan** on large tables → needs an index
- **Nested Loop** with large outer set → consider Hash Join
- **Sort** with high cost → add index matching ORDER BY
- **Buffers shared read** high → data not in cache, check memory

### Common Query Optimizations

**Avoid SELECT \*:**
```sql
-- Bad
SELECT * FROM users WHERE id = 1;

-- Good: only fetch what you need
SELECT id, name, email FROM users WHERE id = 1;
```

**Use EXISTS instead of IN for subqueries:**
```sql
-- Slower
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- Faster
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

**Batch inserts:**
```sql
-- Slow: individual inserts
INSERT INTO logs (message) VALUES ('a');
INSERT INTO logs (message) VALUES ('b');

-- Fast: batch insert
INSERT INTO logs (message) VALUES ('a'), ('b'), ('c');
```

**Use CTEs wisely (Postgres 12+ inlines them when possible):**
```sql
WITH active_users AS (
  SELECT id, name FROM users WHERE status = 'active'
)
SELECT au.name, COUNT(o.id)
FROM active_users au
JOIN orders o ON o.user_id = au.id
GROUP BY au.id, au.name;
```

## Connection Pooling

### Why Pool Connections

Each Postgres connection uses ~10MB of memory. Without pooling, 100 concurrent requests = 1GB just for connections.

### PgBouncer Configuration

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
pool_mode = transaction    # Best for web apps
max_client_conn = 1000
default_pool_size = 20     # Match your CPU cores * 2
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
```

### Application-Level Pooling (Node.js)

```typescript
// Prisma
const prisma = new PrismaClient({
  datasources: {
    db: { url: process.env.DATABASE_URL + '?connection_limit=20&pool_timeout=10' },
  },
});

// pg (node-postgres)
import { Pool } from 'pg';
const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});
```

## N+1 Query Prevention

### The Problem

```typescript
// N+1: 1 query for users + N queries for orders
const users = await db.user.findMany();
for (const user of users) {
  user.orders = await db.order.findMany({ where: { userId: user.id } });
}
```

### Solutions

**Prisma — include/select:**
```typescript
const users = await db.user.findMany({
  include: { orders: true },
});
```

**Raw SQL — JOIN:**
```sql
SELECT u.*, o.id as order_id, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

**GraphQL — DataLoader:**
```typescript
const orderLoader = new DataLoader(async (userIds: string[]) => {
  const orders = await db.order.findMany({
    where: { userId: { in: userIds } },
  });
  return userIds.map(id => orders.filter(o => o.userId === id));
});
```

## PostgreSQL Tuning

### Key Configuration Parameters

```ini
# Memory (set based on available RAM)
shared_buffers = '256MB'          # 25% of RAM for dedicated DB server
effective_cache_size = '768MB'    # 75% of RAM
work_mem = '16MB'                 # Per-operation sort memory
maintenance_work_mem = '128MB'    # For VACUUM, CREATE INDEX

# WAL
wal_buffers = '16MB'
checkpoint_completion_target = 0.9

# Query Planner
random_page_cost = 1.1            # For SSD storage (default 4.0 is for HDD)
effective_io_concurrency = 200    # For SSD

# Connections
max_connections = 100             # Use pooler for more
```

### Vacuuming

```sql
-- Check bloat
SELECT schemaname, relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Manual vacuum (rarely needed if autovacuum is tuned)
VACUUM ANALYZE users;
```

## Migration Best Practices

### Safe Migrations (Zero-Downtime)

**Adding a column:**
```sql
-- Safe: nullable column with no default
ALTER TABLE users ADD COLUMN phone TEXT;

-- Safe in Postgres 11+: column with default (no table rewrite)
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
```

**Adding an index without locking:**
```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

**Renaming a column (requires app coordination):**
1. Add new column
2. Backfill data
3. Update app to write to both columns
4. Switch app to read from new column
5. Stop writing to old column
6. Drop old column

**Dangerous operations to avoid in production:**
- `ALTER TABLE ... ALTER COLUMN ... TYPE` (rewrites table)
- `CREATE INDEX` without `CONCURRENTLY` (locks writes)
- `DROP COLUMN` on hot tables without coordination
- `LOCK TABLE` in any form

### Migration File Naming

```
001_create_users.sql
002_create_orders.sql
003_add_user_email_index.sql
004_add_orders_status_column.sql
```

## Monitoring Queries

```sql
-- Slowest queries (requires pg_stat_statements extension)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Active connections
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```
