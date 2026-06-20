# L7 — Application Layer

> HTTP, HTTPS, DNS, TLS. The layer your users actually interact with.

---

## Table of Contents

1. [What L7 Does](#1-what-l7-does)
2. [HTTP](#2-http)
3. [HTTPS and TLS](#3-https-and-tls)
4. [DNS](#4-dns)
5. [On-prem: F5 L7 Load Balancing](#5-on-prem-f5-l7-load-balancing)
6. [AWS: Application Load Balancer (ALB) and Route53](#6-aws-application-load-balancer-alb-and-route53)
7. [On-prem vs AWS Mapping](#7-on-prem-vs-aws-mapping)

---

## 1. What L7 Does

L7 is the layer applications speak. It understands the **content** of the traffic — not just where it's going, but what it is.

- HTTP/HTTPS: web traffic
- DNS: name → IP resolution
- gRPC, WebSockets, SMTP — all L7 protocols

L7 load balancers and proxies can make routing decisions based on URLs, headers, cookies, body content.

---

## 2. HTTP

HTTP (HyperText Transfer Protocol) is a request-response protocol.

### Request structure
```
GET /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

```
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "dor", "role": "sre"}
```

### Response structure
```
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-Id: abc123

{"id": 42, "name": "dor"}
```

### Status codes you must know

| Code | Meaning | Notes |
|---|---|---|
| 200 | OK | success |
| 201 | Created | POST success |
| 204 | No Content | success, no body |
| 301 | Moved Permanently | redirect, client caches it |
| 302 | Found | redirect, temporary |
| 400 | Bad Request | client sent invalid data |
| 401 | Unauthorized | not authenticated |
| 403 | Forbidden | authenticated but not allowed |
| 404 | Not Found | resource doesn't exist |
| 429 | Too Many Requests | rate limited |
| 500 | Internal Server Error | server bug |
| 502 | Bad Gateway | upstream returned invalid response |
| 503 | Service Unavailable | server overloaded or down |
| 504 | Gateway Timeout | upstream didn't respond in time |

**502 vs 503 vs 504:**
```
502  → load balancer reached backend, backend gave garbage response
503  → load balancer can't reach any healthy backend
504  → load balancer reached backend, backend was too slow
```
These three are the most common SRE alert codes. Know them cold.

### HTTP versions

```
HTTP/1.0   → one request per TCP connection
HTTP/1.1   → keep-alive: multiple requests per connection, but still sequential
HTTP/2     → multiplexing: many requests in parallel over one connection, binary protocol
HTTP/3     → runs on QUIC (UDP-based), lower latency, better mobile performance
```

### HTTP/1.1 head-of-line blocking

HTTP/1.1 is a text protocol — one request, wait for response, then send the next. Even with keep-alive (reusing the TCP connection), requests are **sequential on that connection**.

```
Connection 1:  [req1 ──────────────▶ resp1] [req2 ──────────▶ resp2]
                wait...                       wait...
```

Browsers work around this by opening **6 parallel TCP connections** per origin. But each connection has its own TCP + TLS handshake cost. Under high concurrency this creates thousands of connections server-side.

### HTTP/2 multiplexing

HTTP/2 is a **binary, framed protocol**. Each request gets a stream ID. Multiple streams travel concurrently over one TCP connection.

```
One TCP connection:
  Stream 1: [GET /] ──────────────────────▶ [200 + body]
  Stream 2: [GET /style.css] ─────────────▶ [200 + body]
  Stream 3: [GET /app.js] ────────────────▶ [200 + body]
            all at the same time
```

No head-of-line blocking at the HTTP layer. One connection, many parallel requests.

**HTTP/2 still has TCP head-of-line blocking:** if one TCP segment is lost, all streams stall until TCP retransmits it.

### HTTP/3 / QUIC

HTTP/3 replaces TCP with **QUIC** (a protocol built on UDP):
- Each stream is independent at the transport layer — one lost packet stalls only that stream, not all streams
- TLS 1.3 is built in — 1-RTT or 0-RTT connection setup
- Connection migration — if your IP changes (phone switches from WiFi to cellular), the QUIC connection survives

---

## 3. HTTPS and TLS

HTTPS = HTTP running inside a TLS tunnel.

### TLS handshake (simplified)
```
Client                              Server
  │                                   │
  │──── ClientHello ─────────────────▶│  "I support TLS 1.3, here are my cipher suites"
  │                                   │
  │◀─── ServerHello + Certificate ────│  "Use this cipher. Here's my cert (signed by CA)"
  │                                   │
  │  [client verifies cert against    │
  │   trusted CA root store]          │
  │                                   │
  │──── Key Exchange ────────────────▶│  both sides derive session keys
  │                                   │
  │        [encrypted data]           │
```

**Key concepts:**
- **Certificate:** proves the server is who it claims to be. Signed by a CA (Certificate Authority).
- **CA (Certificate Authority):** a trusted third party (DigiCert, Let's Encrypt, AWS ACM) that signs certs
- **SNI (Server Name Indication):** allows multiple HTTPS sites on one IP — client sends the hostname in the TLS handshake so the server knows which cert to present
- **SSL offloading / TLS termination:** the load balancer handles TLS, forwards plain HTTP to backends — reduces CPU load on app servers

**Certificate chain:**
```
Root CA (DigiCert)
  └── Intermediate CA
        └── Your cert (api.example.com)
```
Browsers trust Root CAs. Your cert is trusted because the chain leads back to a root.

### ALPN — Application Layer Protocol Negotiation

ALPN is a TLS extension that lets client and server negotiate **which application protocol to use** inside the TLS handshake — before any HTTP is sent.

```
ClientHello includes:  ALPN: ["h2", "http/1.1"]
ServerHello responds:  ALPN: "h2"
→ both sides know to use HTTP/2 from the first encrypted byte
```

Without ALPN, you'd need a separate round-trip to negotiate the protocol. ALPN is how HTTP/2 gets enabled — the negotiation happens for free inside the TLS handshake.

**Debug it:**
```bash
curl -v https://example.com 2>&1 | grep -i "ALPN\|h2"
openssl s_client -alpn h2 -connect example.com:443
```

### HSTS — HTTP Strict Transport Security

A response header that tells browsers: **always use HTTPS for this domain, never HTTP**, even if the user types `http://`.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**The problem it solves:** the very first HTTP request to a site (before HSTS is set) can be intercepted and redirected to a fake HTTPS site. HSTS prevents the initial HTTP request from ever happening after the first visit.

**HSTS preload:** browsers ship with a built-in list of domains that are HSTS-only. Even the first-ever visit uses HTTPS. Submit your domain at hstspreload.org.

**SRE gotcha:** if you set HSTS with a long max-age and then need to serve HTTP (during cert incident, or migrating off HTTPS), browsers will refuse to connect for up to a year for returning users.

### TLS Session Resumption

Re-doing the full TLS handshake on every connection is expensive. Session resumption lets clients **skip the key exchange** on subsequent connections.

**Session tickets:** server encrypts session state and sends it to the client as a "ticket." Next connection, client sends the ticket back, server decrypts it, skips the handshake.

```
First connection:   ClientHello → ServerHello + Cert + Session Ticket → Key Exchange → Done
Second connection:  ClientHello + Session Ticket → ServerHello → Done (1 RTT instead of 2)
```

**TLS 1.3 0-RTT:** even faster — client can send application data with the very first packet using a pre-shared key from the previous session. Trade-off: replay attack risk (same data could be replayed by an attacker). Not safe for non-idempotent requests.

### Private CAs

Public CAs (DigiCert, Let's Encrypt, AWS ACM) are pre-trusted by everyone because they're in the OS/browser trust store. But companies often run their own **private CA** for internal and B2B services.

**Why run a private CA:**
- Issue and revoke certs instantly, no third party, no cost per cert
- Internal APIs that should never be hit by a random browser don't need a public CA
- Enables mTLS — you control who gets client certificates (see below)

**The catch:** your private CA is not in anyone's trust store. Any system that needs to connect to a service using your private certs must first **install your CA certificate manually** — otherwise they get:
```
SSL Error: certificate signed by unknown authority
```

This is why companies distribute their CA cert to partners and vendors. Installing it tells the client: "trust certs signed by this CA."

```bash
# Install a CA cert on Linux (so all apps trust it system-wide)
cp company-ca.crt /usr/local/share/ca-certificates/
update-ca-certificates

# Or pass it per-request with curl
curl --cacert company-ca.crt https://internal-api.example.com/
```

### mTLS — Mutual TLS

Standard TLS is one-sided: the **server** proves its identity to the client. The client is anonymous.

**Mutual TLS (mTLS)** requires **both sides** to present a certificate:

```
Standard TLS:                       mTLS:
                                    
Client → "prove you're example.com" Client → "prove you're example.com"
Server presents cert ✅             Server presents cert ✅
Connection established              Server → "now prove who you are"
                                    Client presents its own cert ✅
                                    Connection established
```

**Why this matters:** with mTLS, the server can reject any connection that doesn't hold a certificate *it issued*. Even if an attacker knows the URL and the port is open, they're blocked at the TLS layer — before a single HTTP request is processed. No cert = no connection.

**The trust requirement — both sides need each other's CA:**

```
Company A runs API server       Company B is a vendor connecting to it

Company A needs:                Company B needs:
  - Its own server cert           - Company A's CA cert
    (signed by A's private CA)      (to trust A's server cert)
  - Company B's CA cert           - Its own client cert
    (to verify B's client cert)     (signed by B's private CA)
                                  - Company A's CA cert
                                    (already covered above)
```

Each side must have:
1. **Their own cert** (to present when asked)
2. **The other side's CA cert** (to verify what they receive)

**Real-world scenario:** a payment processor connecting to a gambling company's API. Both sides run their own internal CAs. The gambling company gives the payment processor their CA cert. The payment processor gives the gambling company their CA cert. Now both sides can verify each other at the TLS layer — no passwords, no API keys, the certificate *is* the authentication.

**When mTLS breaks:**
```
Client gets:  "certificate required" or "bad certificate"
→ Client forgot to present its client cert, or presented the wrong one

Client gets:  "certificate signed by unknown authority"  
→ Client doesn't have the server's CA cert installed

Server gets:  "certificate signed by unknown authority"
→ Server doesn't have the client's CA cert installed
              (or the client cert was issued by a different CA than expected)
```

### Common TLS issues SREs deal with
```
Certificate expired         → HTTPS breaks entirely, users see browser warning
Wrong hostname in cert      → cert for api.example.com used on www.example.com → error
Self-signed cert            → not trusted by browsers unless manually installed
Mixed content               → HTTPS page loading HTTP resources → blocked by browsers
TLS version mismatch        → client needs TLS 1.2, server only offers 1.3 (or vice versa)
ALPN mismatch               → server doesn't advertise h2, clients fall back to HTTP/1.1
HSTS misconfigured          → max-age too long before you're sure HTTPS is stable
mTLS — missing client cert  → server rejects connection before HTTP layer
mTLS — CA not installed     → "unknown authority" on either side
```

---

## 4. DNS

DNS (Domain Name System) translates hostnames to IP addresses.

### How DNS resolution works

```
Browser: what is the IP for api.example.com?

1. Check local cache → not found
2. Ask OS resolver (127.0.0.53) → not found
3. Ask recursive resolver (8.8.8.8 or your ISP's resolver)
4. Recursive resolver asks root nameserver → "try .com nameserver"
5. Recursive resolver asks .com nameserver → "try example.com nameserver"
6. Recursive resolver asks example.com nameserver → "api.example.com = 203.0.113.5"
7. Resolver caches the answer (for TTL seconds), returns to browser
```

### DNS record types

| Record | Purpose | Example |
|---|---|---|
| `A` | hostname → IPv4 | `api.example.com → 203.0.113.5` |
| `AAAA` | hostname → IPv6 | `api.example.com → 2001:db8::1` |
| `CNAME` | hostname → hostname | `www.example.com → example.com` |
| `MX` | mail server for domain | `example.com → mail.example.com` |
| `TXT` | arbitrary text | SPF records, domain verification |
| `NS` | nameservers for domain | `example.com NS → ns1.awsdns.com` |
| `PTR` | reverse DNS (IP → hostname) | `203.0.113.5 → api.example.com` |
| `SOA` | start of authority (zone metadata) | serial number, refresh intervals |

**TTL (Time To Live):** how long resolvers cache a DNS record (in seconds).
- Low TTL (60-300s) → fast failover, but more DNS queries
- High TTL (3600s+) → cached longer, cheaper, but slow to propagate changes

**CNAME gotcha:** you cannot use a CNAME on the root domain (`example.com`) — only subdomains. This is the "CNAME at apex" problem. AWS Route53 solves this with ALIAS records.

### Debugging DNS
```bash
dig api.example.com              # full DNS lookup
dig api.example.com A            # only A records
dig @8.8.8.8 api.example.com     # query specific resolver
dig +trace api.example.com       # trace full resolution chain
nslookup api.example.com         # older alternative
host api.example.com             # simple lookup
```

---

## 5. On-prem: F5 L7 Load Balancing

At L7, F5 understands HTTP. This lets you make routing decisions based on content.

### F5 L7 model: same VIP → Pool structure, plus HTTP awareness

```
Client
  │  HTTP GET /api/users
  ▼
[VIP: 10.0.1.100:80]   ← F5 terminates TCP connection here
  │
  │  F5 reads HTTP request, applies iRules and profiles
  │
  ├── if URL starts with /api → pool: api-servers
  ├── if URL starts with /static → pool: cdn-servers
  └── default → pool: web-servers
```

### HTTP Profiles

F5 HTTP profiles control how F5 handles HTTP traffic:

```
HTTP compression          → compress responses (gzip) before sending to client
X-Forwarded-For           → insert client's real IP into header (backends need this)
HTTP redirect             → redirect HTTP to HTTPS
OneConnect                → reuse server-side TCP connections (connection pooling)
Response caching          → cache static responses at the F5
```

### iRules

iRules are F5's scripting language (Tcl-based) for custom traffic manipulation:

```tcl
# Redirect HTTP to HTTPS
when HTTP_REQUEST {
    if { [HTTP::uri] starts_with "/old-path" } {
        HTTP::redirect "https://[HTTP::host]/new-path[HTTP::uri]"
    }
}

# Route based on header
when HTTP_REQUEST {
    if { [HTTP::header "X-Version"] eq "v2" } {
        pool v2-pool
    } else {
        pool v1-pool
    }
}
```

### SSL Offloading on F5

```
Client ─── HTTPS ──▶ F5 ─── HTTP ──▶ Backend servers
            443           80

F5 terminates TLS:
- holds the SSL certificate
- decrypts incoming traffic
- forwards plain HTTP to backends
- backends don't need to handle SSL (saves CPU)
```

**SSL re-encryption (end-to-end SSL):**
```
Client ─── HTTPS ──▶ F5 ─── HTTPS ──▶ Backend servers
            443                443

F5 decrypts, inspects, re-encrypts before forwarding
Used when compliance requires encrypted traffic throughout
```

---

## 6. AWS: Application Load Balancer (ALB) and Route53

### ALB — L7 Load Balancer

ALB is the AWS equivalent of F5 with an HTTP profile. It understands HTTP/HTTPS and routes based on content.

```
Client
  │  HTTPS GET /api/users
  ▼
[ALB]  my-alb-xxxxx.us-east-1.elb.amazonaws.com:443
  │
  │  ALB terminates TLS (using ACM certificate)
  │  ALB evaluates listener rules
  │
  ├── if path = /api/*      → Target Group: api-servers
  ├── if path = /static/*   → Target Group: cdn-servers
  ├── if header X-Beta=true → Target Group: beta-servers
  └── default               → Target Group: web-servers
```

### ALB Listener Rules

Rules are evaluated in priority order:

```
Priority 1: IF path = /api/*          → forward to api-tg
Priority 2: IF header X-Version = v2  → forward to v2-tg
Priority 3: IF host = admin.example.com → redirect 403
Default:    forward to web-tg
```

**Actions:**
```
forward         → send to target group
redirect        → 301/302 redirect (HTTP → HTTPS, old URL → new URL)
fixed-response  → return a static response (maintenance page, health check)
authenticate    → integrate with Cognito or OIDC (auth before forwarding)
```

### ALB + ACM (TLS certificates)

ACM (AWS Certificate Manager) provides free TLS certs, auto-renewing.

```
ALB listener on :443
  └── SSL certificate from ACM (*.example.com)
  └── ALB handles TLS termination
  └── Forwards HTTP to target group on :80
```

ALB supports **SNI** — multiple certificates on one ALB for different hostnames.

### Route53 — AWS DNS

Route53 is AWS's DNS service. Same concepts as any DNS, with AWS features.

**Record types Route53 adds:**
```
ALIAS record    → like CNAME but works at root domain
                  maps example.com → my-alb.elb.amazonaws.com
                  (solves the CNAME at apex problem)
```

**Routing policies:**
```
Simple          → one IP, standard DNS
Weighted        → 80% to v1, 20% to v2 (canary deployments)
Latency         → route to the AWS region with lowest latency for client
Failover        → primary record, if health check fails → switch to secondary
Geolocation     → route based on client's country/region
Health checks   → Route53 monitors endpoints, removes unhealthy from DNS
```

**Route53 for failover:**
```
Primary:   api.example.com → ALB in us-east-1    (health check: ON)
Secondary: api.example.com → ALB in us-west-2    (only serves if primary fails)
```

---

## 7. On-prem vs AWS Mapping

| On-prem (F5 L7) | AWS equivalent |
|---|---|
| VIP with HTTP profile | ALB |
| iRule (URL routing) | ALB listener rule (path/host/header conditions) |
| SSL offloading | ALB with ACM certificate |
| X-Forwarded-For header | ALB inserts X-Forwarded-For automatically |
| Pool | Target Group |
| Pool member | EC2 instance / IP target |
| Cookie persistence | ALB sticky sessions (duration-based or app-based) |
| F5 DNS (GTM) | Route53 |
| GTM health monitor | Route53 health check |
| GTM geo routing | Route53 geolocation policy |
| GTM failover | Route53 failover routing policy |
