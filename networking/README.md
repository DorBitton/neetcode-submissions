# Networking

> **Focus: L3, L4, L7 only.** These are the three layers that matter for SRE interviews.

---

## File Map

| File | What's in it |
|---|---|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | All commands, ports, protocols on one page |
| [`concepts/l3-network-layer.md`](./concepts/l3-network-layer.md) | ✅ IP, CIDR, subnetting, routing, BGP — on-prem routers + AWS VPC |
| [`concepts/l4-transport-layer.md`](./concepts/l4-transport-layer.md) | TCP/UDP, ports, handshake, connections — F5 TCP VIPs + AWS NLB |
| [`concepts/l7-application-layer.md`](./concepts/l7-application-layer.md) | HTTP/HTTPS, DNS, TLS — F5 iRules/profiles + AWS ALB + Route53 |
| [`interview-questions.md`](./interview-questions.md) | 20 networking questions you will get asked |

---

## The three layers — quick map

```
L7  Application   HTTP, HTTPS, DNS, TLS       F5 HTTP profile / iRule    AWS ALB, Route53
L4  Transport     TCP, UDP, ports              F5 TCP/UDP VIP             AWS NLB
L3  Network       IP, CIDR, routing            On-prem routers, BGP       AWS VPC, route tables
```

---

## Practice Tasks (prepare.sh)

Work through these at [prepare.sh/track/devops](https://prepare.sh/track/devops) → Networking section.

### Easy (5)
- [ ] Validating DNS Consistency
- [ ] Network Packet Loss Diagnosis
- [ ] Network Port Service Cleanup
- [ ] Temporary Route Configuration
- [ ] Network Socket Usage Analysis

### Medium (3)
- [ ] Validating Network Routes
- [ ] Inspecting HTTP Traffic Flow
- [ ] Forward Traffic Between Ports

### Hard (1)
- [ ] Macvlan Network Configuration Fix

---

## Study order

1. ✅ L3 — understand IP and routing first, everything else builds on it
2. L4 — understand TCP before HTTP (HTTP runs on top of TCP)
3. L7 — HTTP, DNS, TLS
