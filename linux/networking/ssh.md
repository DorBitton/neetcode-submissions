# SSH — Secure Shell

> Remote access to servers. Key-based auth, hardening, and the most common access issues SREs deal with.

---

## How SSH works (quick)

```
Client                          Server (sshd)
  │                               │
  │──── TCP connect :22 ─────────▶│
  │◀─── server host key ──────────│  "here's my public key, are you sure you trust me?"
  │  [client checks known_hosts]  │
  │──── auth (key or password) ──▶│
  │         [shell]               │
```

**Server host key** — the server's identity. Stored in `/etc/ssh/ssh_host_*`. The first time you connect, SSH asks "are you sure?" — you're accepting the server's fingerprint into `~/.ssh/known_hosts`.

---

## Key-based authentication

Passwords are weak and log-able. Key-based auth uses asymmetric cryptography — you prove identity by having the private key that matches a public key the server holds.

```bash
# 1. Generate a key pair (on your local machine)
ssh-keygen -t ed25519 -C "dor@company.com"
# Creates: ~/.ssh/id_ed25519 (private key — never share)
#          ~/.ssh/id_ed25519.pub (public key — safe to share)

# 2. Copy public key to the server
ssh-copy-id user@server                         # easiest method
# Or manually:
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys   # on the server

# 3. Connect
ssh user@server                                 # uses key automatically
ssh -i ~/.ssh/custom_key user@server            # specify key explicitly
```

**File permissions matter — SSH is strict:**
```bash
chmod 700 ~/.ssh                     # directory: owner rwx only
chmod 600 ~/.ssh/authorized_keys     # file: owner rw only
chmod 600 ~/.ssh/id_ed25519          # private key: owner rw only
# SSH will refuse to use keys with wrong permissions
```

---

## sshd_config — server configuration

The SSH daemon config lives at `/etc/ssh/sshd_config`. After editing:
```bash
sshd -t                             # test config for syntax errors (ALWAYS do this)
systemctl restart sshd              # apply changes
```

**Key hardening settings:**
```bash
# /etc/ssh/sshd_config

Port 22                             # change to non-standard port to reduce scan noise (e.g. 2222)
PermitRootLogin no                  # never allow direct root login
PasswordAuthentication no           # force key-based auth (set AFTER keys are working)
PubkeyAuthentication yes            # ensure key auth is on
AuthorizedKeysFile .ssh/authorized_keys

MaxAuthTries 3                      # lockout after 3 failed attempts
LoginGraceTime 20                   # disconnect if not authenticated in 20s
ClientAliveInterval 300             # keep-alive every 5 minutes
ClientAliveCountMax 2               # disconnect after 2 missed keep-alives

AllowUsers dor admin                # whitelist specific users (optional)
AllowGroups sshusers                # or by group
```

---

## Client config — ~/.ssh/config

Saves typing for servers you connect to often:

```
# ~/.ssh/config
Host prod-web
    HostName 203.0.113.10
    User ubuntu
    IdentityFile ~/.ssh/prod_key
    Port 2222

Host bastion
    HostName bastion.company.com
    User ec2-user
    IdentityFile ~/.ssh/bastion_key

# Jump through bastion to reach internal host
Host internal-db
    HostName 10.0.2.15
    User ubuntu
    ProxyJump bastion
```

Now `ssh prod-web` connects with all the right settings.

---

## SSH tunneling

```bash
# Local port forward: access remote service locally
ssh -L 5432:db.internal:5432 user@bastion
# Now: psql -h localhost -p 5432 connects to db.internal through bastion

# Remote port forward: expose local service on remote host
ssh -R 8080:localhost:3000 user@server
# Now: requests to server:8080 come to your local :3000

# SOCKS proxy: route browser traffic through SSH
ssh -D 1080 user@server
# Set browser to use SOCKS5 proxy on localhost:1080
```

---

## Troubleshooting

**"Permission denied (publickey)":**
```bash
ssh -v user@server                  # verbose — shows exactly where auth fails
# Common causes:
ls -la ~/.ssh/                      # wrong permissions on ~/.ssh or keys?
cat ~/.ssh/authorized_keys          # is the public key actually there?
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys   # fix permissions
```

**"Host key verification failed":**
```bash
# The server's host key changed (reinstall, IP reassigned, or MITM attack)
ssh-keygen -R server-hostname       # remove old key from known_hosts
# Then reconnect and accept the new fingerprint
# If unexpected: verify with the server owner before accepting
```

**"Connection refused":**
```bash
systemctl status sshd               # is sshd running?
ss -tulpn | grep :22                # is it listening?
ufw status                          # is port 22 blocked?
```

**"Connection timed out":**
```bash
ping server-ip                      # basic reachability?
nc -zv server-ip 22                 # is port 22 reachable from here?
# Timeout = firewall dropping packets silently (not refusing)
```

**Locked out after setting PasswordAuthentication no:**
- Need console access (cloud provider's web console / serial console)
- Or: had another session open (don't close all sessions before verifying keys work)
- Prevention: **test key login works before disabling password auth**

---

## SRE best practices

```
✅  Use ed25519 keys (faster, more secure than RSA-2048)
✅  Set PermitRootLogin no
✅  Set PasswordAuthentication no (after keys are working and tested)
✅  Use a bastion/jump host for accessing private subnet servers
✅  Rotate host keys after a server compromise
✅  Use AWS Systems Manager Session Manager instead of SSH where possible
    (no port 22 open at all, audit trail built in)

❌  Never share private keys
❌  Never use password auth in production
❌  Never allow root login via SSH
❌  Never expose SSH to 0.0.0.0/0 without fail2ban or an IP allowlist
```
