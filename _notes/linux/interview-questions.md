# Linux Interview Questions

25 questions you'll actually get asked. Organized by topic.

---

## Filesystem & Navigation

**Q1: What is the difference between an absolute path and a relative path?**

An **absolute path** starts from the root `/` and gives the full location of a file:
`/home/dor/projects/app.py`. It works from any directory.

A **relative path** is relative to your current directory:
`projects/app.py` or `../other/file.txt`. It only works when you're in the right place.

---

**Q2: What does `ls -la` show that `ls` doesn't?**

- `-l` adds long format: permissions, owner, group, file size, last modified date
- `-a` shows hidden files (files starting with `.` like `.bashrc`, `.gitconfig`)

Combined, you see a full picture of every file including hidden ones.

---

**Q3: What is an inode?**

An inode is a data structure the filesystem uses to store **metadata** about a file:
size, owner, permissions, timestamps, and pointers to the actual data blocks on disk.

The filename is NOT stored in the inode — it's stored in the directory.
A directory is just a mapping of names → inode numbers.

```bash
ls -i file.txt    # shows inode number
stat file.txt     # shows full inode metadata
```

---

**Q4: What is the difference between a hard link and a symbolic link?**

| | Hard link | Symbolic link |
|---|---|---|
| Points to | inode (same data) | a path (string) |
| If original deleted | data still exists | link breaks |
| Cross-filesystem | No | Yes |
| Can link directory | No | Yes |

```bash
ln original hardlink      # hard link
ln -s original softlink   # symbolic link
```

A hard link is like giving the same file two names. A soft link is like a shortcut.

---

**Q5: What do the columns in `ls -l` mean?**

```
-rw-r--r--  1  dor  staff  1234  Jun 10  file.txt
^           ^  ^    ^      ^     ^
type+perms  links  owner  group  size   date
```

First character: `-` file, `d` directory, `l` symlink.
Next 9 characters: permissions in three groups of 3 (owner, group, others).

---

## Permissions

**Q6: How do Linux file permissions work?**

Every file has three sets of `rwx` permissions: for the **owner**, **group**, and **others**.

- `r` (4) = read
- `w` (2) = write
- `x` (1) = execute

`chmod 755 file` → owner: `rwx` (7), group: `r-x` (5), others: `r-x` (5)

On directories: `r` = can list, `w` = can create/delete inside, `x` = can enter (`cd`).

---

**Q7: What does `chmod 600 ~/.ssh/id_rsa` do and why is it needed?**

Sets permissions to `rw-------` — only the owner can read and write, nobody else.

SSH refuses to use a private key if it's readable by others. This is a security check:
if your private key is world-readable, it's compromised.

---

**Q8: What is the difference between `sudo` and `su`?**

- `sudo command` — runs a **single command** as root, using **your password**, and logs it
- `su username` — **switches to another user** for the rest of the session, needs **their password**
- `sudo su` — common pattern: use your sudo rights to become root permanently

`sudo` is preferred because it's auditable (logged) and requires less trust (no root password shared).

---

**Q9: What is setuid and why is it a security concern?**

The setuid bit (`chmod u+s file`) makes a file run with the **owner's permissions** rather than the caller's.
`/usr/bin/passwd` is setuid root — a normal user can change their password because passwd runs as root.

Security concern: if a setuid-root binary has a bug, an attacker can exploit it to gain root access.
```bash
find / -perm -4000 2>/dev/null    # find all setuid files
```

---

## Processes

**Q10: What is the difference between `kill` and `kill -9`?**

- `kill PID` sends **SIGTERM** (15) — asks the process to stop gracefully. The process can catch this signal, finish cleanup, and exit cleanly.
- `kill -9 PID` sends **SIGKILL** — the kernel terminates the process immediately. The process cannot catch or ignore it. No cleanup happens.

Always try `kill` first. Use `-9` only if the process doesn't respond.

---

**Q11: What is a zombie process?**

A process that has finished executing but its entry still exists in the process table because the parent hasn't read its exit status yet. Shows as `Z` in `ps` or `top`.

Zombies don't consume CPU or memory but do use a PID slot.
They're cleaned up when the parent calls `wait()` or when the parent dies.

---

**Q12: What does `ps aux` show?**

A snapshot of all running processes:
- `a` — all users
- `u` — user-friendly format (shows username, CPU%, MEM%)
- `x` — include processes not attached to a terminal (daemons)

```bash
ps aux | grep nginx     # find nginx process and its PID
```

---

**Q13: How do you run a process in the background?**

```bash
command &              # start in background immediately
Ctrl+Z then bg         # suspend current process, resume in background

jobs                   # list background jobs
fg %1                  # bring job 1 to foreground
```

---

## Pipes & Streams

**Q14: What is a pipe and how does it work?**

A pipe `|` connects the **stdout** of one command to the **stdin** of the next.
Neither command knows about the other — they just read/write streams.

```bash
ps aux | grep nginx | wc -l
# ps writes to stdout → grep reads it, filters, writes → wc counts lines
```

---

**Q15: What is the difference between `>` and `>>`?**

- `>` redirects stdout to a file, **overwriting** it
- `>>` redirects stdout to a file, **appending** to it

```bash
echo "first" > file.txt    # file contains: "first"
echo "second" >> file.txt  # file contains: "first\nsecond"
echo "third" > file.txt    # file contains: "third" (overwrites!)
```

---

**Q16: What is `/dev/null`?**

A special device file that discards everything written to it and returns EOF when read.
Used to silence output you don't care about.

```bash
command > /dev/null 2>&1    # discard all output (stdout and stderr)
command 2>/dev/null          # discard only errors
```

---

**Q17: What does `2>&1` mean?**

It redirects file descriptor 2 (stderr) to the same destination as file descriptor 1 (stdout).
Used when you want stdout and stderr going to the same place.

```bash
command > output.txt 2>&1   # both stdout and stderr → output.txt
# order matters: > sets stdout first, then 2>&1 redirects stderr to stdout's destination
```

---

## System & Logs

**Q18: How do you check disk space on a Linux system?**

```bash
df -h              # disk space on all mounted filesystems (human-readable)
du -sh /var/log/   # disk usage of a specific directory
du -sh *           # disk usage of each item in current dir
```

`df` = disk free (whole filesystem), `du` = disk usage (a specific path).

---

**Q19: How do you find all files modified in the last 24 hours?**

```bash
find / -mtime -1 2>/dev/null    # files modified < 1 day ago
find /home -mmin -60            # modified in last 60 minutes
```

---

**Q20: How do you monitor a log file in real time?**

```bash
tail -f /var/log/syslog         # follow syslog
tail -f app.log | grep "ERROR"  # follow AND filter
journalctl -f                   # follow systemd journal
journalctl -f -u nginx          # follow logs for a specific service
```

---

## Scheduling & Networking

**Q21: How does crontab work? Write a cron job that runs at midnight every day.**

Crontab is the Linux job scheduler. Cron syntax: `minute hour day month weekday command`.

```bash
0 0 * * * /home/dor/daily_backup.sh
```

- `0` minute, `0` hour → midnight
- `* * *` → every day, every month, every weekday

```bash
crontab -e    # edit your cron jobs
crontab -l    # list current cron jobs
```

---

**Q22: What is the difference between `cron` and `at`?**

- `cron` — for **recurring** jobs (run every day, every hour, etc.)
- `at` — for **one-time** scheduled jobs (run once at a specific time)

```bash
at 10:30 AM tomorrow          # schedule a one-time command
echo "backup.sh" | at 2pm     # pipe the command to at
atq                            # list scheduled at jobs
```

---

## Practical / Troubleshooting

**Q23: A process is using 100% CPU. How do you find and stop it?**

```bash
top                          # see which PID is consuming CPU
# or
ps aux --sort=-%cpu | head   # sorted by CPU descending

kill PID                     # try graceful stop first
kill -9 PID                  # force stop if needed
```

---

**Q24: How do you find which process is listening on port 80?**

```bash
ss -tlnp | grep :80          # preferred (ss = socket stats)
netstat -tlnp | grep :80     # older alternative
lsof -i :80                  # list open files on port 80
```

---

**Q25: How do you check what caused the system to reboot?**

```bash
last reboot                      # history of reboots
journalctl --list-boots          # list boot sessions (systemd)
journalctl -b -1 -p err          # errors from previous boot
dmesg | grep -i "error\|panic"   # kernel messages
```
