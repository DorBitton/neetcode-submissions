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

---

## Packet loss diagnosis

```bash
ping -c 100 8.8.8.8                    # send 100 pings, get loss %
ping -c 100 8.8.8.8 | tail -3         # see the summary line only
mtr 8.8.8.8                           # live traceroute — watch which hop drops packets
mtr --report 8.8.8.8                  # run 10 rounds, print report (good for logging)
mtr --report --no-dns 8.8.8.8         # skip DNS resolution (faster)
# Interpretation:
# Loss at hop N but not hops after N = ICMP de-prioritized at that router (not real loss)
# Loss at hop N AND all hops after = real packet loss at hop N
```

---

## Network socket summary

```bash
ss -s                                  # socket summary: TCP states and counts
# Shows: TCP: 42 (estab 18, closed 5, orphan 0, synrecv 0, timewait 5/0)
ss -tan state time-wait | wc -l       # count TIME_WAIT sockets
ss -tan state established | wc -l     # count ESTABLISHED connections
ss -tan state syn-recv | wc -l        # count half-open (SYN flood indicator)
```

---

## tcpdump — inspecting HTTP traffic

```bash
tcpdump -i eth0 port 80               # capture HTTP traffic on eth0
tcpdump -i any port 80 -A             # any interface, print ASCII (readable HTTP bodies)
tcpdump -i eth0 'tcp port 80 and host 10.0.0.5'   # filter to specific host
tcpdump -w capture.pcap -i eth0 port 443   # write to file (open in Wireshark)
tcpdump -i eth0 -nn port 80 -c 50    # -nn=no DNS resolution, capture 50 packets then stop
# For HTTPS: you see the TLS handshake but not the content (encrypted)
# Use openssl s_client or curl -v for HTTPS content inspection
```

---

## Service port health check

```bash
nc -zv host 80                        # TCP connect test (z=no data, v=verbose)
nc -zv host 22 80 443                 # test multiple ports at once
nc -zvw3 host 5432                    # 3-second timeout
timeout 3 bash -c 'echo > /dev/tcp/host/80' && echo open || echo closed  # no nc needed

# Find and clean up a process holding a port:
ss -tulpn | grep :8080                # find PID holding port 8080
lsof -i :8080                         # alternative: lists process name and PID
kill <PID>                            # stop it gracefully
# Or if it's a service:
systemctl stop <service>
```

---

## conntrack — connection tracking

```bash
conntrack -L                           # list all tracked connections
conntrack -L | grep ESTABLISHED | wc -l   # count established
conntrack -L | grep SYN_SENT          # connections stuck in SYN (possible firewall drop)
conntrack -D --dst-nat 10.0.0.5       # delete tracked connections to an IP

# Connection table limits:
cat /proc/sys/net/netfilter/nf_conntrack_count   # current tracked connections
cat /proc/sys/net/netfilter/nf_conntrack_max     # maximum before dropping packets
# "nf_conntrack: table full, dropping packet" → raise the max:
sysctl -w net.netfilter.nf_conntrack_max=131072
echo "net.netfilter.nf_conntrack_max=131072" >> /etc/sysctl.conf  # persist
```

---

## MTU / VPN mismatch

```bash
ip link show eth0                      # MTU shown in output (default: mtu 1500)
ip link set eth0 mtu 1400             # lower MTU (VPN tunnels need this)

# Find path MTU — largest packet that gets through without fragmenting:
ping -M do -s 1472 <destination>      # -M do = don't fragment, -s = payload bytes
# 1472 bytes payload + 28 bytes IP/ICMP header = 1500 total
# If it fails, lower -s until it succeeds → that number + 28 = your path MTU

# VPN scenario: VPN interface has 1400 byte MTU but packets are 1500 → silent drops
# Fix: lower MTU on the VPN interface
ip link set tun0 mtu 1400
```

---

## SYN flood detection

```bash
ss -s                                  # check SYN-RECV count in summary
ss -tan state syn-recv | wc -l        # count half-open connections (should be near 0)
netstat -n | grep SYN_RECV | wc -l    # older alternative

# High SYN_RECV count = SYN flood attack in progress

# Kernel-level defense:
sysctl -w net.ipv4.tcp_syncookies=1             # enable SYN cookies (main defense)
sysctl -w net.ipv4.tcp_max_syn_backlog=2048     # increase backlog queue

# iptables rate limiting (limit new SYN packets per second):
iptables -A INPUT -p tcp --syn -m limit --limit 5/s --limit-burst 10 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP
```

---

## Network namespaces

```bash
ip netns list                          # list network namespaces
ip netns add myns                      # create a namespace
ip netns exec myns ip link list        # run a command inside the namespace
ip netns exec myns ping 8.8.8.8       # test connectivity from inside namespace
ip netns del myns                      # delete namespace

# Connect two namespaces with a veth pair:
ip link add veth0 type veth peer name veth1   # create pair
ip link set veth1 netns myns                  # move veth1 into namespace
ip addr add 192.168.100.1/24 dev veth0        # assign IP on host side
ip netns exec myns ip addr add 192.168.100.2/24 dev veth1  # assign IP in namespace
ip link set veth0 up
ip netns exec myns ip link set veth1 up
```

---

## Port exhaustion (ephemeral ports)

```bash
# Symptom: "Cannot assign requested address" — ran out of ephemeral ports
ss -s                                  # check total socket counts
cat /proc/sys/net/ipv4/ip_local_port_range   # current range (default: 32768–60999 = ~28K ports)

# Fix 1: widen the port range
sysctl -w net.ipv4.ip_local_port_range="10000 65000"   # ~55K ports

# Fix 2: reduce TIME_WAIT hold time
sysctl -w net.ipv4.tcp_fin_timeout=15
sysctl -w net.ipv4.tcp_tw_reuse=1      # reuse TIME_WAIT sockets for new outbound connections

# Check current TIME_WAIT count:
ss -tan | grep TIME-WAIT | wc -l
```

---

## Macvlan network configuration

```bash
# Macvlan: gives containers their own MAC address on the physical network
# They appear as physical hosts to the network switch

# Create a macvlan interface on the host:
ip link add macvlan0 link eth0 type macvlan mode bridge
ip addr add 192.168.1.50/24 dev macvlan0
ip link set macvlan0 up

# Docker macvlan network:
docker network create -d macvlan \
  --subnet 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  -o parent=eth0 macvlan_net

# Common fix: enable promiscuous mode on host NIC (required for macvlan to work):
ip link set eth0 promisc on

# Known limitation: containers on macvlan CANNOT communicate with the host directly
# Fix: create a macvlan interface on the host in the same subnet
ip link add macvlan-host link eth0 type macvlan mode bridge
ip addr add 192.168.1.254/24 dev macvlan-host
ip link set macvlan-host up
```
