# Processes, Monitoring & Scheduling

> Covers lessons 8, 9, 16 — fill in as you complete them

---

## Table of Contents

1. [What is a Process?](#1-what-is-a-process)
2. [top — Live System Monitor](#2-top--live-system-monitor)
3. [ps — Snapshot of Processes](#3-ps--snapshot-of-processes)
4. [Controlling Processes](#4-controlling-processes)
5. [Background & Foreground Jobs](#5-background--foreground-jobs)
6. [Crontab — Scheduling](#6-crontab--scheduling)
7. [Command History & Aliases](#7-command-history--aliases)

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

## 6. Crontab — Scheduling

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

# Run every 5 minutes
*/5 * * * * /home/dor/check.sh

# Run at 9am every Monday
0 9 * * 1 /home/dor/weekly_report.sh

# Run at midnight every day
0 0 * * * /home/dor/daily_cleanup.sh

# Run at 2:30pm on weekdays (Mon-Fri)
30 14 * * 1-5 /home/dor/remind.sh

# Run once on a specific date (Jan 1 at midnight)
0 0 1 1 * /home/dor/new_year.sh
```

**Tips:**
- Use absolute paths in cron jobs — cron has a minimal environment with no `$PATH`
- Redirect output to a log file or `/dev/null`:
  ```bash
  0 * * * * /home/dor/backup.sh >> /var/log/backup.log 2>&1
  ```
- Test your script manually before adding to cron

---

## 7. Command History & Aliases

```bash
history              # show numbered history of commands
history | tail -20   # last 20 commands
history | grep git   # search history
!!                   # run last command again
!n                   # run command number n from history
!git                 # run most recent command starting with "git"
Ctrl+R               # reverse search — type to search history interactively
```

### Aliases

```bash
alias ll='ls -la'           # create alias for current session
alias gs='git status'
alias ..='cd ..'
unalias ll                  # remove alias
alias                       # list all aliases
```

**To persist aliases** — add them to your shell config file:
```bash
# ~/.bashrc (bash) or ~/.zshrc (zsh)
alias ll='ls -la'
alias gs='git status'
alias ..='cd ..'

# After editing, reload:
source ~/.bashrc
# or:
source ~/.zshrc
```
