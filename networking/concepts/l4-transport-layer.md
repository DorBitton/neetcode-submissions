# L4 — Transport Layer

> TCP, UDP, ports, and load balancing at the connection level.

---

## Table of Contents

1. [What L4 Does](#1-what-l4-does)
2. [TCP vs UDP](#2-tcp-vs-udp)
3. [TCP in Depth](#3-tcp-in-depth)
4. [Ports](#4-ports)
5. [On-prem: F5 L4 Load Balancing (VIPs and Pools)](#5-on-prem-f5-l4-load-balancing-vips-and-pools)
6. [AWS: Network Load Balancer (NLB)](#6-aws-network-load-balancer-nlb)
7. [On-prem vs AWS Mapping](#7-on-prem-vs-aws-mapping)

---

## 1. What L4 Does

L4 is responsible for **end-to-end communication between processes** on two hosts.

- Adds the concept of **ports** — so multiple processes on one IP can communicate
- Provides either **reliability** (TCP) or **speed** (UDP)
- Does not know what the data means — that's L7's job

Key protocols: **TCP** and **UDP**

---

## 2. TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Connection | Connection-oriented (3-way handshake) | Connectionless |
| Reliability | Guaranteed delivery, retransmits lost packets | No guarantee, fire and forget |
| Ordering | In-order delivery | No ordering |
| Speed | Slower (overhead of reliability) | Faster (no overhead) |
| Use cases | HTTP, HTTPS, SSH, databases | DNS, video streaming, gaming, VoIP |

**Rule of thumb:**
- Use TCP when **correctness matters** (you can't have missing data)
- Use UDP when **speed matters** and some loss is acceptable

---

## 3. TCP in Depth

### The 3-way handshake (connection setup)

```
Client                          Server
  │                               │
  │──── SYN ──────────────────────▶│   "I want to connect, my seq=X"
  │                               │
  │◀─── SYN-ACK ──────────────────│   "OK, my seq=Y, I got your seq=X"
  │                               │
  │──── ACK ──────────────────────▶│   "Got it, let's go"
  │                               │
  │        [data transfer]        │
```

**Why this matters for SRE:**
- Every TCP connection costs a handshake (1.5 round trips before data flows)
- Under high load, servers run out of ephemeral ports or connection table space
- SYN flood attacks exploit the handshake (send SYN, never ACK → server holds half-open connections)

### TCP connection states

```
LISTEN      → server waiting for connections
SYN_SENT    → client sent SYN, waiting for SYN-ACK
ESTABLISHED → connection active, data flowing
FIN_WAIT    → one side closing the connection
TIME_WAIT   → waiting to ensure remote has received the close (lasts 2 * MSL, ~60-120s)
CLOSE_WAIT  → received FIN from remote, waiting for local app to close
```

**TIME_WAIT is a common SRE issue:** under high connection churn (many short-lived connections), sockets pile up in TIME_WAIT and exhaust ephemeral ports.

```bash
# Check connection states
ss -s                      # socket summary
ss -tan | grep TIME_WAIT   # count TIME_WAIT connections
netstat -an | grep ESTABLISHED | wc -l   # count established connections
```

### TCP tuning knobs SREs touch

```bash
# View current limits
cat /proc/sys/net/ipv4/ip_local_port_range   # ephemeral port range
cat /proc/sys/net/core/somaxconn             # max listen backlog
cat /proc/sys/net/ipv4/tcp_tw_reuse          # reuse TIME_WAIT sockets

# Common tuning
sysctl net.ipv4.ip_local_port_range="1024 65535"   # more ephemeral ports
sysctl net.ipv4.tcp_tw_reuse=1                      # reuse TIME_WAIT
sysctl net.core.somaxconn=65535                     # bigger listen queue
```

---

## 4. Ports

Ports identify which process on a host should receive a packet.

- **Well-known ports (0-1023):** reserved for system services, require root
- **Registered ports (1024-49151):** common applications
- **Ephemeral ports (49152-65535):** client-side, assigned automatically

**Common ports you must know:**

| Port | Protocol | Service |
|---|---|---|
| 22 | TCP | SSH |
| 25 | TCP | SMTP (email) |
| 53 | TCP/UDP | DNS |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |
| 3306 | TCP | MySQL |
| 5432 | TCP | PostgreSQL |
| 6379 | TCP | Redis |
| 8080 | TCP | HTTP (alt) |
| 9090 | TCP | Prometheus |
| 9200 | TCP | Elasticsearch |

---

## 4a. ICMP — Internet Control Message Protocol

ICMP is a Layer 3 protocol (it rides on IP, not TCP/UDP) used by network devices to send **error and diagnostic messages** back to senders.

### Key ICMP message types

| Type | Name | What it means |
|---|---|---|
| 0 / 8 | Echo reply / Echo request | `ping` — basic reachability test |
| 3 | Destination unreachable | Packet couldn't be delivered (port closed, network unreachable) |
| 11 | Time exceeded | TTL hit zero — `traceroute` uses this |
| 12 | Parameter problem | Malformed IP header |

**Packet Too Big (Type 3, Code 4):** one of the most important for SREs.

When a packet is larger than the MTU (Maximum Transmission Unit) of a link along the path, the router drops the packet and sends an ICMP "Packet Too Big" back to the sender. The sender then reduces its packet size.

If ICMP is blocked, the sender never gets this message and the connection silently hangs.

### MTU and Path MTU Discovery

**MTU (Maximum Transmission Unit):** the largest packet a link can carry.
- Ethernet standard: **1500 bytes**
- Jumbo frames (some data center configs): up to 9000 bytes

**Path MTU Discovery (PMTUD):** TCP discovers the smallest MTU along the entire path so it doesn't send oversized packets. It does this by:
1. Sending packets with the "Don't Fragment" (DF) bit set
2. If a router can't forward it, it sends back ICMP Packet Too Big
3. TCP reduces the MSS (Maximum Segment Size) and retries

**The ICMP blocking problem:** many "security-hardened" environments block all ICMP. This breaks PMTUD. Symptoms:
- Connection establishes fine (small packets work)
- Large transfers hang or fail silently (big packets get dropped, no ICMP error returned)
- VPN tunnels are a common place this shows up (tunnel overhead reduces effective MTU)

```bash
# Debug MTU issues
ping -M do -s 1472 8.8.8.8    # send 1500-byte packet (1472 data + 28 IP/ICMP headers), DF set
                                # if it fails, MTU is below 1500
tracepath example.com          # discovers MTU along path (unlike traceroute)
ip link show eth0 | grep mtu   # show interface MTU
```

### Why you should never block all ICMP

Common mistake: block ICMP entirely for "security." This breaks:
- `ping` (obviously)
- `traceroute` / MTU discovery (PMTUD silently fails)
- Large TCP transfers that need to negotiate smaller packet sizes

**What you should actually do:** block ICMP echo (ping) if you must for security, but always allow:
- `ICMP Type 3` (Destination Unreachable) — needed for PMTUD and port-unreachable signals
- `ICMP Type 11` (Time Exceeded) — needed for traceroute to work

### ICMP in SRE work

```bash
ping -c 5 8.8.8.8               # basic connectivity test, check packet loss %
traceroute 8.8.8.8              # map the path, find where packets stop
mtr 8.8.8.8                    # continuous traceroute with live stats (best for debugging)
ping -f -c 1000 10.0.0.1       # flood ping — stress test, measure loss rate
```

`mtr` is the most useful tool for diagnosing routing issues — it combines `ping` and `traceroute` and shows live packet loss per hop.

---

## 5. On-prem: F5 L4 Load Balancing (VIPs and Pools)

F5 BIG-IP is the dominant on-prem load balancer. Understanding its model is essential for big tech SRE interviews where on-prem infra is in scope.

### The F5 model: VIP → Pool → Members

```
Client
  │
  ▼
[VIP]  10.0.1.100:80          ← Virtual IP: the address clients connect to
  │
  ▼
[Pool]  my-app-pool            ← group of backend servers
  ├── Member: 10.0.2.10:8080  ← pool member 1
  ├── Member: 10.0.2.11:8080  ← pool member 2
  └── Member: 10.0.2.12:8080  ← pool member 3
```

**VIP (Virtual IP):** the IP:port clients connect to. The F5 owns this IP. Clients never know the backend IPs exist.

**Pool:** a group of real servers. The F5 picks one per connection using a load balancing method.

**Pool Member:** a real server (IP:port). F5 health checks each member and removes unhealthy ones from rotation.

### L4 vs L7 on F5

| | L4 (TCP/UDP) | L7 (HTTP) |
|---|---|---|
| F5 sees | IP/port only | Full HTTP headers, URLs, cookies |
| Performance | Faster, lower overhead | Slower, more CPU |
| Routing decisions | Based on IP/port | Based on URL, headers, cookies |
| Use when | Any TCP/UDP app, raw performance | HTTP apps, need URL routing or cookie persistence |

### Load balancing methods (F5)

```
Round Robin         → distribute evenly in order
Least Connections   → send to member with fewest active connections (best for variable request times)
Ratio               → weighted distribution (80% to fast servers, 20% to slow)
Priority Group      → send to group A, only use group B if A is down (active/standby)
```

### Persistence (session stickiness)

When a client must always reach the same backend (e.g., session state stored on server):

```
Source IP persistence   → same client IP always goes to same member
Cookie persistence      → F5 inserts a cookie, client sends it back, F5 routes accordingly
SSL Session ID          → persist based on TLS session ID
```

### Health checks

F5 monitors members and removes them if they fail:

```
ICMP ping             → basic "is the host up?"
TCP connect           → can we establish a connection?
HTTP GET /health      → does the app respond 200? (better — tests the app itself)
Custom script         → run a script, check exit code
```

**Interval / timeout / threshold:**
```
interval=5s, timeout=16s, threshold=1
→ check every 5s, if no response in 16s, mark down after 1 failure
```

---

## 6. AWS: Network Load Balancer (NLB)

NLB is AWS's L4 load balancer. Same concept as F5 TCP VIPs, different terminology.

```
Client
  │
  ▼
[NLB]  my-nlb-xxxxx.elb.amazonaws.com:443
  │
  ▼
[Target Group]  my-targets
  ├── EC2: 10.0.1.10:443
  ├── EC2: 10.0.1.11:443
  └── EC2: 10.0.1.12:443
```

**NLB characteristics:**
- Operates at L4 (TCP, UDP, TLS)
- Extremely high performance — millions of requests per second
- Preserves client source IP (unlike ALB which uses X-Forwarded-For)
- Static IP per AZ (or Elastic IP) — good for whitelisting
- No HTTP-aware routing (that's ALB)

**Target types:**
```
Instance    → EC2 instance IDs
IP          → any IP (including on-prem via Direct Connect)
Lambda      → Lambda functions (limited)
ALB         → another load balancer (NLB → ALB pattern)
```

**Health checks:**
```
TCP         → can we connect?
HTTP/HTTPS  → does the app respond 200?
```

**When to use NLB vs ALB:**
```
NLB:
- TCP/UDP protocols (not HTTP)
- Need static IP
- Need to preserve client source IP
- Extremely high throughput / low latency
- On-prem targets via Direct Connect

ALB:
- HTTP/HTTPS traffic
- Need URL-based or header-based routing
- Need to inspect/modify requests (WAF, auth)
- Websockets
```

---

## 7. On-prem vs AWS Mapping

| On-prem (F5) | AWS (NLB) |
|---|---|
| VIP (Virtual IP) | NLB DNS name / static IP |
| Pool | Target Group |
| Pool Member | Target (EC2, IP) |
| Health monitor | Health check |
| Persistence profile | Stickiness settings on Target Group |
| Priority group (active/standby) | Multi-AZ with failover |
| iRule (TCP) | NLB listener rules (limited at L4) |
| SNAT (hide client IP) | NLB with proxy protocol or preserve source IP |
