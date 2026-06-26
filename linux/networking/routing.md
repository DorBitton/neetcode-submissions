# Routing

Core routing commands and diagnostics for SRE interviews.

---

## 1. View the routing table

```bash
ip route show                     # full routing table
ip route show table all           # all routing tables (including policy routes)
ip route get 8.8.8.8              # which route handles this specific destination
route -n                          # older alternative, numeric output (no DNS lookups)
```

---

## 2. Add and remove routes

```bash
# Add routes (temporary — lost on reboot)
ip route add 10.10.5.0/24 via 192.168.1.1                    # route subnet through gateway
ip route add 10.10.5.0/24 via 192.168.1.1 dev eth0           # specify the interface too
ip route add default via 192.168.1.1                          # set default gateway

# Remove routes
ip route del 10.10.5.0/24                                     # delete a specific route
ip route del default                                           # remove current default gateway

# Replace (atomic — no gap between delete and add)
ip route replace default via 192.168.1.254
```

> **Note:** All `ip route` changes are temporary. They survive until reboot or a network service restart.

---

## 3. Validating a route works

Use this sequence to confirm end-to-end reachability:

```bash
ip route get 10.10.5.1            # confirms which route is selected for this IP
ping -c 3 192.168.1.1             # can we reach the next-hop gateway?
traceroute 10.10.5.1              # trace the full path — spot where packets drop
```

**Scenario — Validating Network Routes (Google):**

```bash
# Step 1: confirm route exists
ip route show | grep 10.10.5.0

# Step 2: confirm which route handles the target IP
ip route get 10.10.5.1
# Output: 10.10.5.1 via 192.168.1.1 dev eth0 src 192.168.1.50

# Step 3: verify gateway is reachable
ping -c 3 192.168.1.1

# Step 4: trace the full path
traceroute 10.10.5.1
```

---

## 4. CIDR and overlapping subnets

### CIDR quick reference

| Notation | Addresses | Example |
|----------|-----------|---------|
| /8       | 16,777,216 | 10.0.0.0/8 |
| /16      | 65,536    | 10.10.0.0/16 |
| /24      | 256       | 10.10.5.0/24 |
| /25      | 128       | 10.10.5.0/25 |
| /30      | 4         | 10.10.5.0/30 |
| /32      | 1         | 10.10.5.1/32 |

### Longest prefix match

Linux selects the **most specific** (longest prefix) route. If two routes overlap, the one with the higher CIDR number wins:

```
10.10.0.0/16   via 192.168.1.1    # broad
10.10.5.0/24   via 192.168.2.1    # more specific — wins for 10.10.5.x traffic
```

### Spot overlapping subnets

```bash
ip route show | grep "10\."       # filter for 10.x routes — look for overlapping prefixes
ip route show | sort              # sorted output makes overlaps easier to see visually
```

### Diagnose which route handles a specific IP

```bash
ip route get 10.10.5.1
# If output shows the wrong gateway, you have an overlap or misconfigured route
```

**Scenario — Fixing Overlapping Subnets (Cisco):**

```bash
# Problem: 10.10.0.0/16 and 10.10.5.0/24 point to different gateways
# Traffic to 10.10.5.x goes the wrong way

ip route show | grep "10\.10\."
# 10.10.0.0/16  via 192.168.1.1     (should be the broad route)
# 10.10.5.0/24  via 192.168.1.1     (duplicate — wrong gateway)

# Fix: delete the incorrect specific route, re-add with correct gateway
ip route del 10.10.5.0/24
ip route add 10.10.5.0/24 via 192.168.2.1

# Verify
ip route get 10.10.5.1
# Should now show: via 192.168.2.1
```

---

## 5. Scenario bank

### Temporary Route Configuration (Spotify)

Add a route for testing — survives only until reboot or route flush:

```bash
ip route add 172.16.50.0/24 via 10.0.0.1 dev eth1   # add temporary test route
ip route show | grep 172.16.50                        # confirm it's there
ping -c 3 172.16.50.1                                 # test reachability

# Undo when done
ip route del 172.16.50.0/24
```

### Route Subnet Through Gateway (Infosys)

```bash
# Route a specific subnet through a non-default gateway
ip route add 192.168.100.0/24 via 10.10.0.1 dev eth0

# Set or replace the default gateway
ip route replace default via 10.10.0.254

# Confirm default gateway
ip route show default
# or
ip route | grep default
```

---

## 6. Persistent routes

For routes that survive reboot, configure them in the network manager — not via `ip route`.

**Ubuntu (Netplan)** — `/etc/netplan/01-netcfg.yaml`:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      routes:
        - to: 10.10.5.0/24
          via: 192.168.1.1
```

```bash
netplan apply    # apply changes without reboot
```

> For other distros (RHEL, Debian legacy), see `/etc/network/interfaces` or `nmcli` — syntax differs, concept is the same.
