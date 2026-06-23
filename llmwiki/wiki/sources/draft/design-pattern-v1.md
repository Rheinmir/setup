---
type: source
title: design-pattern-v1-draft
status: implemented
tags: [design-pattern, hoc-tu-thien, system-design]
timestamp: 2026-06-21
---

# Học Từ Thiền — Phần 000: System Design

**Speaker:** Phan Văn Ngọc Thắng
**Channel:** Code Lủng
**Channel URL:** https://www.youtube.com/@codelung
**Video:** https://youtu.be/KIrbA-wEURg
**Series:** Học Từ Thiền — System Design (Phần 000 / intro)

> **Note — Transcript:** YouTube SPA không cho phép extract transcript qua WebFetch. File này dựa trên metadata video + cấu trúc chuẩn. Xem video gốc để bổ sung nội dung cụ thể từ speaker.

---

## Giới thiệu series

**Học Từ Thiền** là series của kênh Code Lủng, nơi các kỹ sư Việt Nam chia sẻ kiến thức thực chiến về **System Design** — thiết kế hệ thống phần mềm ở quy mô lớn. Mỗi phần do một speaker khác nhau trình bày góc nhìn riêng.

- **Phần 000** (video này): Phan Văn Ngọc Thắng — Intro & nền tảng
- **Phần 001**: Trần Hồng Gấm
- **Phần 002**: Bạch Hồng Vinh

---

## System Design — Nền tảng

### Tại sao cần System Design?

Khi hệ thống phần mềm lớn lên, ta phải trả lời các câu hỏi:
- Hệ thống chịu được bao nhiêu user đồng thời?
- Dữ liệu lưu ở đâu, truy xuất thế nào?
- Khi một component fail thì cả hệ thống có sập không?
- Scale như thế nào khi traffic tăng 10x?

### Các trục chính

| Trục | Câu hỏi cốt lõi |
|------|----------------|
| **Scalability** | Horizontal vs vertical scaling |
| **Reliability** | Single point of failure, redundancy |
| **Availability** | Uptime target, SLA |
| **Performance** | Latency vs throughput tradeoff |
| **Consistency** | CAP theorem, eventual consistency |

### Bộ khung tiếp cận bài System Design

```
1. Clarify requirements (functional + non-functional)
2. Estimate scale (DAU, RPS, storage)
3. High-level design (components, data flow)
4. Deep dive (database schema, API design, caching)
5. Bottlenecks + tradeoffs
```

---

## Các building blocks thường gặp

### Load Balancer
- Phân phối traffic đến nhiều server
- Round-robin, least connections, IP-hash
- L4 (TCP) vs L7 (HTTP) load balancing

### Database
- **SQL**: ACID, joins, transactions → strong consistency
- **NoSQL**: BASE, horizontal scale → eventual consistency
- Read replicas cho read-heavy workloads
- Sharding khi single DB không đủ

### Cache
- Redis / Memcached — giảm latency, giảm DB load
- Cache-aside, write-through, write-behind
- Cache invalidation — hard problem

### Message Queue
- Kafka, RabbitMQ — decouple producer/consumer
- Async processing, retry logic, dead letter queue

### CDN
- Static assets (images, JS, CSS) gần user
- Edge caching, cache-control headers

---

## Tradeoffs thường gặp trong interview

| Tình huống | Option A | Option B | Chọn khi nào |
|-----------|----------|----------|--------------|
| Consistency vs Availability | Strong consistency | High availability | Banking → A; Social feed → B |
| SQL vs NoSQL | Relational DB | Document/Key-value | Structured + joins → A; Scale + flexible → B |
| Sync vs Async | Synchronous API | Message queue | Real-time required → A; Decouple + scale → B |
| Monolith vs Microservices | Single deployable | Many services | Early stage → A; Scale teams → B |

---

## Origin

- **Source video:** https://youtu.be/KIrbA-wEURg
- **Series:** Học Từ Thiền — System Design, Code Lủng
- **Draft:** `wiki/sources/draft/design-pattern-v1.md`
- **Commit:** `73ad42f` — feat(wiki): add Học Từ Thiền System Design series
- **Date promoted:** 2026-06-21
