# Linux Firewall

> Controlling which traffic is allowed in and out. iptables under the hood, ufw as the friendly interface.

---

## The mental model

```
Incoming packet → iptables INPUT chain → allow or drop
Outgoing packet → iptables OUTPUT chain → allow or drop
Forwarded packet → iptables FORWARD chain → allow or drop (for routers/NAT)
```

Linux has **iptables** (the real engine) and **ufw** / **firewalld** (friendlier wrappers). Most Ubuntu systems use ufw. Most SRE troubleshooting involves figuring out what rule is blocking traffic and removing it.

---

## ufw — Uncomplicated Firewall

```bash
ufw status                  # is it enabled? what rules exist?
ufw status verbose          # more detail, including default policies
ufw status numbered         # rules with numbers (for deletion)

# Enable / disable
ufw enable                  # turn on (careful — may lock out SSH if port 22 isn't allowed)
ufw disable                 # turn off

# Allow traffic
ufw allow 22                # allow SSH (port 22, any protocol)
ufw allow 22/tcp            # allow SSH (TCP only)
ufw allow 80/tcp            # HTTP
ufw allow 443/tcp           # HTTPS
ufw allow from 10.0.0.0/8   # allow any traffic from this subnet
ufw allow from 10.0.1.5 to any port 5432  # specific IP to specific port

# Deny traffic
ufw deny 23                 # block telnet

# Delete rules
ufw status numbered         # see rule numbers
ufw delete 3                # delete rule number 3
ufw delete allow 80         # delete by rule spec

# Reset everything
ufw reset                   # remove all rules (prompts confirmation)
```

---

## iptables — the underlying engine

ufw writes iptables rules. When troubleshooting at a lower level:

```bash
iptables -L                         # list all rules
iptables -L -n                      # numeric (don't resolve IPs/ports to names)
iptables -L -n -v                   # verbose (show packet counts)
iptables -L INPUT -n -v             # just the INPUT chain
iptables -L --line-numbers          # show rule numbers for deletion

# Add rules
iptables -A INPUT -p tcp --dport 80 -j ACCEPT    # allow port 80 in
iptables -A INPUT -s 10.0.0.5 -j DROP            # drop all from IP

# Delete rules
iptables -D INPUT 3                  # delete INPUT rule #3
iptables -D INPUT -p tcp --dport 80 -j ACCEPT  # delete by spec

# Flush (clear all rules)
iptables -F                          # flush all rules (WARNING: no firewall after this)
iptables -F INPUT                    # flush just INPUT chain
```

**iptables rule order matters** — rules are evaluated top to bottom, first match wins.

---

## Common troubleshooting sequence

**Service is running but unreachable from outside:**
```bash
# 1. Confirm service is listening
ss -tulpn | grep :80            # is nginx actually listening on port 80?

# 2. Test locally (bypass firewall)
curl localhost:80               # does it respond locally?

# 3. Check the firewall
ufw status verbose              # is the port blocked?
iptables -L INPUT -n -v        # look for DROP or REJECT rules

# 4. Temporarily allow the port
ufw allow 80/tcp

# 5. Test from outside
curl http://<server-ip>
```

**Find the blocking rule:**
```bash
iptables -L INPUT -n --line-numbers
# Look for:
#   -j DROP or -j REJECT targeting your port
#   -s <source IP> -j DROP affecting your client
```

**Remove a specific blocking rule:**
```bash
iptables -L INPUT --line-numbers   # find the rule number
iptables -D INPUT 5                # delete rule 5
```

---

## Default policies

The default policy applies when no rule matches:

```bash
iptables -L | head -5
# Chain INPUT (policy ACCEPT)     ← default: accept everything
# Chain INPUT (policy DROP)       ← default: drop everything not explicitly allowed
```

A DROP default is more secure but requires explicitly allowing everything (including SSH). An ACCEPT default is more permissive.

---

## Saving firewall rules

iptables rules are in memory — they don't survive reboot by default.

```bash
# Ubuntu/Debian
iptables-save > /etc/iptables/rules.v4
# (or use ufw, which is persistent by default)

# Restore
iptables-restore < /etc/iptables/rules.v4
```

ufw is persistent automatically — rules survive reboot.

---

## SRE scenarios

**Locked yourself out of SSH:**
- If you have console access: log in via console, `ufw allow 22` or `iptables -F`
- If cloud VM: use the cloud provider's serial console or rescue mode
- Prevention: **always allow port 22 before enabling ufw**

```bash
ufw allow 22/tcp   # do this BEFORE ufw enable
ufw enable
```

**Application deployed but external requests time out (not refused, time out):**
→ Firewall is silently dropping packets. REJECT sends back an error, DROP doesn't.
```bash
iptables -L INPUT -n | grep DROP
ufw status verbose | grep DENY
```

**Diagnose with specific source IP:**
```bash
iptables -L INPUT -n -v | grep "10.0.0.5"    # is this specific IP being dropped?
```

---

## iptables NAT and port forwarding

```bash
# Enable IP forwarding (required for any forwarding/NAT to work):
sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf  # persist across reboots

# Forward port 8080 on this host → port 80 on an internal server:
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 10.0.0.5:80
iptables -A FORWARD -p tcp -d 10.0.0.5 --dport 80 -j ACCEPT
# PREROUTING = applied before routing decision (for incoming packets)

# Masquerade (SNAT) — needed so reply packets route back correctly:
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Load balance across two backends (round-robin with statistic module):
iptables -t nat -A PREROUTING -p tcp --dport 80 \
  -m statistic --mode nth --every 2 --packet 0 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.2:80
# First rule matches every 2nd packet starting from packet 0 → backend 1
# Second rule catches the rest → backend 2

# View NAT rules:
iptables -t nat -L -n -v --line-numbers

# Delete a NAT rule by number:
iptables -t nat -D PREROUTING 2
```

---

## Allow outbound SMTP (port 25)

```bash
# Check if outbound SMTP is blocked (cloud providers often block port 25 to prevent spam):
nc -zv smtp.gmail.com 25              # "Connection refused" or timeout = blocked
telnet smtp.gmail.com 25              # alternative test

# Allow outbound port 25:
iptables -A OUTPUT -p tcp --dport 25 -j ACCEPT
ufw allow out 25/tcp                  # if using ufw

# Verify:
iptables -L OUTPUT -n -v | grep 25
```

---

## Restore blocked SSH access

```bash
# Scenario: accidentally blocked SSH while connected — act fast (you still have a session)

# Option 1 — insert an ACCEPT rule at the top (before any DROP rules):
iptables -I INPUT 1 -p tcp --dport 22 -j ACCEPT   # -I inserts at position 1 (top)
ufw insert 1 allow 22/tcp                           # ufw equivalent

# Option 2 — if ufw is the problem, disable it entirely:
ufw disable                           # disables ufw, all traffic allowed through iptables defaults

# Option 3 — if locked out completely (no session open):
# Use cloud provider's web console / serial console access
# Then: iptables -F (flush all) or ufw allow 22 && ufw reload

# Prevention (always do this before enabling ufw):
ufw allow 22/tcp && ufw enable        # allow SSH first, THEN enable
sshd -t                               # always validate sshd config before restarting

# Check what's blocking you:
iptables -L INPUT -n -v --line-numbers | grep -E "DROP|REJECT|22"
ufw status verbose | grep -E "DENY|22"
```
