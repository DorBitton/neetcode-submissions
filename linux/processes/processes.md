# Processes, Monitoring & Scheduling

> Covers lessons 8, 9, 16 — fill in as you complete them

---

## Table of Contents

1. [What is a Process?](#1-what-is-a-process)
2. [top — Live System Monitor](#2-top--live-system-monitor)
3. [ps — Snapshot of Processes](#3-ps--snapshot-of-processes)
4. [Controlling Processes](#4-controlling-processes)
5. [Background & Foreground Jobs](#5-background--foreground-jobs)
6. [Resource Limits — ulimit, nice, renice, ionice](#6-resource-limits--ulimit-nice-renice-ionice)
7. [Process Inspection — D-state, lsof, memory, hierarchy](#7-process-inspection--d-state-lsof-memory-hierarchy)
8. [Crontab — Scheduling](#8-crontab--scheduling)

---

## 1. What is a Process?

A **process** is a running instance of a program.
Every process has:
- a **PID** (process ID) — unique number assigned by the kernel
- a **PPID** (parent PID) — who spawned it
- an **owner** — the user it runs as
- **CPU** and **memory** usage
- a **state**: running, sleeping, stopped, zombie

```bash
# When you open a terminal, the shell is a process
# When you run ls, a child process is spawned, runs, exits
# Long-running servers (nginx, postgres) are persistent processes
```

---

## 2. top — Live System Monitor

`top` gives you a real-time view of what's running and consuming resources.

```bash
top              # launch
htop             # improved version (color, mouse support — install separately)
```

**Reading the top output:**

```
top - 09:01:02 up 3 days, 2:15,  2 users,  load average: 0.15, 0.10, 0.09
Tasks: 120 total,   1 running, 119 sleeping
%Cpu(s):  3.5 us,  0.5 sy,  0.0 ni, 95.8 id,  0.2 wa
MiB Mem:   7849.8 total,   1234.5 free,   3456.7 used
MiB Swap:   2048.0 total,   2048.0 free

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM   TIME+   COMMAND
 1234 dor       20   0  234512  45678  12345 S   2.5   0.6   0:12.34 node
 5678 root      20   0  123456  23456   4567 S   0.5   0.3   2:34.56 nginx
```

| Column | Meaning |
|---|---|
| PID | process ID |
| USER | owner |
| %CPU | CPU usage |
| %MEM | memory usage |
| S | state (S=sleeping, R=running, Z=zombie) |
| COMMAND | the program name |

**Inside top:**
- `q` — quit
- `k` — kill a process (enter PID)
- `M` — sort by memory
- `P` — sort by CPU
- `1` — show per-CPU stats

---

## 3. ps — Snapshot of Processes

`ps` shows a snapshot (not live). Use it when you need to script or pipe results.

```bash
ps                    # your processes in current shell
ps aux                # ALL processes, ALL users, detailed
ps aux | grep nginx   # find a specific process
ps -p 1234            # info about a specific PID
ps -u dor             # processes owned by user dor
```

**`ps aux` columns:**
```
USER   PID  %CPU %MEM  VSZ    RSS    TTY   STAT  START   TIME   COMMAND
dor    1234  2.5  0.6  234512 45678  pts/0 S     09:00   0:12   node server.js
```

| Column | Meaning |
|---|---|
| VSZ | virtual memory size |
| RSS | resident memory (actually in RAM) |
| STAT | state (S=sleep, R=run, Z=zombie, T=stopped) |
| TTY | terminal it's attached to |

---

## 4. Controlling Processes

```bash
kill PID             # send SIGTERM — ask process to stop gracefully
kill -9 PID          # send SIGKILL — force immediate stop (no cleanup)
kill -15 PID         # SIGTERM (same as default kill)
pkill nginx          # kill by name
killall nginx        # kill all processes with that name

# Common signals:
# SIGTERM (15) — please stop (process can handle it, save state)
# SIGKILL (9)  — stop NOW (cannot be caught or ignored)
# SIGHUP (1)   — reload config (used with servers like nginx)
```

**When to use which:**
1. Try `kill PID` first (graceful)
2. If that doesn't work, `kill -9 PID` (force)

---

## 5. Background & Foreground Jobs

```bash
command &            # run command in background
Ctrl+Z               # suspend current process
Ctrl+C               # interrupt (terminate) current process

jobs                 # list background/suspended jobs
bg %1                # resume job 1 in background
fg %1                # bring job 1 to foreground
fg                   # bring most recent job to foreground
```

```bash
# Example: run a long process in background
./build.sh &         # starts immediately, shell stays free
# Output: [1] 4567  (job number and PID)

jobs
# [1]+  Running    ./build.sh &

fg %1                # bring it back to foreground
```

---

## 6. Resource Limits — ulimit, nice, renice, ionice

Linux gives you three levers to control how much CPU, memory, and disk I/O any process can consume.

---

### ulimit — Per-Process Hard Limits

`ulimit` sets kernel-enforced limits on what a shell (and its child processes) can use. Think of it as a safety net so one runaway process can't take down the whole box.

```bash
ulimit -a                   # show all current limits
ulimit -n                   # max open file descriptors (default 1024)
ulimit -u                   # max number of processes a user can spawn
ulimit -m                   # max memory in KB
ulimit -c                   # core dump file size (0 = disabled)
ulimit -t                   # max CPU time in seconds

# Set limits for the current session
ulimit -n 65535             # raise open files to 65535
ulimit -n unlimited         # remove the limit (only root can exceed hard limit)
```

**Soft vs Hard limits:**
- **Soft** — the current enforced value; a process can raise it up to the hard limit
- **Hard** — the ceiling; only root can raise it

```bash
ulimit -Sn 4096             # set soft limit for open files
ulimit -Hn 65535            # set hard limit for open files
```

**Persisting ulimits** — session limits vanish on logout. To persist:
```bash
# /etc/security/limits.conf  (for login sessions via PAM)
# <domain>  <type>  <item>   <value>
dor         soft    nofile   65535
dor         hard    nofile   65535
*           soft    core     0        # disable core dumps for everyone
```

**Why SREs care:** Databases and web servers routinely hit the default 1024 open-file limit under load. `Too many open files` errors are almost always a missing `ulimit -n` increase.

---

### CPU Priority — nice and renice

Every process has a **niceness value** from **-20 (highest priority) to +19 (lowest priority)**. The default is 0.

The kernel uses niceness to decide how much CPU time to allocate when processes compete. A "nicer" process voluntarily gives up CPU to others.

```
-20  ←  most CPU (least nice to others)
  0  ←  default
+19  ←  least CPU (most nice to others)
```

```bash
# Start a process with a specific niceness
nice -n 10 ./backup.sh          # run backup.sh at low priority (nice=10)
nice -n -5 ./realtime-app       # higher priority (need root for negative values)

# Change priority of a RUNNING process
renice -n 10 -p 1234            # lower priority of PID 1234 to nice=10
renice -n 10 -u dor             # lower priority of ALL processes owned by dor
renice -n -5 -p 5678            # raise priority (root only)
```

**See niceness in top/ps:**
```bash
top     # NI column = nice value, PR column = actual kernel priority (PR = 20 + NI)
ps -eo pid,ni,comm              # show PID, nice value, command name
```

**Real-world patterns:**
| Workload | Niceness | Why |
|---|---|---|
| Database (postgres, mysql) | -5 to 0 | Critical path — needs CPU |
| Message queue (kafka, rabbit) | 0 | Normal priority |
| Batch backup job | +10 to +15 | Should not compete with live traffic |
| Log compression | +19 | Background, never urgent |

---

### I/O Priority — ionice

CPU niceness controls CPU scheduling. **`ionice`** controls disk I/O scheduling — how the kernel's I/O scheduler (CFQ) orders disk requests.

#### I/O Scheduling Classes

| Class | Value | Meaning |
|---|---|---|
| **Idle** | 3 | Gets I/O only when nothing else needs the disk. Starved if disk is busy. |
| **Best-effort** | 2 | Default for most processes. Shares disk fairly by niceness (0–7). |
| **Realtime** | 1 | Gets disk access first, always. Use with care — can starve other processes. |
| **None** | 0 | Inherits class from parent (usually becomes best-effort). |

```bash
ionice -c 3 -p 1234             # set PID 1234 to idle class (lowest I/O priority)
ionice -c 2 -n 7 -p 1234       # best-effort, lowest priority within class (0=high, 7=low)
ionice -c 1 -n 0 -p 5678       # realtime, highest priority (root only)

# Start a new command with I/O priority set
ionice -c 3 ./bulk-archive.sh   # run archiver at idle I/O priority
ionice -c 1 -n 0 postgres       # give postgres real-time I/O (production pattern)
```

**What "Idle" means in practice:**

When a process is set to I/O class **Idle**, the kernel's I/O scheduler will only give it disk access during gaps when no other process has a pending I/O request. On a busy server with active databases, a backup job at Idle can be nearly invisible to production traffic — it drip-feeds through leftover disk time.

This is why `ionice -c 3` is the standard tool for:
- Backup jobs (`rsync`, `tar`, `mysqldump`)
- Log archival
- Bulk file operations during business hours
- Any find + copy that would otherwise spike disk wait

**Finding I/O offenders:**

```bash
iotop                           # live view — like top, but for disk I/O (needs root)
iotop -o                        # show only processes with active I/O
iotop -b -n 5                   # non-interactive, 5 snapshots (good for scripting)

# iotop output columns:
# TID   PRIO   USER   DISK READ   DISK WRITE   SWAPIN   IO%   COMMAND
# 8821  be/4   mysql  0.00 B/s    12.34 M/s    0.00%    45%   mysqld
```

**Combining CPU + I/O priority (the full pattern):**
```bash
# Demote a backup to low CPU and idle I/O simultaneously
nice -n 19 ionice -c 3 ./backup.sh

# Elevate a database process after the fact
renice -n -5 -p $(pgrep postgres)
ionice -c 1 -n 0 -p $(pgrep postgres)
```

#### The KillerCoda scenario answer

When the scenario asks you to "reduce I/O of the top offender using idle priority":

1. Find the offender: `iotop -o` or `iotop -b -n 1`
2. Set its I/O to idle: `ionice -c 3 -p <PID>`
3. Optionally lower CPU priority too: `renice -n 19 -p <PID>`
4. Protect critical jobs: `ionice -c 1 -n 0 -p $(pgrep postgres)` and `ionice -c 1 -n 0 -p $(pgrep rabbitmq)`

---

## 7. Process Inspection — D-state, lsof, memory, hierarchy

### D-state processes

```bash
# D = uninterruptible sleep — process waiting on kernel I/O (disk, NFS, etc.)
# Cannot be killed with kill -9 — must resolve the underlying I/O issue
ps aux | grep " D "                    # find D-state processes
cat /proc/<PID>/wchan                  # what kernel function is it waiting on?
cat /proc/<PID>/status | grep State   # State: D (disk sleep)
# Stuck in D state forever → hung NFS mount, failing disk, or kernel bug
# Fix: unmount the hung filesystem, or reboot (last resort)
```

### lsof — list open files

```bash
lsof -p <PID>                          # all files open by a process
lsof +D /var/log                       # what processes have files open in this dir?
lsof | grep deleted                    # files deleted but still held open (disk leak!)
lsof -i :80                            # what process has port 80 open?
ls /proc/<PID>/fd | wc -l             # count open file descriptors for a process
```

### File descriptor leaks

```bash
# Symptom: "too many open files" errors, fd count growing without bound
ls /proc/<PID>/fd | wc -l            # current fd count for a process
cat /proc/<PID>/limits | grep "open files"  # soft and hard limits
# Fix for current session:
ulimit -n 65535
# Fix permanently via /etc/security/limits.conf (see resource limits section above)
# Find the leak: lsof -p <PID> | wc -l  — watch it grow over time
```

### Memory leak / RSS monitoring

```bash
ps -eo pid,rss,vsz,comm --sort=-rss | head -10   # top 10 RSS consumers
watch -n 5 'ps -p <PID> -o pid,rss,vsz'          # watch one process grow every 5s
# RSS = resident set size = memory actually in RAM
# If RSS grows unboundedly over time without plateauing → memory leak
cat /proc/<PID>/status | grep -E "VmRSS|VmSize|VmSwap"  # detailed breakdown
```

### High swap per process

```bash
# Find which processes are using the most swap:
for f in /proc/[0-9]*/status; do
  awk '/VmSwap|^Name/{printf $2 " " $3 "\n"}' "$f" 2>/dev/null
done | sort -k2 -rn | head -10
# If smem is installed (cleaner output):
smem -r | head -10
```

### Process hierarchy

```bash
pstree                                  # tree of all processes from PID 1
pstree -p                               # include PIDs
pstree <PID>                            # subtree for a specific process
ps -eo pid,ppid,comm --sort=ppid        # parent-child relationships in table form
ps --ppid <PID>                         # direct children of a process
```

### Uptime and load average

```bash
uptime
# output: 09:15:00 up 3 days,  2 users,  load average: 1.23, 0.95, 0.88
#                                                        ^1min  ^5min  ^15min
# Load average = average number of processes in run queue (running or waiting for CPU)
# Rule of thumb: load > nproc = system is overloaded
nproc                                  # how many CPU cores?
cat /proc/loadavg                      # same data, scriptable format
w                                      # uptime + logged-in users + their activity
```

---

## 8. Crontab — Scheduling

Cron is the Linux task scheduler. `crontab` manages your scheduled jobs.

```bash
crontab -e           # open editor to add/edit/remove jobs
crontab -l           # list your current cron jobs
crontab -r           # remove ALL your cron jobs (careful!)
```

### Cron Syntax

```
* * * * *  command to run
│ │ │ │ │
│ │ │ │ └── day of week  (0-7, Sunday = 0 or 7)
│ │ │ └──── month        (1-12)
│ │ └────── day of month (1-31)
│ └──────── hour         (0-23)
└────────── minute       (0-59)
```

**Special values:**
| Value | Meaning |
|---|---|
| `*` | every unit |
| `*/5` | every 5 units |
| `1,3,5` | at 1, 3, and 5 |
| `1-5` | from 1 to 5 |

### Examples

```bash
# Run at minute 0 of every hour
0 * * * * /home/dor/backup.sh

# Run at midnight every day
0 0 * * * /home/dor/daily_cleanup.sh
```

**Tips:**
- Use absolute paths in cron jobs — cron has a minimal environment with no `$PATH`
- Redirect output to a log file or `/dev/null`:
  ```bash
  0 * * * * /home/dor/backup.sh >> /var/log/backup.log 2>&1
  ```
- Test your script manually before adding to cron

---
