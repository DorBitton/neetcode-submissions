# Networking Quick Reference

Jump to:
- [IP & Subnetting](#ip--subnetting)
- [TCP / UDP](#tcp--udp)
- [HTTP Status Codes](#http-status-codes)
- [DNS Records](#dns-records)
- [Ports](#common-ports)
- [Load Balancers — F5 vs AWS](#load-balancers--f5-vs-aws)
- [Debugging Commands](#debugging-commands)

---

## IP & Subnetting

```
/32  =  1 IP         (single host)
/30  =  2 usable     (point-to-point)
/28  = 14 usable
/24  = 254 usable    (standard subnet)
/22  = 1022 usable
/16  = 65534 usable  (VPC block)

Private ranges:
  10.0.0.0/8
  172.16.0.0/12
  192.168.0.0/16
```

---

## TCP / UDP

```
TCP  connection-oriented, reliable, ordered  → HTTP, SSH, databases
UDP  connectionless, fast, lossy             → DNS, video, gaming

TCP 3-way handshake:  SYN → SYN-ACK → ACK

Connection states:
  LISTEN      server waiting
  ESTABLISHED data flowing
  TIME_WAIT   closing (lasts ~60s)
  CLOSE_WAIT  waiting for app to close

Ephemeral port range: 49152–65535 (Linux default: 32768–60999)
```

---

## HTTP Status Codes

```
2xx  Success
  200  OK
  201  Created
  204  No Content

3xx  Redirect
  301  Moved Permanently (cached)
  302  Found (not cached)

4xx  Client Error
  400  Bad Request
  401  Unauthorized (not logged in)
  403  Forbidden (logged in, not allowed)
  404  Not Found
  429  Rate Limited

5xx  Server Error
  500  Internal Server Error (bug)
  502  Bad Gateway (upstream gave garbage)
  503  Service Unavailable (no healthy backends)
  504  Gateway Timeout (upstream too slow)
```

---

## DNS Records

```
A      hostname → IPv4          api.example.com → 1.2.3.4
AAAA   hostname → IPv6
CNAME  hostname → hostname      www → example.com  (not on root domain!)
MX     mail server
TXT    arbitrary text           SPF, verification
NS     nameservers for zone
PTR    reverse DNS (IP → name)
ALIAS  like CNAME but on root   Route53 only
```

**TTL:** how long resolvers cache the record. Low = fast failover. High = less DNS load.

---

## Common Ports

```
22    SSH
25    SMTP
53    DNS (TCP + UDP)
80    HTTP
443   HTTPS
3306  MySQL
5432  PostgreSQL
6379  Redis
8080  HTTP alt
9090  Prometheus
9200  Elasticsearch
```

---

## Load Balancers — F5 vs AWS

```
Layer   On-prem (F5)           AWS
──────────────────────────────────────────
L4      TCP/UDP VIP            NLB
L7      HTTP VIP + profile     ALB
DNS     GTM                    Route53

F5 model:    VIP → Pool → Pool Members
AWS model:   LB → Listener Rules → Target Group → Targets

F5 routing:  iRules (Tcl scripting)
ALB routing: Listener rules (path, host, header conditions)

TLS:
  F5:   SSL profile on VIP, cert on F5
  ALB:  ACM certificate on listener

Client IP:
  NLB:  preserves source IP natively
  ALB:  client IP in X-Forwarded-For header
  F5:   inserts X-Forwarded-For via HTTP profile

Persistence (stickiness):
  F5:   source IP, cookie, SSL session
  ALB:  sticky sessions (duration-based or app cookie)
  NLB:  source IP 5-tuple hash
```

---

## AWS Networking Quick Map

```
VPC              = your private network
Subnet           = subnet within VPC (tied to one AZ)
Route Table      = routing rules for subnet
Internet Gateway = door to the internet (public subnets)
NAT Gateway      = outbound internet for private subnets
Security Group   = stateful firewall on instance/ENI level
NACL             = stateless firewall on subnet level
VPC Peering      = connect two VPCs directly
Transit Gateway  = hub connecting many VPCs + on-prem
Direct Connect   = dedicated physical line on-prem → AWS
Site-to-Site VPN = encrypted tunnel on-prem → AWS
```

---

## Debugging Commands

```bash
# Connectivity
ping 8.8.8.8                        # basic reachability
traceroute 8.8.8.8                  # path to destination
curl -v https://api.example.com     # full HTTP request with headers
curl -I https://api.example.com     # headers only

# DNS
dig api.example.com                 # DNS lookup
dig @8.8.8.8 api.example.com        # use specific resolver
dig +trace api.example.com          # trace full chain
nslookup api.example.com

# Ports & connections
ss -tlnp                            # listening TCP ports
ss -tan | grep ESTABLISHED | wc -l  # count connections
ss -tan | grep TIME_WAIT | wc -l    # TIME_WAIT connections
netstat -tlnp                       # older alternative
lsof -i :80                         # what's using port 80
nc -zv host 443                     # test if port is open

# TLS
openssl s_client -connect host:443  # inspect TLS cert
openssl s_client -connect host:443 -servername api.example.com  # with SNI
echo | openssl s_client -connect host:443 2>/dev/null | openssl x509 -noout -dates  # cert expiry

# Routing
ip route show                       # routing table
ip route get 8.8.8.8                # which route for this IP
```
