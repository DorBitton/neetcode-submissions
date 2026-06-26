# DNS — Linux Configuration, Diagnostics, and Zone Transfers

---

## 1. Linux DNS Resolution Order

Linux resolves hostnames in a specific order defined by `/etc/nsswitch.conf`.

```bash
grep hosts /etc/nsswitch.conf
# hosts: files dns
```

- `files` — checks `/etc/hosts` first
- `dns` — queries nameservers in `/etc/resolv.conf` second

`/etc/hosts` always wins if it has an entry. This is why hardcoded overrides in `/etc/hosts` can mask real DNS issues.

```bash
# Show effective resolution — combines /etc/hosts and DNS
getent hosts example.com

# Show what /etc/hosts has directly
grep example.com /etc/hosts
```

---

## 2. /etc/resolv.conf — Which DNS Servers to Query

```bash
cat /etc/resolv.conf
```

Key directives:

```
nameserver 8.8.8.8          # primary DNS server
nameserver 8.8.4.4          # fallback DNS server
search corp.example.com     # appended to bare hostnames (e.g. "web" → "web.corp.example.com")
options ndots:5             # number of dots required to treat a name as absolute before appending search domain
```

**On systemd-resolved systems** (Ubuntu 20.04+, RHEL 8+):

```bash
resolvectl status           # shows per-interface DNS servers and search domains
resolvectl query example.com  # explicit DNS query through systemd-resolved
```

`/etc/resolv.conf` may be a symlink to `/run/systemd/resolve/stub-resolv.conf` on these systems — editing the symlink target directly does not persist.

---

## 3. dig — DNS Lookups

### Basic queries

```bash
dig example.com              # A record (IPv4 address)
dig example.com AAAA         # IPv6 address
dig example.com MX           # mail exchange records
dig example.com NS           # authoritative nameservers
dig example.com TXT          # TXT records (SPF, DKIM, etc.)
dig example.com CNAME        # canonical name alias
```

### Targeted and concise output

```bash
dig +short example.com           # just the IP, no headers
dig +short example.com MX        # just MX records
dig @8.8.8.8 example.com        # query a specific DNS server (bypasses resolv.conf)
dig @8.8.8.8 +short example.com # specific server, short output
```

### Reverse DNS (PTR records)

```bash
dig -x 8.8.8.8              # reverse lookup — who owns this IP?
dig -x 8.8.8.8 +short       # just the PTR record hostname
```

### Full resolution chain

```bash
dig +trace example.com       # traces from root → TLD → authoritative nameserver
```

Use `+trace` when you need to see exactly where in the delegation chain a record is coming from, or where it breaks.

---

## 4. Validating DNS Consistency

**Scenario (SAP):** Verify that all DNS servers return the same answer for a hostname — catch propagation lag or stale records.

```bash
# Query the same name against multiple servers
dig @8.8.8.8 example.com +short
dig @1.1.1.1 example.com +short
dig @<internal-nameserver> example.com +short

# Compare all at once
for ns in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo -n "$ns: "
  dig @$ns example.com +short
done
```

What to look for:
- Different IP answers → propagation lag or split-brain DNS
- TTL differences → one server has a cached old record
- NXDOMAIN from one server but answer from another → zone not yet propagated

```bash
# Check TTL remaining on a record (how long until it refreshes)
dig example.com | grep -E "^example|IN"
```

---

## 5. Verify Reverse DNS (PTR Records)

**Scenario (Walmart):** Forward and reverse DNS should match. A mismatch breaks email delivery, some auth systems, and security tooling.

```bash
# Step 1: forward lookup — what IP does the hostname resolve to?
dig +short example.com

# Step 2: reverse lookup — what hostname does the IP resolve to?
dig -x <IP-from-step-1> +short

# Both should return each other. If they don't, the PTR record is missing or wrong.
```

Example of a mismatch:

```bash
dig +short mail.example.com
# 203.0.113.10

dig -x 203.0.113.10 +short
# other-host.provider.com.     ← mismatch — PTR points somewhere else
```

PTR records live in the reverse DNS zone (`in-addr.arpa`) and are usually managed by the IP owner (ISP or cloud provider), not the domain owner. On AWS, set reverse DNS via Elastic IP settings. On-prem, coordinate with your network team or ISP.

---

## 6. Diagnosing DNS Not Working

**Scenario (PayPal):** "Name does not resolve" — systematic approach.

### Step 1: Is it DNS or network?

```bash
ping -c 1 8.8.8.8            # if this works, the network is up
ping -c 1 example.com        # if this fails but IP ping works → DNS problem
```

### Step 2: Check resolv.conf

```bash
cat /etc/resolv.conf          # is there a valid nameserver?
```

### Step 3: Query the configured nameserver directly

```bash
dig @$(grep nameserver /etc/resolv.conf | head -1 | awk '{print $2}') example.com
```

### Step 4: Try a known-good public DNS

```bash
dig @8.8.8.8 example.com +short
```

**Interpret results:**

| Result | Meaning |
|---|---|
| `@8.8.8.8` works, system DNS fails | Problem is in `/etc/resolv.conf` — wrong or unreachable nameserver |
| Both fail | Network block on port 53, or DNS server is down |
| Both work in `dig`, but `ping example.com` still fails | Check `/etc/nsswitch.conf`, or `/etc/hosts` has a wrong override |
| Works sometimes | Flapping nameserver or TTL causing inconsistent cache hits |

### Step 5: Check systemd-resolved (if applicable)

```bash
resolvectl status             # are DNS servers configured per interface?
systemctl status systemd-resolved
journalctl -u systemd-resolved --since "10 minutes ago"
```

### Step 6: Check firewall

```bash
# DNS uses UDP 53 (queries) and TCP 53 (zone transfers, large responses)
ss -tulnp | grep 53
iptables -L -n | grep 53
```

---

## 7. DNS Zone Transfers (BIND/named)

**Scenario (BMW):** Configure a secondary DNS server to pull zone data from a primary via AXFR zone transfer.

### What a zone transfer is

A secondary DNS server is a read-only replica. It pulls the full zone (AXFR) or incremental changes (IXFR) from the primary. This provides redundancy — if primary goes down, the secondary still answers queries.

### Primary named.conf — allow the secondary to pull

```
zone "example.com" IN {
    type master;
    file "/etc/bind/db.example.com";
    allow-transfer { 192.168.1.2; };   // secondary DNS IP only — not "any"
};
```

### Secondary named.conf — pull from primary

```
zone "example.com" IN {
    type slave;
    file "/var/cache/bind/db.example.com";
    masters { 192.168.1.1; };          // primary DNS IP
};
```

### Test zone transfer manually

```bash
# Run from the secondary, or any machine — verifies the primary allows transfer
dig @192.168.1.1 example.com AXFR
```

If it returns zone records, the transfer is allowed. If it returns `Transfer failed` or `REFUSED`, check:

1. `allow-transfer` in primary's named.conf — is the secondary's IP listed?
2. Firewall — port 53/tcp must be open between secondary and primary
3. Primary named is running: `systemctl status named`

### Validate config and reload

```bash
named-checkconf                                          # validate named.conf syntax
named-checkzone example.com /etc/bind/db.example.com    # validate zone file
rndc reload                                              # graceful reload (no service restart needed)
rndc reload example.com                                  # reload a single zone only
```

Always run `named-checkconf` and `named-checkzone` before reloading — a syntax error in named.conf will stop the reload from applying.

### Verify transfer happened on secondary

```bash
# Check logs on secondary after rndc reload or zone refresh
journalctl -u named | grep "example.com"
# Look for: "zone example.com/IN: Transfer started" and "transferred serial"

# Or confirm the zone file was written
ls -lh /var/cache/bind/db.example.com
```
