# Linux — SRE/DevOps Interview Prep

> **Open [`CHEATSHEET.md`](./CHEATSHEET.md) when you need a command fast.**
> Use the topic subdirectory files to understand the *why* behind commands.

---

## File Map

### Quick Reference
| File | What's in it |
|---|---|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | Every command on one page — open this first |
| [`interview-questions.md`](./interview-questions.md) | 25 interview questions with answers |

### Topic Files
| File | Covers |
|---|---|
| [`processes/processes.md`](./processes/processes.md) | top, ps, signals, jobs, resource limits (nice/renice/ionice/ulimit), D-state, lsof, memory leaks, process hierarchy |
| [`storage/filesystem.md`](./storage/filesystem.md) | Navigation, files, dirs, links, inodes, find |
| [`storage/disks.md`](./storage/disks.md) | lsblk, df, du, mount, fstab, inode exhaustion, disk quotas |
| [`storage/backup.md`](./storage/backup.md) | tar, rsync, restore, verification |
| [`networking/network-tools.md`](./networking/network-tools.md) | ss, ping, mtr, traceroute, curl, tcpdump, conntrack, MTU, SYN flood, namespaces, port exhaustion, macvlan |
| [`networking/firewall.md`](./networking/firewall.md) | ufw, iptables INPUT/OUTPUT, NAT/DNAT, port forwarding, load balancing |
| [`networking/dns.md`](./networking/dns.md) | resolv.conf, nsswitch.conf, dig, reverse DNS, zone transfers (BIND) |
| [`networking/routing.md`](./networking/routing.md) | ip route, CIDR, overlapping subnets, gateway config |
| [`networking/tls.md`](./networking/tls.md) | openssl, cert inspection, CSR, self-signed, chain, mTLS, private key permissions |
| [`networking/ssh.md`](./networking/ssh.md) | Key auth, sshd_config, tunneling, lockout troubleshooting |
| [`services/systemd.md`](./services/systemd.md) | systemctl, unit files, service debugging, reboot history |
| [`services/streams.md`](./services/streams.md) | stdin/stdout/stderr, pipes, redirections |
| [`logs/logs.md`](./logs/logs.md) | /var/log files, journalctl, logrotate, inotifywait, SLO error budget |
| [`logs/text-processing.md`](./logs/text-processing.md) | grep, awk, sed, cut, sort, split — log analysis pipelines |
| [`users/users.md`](./users/users.md) | Users, groups, sudo, permissions, sessions, login violations, credential scanning |

---

## Practice Tasks (prepare.sh)

Work through these hands-on scenarios at [prepare.sh/track/devops](https://prepare.sh/track/devops).

### Linux Track (98 questions)

#### Processes & I/O
- [ ] Managing High I/O Processes (Revolut) — Easy
- [ ] Managing Process Overload (Booking.com) — Medium
- [ ] Identifying D State Processes (Datadog) — Medium
- [ ] Performance-Based Backend Selection (Amazon) — Easy
- [ ] Trace Process Service Ownership (NVIDIA) — Hard
- [ ] Monitoring Process Ownership (HashiCorp) — Medium
- [ ] Uptime and Load Average Audit (Microsoft) — Easy
- [ ] Diagnose Nginx CPU Bottleneck (Palantir) — Easy
- [ ] CPU Resource Management Priority (RedHat) — Easy
- [ ] Track Forking Process Hierarchies (Splunk) — Easy
- [ ] Discover Unexpected Background Jobs (Plus500) — Medium
- [ ] Throttle High I/O Process (Ebay) — Easy
- [ ] Identify High Disk I/O Process (Dropbox) — Medium
- [ ] Trace Stalled Script Execution (Atlassian) — Medium
- [ ] Analyze File Descriptor Leak (Reddit) — Medium
- [ ] Identify High Swap Processes (NewRelic) — Hard
- [ ] Detect Memory Leak by Monitoring RSS (Google) — Medium

#### Disk & Filesystem
- [ ] Filesystem Inconsistencies (Twitch) — Medium
- [ ] Analyzing Log Partition Usage (RedHat) — Medium
- [ ] Using Unmounted Partitions (RedHat) — Medium
- [ ] Investigate Mounted Disk Usage (Databricks) — Medium
- [ ] Rapid Disk Growth on /var (Google) — Hard
- [ ] Purge Empty Folders (CrowdStrike) — Easy
- [ ] Log File Volume Assessment (JPMorgan) — Easy
- [ ] Upload-Safe File Partitioning (GoDaddy) — Medium
- [ ] Fix Inode Exhaustion Issue (DeutscheBank) — Medium
- [ ] Configuring Multi-User Quotas (Twitch) — Medium

#### Logs & Files
- [ ] Tracing Log File Writes (Bloomberg) — Easy
- [ ] Managing Log File Rotation (Coinbase) — Medium
- [ ] Handling Large Log Archives (Amazon) — Easy
- [ ] Selective Log Archive Creation (SAP) — Medium
- [ ] Sorted Log Aggregation (Airbnb) — Easy
- [ ] Log File Disk Consumption (Autodesk) — Medium
- [ ] Real-Time Log Timestamping (Adobe) — Medium
- [ ] Track Configuration File Changes (HashiCorp) — Medium
- [ ] Release Locked Log File (Infosys) — Medium
- [ ] Recursive Keyword Finder (X) — Easy
- [ ] Recursive Database File Backup (GitLab) — Easy

#### Systemd & Services
- [ ] Troubleshoot systemd Startup Failure (Microsoft) — Medium
- [ ] Manage Service Failure Recovery (Apple) — Hard
- [ ] Update Cloud Configs (Stripe) — Medium
- [ ] Cron-Based Process Monitoring (RedHat) — Medium
- [ ] Debug Service Crash Loop (CrowdStrike) — Medium
- [ ] Debug Failed Service Startup (Citi) — Medium
- [ ] Monitor System Reboot Patterns (Booking.com) — Medium
- [ ] Diagnose Hardware Error Messages (CGI) — Easy
- [ ] Viewing systemd Service Logs from Current Boot (Google) — Easy

#### Security & Users
- [ ] Application Config Setup (Meta) — Medium
- [ ] Automated Vulnerability Detection (Slack) — Medium
- [ ] User Session Cleanup (CGI) — Medium
- [ ] Detect Login Time Violations (UBS) — Easy
- [ ] Audit Shell Access and Activity (Walmart) — Hard
- [ ] Credential Leak Detection (ActivisionBlizzard) — Medium
- [ ] Block SSH Brute-Force Attacks (VMware) — Medium
- [ ] Rate Limit Database Connections (Walmart) — Medium
- [ ] Identify and Remove Compromised User Accounts (Nintendo) — Easy
- [ ] Create Non-Interactive System User (Booking.com) — Easy
- [ ] Add User to Sudo Group (Citi) — Easy
- [ ] Find Files Owned by Non-Existent Users (CGI) — Easy

#### TLS & Certificates
- [ ] Fix HTTPS Certificate Error (GitHub) — Medium
- [ ] Fix Mutual TLS Authentication (Nintendo) — Medium
- [ ] Debug TLS to HTTP Mismatch (Google) — Medium
- [ ] Fix Broken TLS Certificate Chain (GitHub) — Easy
- [ ] Diagnose TLS Handshake and Protocol Support (Stripe) — Easy
- [ ] Fix Missing SAN in TLS Certificate (Microsoft) — Easy
- [ ] Generate RSA Key and Certificate Signing Request (Walmart) — Easy
- [ ] Generate Self-Signed Certificate for Development (Netflix) — Easy
- [ ] Inspect TLS Certificate Issuer and Validity (CrowdStrike) — Easy
- [ ] Fix Private Key File Permissions (Reddit) — Easy
- [ ] Calculate SLO Error Budget from Access Logs (Meta) — Medium

#### SSH
- [ ] Debug SSH Lockout (TCS) — Medium

#### Networking
- [ ] Validating Network Routes (Google) — Medium
- [ ] Network Packet Loss Diagnosis (Cloudflare) — Easy
- [ ] Network Port Service Cleanup (Apple) — Easy
- [ ] Temporary Route Configuration (Spotify) — Easy
- [ ] Inspecting HTTP Traffic Flow (Airbnb) — Medium
- [ ] Network Socket Usage Analysis (SAP) — Easy
- [ ] Verify Host Network Access (DoorDash) — Medium
- [ ] Port Conflict Resolution (Datadog) — Easy
- [ ] Forward Traffic Between Ports (Meta) — Medium
- [ ] Route Subnet Through Gateway (Infosys) — Medium
- [ ] Investigate Conntrack Connection States (Stripe) — Medium
- [ ] Detect SYN Flood Patterns (IBM) — Medium
- [ ] Fix Port Exhaustion for High-Speed Scraper (X) — Medium
- [ ] Connect Isolated Network Namespaces (Databricks) — Medium
- [ ] Load Balance with iptables DNAT (VMware) — Medium
- [ ] Allow Outbound SMTP Traffic (Visa) — Medium
- [ ] Restore Blocked SSH Access (CrowdStrike) — Medium
- [ ] Network Path Latency (CreditSuisse) — Medium
- [ ] Automated Archive and Retention (Microsoft) — Hard

---

### Networking Track (21 questions)

- [ ] Validating Network Routes (Google) — Medium
- [ ] Validating DNS Consistency (SAP) — Easy
- [ ] Network Packet Loss Diagnosis (Cloudflare) — Easy
- [ ] Network Port Service Cleanup (Apple) — Easy
- [ ] Fixing Overlapping Subnets (Cisco) — Medium
- [ ] Temporary Route Configuration (Spotify) — Easy
- [ ] Inspecting HTTP Traffic Flow (Airbnb) — Medium
- [ ] VPN MTU Mismatch Diagnosis (Kayak) — Medium
- [ ] Diagnosing Linux DNS Configuration (PayPal) — Medium
- [ ] Network Path Latency (CreditSuisse) — Medium
- [ ] Network Socket Usage Analysis (SAP) — Easy
- [ ] Service Port Health Check (Netflix) — Medium
- [ ] Restore Blocked SSH Access (CrowdStrike) — Medium
- [ ] Allow Outbound SMTP Traffic (Visa) — Medium
- [ ] Inspect HTTPS Headers Advanced (TikTok) — Medium
- [ ] Verify Reverse DNS Records (Walmart) — Medium
- [ ] Forward Traffic Between Ports (Meta) — Medium
- [ ] Load Balance with iptables DNAT (VMware) — Medium
- [ ] Route Subnet Through Gateway (Infosys) — Medium
- [ ] Configure Secondary DNS Zone Transfers (BMW) — Hard
- [ ] Macvlan Network Configuration Fix (Uber) — Hard
