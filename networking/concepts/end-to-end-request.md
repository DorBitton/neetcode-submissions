# What Happens When You `curl https://example.com`

The single most common networking question in SRE interviews. Tests everything — DNS, TCP, TLS, HTTP, routing — in one answer.

---

## The Short Answer (30 seconds)

> DNS resolves the hostname to an IP. TCP connects to that IP (3-way handshake). TLS negotiates encryption and verifies the server's certificate. HTTP sends the GET request and receives the response. BGP is what routes packets across the internet between all those hops.

That's the skeleton. Interviewers want to see you go deeper on any layer.

---

## Step 1 — DNS Resolution

Before any packet goes anywhere, you need an IP address.

```
curl https://example.com
  │
  ├─ 1. Check local cache (OS, /etc/hosts)
  ├─ 2. Ask local recursive resolver (127.0.0.53 or ISP resolver)
  │       ├─ Ask root nameserver → "try .com nameservers"
  │       ├─ Ask .com nameserver → "try example.com nameservers"
  │       └─ Ask example.com nameserver → "93.184.216.34"
  └─ 3. Cache result (for TTL seconds), return IP to curl
```

**What can go wrong here:**
- Stale TTL → old IP still cached during a migration
- DNS hijack → wrong IP returned (BGP route leak upstream)
- Resolver down → total DNS failure for all names
- Wrong NS record → traffic hits the wrong nameserver

**Commands to see it live:**
```bash
dig +trace example.com     # shows every hop of the resolution chain
dig @8.8.8.8 example.com   # bypass local resolver, query Google directly
```

---

## Step 2 — TCP 3-Way Handshake

Now that you have the IP, you need to establish a connection.

```
curl (client)                        example.com (server)
     │                                     │
t=0  │──── SYN ───────────────────────────▶│
     │                                     │
t=28 │◀─── SYN-ACK ───────────────────────│
     │                                     │
t=28 │──── ACK ───────────────────────────▶│
     │                                     │
     │   connection established             │
```

If the server is 28ms away (one-way), the TCP handshake costs **1 RTT = 56ms** before any data can flow.

**What can go wrong here:**
- `Connection refused` → nothing listening on that port
- `Connection timed out` → firewall dropping packets silently
- SYN-ACK never arrives → routing problem, ISP block
- Server's accept queue full → connection just dropped under load

---

## Step 3 — TLS Handshake

Because the URL is `https://`, curl must negotiate TLS before sending the HTTP request.

```
curl (client)                        example.com (server)
     │                                     │
     │──── ClientHello ───────────────────▶│  "I support TLS 1.3, here are ciphers + ALPN (h2, http/1.1)"
     │                                     │
     │◀─── ServerHello + Certificate ──────│  "Use AES-256, here's my cert. ALPN: h2"
     │                                     │
     │  [client verifies cert:             │
     │   trusted CA? hostname match?       │
     │   not expired?]                     │
     │                                     │
     │──── Key Exchange / Finished ───────▶│  both sides derive session keys
     │                                     │
     │◀─── Server Finished ────────────────│
     │                                     │
     │        [encrypted data]             │
```

**TLS 1.2:** 2 RTTs (112ms at 56ms RTT)
**TLS 1.3:** 1 RTT (56ms at 56ms RTT) — this is why upgrading to TLS 1.3 matters

**What ALPN does:** inside the ClientHello, curl says "I support h2 and http/1.1." The server responds with which one to use. This is how HTTP/2 negotiation happens — inside TLS, before the HTTP request is sent.

**What can go wrong here:**
- Certificate expired → hard failure, browser/curl refuses
- Hostname mismatch → cert is for `api.example.com`, you hit `www.example.com`
- CA not trusted → self-signed cert in production
- TLS version mismatch → client wants 1.2 minimum, server only offers 1.1 (old system)
- Cipher suite mismatch → rare, but happens with very old clients

---

## Step 4 — HTTP Request and Response

Now finally the actual request:

```
curl (client)                        example.com (server)
     │                                     │
     │──── GET / HTTP/2 ──────────────────▶│
     │     Host: example.com               │
     │     Accept: */*                     │
     │     User-Agent: curl/7.x            │
     │                                     │
     │◀─── HTTP/2 200 OK ──────────────────│
     │     Content-Type: text/html         │
     │     Content-Length: 1256            │
     │                                     │
     │     [body]                          │
```

With HTTP/2 (negotiated via ALPN in TLS): **1 RTT = 56ms** for request + response.

---

## The Latency Math — Why CDNs Exist

```
Step                        Latency (28ms one-way = 56ms RTT)
─────────────────────────────────────────────────────────────
TCP handshake               1 RTT   =  56ms
TLS 1.2 handshake           2 RTTs  = 112ms
TLS 1.3 handshake           1 RTT   =  56ms
HTTP request/response        1 RTT   =  56ms
─────────────────────────────────────────────────────────────
Total (TLS 1.2 + HTTP)      4 RTTs  = 224ms   ← a quarter second, just for connection setup
Total (TLS 1.3 + HTTP)      3 RTTs  = 168ms
```

**Real-world one-way latency at the speed of light:**

| Route | One-way | RTT | 4 RTTs (TLS 1.2 + HTTP) |
|---|---|---|---|
| Same city | ~1ms | ~2ms | ~8ms |
| US coast-to-coast | ~28ms | ~56ms | ~224ms |
| New York → London | ~35ms | ~70ms | ~280ms |
| New York → Sydney | ~80ms | ~160ms | ~640ms |
| Around the world | ~100ms | ~200ms | ~800ms |

**The insight:** every RTT costs real time, and you can't go faster than light. If your server is in Virginia and your user is in Sydney, even a single HTTP request takes 640ms — before the app does anything. This is the entire reason CDNs exist: **get the data physically closer to the user**.

---

## Step 5 — BGP Routes Packets Across the Internet

All of the above happens over the internet. BGP is what makes that work.

Every hop between your machine and the server is a router. Routers use BGP to build their routing tables — maps of "to reach this IP range, send to this neighbor."

```
Your laptop → ISP router → ISP backbone → 
  internet exchange → upstream provider → 
    example.com's edge router → example.com's server
```

BGP is eventually consistent and has no built-in security. A misconfigured or malicious BGP announcement can divert traffic to the wrong destination (BGP hijack). This happens several times per year to major networks.

See `l3-network-layer.md` → BGP Hijacking for details.

---

## HTTP/1.1 vs HTTP/2 in this flow

**HTTP/1.1 head-of-line blocking:**
```
Request 1 ──────────────────────▶ wait... wait... response 1
Request 2 (blocked) ─────────────────────────────────────────▶ response 2
```
HTTP/1.1 sends one request per connection and waits for the response before sending the next. Browsers work around this by opening 6+ parallel TCP connections — which multiplies the TCP + TLS handshake cost.

**HTTP/2 multiplexing:**
```
Stream 1 ──▶ (response 1 arrives)
Stream 2 ──▶ (response 2 arrives)
Stream 3 ──▶ (response 3 arrives)
            ↑ all in parallel, one TCP connection
```
HTTP/2 is a binary, framed protocol. Multiple requests travel concurrently over a single TCP connection. No head-of-line blocking at the HTTP layer.

**HTTP/3 (QUIC):**
- Replaces TCP with QUIC (UDP-based)
- Eliminates TCP head-of-line blocking entirely
- Built-in TLS 1.3 — 0-RTT or 1-RTT connection setup
- Better on lossy/mobile networks (TCP reorders the whole stream on packet loss; QUIC doesn't)

---

## The Full Interview Answer (structured)

When asked "what happens when you type `https://example.com`":

**Layer by layer:**
1. **DNS** — hostname → IP via recursive resolver chain (root → TLD → NS → answer)
2. **TCP** — 3-way handshake (SYN / SYN-ACK / ACK), 1 RTT cost
3. **TLS** — negotiate cipher, server proves identity with cert (signed by CA), derive session keys — 1-2 RTT cost
4. **HTTP** — GET request, server responds — 1 RTT cost
5. **BGP** — underneath all of this, routing packets across the internet between ASes

**Add depth if they probe:**
- Latency math: 4 RTTs coast-to-coast = 224ms before a byte of content arrives → why CDNs exist
- ALPN: HTTP/2 is negotiated inside the TLS handshake
- HSTS: after first visit, browser forces HTTPS for all future requests
- TLS session resumption: second connection to same server can skip the key exchange step
- BGP hijacking: why the internet is fragile, what route leaks look like
