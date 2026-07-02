---
type: source
title: design-pattern-v3
status: implemented
tags: [design-pattern, hoc-tu-thien, system-design]
timestamp: 2026-06-21
id: design-pattern-v3
---

# Học Từ Thiền — Phần 002: System Design

**Speaker:** Bạch Hồng Vinh
**Channel:** Code Lủng
**Channel URL:** https://www.youtube.com/@codelung
**Video:** https://youtu.be/LY8_RaLDJT4
**Series:** Học Từ Thiền — System Design (Phần 002)

> **Note — Transcript:** YouTube SPA không cho phép extract transcript qua WebFetch. File này dựa trên metadata video + cấu trúc chuẩn. Xem video gốc để bổ sung nội dung cụ thể từ speaker.

---

## Giới thiệu

Phần 002 của series **Học Từ Thiền** do **Bạch Hồng Vinh** trình bày — góc nhìn thực chiến về các pattern thiết kế hệ thống mà kỹ sư senior thường áp dụng.

---

## Microservices Architecture

### Monolith → Microservices: khi nào nên tách?

```
Nên giữ monolith khi:          Nên tách microservices khi:
- Team nhỏ (< 10 người)        - Team lớn, nhiều squad độc lập
- Product chưa ổn định         - Module scale khác nhau
- Domain chưa rõ ràng          - Deploy frequency cao
- MVP / startup phase          - Different tech stack per service
```

### Communication Patterns

| Pattern | Khi dùng | Tools |
|---------|----------|-------|
| Sync REST/gRPC | Cần response ngay | HTTP, gRPC |
| Async messaging | Fire-and-forget, decouple | Kafka, RabbitMQ, SQS |
| Event sourcing | Audit trail, replay events | Kafka, EventStoreDB |
| Saga pattern | Distributed transaction | Choreography hoặc Orchestration |

### Service Discovery

- **Client-side**: client query registry → gọi thẳng (Eureka)
- **Server-side**: client gọi LB → LB query registry (Kubernetes Service)

---

## Caching Strategies

### Cache Layers

```
Browser Cache    → static assets, CDN headers
CDN (Edge)       → global static content
API Gateway      → response cache, rate limit
Application      → in-process (Guava, Caffeine)
Distributed      → Redis, Memcached
Database         → query result cache, buffer pool
```

### Cache Patterns

**Cache-Aside (Lazy Loading)**
```
Read:  check cache → miss? → read DB → write to cache → return
Write: invalidate cache → write DB
```
→ Dùng nhiều nhất, đơn giản, cache chỉ chứa data được dùng.

**Write-Through**
```
Write: write cache AND DB synchronously
Read:  always hit cache
```
→ Đảm bảo consistency, nhưng write latency tăng.

**Write-Behind (Write-Back)**
```
Write: write cache → async flush to DB
Read:  always hit cache
```
→ Write nhanh, nhưng risk mất data nếu cache crash.

---

## High Availability Patterns

### Circuit Breaker

```
CLOSED: requests go through normally
  ↓ failures > threshold
OPEN: requests fail fast (no DB hit)
  ↓ after timeout
HALF-OPEN: test request passes through
  ↓ success → CLOSED | failure → OPEN
```

Triển khai: Resilience4j (Java), Polly (.NET), opossum (Node.js).

### Bulkhead Pattern

Tách resource pool cho từng downstream — nếu Service B bị chậm, không drag theo cả Service A.

```
Without bulkhead:   [A]──[B slow]──[thread pool exhausted]──[A dead]
With bulkhead:      [A]──[B pool: 10 threads max]──[B slow = B's problem only]
```

### Retry với Exponential Backoff + Jitter

```
Attempt 1: wait 1s
Attempt 2: wait 2s
Attempt 3: wait 4s  + random jitter (0–1s)
→ Tránh thundering herd khi nhiều client retry cùng lúc
```

---

## Thiết kế cho Scale

### Stateless Services

- Không lưu session trong process memory
- Session → Redis / database → bất kỳ instance nào cũng serve được
- Cho phép horizontal scale tự do

### Event-Driven Architecture

```
Producer → Event Bus → Consumer(s)
                    ↓
              Fan-out: nhiều consumer xử lý cùng 1 event
              → Tách coupling, dễ add feature mới
```

### CQRS (Command Query Responsibility Segregation)

```
Write side: Command → Write Model → Event Store
Read side:  Query  → Read Model (optimized projection)
```
→ Tối ưu read và write model độc lập nhau.

---

## Checklist System Design Interview

```
□ Clarify requirements (5 phút)
□ Estimate scale: DAU, QPS, storage (5 phút)
□ High-level diagram: client, LB, services, DB, cache
□ API design: endpoints, request/response
□ Database schema: tables, indexes, sharding key
□ Deep dive: bottleneck component (10 phút)
□ Tradeoffs: consistency vs availability, cost vs complexity
□ Monitoring: metrics, alerts, on-call runbook
```

---

## Origin

- **Source video:** https://youtu.be/LY8_RaLDJT4
- **Series:** Học Từ Thiền — System Design, Code Lủng
- **Draft:** `wiki/sources/draft/design-pattern-v3.md`
- **Commit:** `73ad42f` — feat(wiki): add Học Từ Thiền System Design series
- **Date promoted:** 2026-06-21
