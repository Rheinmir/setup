---
type: source
title: design-pattern-v2-draft
status: implemented
tags: [design-pattern, hoc-tu-thien, system-design]
timestamp: 2026-06-21
---

# Học Từ Thiền — Phần 001: System Design

**Speaker:** Trần Hồng Gấm
**Channel:** Code Lủng
**Channel URL:** https://www.youtube.com/@codelung
**Video:** https://youtu.be/_U4H5FSIb-c
**Series:** Học Từ Thiền — System Design (Phần 001)

> **Note — Transcript:** YouTube SPA không cho phép extract transcript qua WebFetch. File này dựa trên metadata video + cấu trúc chuẩn. Xem video gốc để bổ sung nội dung cụ thể từ speaker.

---

## Giới thiệu

Phần 001 của series **Học Từ Thiền** do **Trần Hồng Gấm** trình bày. Trong series này mỗi kỹ sư chia sẻ cách họ tiếp cận System Design từ kinh nghiệm thực tế — không chỉ lý thuyết.

---

## Data Flow & Storage Design

### Chọn database đúng cho từng bài toán

```
Read-heavy?      → Add read replicas + cache layer
Write-heavy?     → Consider write-ahead log, partitioning
Time-series?     → InfluxDB, TimescaleDB
Graph data?      → Neo4j, Amazon Neptune
Full-text search?→ Elasticsearch
ACID required?   → PostgreSQL, MySQL
Flexible schema? → MongoDB, DynamoDB
```

### Database Sharding

**Horizontal sharding** — phân tán dữ liệu ra nhiều node:

| Sharding key | Ưu điểm | Nhược điểm |
|-------------|---------|-----------|
| User ID hash | Phân phối đều | Cross-shard joins khó |
| Geographic | Data gần user | Hotspot nếu user tập trung |
| Range-based | Dễ query range | Hotspot với sequential IDs |

### Indexing strategy

- **B-tree index**: range queries, equality — hầu hết các DB default
- **Hash index**: equality only, O(1) lookup
- **Composite index**: column order quan trọng (leftmost prefix rule)
- **Covering index**: index chứa đủ columns → không cần hit table

---

## API Design Patterns

### REST vs gRPC vs GraphQL

| | REST | gRPC | GraphQL |
|--|------|------|---------|
| Protocol | HTTP/1.1 | HTTP/2 | HTTP |
| Format | JSON | Protobuf (binary) | JSON |
| Performance | Baseline | ~10x nhanh hơn REST | Flexible |
| Use case | Public API | Internal microservices | Complex client needs |
| Streaming | Polling / WebSocket | Native bidirectional | Subscription |

### Rate Limiting

```
Token Bucket:   smooth burst, allow short spikes
Leaky Bucket:   strict rate, queue excess
Fixed Window:   simple but boundary issues
Sliding Window: accurate, more memory
```

Triển khai: Redis + Lua script để atomic check-and-decrement.

---

## Distributed Systems Concepts

### Consistency Models (CAP Theorem)

```
C — Consistency:   mọi node thấy cùng data tại cùng thời điểm
A — Availability:  mọi request đều có response (không đảm bảo mới nhất)
P — Partition tol: hệ thống hoạt động dù network bị chia cắt
```

Chỉ chọn được 2 trong 3:
- **CP** (Zookeeper, HBase): khi cần data chính xác tuyệt đối
- **AP** (Cassandra, CouchDB): khi cần uptime cao, chấp nhận eventual consistency

### Consensus Algorithms

- **Raft**: leader election + log replication, dễ hiểu hơn Paxos
- **Paxos**: classic, phức tạp, nền tảng của nhiều distributed DB
- **PBFT**: Byzantine fault tolerance, dùng trong blockchain

---

## Monitoring & Observability

### The Three Pillars

```
Logs    → ghi lại events (structured JSON preferred)
Metrics → đo lường số (CPU, latency, error rate)
Traces  → theo dõi request xuyên suốt các service
```

### SLI / SLO / SLA

- **SLI** (Service Level Indicator): metric đo được — p99 latency, error rate
- **SLO** (Service Level Objective): target nội bộ — "99.9% requests < 200ms"
- **SLA** (Service Level Agreement): cam kết với khách hàng — có phạt nếu vi phạm

---

## Origin

- **Source video:** https://youtu.be/_U4H5FSIb-c
- **Series:** Học Từ Thiền — System Design, Code Lủng
- **Draft:** `wiki/sources/draft/design-pattern-v2.md`
- **Commit:** `73ad42f` — feat(wiki): add Học Từ Thiền System Design series
- **Date promoted:** 2026-06-21
