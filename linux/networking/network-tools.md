# Linux Network Troubleshooting Tools

> The commands SREs use to diagnose connectivity, find what's listening, and debug network issues from inside a Linux host.

---

## What's listening on this host?

```bash
ss -tulpn                           # the modern standard
# -t  TCP
# -u  UDP
# -l  listening only
# -p  show process name and PID
# -n  numeric (don't resolve port names)

netstat -tulpn                      # older equivalent (same flags)
```

**Output:**
```
Netid  State   Local Address:Port   Process
tcp    LISTEN  0.0.0.0:80           users:(("nginx",pid=1234))
tcp    LISTEN  127.0.0.1:5432       users:(("postgres",pid=5678))
tcp    LISTEN  0.0.0.0:22           users:(("sshd",pid=910))
```

**What to look for:**
```
0.0.0.0:80    → listening on all interfaces (externally reachable)
127.0.0.1:80  → listening on loopback only (not externally reachable)
:::80          → IPv6 all interfaces
```

**Common investigation:**
```bash
ss -tulpn | grep :80               # is nginx actually running on port 80?
ss -tulpn | grep LISTEN            # everything that's listening
ss -tan | grep ESTABLISHED | wc -l # how many established connections?
ss -tan | grep TIME_WAIT | wc -l   # TIME_WAIT socket count (SRE concern under load)
```

---

## Testing connectivity

```bash
ping 8.8.8.8                       # basic reachability (ICMP)
ping -c 5 8.8.8.8                  # send exactly 5 pings
ping -i 0.2 8.8.8.8                # faster (every 200ms)

traceroute 8.8.8.8                 # show each hop to destination
mtr 8.8.8.8                        # live continuous traceroute (best tool for routing issues)

curl -v https://example.com        # full HTTP request with debug output
curl -I https://example.com        # headers only (HEAD request)
curl -o /dev/null -w "%{http_code} %{time_total}\n" https://example.com   # status + timing
wget -q -O- https://example.com | head   # alternative to curl

# Test if a port is open
nc -zv example.com 443             # TCP connection test to port 443
nc -zv 10.0.1.5 5432              # test postgres port reachability
nc -zvu example.com 53             # UDP port test
timeout 3 bash -c 'echo > /dev/tcp/10.0.1.5/5432' && echo "open" || echo "closed"
```

---

## DNS troubleshooting

```bash
dig example.com                    # full DNS lookup
dig example.com A                  # only A records
dig @8.8.8.8 example.com          # query specific DNS server
dig +short example.com             # just the IP
dig +trace example.com             # trace full resolution chain

nslookup example.com               # simpler alternative
host example.com                   # simple lookup

# Check what DNS server this host uses
cat /etc/resolv.conf               # configured DNS servers
```

**DNS not resolving at all:**
```bash
cat /etc/resolv.conf               # is a nameserver configured?
ping 8.8.8.8                       # can we reach the internet at all?
dig @8.8.8.8 example.com          # try Google's DNS directly
# If @8.8.8.8 works but not local: local DNS is the problem
```

---

## Routing

```bash
ip route show                      # current routing table
ip route get 8.8.8.8              # which route would be used for this IP?
route -n                           # older alternative

# Is the default gateway set?
ip route show | grep default       # should show: default via <gateway IP>
```

**"Network unreachable":**
```bash
ip route show                      # no default route?
ip route add default via 10.0.0.1  # add default gateway (temporary)
```

---

## Firewall and packet flow

```bash
# Check if a port is being blocked (from outside, use nc or telnet)
nc -zv <server-ip> 80

# On the server side
ss -tulpn | grep :80               # is something listening?
ufw status                         # is ufw blocking it?
iptables -L INPUT -n | grep 80     # any iptables rules?
```

---

## Checking /etc/hosts

```bash
cat /etc/hosts                     # local DNS overrides
# Format: IP  hostname  alias
# 127.0.0.1  localhost
# 10.0.0.5   db.internal db
```

`/etc/hosts` takes priority over DNS. If a hostname resolves to the wrong IP, check here first.

```bash
getent hosts example.com           # shows effective resolution (hosts + DNS)
```

---

## Troubleshooting sequences

**Service running, port open, but can't connect from outside:**
```bash
ss -tulpn | grep :8080             # 1. is it listening on 0.0.0.0 or just 127.0.0.1?
ufw status                         # 2. is the firewall blocking it?
curl localhost:8080                # 3. does it work locally?
nc -zv <external-ip> 8080         # 4. test from outside
# If locally works but outside doesn't: firewall or binding issue
```

**Can ping IP but can't resolve hostname:**
```bash
cat /etc/resolv.conf               # DNS server configured?
dig @<dns-server> hostname         # test DNS server directly
cat /etc/hosts                     # any conflicting local entry?
```

**Intermittent connection drops:**
```bash
mtr 8.8.8.8                        # watch live — which hop shows packet loss?
ping -c 100 8.8.8.8 | tail -5      # % packet loss summary
```

**High number of connections — is the service under load?**
```bash
ss -tan | grep ESTABLISHED | wc -l  # total established
ss -tan | grep TIME_WAIT | wc -l    # TIME_WAIT sockets (under churn)
ss -tan state established '( dport = :80 )' | wc -l   # to port 80 specifically
```
