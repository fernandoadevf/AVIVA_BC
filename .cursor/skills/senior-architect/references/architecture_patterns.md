# Architecture Patterns Reference

## Monolith

### When to Use
- Small team (1-5 developers)
- Early-stage product, unclear domain boundaries
- Simple deployment requirements
- Tight budget / fast time-to-market

### Structure
```
src/
├── controllers/     # HTTP handlers
├── services/        # Business logic
├── repositories/    # Data access
├── models/          # Domain entities
├── middleware/       # Cross-cutting concerns
├── utils/           # Shared helpers
└── config/          # Configuration
```

### Example (Express + TypeScript)
```typescript
// src/controllers/userController.ts
import { Request, Response } from 'express';
import { UserService } from '../services/userService';

export class UserController {
  constructor(private userService: UserService) {}

  async getUser(req: Request, res: Response) {
    const user = await this.userService.findById(req.params.id);
    if (!user) return res.status(404).json({ error: 'User not found' });
    return res.json(user);
  }
}

// src/services/userService.ts
import { UserRepository } from '../repositories/userRepository';

export class UserService {
  constructor(private userRepo: UserRepository) {}

  async findById(id: string) {
    return this.userRepo.findById(id);
  }
}
```

### Anti-Patterns
- **God class**: One service handling everything — split by domain
- **Circular dependencies between layers**: Controllers importing repositories directly
- **No layer boundaries**: Business logic in controllers

---

## Modular Monolith

### When to Use
- Growing team (5-15 developers)
- Clear domain boundaries emerging
- Want microservice benefits without operational complexity
- Planning eventual migration to microservices

### Structure
```
src/
├── modules/
│   ├── users/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── events/
│   │   └── index.ts          # Public API of this module
│   ├── orders/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── events/
│   │   └── index.ts
│   └── payments/
│       └── ...
├── shared/                    # Shared kernel
│   ├── events/
│   ├── types/
│   └── utils/
└── infrastructure/
    ├── database/
    ├── messaging/
    └── http/
```

### Key Rules
1. Modules communicate only through their public API (index.ts)
2. No direct database access across modules
3. Use events for async cross-module communication
4. Shared kernel is minimal and stable

### Example (Inter-module Communication)
```typescript
// src/modules/orders/services/orderService.ts
import { EventBus } from '../../shared/events/eventBus';

export class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private eventBus: EventBus,
  ) {}

  async createOrder(data: CreateOrderDTO) {
    const order = await this.orderRepo.create(data);
    await this.eventBus.publish('order.created', {
      orderId: order.id,
      userId: data.userId,
      total: data.total,
    });
    return order;
  }
}

// src/modules/payments/events/handlers.ts
export function onOrderCreated(event: OrderCreatedEvent) {
  // Process payment for the new order
}
```

### Anti-Patterns
- **Shared database tables across modules**: Each module owns its tables
- **Direct imports between modules**: Always go through the public API
- **Oversized shared kernel**: Keep it minimal

---

## Microservices

### When to Use
- Large organization (15+ developers, multiple teams)
- Independent scaling requirements per domain
- Different tech stacks per service
- Need independent deployment cycles

### Structure
```
services/
├── user-service/
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
├── order-service/
│   ├── src/
│   ├── Dockerfile
│   └── ...
├── payment-service/
│   └── ...
├── api-gateway/
│   └── ...
├── shared/
│   ├── proto/              # gRPC definitions
│   └── events/             # Event schemas
├── docker-compose.yml
└── k8s/
    ├── user-service.yaml
    ├── order-service.yaml
    └── ...
```

### Communication Patterns

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| REST | Simple CRUD, external APIs | Universal, simple | Tight coupling, synchronous |
| gRPC | Internal service-to-service | Fast, typed contracts | Complex setup |
| Message Queue | Async workflows, events | Decoupled, resilient | Eventual consistency |
| GraphQL Federation | Unified API gateway | Single endpoint | Complexity |

### Example (Event-Driven with Message Queue)
```typescript
// order-service/src/events/publisher.ts
import { Channel } from 'amqplib';

export async function publishOrderCreated(channel: Channel, order: Order) {
  channel.publish('orders', 'order.created', Buffer.from(JSON.stringify({
    eventId: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    data: { orderId: order.id, userId: order.userId, total: order.total },
  })));
}

// payment-service/src/events/consumer.ts
export async function handleOrderCreated(message: ConsumeMessage) {
  const event = JSON.parse(message.content.toString());
  await processPayment(event.data);
}
```

### Anti-Patterns
- **Distributed monolith**: Services that can't deploy independently
- **Shared database**: Each service must own its data
- **Synchronous chains**: A -> B -> C -> D all synchronous = fragile
- **No API versioning**: Breaking changes cascade

---

## Event-Driven Architecture

### When to Use
- Async workflows (order processing, notifications)
- Need to decouple producers from consumers
- Event sourcing requirements
- Real-time data pipelines

### Patterns

#### Event Notification
Producer publishes minimal event; consumer queries for details.
```typescript
// Producer
eventBus.publish('user.updated', { userId: '123' });

// Consumer
eventBus.subscribe('user.updated', async (event) => {
  const user = await userApi.getUser(event.userId);
  await updateSearchIndex(user);
});
```

#### Event-Carried State Transfer
Event contains all needed data; consumer doesn't need to query back.
```typescript
eventBus.publish('user.updated', {
  userId: '123',
  name: 'John',
  email: 'john@example.com',
  updatedAt: '2025-01-01T00:00:00Z',
});
```

#### Event Sourcing
Store events as the source of truth; derive state from event log.
```typescript
interface DomainEvent {
  aggregateId: string;
  type: string;
  data: unknown;
  timestamp: Date;
  version: number;
}

class OrderAggregate {
  private events: DomainEvent[] = [];
  private state: OrderState = { status: 'draft', items: [], total: 0 };

  apply(event: DomainEvent) {
    this.events.push(event);
    switch (event.type) {
      case 'ItemAdded':
        this.state.items.push(event.data as OrderItem);
        this.state.total += (event.data as OrderItem).price;
        break;
      case 'OrderConfirmed':
        this.state.status = 'confirmed';
        break;
    }
  }

  static fromEvents(events: DomainEvent[]): OrderAggregate {
    const aggregate = new OrderAggregate();
    events.forEach(e => aggregate.apply(e));
    return aggregate;
  }
}
```

### Anti-Patterns
- **Event storms**: Too many fine-grained events
- **Missing idempotency**: Consumers must handle duplicate events
- **No dead letter queue**: Failed events disappear
- **Unversioned events**: Schema changes break consumers

---

## CQRS (Command Query Responsibility Segregation)

### When to Use
- Read/write patterns are very different
- Need to optimize reads independently (e.g., search, dashboards)
- Complex domain with many aggregates
- High read-to-write ratio

### Structure
```
src/
├── commands/                  # Write side
│   ├── createOrder.ts
│   ├── updateOrder.ts
│   └── handlers/
├── queries/                   # Read side
│   ├── getOrder.ts
│   ├── listOrders.ts
│   └── handlers/
├── models/
│   ├── write/                 # Normalized, domain-rich
│   │   └── order.ts
│   └── read/                  # Denormalized, query-optimized
│       └── orderView.ts
└── projections/               # Sync write -> read models
    └── orderProjection.ts
```

### Example
```typescript
// Write side - rich domain model
class Order {
  confirm() {
    if (this.status !== 'pending') throw new Error('Can only confirm pending orders');
    if (this.items.length === 0) throw new Error('Cannot confirm empty order');
    this.status = 'confirmed';
    this.confirmedAt = new Date();
  }
}

// Read side - optimized view
interface OrderListView {
  id: string;
  customerName: string;
  totalFormatted: string;
  itemCount: number;
  status: string;
  createdAt: string;
}

// Projection keeps read model in sync
class OrderProjection {
  async onOrderConfirmed(event: OrderConfirmedEvent) {
    await this.readDb.query(`
      UPDATE order_views SET status = 'confirmed', confirmed_at = $1 WHERE id = $2
    `, [event.confirmedAt, event.orderId]);
  }
}
```

---

## Serverless

### When to Use
- Sporadic/unpredictable traffic
- Event-driven processing (file uploads, webhooks, cron jobs)
- Want zero infrastructure management
- Cost optimization for low-traffic services

### Structure (AWS Lambda + API Gateway)
```
functions/
├── api/
│   ├── getUser/
│   │   └── handler.ts
│   ├── createOrder/
│   │   └── handler.ts
│   └── processPayment/
│       └── handler.ts
├── events/
│   ├── onFileUploaded/
│   │   └── handler.ts
│   └── onOrderCreated/
│       └── handler.ts
├── scheduled/
│   └── dailyReport/
│       └── handler.ts
├── shared/
│   ├── db.ts
│   └── auth.ts
└── serverless.yml
```

### Anti-Patterns
- **Cold start sensitive paths**: Don't use for real-time, latency-critical APIs
- **Large functions**: Keep functions focused and small
- **Shared mutable state**: Functions are stateless; use external stores
- **Vendor lock-in**: Abstract cloud-specific APIs behind interfaces

---

## Hexagonal Architecture (Ports & Adapters)

### When to Use
- Domain logic must be testable without infrastructure
- Multiple input channels (REST, GraphQL, CLI, events)
- Multiple output channels (different DBs, external APIs)
- Long-lived projects where infrastructure may change

### Structure
```
src/
├── domain/                    # Core business logic (no external deps)
│   ├── entities/
│   ├── value-objects/
│   ├── services/
│   └── ports/                 # Interfaces
│       ├── inbound/           # Use cases
│       │   └── CreateOrderPort.ts
│       └── outbound/          # Repository/external service interfaces
│           ├── OrderRepository.ts
│           └── PaymentGateway.ts
├── application/               # Use case implementations
│   └── CreateOrderUseCase.ts
├── adapters/
│   ├── inbound/               # Driving adapters
│   │   ├── rest/
│   │   ├── graphql/
│   │   └── cli/
│   └── outbound/              # Driven adapters
│       ├── postgres/
│       ├── stripe/
│       └── sendgrid/
└── config/
    └── container.ts           # Dependency injection
```

### Key Rule
Dependencies point inward: adapters -> application -> domain. The domain never imports from adapters.
