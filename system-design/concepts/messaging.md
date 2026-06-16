# Messaging Systems: Kafka vs RabbitMQ

> Core question: **do you need a smart broker or a smart consumer?**

---

## Mental Model

```
RabbitMQ  →  Smart Broker, Simple Consumers
            The broker routes, filters, tracks, and removes messages.
            Consumers just receive and process.

Kafka     →  Simple Broker, Smart Consumers
            The broker is a durable, ordered log.
            Consumers track their own position (offset) and replay at will.
```

---

## RabbitMQ — Smart Broker

**Model:** message queue (traditional)

The broker is in charge:
- Routes messages to the right queues based on exchange rules
- Tracks what's been delivered and acknowledged
- Removes messages once consumed (they're gone)
- Supports complex routing: direct, topic, fanout, headers

**Use when:**
- You need complex routing logic (different message types → different consumers)
- Messages should be processed exactly once and deleted after
- Task queues: background jobs, email sending, order processing
- You want simpler consumer code (broker handles the complexity)
- Lower throughput but low-latency delivery matters

**Delivery guarantees:**
- At-most-once, at-least-once, or exactly-once (with manual ack)
- Message is ACKed → removed from queue. No replay.

**Persistence:**
- Optional. Can configure durable queues and persistent messages.
- Not designed for long-term retention.

---

## Kafka — Distributed Log

**Model:** distributed commit log (event streaming)

The log is in charge:
- Every message appended to a topic partition as an immutable log entry
- Messages are NOT deleted after consumption — retained for configurable time
- Consumers track their own offset (position in the log)
- Multiple consumer groups can independently read the same data

**Use when:**
- High throughput (millions of events/sec)
- Multiple downstream systems consume the same events independently
- You need event replay (re-process historical data, audit, debugging)
- Event sourcing or CDC (Change Data Capture)
- Stream processing pipelines (with Kafka Streams or Flink)

**Delivery guarantees:**
- At-least-once by default (consumer commits offset after processing)
- Exactly-once with Kafka transactions (more complex)

**Ordering:**
- Guaranteed within a partition
- No ordering guarantee across partitions

**Persistence:**
- By design. Retention is configurable (time-based or size-based).
- Default 7 days. You can keep messages forever.

---

## Comparison Table

| | RabbitMQ | Kafka |
|---|---|---|
| Model | Message queue | Distributed log |
| Smart part | Broker | Consumer |
| Routing | Exchange rules (complex) | Topic + partition (simple) |
| After consume | Message deleted | Message retained |
| Replay | No | Yes |
| Ordering | Per queue | Per partition |
| Throughput | Medium | Very high |
| Consumer independence | Competing consumers | Independent consumer groups |
| Best for | Task queues, RPC, routing | Event streaming, pipelines, replay |

---

## Decision Guide

**Choose RabbitMQ when:**
- You're building a task/job queue (background email, image processing)
- Routing complexity: "send this type of message to this type of worker"
- You want simple consumers and a smart broker to manage delivery

**Choose Kafka when:**
- Multiple services need the same event stream
- You need to replay events (debugging, onboarding new consumers, auditing)
- High throughput is a requirement
- You're doing real-time analytics or stream processing
- Event sourcing / CQRS architecture

---

## On-Prem vs AWS

| | On-prem self-managed | AWS managed |
|---|---|---|
| Kafka | Apache Kafka on your own VMs | Amazon MSK (Managed Streaming for Kafka) |
| RabbitMQ | RabbitMQ on your own VMs | Amazon MQ (managed RabbitMQ or ActiveMQ) |
| Simpler queue | — | Amazon SQS (no broker complexity, just a queue) |
| Pub/sub | — | Amazon SNS (fan-out to multiple subscribers) |

**SQS + SNS pattern (AWS-native alternative):**
- SNS topic receives events and fans out to multiple SQS queues
- Each SQS queue is consumed by a different service
- Simpler than Kafka/RabbitMQ for cloud-native architectures

---

## Interview Answer Framework

When asked "Kafka vs RabbitMQ":

1. **Start with the model:** "Kafka is a distributed log where consumers track offsets. RabbitMQ is a traditional message queue where the broker tracks delivery."
2. **Key differentiator:** "The biggest difference is replay — Kafka keeps messages after they're consumed, RabbitMQ deletes them."
3. **When to use each:** "If I need high throughput, multiple consumers on the same stream, or event replay — Kafka. If I need complex routing, task queues, or simple consumers — RabbitMQ."
4. **AWS angle if relevant:** "On AWS I'd use MSK for Kafka or Amazon MQ for RabbitMQ. For simpler use cases SQS/SNS is often enough."
