# Networking Interview Questions

20 questions across L3, L4, and L7. Practice answering out loud.

---

## L3 — Network Layer

**Q1: What is the difference between a public and a private IP address?**

Private IPs (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`) are not routable on the internet — they're used inside private networks. Public IPs are globally unique and routable. NAT (Network Address Translation) allows many private IPs to share one public IP for outbound internet access. In AWS, instances in private subnets use a NAT Gateway to reach the internet without being directly reachable from it.

---

**Q2: What does /24 mean in 10.0.1.0/24? How many hosts can it have?**

`/24` is CIDR notation — 24 bits are the network prefix, 8 bits are for hosts. `2^8 = 256` total addresses, minus network address and broadcast = **254 usable hosts**.

To subnet further: `/25` gives two subnets of 126 hosts each. `/28` gives 14 hosts.

---

**Q3: What is a routing table and how does a router decide which path to use?**

A routing table is a list of network destinations and where to send packets for each. When a packet arrives, the router finds all matching routes and picks the **most specific** one (longest prefix match). A `/28` route wins over a `/16` route even if both match.

The default route `0.0.0.0/0` matches everything — it's the fallback when nothing more specific matches.

---

**Q4: What is BGP and when would you encounter it as an SRE?**

BGP (Border Gateway Protocol) is how networks advertise reachable IP prefixes to each other. On the internet, ISPs use BGP to exchange routes. In large on-prem environments, BGP is used between data centers for failover — advertising the same IP block from two locations, so traffic routes to the healthy one.

As an SRE you encounter BGP when: setting up AWS Direct Connect (uses BGP to exchange routes between on-prem and AWS), troubleshooting multi-datacenter failover, or in postmortems when a BGP misconfiguration caused an outage.

---

**Q5: What is the difference between a Security Group and a NACL in AWS?**

| | Security Group | NACL |
|---|---|---|
| Level | Instance / ENI | Subnet |
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions) |
| Rules | Allow only | Allow and deny |
| Evaluation | All rules evaluated | Rules evaluated in number order, first match wins |

Security Groups are the primary tool — you use them most. NACLs are a second layer for subnet-level blocking (e.g., blocking a specific IP range from an entire subnet).

---

## L4 — Transport Layer

**Q6: What is the TCP 3-way handshake? Why does it matter for SREs?**

```
SYN → SYN-ACK → ACK
```

Client sends SYN, server responds SYN-ACK, client confirms with ACK. Connection is established after 1.5 round trips — before any data flows.

SRE implications:
- Every new connection costs a handshake — high connection churn hurts latency
- SYN flood attacks send SYN but never ACK, filling the server's half-open connection table
- TIME_WAIT sockets (post-connection cleanup) linger for ~60s, can exhaust ephemeral ports under load

---

**Q7: What is TIME_WAIT and why is it a problem at scale?**

After a TCP connection closes, the side that initiated the close enters `TIME_WAIT` for 2×MSL (~60-120 seconds). This ensures delayed packets from the old connection don't corrupt a new one on the same port.

At high request rates (many short-lived connections), TIME_WAIT sockets accumulate and can exhaust the ephemeral port range (typically ~28,000 ports on Linux). The fix: enable `tcp_tw_reuse`, expand the port range, or use connection pooling to avoid creating new connections constantly.

---

**Q8: What is the difference between TCP and UDP? Give examples of each.**

TCP: reliable, ordered, connection-oriented. Use when data must arrive correctly: HTTP/HTTPS, SSH, database connections, file transfers.

UDP: unreliable, connectionless, fast. Use when speed matters more than perfect delivery: DNS lookups, video streaming, VoIP, gaming. A single dropped UDP packet in a video call is less bad than waiting for TCP to retransmit it.

---

**Q9: What is the difference between NLB and ALB in AWS?**

NLB (L4): routes based on IP/port only. Extremely fast, preserves client source IP, supports TCP/UDP, has static IPs. Use for: non-HTTP protocols, need for static IP, very high throughput.

ALB (L7): understands HTTP. Routes based on URL path, hostname, headers, cookies. Supports WAF, authentication, redirects. Use for: HTTP/HTTPS apps, URL-based routing, microservices.

A common pattern: NLB in front of ALB when you need a static IP (for whitelisting) but also need L7 routing.

---

**Q10: Walk me through what happens when your app server runs out of ephemeral ports.**

New outbound connections fail with `EADDRINUSE` or similar. Symptoms: connection timeouts, "cannot assign requested address" errors in logs. The app may look healthy but can't connect to downstream services (database, Redis, other microservices).

Diagnose: `ss -s` shows socket counts, `cat /proc/sys/net/ipv4/ip_local_port_range` shows the range. Fix short-term: `sysctl net.ipv4.ip_local_port_range="1024 65535"`. Fix long-term: add connection pooling so connections are reused instead of created and destroyed per request.

---

## L7 — Application Layer

**Q11: What is the difference between a 502, 503, and 504?**

- **502 Bad Gateway:** the load balancer reached a backend, but the backend returned an invalid response. Backend is running but broken.
- **503 Service Unavailable:** the load balancer has no healthy backends to send the request to. Either they're all down, or the health check is failing.
- **504 Gateway Timeout:** the load balancer reached a backend, but it didn't respond within the timeout. Backend is alive but too slow.

Debugging: 502 → check backend logs for crashes. 503 → check health check configuration and backend status. 504 → check backend latency, look for slow queries or resource exhaustion.

---

**Q12: What happens when you type https://example.com in a browser?**

1. **DNS:** browser resolves `example.com` → IP via local cache, OS, recursive resolver
2. **TCP:** browser opens TCP connection to port 443 (3-way handshake)
3. **TLS:** TLS handshake — server presents certificate, browser verifies it, session keys exchanged
4. **HTTP:** browser sends `GET / HTTP/1.1` with `Host: example.com`
5. **Load balancer:** request hits ALB/F5, routed to a backend based on rules
6. **Backend:** processes request, returns HTML
7. **Response:** browser receives 200 OK with HTML, renders page, fires additional requests for CSS/JS/images

---

**Q13: What is TLS termination and why do we do it at the load balancer?**

TLS termination means the load balancer decrypts HTTPS traffic, then forwards plain HTTP to backends. Benefits:
- Backends don't need SSL certificates or the CPU cost of encryption/decryption
- Load balancer can inspect and route based on HTTP content (URL, headers) — impossible with end-to-end encryption
- Centralized certificate management

The trade-off: traffic between LB and backend is unencrypted. For compliance requirements, you use end-to-end TLS (the LB re-encrypts before forwarding).

---

**Q14: What is SNI and why does it matter?**

SNI (Server Name Indication) is a TLS extension where the client includes the desired hostname in the ClientHello message — before the TLS handshake completes. This lets a server (or load balancer) host multiple HTTPS sites on one IP, presenting the correct certificate for each.

Without SNI, one IP = one certificate. With SNI, one IP can serve many domains. ALB uses SNI to support multiple certificates on a single listener.

---

**Q15: How does DNS failover work in Route53?**

Route53 health checks continuously monitor an endpoint (HTTP, HTTPS, or TCP). You create two records for the same name: primary and secondary, both with `Failover` routing policy.

When the primary health check fails, Route53 stops returning the primary record and starts returning the secondary. TTL determines how quickly clients pick up the change — low TTL (60s) means fast failover.

On-prem equivalent: F5 GTM with health monitors, or BGP route withdrawal (stop advertising the unhealthy data center's prefix).

---

**Q16: What is the difference between a CNAME and an ALIAS record?**

A CNAME maps one hostname to another hostname. It cannot be used at the root domain (`example.com`) — DNS spec forbids it.

An ALIAS record (Route53-specific) also maps to a hostname, but works at the root domain and doesn't count as an extra DNS hop for billing. It maps `example.com → my-alb.elb.amazonaws.com` — something a CNAME can't do.

---

**Q17: What is SSL offloading vs end-to-end TLS?**

SSL offloading: LB terminates TLS, forwards HTTP to backends. Simpler, better performance.

End-to-end TLS: LB terminates TLS, re-encrypts and forwards HTTPS to backends. Required when: compliance mandates encrypted traffic everywhere (PCI-DSS, HIPAA), or you don't trust the network between LB and backend.

---

**Q18: How does cookie-based session persistence work on a load balancer?**

When a client first hits the load balancer, the LB picks a backend and inserts a cookie (e.g., `AWSALB=xxxxx`) in the response. On subsequent requests, the client sends the cookie back. The LB reads it and routes to the same backend.

Used when session state is stored on the server (not in a shared cache like Redis). Better practice: store sessions in Redis/ElastiCache so any backend can serve any request — no stickiness needed.

---

**Q19: What is the difference between L4 and L7 load balancing? When would you choose each?**

L4 (NLB, F5 TCP VIP): routes based on IP and port only. Doesn't inspect content. Faster, lower overhead. Use for: UDP traffic, need static IP, very high throughput, non-HTTP protocols, preserving client source IP.

L7 (ALB, F5 HTTP VIP): inspects HTTP content. Can route based on URL, headers, cookies. Supports redirects, auth, WAF. Use for: HTTP/HTTPS microservices, URL-based routing to different backends, header-based canary deployments.

---

**Q20: A user reports the site is slow. Walk me through your networking investigation.**

```
1. Connectivity: can I reach the site at all? ping / curl -v
2. DNS: is DNS resolving correctly and quickly? dig + time it
3. TLS: is the TLS handshake slow? Check cert validity, OCSP
4. Load balancer: check LB metrics — latency, 5xx rate, healthy target count
5. Target health: are backends healthy? Check target group health in ALB
6. Backend latency: check application metrics — slow queries, high CPU, memory pressure
7. Network path: traceroute to check for packet loss or high latency hops
8. Between services: if microservices, check service-to-service latency, connection pool exhaustion
```

Always correlate with recent deployments or config changes first.
