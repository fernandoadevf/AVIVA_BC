# Backend Security Practices

## Authentication

### JWT Implementation

```typescript
import jwt from 'jsonwebtoken';

const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';

function generateTokens(userId: string, role: string) {
  const accessToken = jwt.sign(
    { sub: userId, role },
    process.env.JWT_SECRET!,
    { expiresIn: ACCESS_TOKEN_EXPIRY, algorithm: 'HS256' }
  );

  const refreshToken = jwt.sign(
    { sub: userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: REFRESH_TOKEN_EXPIRY, algorithm: 'HS256' }
  );

  return { accessToken, refreshToken };
}
```

**Token rotation flow:**
1. Client sends expired access token
2. Server returns 401
3. Client sends refresh token to `/auth/refresh`
4. Server validates refresh token, issues new pair
5. Old refresh token is invalidated (stored in blacklist/DB)

### Auth Middleware

```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

interface AuthRequest extends Request {
  user?: { sub: string; role: string };
}

export function authenticate(req: AuthRequest, res: Response, next: NextFunction) {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    return res.status(401).json({ error: { code: 'UNAUTHORIZED', message: 'Missing token' } });
  }

  try {
    const payload = jwt.verify(header.slice(7), process.env.JWT_SECRET!) as { sub: string; role: string };
    req.user = payload;
    next();
  } catch {
    return res.status(401).json({ error: { code: 'UNAUTHORIZED', message: 'Invalid token' } });
  }
}

export function authorize(...roles: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: { code: 'FORBIDDEN', message: 'Insufficient permissions' } });
    }
    next();
  };
}
```

### Password Hashing

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

Use `argon2` for new projects (more resistant to GPU attacks):
```typescript
import argon2 from 'argon2';

const hash = await argon2.hash(password, { type: argon2.argon2id });
const valid = await argon2.verify(hash, password);
```

## Input Validation & Sanitization

### Zod Validation (TypeScript)

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).trim(),
  password: z.string().min(8).max(128),
  role: z.enum(['user', 'admin']).default('user'),
});

// In route handler
app.post('/api/v1/users', async (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid request body',
        details: result.error.flatten().fieldErrors,
      },
    });
  }
  const user = await createUser(result.data);
  return res.status(201).json({ data: user });
});
```

### SQL Injection Prevention

**Always use parameterized queries:**
```typescript
// DANGEROUS — never do this
const user = await db.query(`SELECT * FROM users WHERE email = '${email}'`);

// Safe — parameterized
const user = await db.query('SELECT * FROM users WHERE email = $1', [email]);

// Safe — Prisma (parameterized by default)
const user = await prisma.user.findUnique({ where: { email } });
```

### XSS Prevention

- Sanitize HTML output with `DOMPurify` or `sanitize-html`
- Set `Content-Type: application/json` for API responses
- Use `helmet` middleware for security headers
- Never render user input as raw HTML

## Rate Limiting

### Per-Endpoint Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { createClient } from 'redis';

const redisClient = createClient({ url: process.env.REDIS_URL });

const apiLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: { code: 'RATE_LIMITED', message: 'Too many requests' } },
});

const authLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { error: { code: 'RATE_LIMITED', message: 'Too many login attempts' } },
});

app.use('/api/', apiLimiter);
app.use('/api/v1/auth/login', authLimiter);
```

## CORS Configuration

```typescript
import cors from 'cors';

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400,
}));
```

## Security Headers (Helmet)

```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));
```

## Secrets Management

### Environment Variables

```bash
# .env (never commit this)
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
JWT_SECRET=your-256-bit-secret
JWT_REFRESH_SECRET=another-256-bit-secret
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### Best Practices
- Never commit `.env` files — add to `.gitignore`
- Use different secrets per environment (dev, staging, prod)
- Rotate secrets periodically
- Use a secrets manager in production (AWS Secrets Manager, Vault, Doppler)
- Generate secrets with: `openssl rand -base64 32`

## Error Handling

### Global Error Handler

```typescript
import { Request, Response, NextFunction } from 'express';

class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: Record<string, string[]>
  ) {
    super(message);
  }
}

function errorHandler(err: Error, req: Request, res: Response, _next: NextFunction) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message, details: err.details },
    });
  }

  // Log unexpected errors, don't expose internals
  console.error('Unexpected error:', err);
  return res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' },
  });
}
```

### Never Expose Internal Errors

```typescript
// DANGEROUS — leaks stack trace and internals
app.get('/users', async (req, res) => {
  try {
    const users = await getUsers();
    res.json(users);
  } catch (err) {
    res.status(500).json({ error: err.message, stack: err.stack }); // Never do this
  }
});

// Safe — generic message, log internally
app.get('/users', async (req, res, next) => {
  try {
    const users = await getUsers();
    res.json({ data: users });
  } catch (err) {
    next(err); // Let global error handler deal with it
  }
});
```

## Logging & Audit

### Structured Logging

```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  redact: ['req.headers.authorization', 'req.body.password'],
});

// Log with context
logger.info({ userId: user.id, action: 'login' }, 'User logged in');
logger.warn({ ip: req.ip, path: req.path }, 'Rate limit approaching');
logger.error({ err, requestId: req.id }, 'Database query failed');
```

### What to Log
- Authentication events (login, logout, failed attempts)
- Authorization failures
- Input validation failures
- Database errors
- External service calls and failures
- Rate limit hits

### What NOT to Log
- Passwords or tokens
- Full credit card numbers
- Personal data (unless required for audit)
- Sensitive headers

## Security Checklist

- [ ] All inputs validated and sanitized
- [ ] Parameterized queries everywhere (no string interpolation)
- [ ] JWT with short expiry + refresh token rotation
- [ ] Passwords hashed with bcrypt (12+ rounds) or argon2id
- [ ] Rate limiting on auth endpoints (5/15min) and API (100/15min)
- [ ] CORS configured with explicit allowed origins
- [ ] Security headers via helmet
- [ ] Secrets in env vars, never in code
- [ ] `.env` in `.gitignore`
- [ ] Error responses don't leak internals
- [ ] Structured logging with sensitive data redacted
- [ ] Dependencies regularly updated (`npm audit`)
- [ ] HTTPS enforced in production
