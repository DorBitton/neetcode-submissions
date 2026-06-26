# Linux Logs

Two parallel logging systems exist on modern Linux: the traditional file-based `/var/log` and the systemd **journal**. Both exist simultaneously — some services write to both.

---

## The two systems side by side

| | `/var/log` (traditional) | `journalctl` (systemd journal) |
|---|---|---|
| Format | Plain text files | Binary database |
| Persistent by default | Yes | Sometimes (depends on config) |
| Read with | `cat`, `tail`, `grep`, `less` | `journalctl` |
| Rotation | `logrotate` | Automatic size/time limits |
| Structured data | No | Yes (JSON-exportable) |
| Boot-scoped queries | Manual | Built-in (`-b`) |

---

## /var/log — traditional file-based logs

### Key files

| File | What it contains |
|---|---|
| `/var/log/syslog` | General system messages (Ubuntu/Debian) |
| `/var/log/messages` | General system messages (RHEL/CentOS) |
| `/var/log/auth.log` | Authentication: sudo, ssh, login attempts |
| `/var/log/kern.log` | Kernel messages (hardware, OOM killer) |
| `/var/log/dmesg` | Kernel ring buffer from boot |
| `/var/log/nginx/access.log` | Nginx HTTP access log |
| `/var/log/nginx/error.log` | Nginx errors |
| `/var/log/mysql/error.log` | MySQL errors |
| `/var/log/apt/` | Package manager activity |
| `/var/log/cron` | Cron job execution (some distros) |

### Reading log files

```bash
tail -f /var/log/syslog              # follow live (most common in practice)
tail -n 100 /var/log/auth.log        # last 100 lines
less /var/log/syslog                 # page through (/ to search inside less)
cat /var/log/syslog | grep ERROR     # filter for errors
grep "Failed password" /var/log/auth.log   # find failed SSH logins
grep -i "oom" /var/log/kern.log      # find OOM killer events
```

### Filtering by time (old-style: grep the timestamp)

```bash
grep "Jun 19" /var/log/syslog              # entries for a specific date
grep "Jun 19 14:" /var/log/syslog          # entries for a specific hour
```

### Disk usage — logs filling up is a real SRE problem

```bash
du -sh /var/log/            # total size of log directory
du -sh /var/log/*           # size per file/subdirectory (find the culprit)
ls -lhS /var/log/           # list by size, largest first
```

If `/var/log` fills the disk, the fix is either:
1. Delete old rotated logs (`/var/log/syslog.1`, `.2.gz`, etc.)
2. Fix logrotate config so rotation happens more aggressively
3. Find what's logging excessively (`lsof +D /var/log | grep -v ".gz"`)

---

## journalctl — systemd journal

The journal collects everything systemd manages: services, the kernel, init, and anything using the systemd logging API. No need to know which file — you query it.

### Basic usage

```bash
journalctl                          # all logs, oldest first (use G to jump to end in pager)
journalctl -f                       # follow live (like tail -f)
journalctl -e                       # jump to end immediately
journalctl -n 50                    # last 50 lines
journalctl --no-pager               # output to stdout (pipe-friendly)
```

### Filter by service (most common in SRE work)

```bash
journalctl -u nginx                 # all logs for nginx
journalctl -u nginx -f              # follow nginx logs live
journalctl -u nginx -u mysql        # logs for multiple services
journalctl -u ssh --since "1 hour ago"
```

### Filter by time

```bash
journalctl --since "2024-06-19 14:00:00"
journalctl --since "1 hour ago"
journalctl --since "10 minutes ago"
journalctl --since yesterday
journalctl --since "2024-06-19 13:00" --until "2024-06-19 14:00"
```

### Filter by priority (log level)

```bash
journalctl -p err              # errors and above (err, crit, alert, emerg)
journalctl -p warning          # warnings and above
journalctl -p debug            # everything including debug (very verbose)
journalctl -u nginx -p err     # combine: nginx errors only
```

Priority levels (syslog scale, 0=most severe):
```
0 emerg    system is unusable
1 alert    action must be taken immediately
2 crit     critical conditions
3 err      error conditions
4 warning  warning conditions
5 notice   normal but significant
6 info     informational
7 debug    debug-level messages
```

### Boot-scoped queries

```bash
journalctl -b                   # current boot only
journalctl -b -1                # previous boot
journalctl -b -2                # two boots ago
journalctl --list-boots         # list all boots with timestamps
journalctl -b -1 -p err         # errors from last boot (useful after a crash)
```

### Kernel messages

```bash
journalctl -k                   # kernel messages only (equivalent to dmesg)
journalctl -k -b -1             # kernel messages from previous boot
dmesg                           # same but uses the kernel ring buffer directly
dmesg -T                        # with human-readable timestamps
dmesg | grep -i "oom"           # find OOM kills
dmesg | grep -i "error"
```

### Output formats

```bash
journalctl -u nginx -o json-pretty     # JSON output (good for parsing)
journalctl -u nginx -o short-precise   # timestamps with microseconds
journalctl -u nginx -o cat             # message only, no metadata
```

### Disk usage of the journal

```bash
journalctl --disk-usage         # how much disk the journal is using
```

---

## logrotate — preventing logs from filling your disk

`logrotate` runs via cron (usually daily) and rotates, compresses, and deletes old log files.

Config location:
- `/etc/logrotate.conf` — global defaults
- `/etc/logrotate.d/` — per-service configs (nginx, rsyslog, etc.)

Example config for `/var/log/nginx/access.log`:

```
/var/log/nginx/*.log {
    daily           # rotate daily
    missingok       # don't error if log file is missing
    rotate 14       # keep 14 rotated files
    compress        # gzip old files
    delaycompress   # don't compress the most recent rotated file
    notifempty      # don't rotate if empty
    create 0640 www-data adm   # permissions for new log file
    sharedscripts
    postrotate
        nginx -s reopen   # tell nginx to reopen log files after rotation
    endscript
}
```

Test your config without running:
```bash
logrotate -d /etc/logrotate.d/nginx    # dry run, shows what would happen
logrotate -f /etc/logrotate.d/nginx    # force rotation now
```

---

## Real-world SRE scenarios

### "The disk is full on /var"

```bash
df -h                              # confirm /var is full
du -sh /var/log/*                  # find the biggest offender
ls -lhS /var/log/nginx/            # look for unexpectedly large files
# If it's a log that isn't rotating:
logrotate -f /etc/logrotate.d/nginx
# Or just clear the specific log (only if you can afford to lose it):
> /var/log/nginx/access.log        # truncate (safer than rm while nginx holds it open)
```

### "A service is failing, what happened?"

```bash
journalctl -u myservice -b -p err  # errors from this boot
journalctl -u myservice --since "5 minutes ago"
journalctl -u myservice -n 50      # last 50 lines
```

### "Who logged in with sudo recently?"

```bash
grep "sudo" /var/log/auth.log | tail -50
journalctl _COMM=sudo --since "1 hour ago"
```

### "Nginx is returning errors — find the pattern"

```bash
tail -f /var/log/nginx/error.log
grep " 502 " /var/log/nginx/access.log | tail -20
awk '$9 == "502"' /var/log/nginx/access.log | wc -l    # count 502s
```

---

## journald configuration

Control how much disk the journal uses:
```
/etc/systemd/journald.conf

SystemMaxUse=1G          # max total disk usage
SystemKeepFree=500M      # always keep this much disk free
MaxRetentionSec=1month   # delete entries older than this
```

After changes: `systemctl restart systemd-journald`

Make journal persistent across reboots (not all distros default to this):
```bash
mkdir -p /var/log/journal              # journal writes here if it exists
systemctl restart systemd-journald
```

---

## Tracing file writes with inotifywait

```bash
# inotifywait watches files/directories for filesystem events in real time
# Install: apt install inotify-tools

inotifywait -m /var/log/app.log              # monitor one file (m = keep monitoring)
inotifywait -m -r /var/log/                  # recursive — any event inside /var/log
inotifywait -m -e modify,create /var/log/    # only specific events (modify or create)
inotifywait -m -e modify /etc/nginx/nginx.conf  # watch a config file for changes

# Events: access, modify, create, delete, moved_to, moved_from, attrib, close_write

# One-shot: wait until file changes, then run a command
inotifywait -e modify /var/log/app.log && echo "file changed"

# Watch for config changes and reload on change:
inotifywait -m -e close_write /etc/myapp/config.yml | while read; do
  systemctl reload myapp
done
```

---

## lsof — finding locked and open log files

```bash
# A deleted log file that's still held open by a process doesn't free disk space
# This is a common cause of "no space left on device" even after deleting log files

lsof | grep deleted                    # find all deleted files still held open
lsof +D /var/log                       # list all files open inside /var/log
fuser /var/log/app.log                 # show PIDs using this exact file

# Scenario: deleted nginx access.log but disk didn't free up
lsof | grep "access.log.*deleted"      # confirm nginx still holds it open
# Fix option 1: truncate the file (frees space without restart):
> /proc/<PID>/fd/<FD>                  # truncate the specific file descriptor
# Fix option 2: restart the service (closes the fd, file actually deleted):
systemctl restart nginx
# Fix option 3: send SIGHUP if service supports log reopen:
kill -HUP <PID>
```

---

## Real-time log timestamping

```bash
# Add timestamps to a command's output that doesn't include them natively

# Using 'ts' from the moreutils package:
./script.sh | ts '[%Y-%m-%d %H:%M:%S]'
command 2>&1 | ts '[%H:%M:%S]'         # timestamp both stdout and stderr

# Using awk (no extra packages needed):
./script.sh | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush() }'
# fflush() prevents output buffering — critical for live monitoring

# Timestamp lines as they arrive in a log file:
tail -f /var/log/app.log | ts '[%Y-%m-%d %H:%M:%S]'

# Write timestamped output to a file:
./script.sh | ts '[%Y-%m-%d %H:%M:%S]' >> /var/log/timestamped.log
```

---

## SLO error budget calculation from access logs

```bash
# SLO (Service Level Objective) example: 99.9% availability
# Error budget = 0.1% of requests can be errors in the measurement window

# Count errors and total requests from nginx access log:
# nginx log format: IP - - [date] "METHOD /path HTTP/1.1" STATUS size
total=$(wc -l < /var/log/nginx/access.log)
errors=$(awk '$9 >= 500' /var/log/nginx/access.log | wc -l)
echo "Total: $total, Errors: $errors"

# Calculate error rate with awk (one pass):
awk 'BEGIN{total=0; errors=0}
     {total++; if($9>=500) errors++}
     END{printf "Error rate: %.4f%%\nBudget remaining: %.4f%%\n",
         errors/total*100, 0.1 - errors/total*100}' \
  /var/log/nginx/access.log

# Filter to a specific time window first:
grep "26/Jun/2024:14:" /var/log/nginx/access.log | awk '$9>=500' | wc -l

# Count by status code:
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```
