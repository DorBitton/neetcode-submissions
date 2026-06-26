# Linux Notes

## Start Here

> **Open [`CHEATSHEET.md`](./CHEATSHEET.md) when you need a command fast.**
> Use the topic subdirectory files to understand the *why* behind commands.

---

## KillerCoda — Pawel Piwosz (lessons 1–20)

| # | Lesson | Status | Concepts |
|---|--------|--------|---------|
| 1 | List files | ✅ | `ls`, flags, hidden files |
| 2 | Your best friend — man | ✅ | `man`, `--help`, searching manual |
| 3 | Work with directories | ✅ | `pwd`, `cd`, `mkdir`, `rmdir` |
| 4 | Create and delete files | ✅ | `touch`, `rm`, `cp`, `mv` |
| 5 | Pipes | ✅ | `\|`, `head`, `tail`, `grep`, `wc` |
| 6 | Reading the file | ✅ | `cat`, `less`, `more`, `nano`, `vi` |
| 7 | Copy and move files | ✅ | `cp -r`, `mv`, renaming |
| 8 | The top command | ✅ | `top`, `htop`, system monitoring |
| 9 | The ps command | ✅ | `ps`, `ps aux`, process listing |
| 10 | Create aliases | ✅ | `alias`, `.bashrc`, `.zshrc` |
| 11 | Work with users | ✅ | `useradd`, `usermod`, `passwd`, `groups` |
| 12 | Your work history | ✅ | `history`, `!!`, `!n`, Ctrl+R |
| 13 | Elevate privileges | ✅ | `sudo`, `su`, `/etc/sudoers` |
| 14 | Work with logs | ✅ | `journalctl`, `/var/log/`, `tail -f` |
| 15 | Streams | ✅ | stdin/stdout/stderr, `>`, `>>`, `2>` |
| 16 | Crontab | ✅ | `crontab -e`, cron syntax, scheduling |
| 17 | Know your files | ✅ | `file`, `stat`, `du`, `df`, `find` |
| 18 | Soft and hard links | ✅ | `ln`, `ln -s`, inode sharing |
| 19 | Inodes | ✅ | what an inode is, `ls -i`, `stat` |
| 20 | Permissions | ✅ | `chmod`, `chown`, `chgrp`, octal notation |
| — | Test your knowledge | ✅ | — |

---

## KillerCoda — Alexis Carbillet (troubleshooting scenarios)

Real-world troubleshooting labs. Harder than the Pawel lessons — closer to what prepare.sh and SRE interviews test.

**Workflow:** do the scenario first, then read the linked notes file to reinforce.

| Scenario | Status | Notes file |
|---|---|---|
| Cron Job Troubleshooting | ⬜ | [`processes/processes.md`](./processes/processes.md) |
| Exploring and Mounting Disks in Linux | ⬜ | [`storage/disks.md`](./storage/disks.md) |
| Linux Disk Full: Log Management | ⬜ | [`logs/logs.md`](./logs/logs.md) |
| Linux Firewall Troubleshooting | ⬜ | [`networking/firewall.md`](./networking/firewall.md) |
| Linux Process Management & Resource Limits | ⬜ | [`processes/processes.md`](./processes/processes.md) |
| Linux Systemd Service Debugging | ⬜ | [`services/systemd.md`](./services/systemd.md) |
| Linux Troubleshooting: Backup and Restore | ⬜ | [`storage/backup.md`](./storage/backup.md) |
| Linux User, Group, and Permissions Troubleshooting | ⬜ | [`users/users.md`](./users/users.md) |
| Log Mining with Grep and Awk | ⬜ | [`logs/text-processing.md`](./logs/text-processing.md) |
| Network Service Troubleshooting | ⬜ | [`networking/network-tools.md`](./networking/network-tools.md) |
| SSH Hardening & Security Audit | ⬜ | [`networking/ssh.md`](./networking/ssh.md) |
| Text Transformation with sed | ⬜ | [`logs/text-processing.md`](./logs/text-processing.md) |

---

## File Map

### Reference (open while working)

| File | What's in it |
|---|---|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | Every command, flag, and example on one page |

### Deep-Dive Concepts (read to understand)

| File | Lessons | What's in it |
|---|---|---|
| [`storage/filesystem.md`](./storage/filesystem.md) | 1, 3, 4, 6, 17 | Navigating, listing, creating, deleting files and dirs |
| [`services/streams.md`](./services/streams.md) | 5, 15 | Pipes, stdin/stdout/stderr, redirections |
| [`processes/processes.md`](./processes/processes.md) | 8, 9, 16 | top, ps, cron, process management |
| [`users/users.md`](./users/users.md) | 11, 13, 20 | Users, groups, sudo, permissions |
| [`logs/logs.md`](./logs/logs.md) | 14 | /var/log files, journalctl, logrotate, real-world scenarios |
| [`services/systemd.md`](./services/systemd.md) | Alexis | systemctl, unit files, service debugging, journalctl |
| [`storage/disks.md`](./storage/disks.md) | Alexis | lsblk, df, mount, umount, fstab |
| [`networking/firewall.md`](./networking/firewall.md) | Alexis | ufw, iptables, blocking/unblocking ports |
| [`logs/text-processing.md`](./logs/text-processing.md) | Alexis | grep, awk, sed, cut — log analysis pipelines |
| [`storage/backup.md`](./storage/backup.md) | Alexis | tar, rsync, restore, verification |
| [`networking/network-tools.md`](./networking/network-tools.md) | Alexis | ss, nc, dig, curl, routing — host-level network debugging |
| [`networking/ssh.md`](./networking/ssh.md) | Alexis | key-based auth, sshd_config, hardening, common lockout fixes |

### Interview Prep

| File | What's in it |
|---|---|
| [`interview-questions.md`](./interview-questions.md) | 25 common Linux interview questions with answers |

---

## Practice Tasks (prepare.sh)

Work through these hands-on scenarios at [prepare.sh/track/devops](https://prepare.sh/track/devops) → Linux section.

### Easy (10)
- [ ] Managing High I/O Processes
- [ ] Tracing Log File Writes
- [ ] Port Conflict Resolution
- [ ] Diagnose Nginx CPU Bottleneck
- [ ] Handling Large Log Archives
- [ ] Validating DNS Consistency
- [ ] Network Packet Loss Diagnosis
- [ ] Network Port Service Cleanup
- [ ] Temporary Route Configuration
- [ ] Network Socket Usage Analysis

### Medium (14)
- [ ] Analyzing Log Partition Usage
- [ ] Using Unmounted Partitions
- [ ] Debug SSH Lockout
- [ ] Monitoring Process Ownership
- [ ] Detect Memory Leak by Monitoring RSS
- [ ] Fix Inode Exhaustion Issue
- [ ] Fix HTTPS Certificate Error
- [ ] Real-Time Log Timestamping
- [ ] Update Cloud Configs
- [ ] Upload-Safe File Partitioning
- [ ] Fix Port Exhaustion for High-Speed Scraper
- [ ] Validating Network Routes
- [ ] Inspecting HTTP Traffic Flow
- [ ] Forward Traffic Between Ports

### Hard (5)
- [ ] Rapid Disk Growth on /var
- [ ] Manage Service Failure Recovery
- [ ] Nginx Rate Limit Calculation
- [ ] Automated Archive and Retention
- [ ] Trace Process Service Ownership
