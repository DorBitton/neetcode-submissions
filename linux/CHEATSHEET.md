# Linux Quick Reference

Jump to:
- [Navigation](#navigation)
- [Files](#files)
- [Viewing Content](#viewing-content)
- [Pipes & Filters](#pipes--filters)
- [Streams & Redirection](#streams--redirection)
- [Processes](#processes)
- [Users & Permissions](#users--permissions)
- [Links & Inodes](#links--inodes)
- [Scheduling](#scheduling)
- [Getting Help](#getting-help)
- [Flags Cheat Sheet](#flags-cheat-sheet)
- [TLS / Certificates](#tls--certificates)
- [I/O Priority](#io-priority)
- [lsof](#lsof)
- [Disk Quotas](#disk-quotas)
- [Network Namespaces](#network-namespaces)
- [conntrack](#conntrack)
- [inotifywait](#inotifywait)
- [Port & Socket Tuning](#port--socket-tuning)
- [User Sessions & Login History](#user-sessions--login-history)
- [Routing](#routing)
- [DNS](#dns)
- [tcpdump](#tcpdump)

---

## Navigation

```bash
pwd                  # print current directory (where am I?)
cd /path/to/dir      # go to absolute path
cd ..                # go up one level
cd ~                 # go to home directory
cd -                 # go back to previous directory
```

---

## Listing Files

```bash
ls                   # list files in current dir
ls -l                # long format (permissions, size, date)
ls -a                # show hidden files (starting with .)
ls -la               # long format + hidden
ls -lh               # human-readable sizes (KB, MB, GB)
ls -lt               # sort by modification time (newest first)
ls -lS               # sort by size (largest first)
ls /path             # list a specific directory
```

**Long format columns:**
```
-rw-r--r--  1  dor  staff  1234  Jun 10 12:00  file.txt
^           ^  ^    ^      ^     ^              ^
type+perms  links owner group  size   date       name
```

---

## Directories

```bash
mkdir dirname        # create directory
mkdir -p a/b/c       # create nested dirs (no error if exists)
rmdir dirname        # remove EMPTY directory
rm -r dirname        # remove directory and all its contents
```

---

## Files

```bash
touch file.txt       # create empty file (or update timestamp)
rm file.txt          # delete file
rm -f file.txt       # force delete (no confirmation)
rm -i file.txt       # interactive delete (asks before deleting)
cp src dst           # copy file
cp -r src/ dst/      # copy directory recursively
mv src dst           # move or rename
```

---

## Viewing Content

```bash
cat file.txt         # print entire file
less file.txt        # scroll through file (q to quit)
head file.txt        # first 10 lines
head -n 20 file.txt  # first 20 lines
tail file.txt        # last 10 lines
tail -n 20 file.txt  # last 20 lines
tail -f file.txt     # follow (live updates — great for logs)
```

---

## Pipes & Filters

The `|` takes the output of the left command and feeds it as input to the right command.

```bash
command1 | command2       # pipe output of cmd1 into cmd2

# Examples
ls -la | grep ".txt"      # filter ls output for .txt files
cat file.txt | wc -l      # count lines in a file
cat file.txt | sort       # sort lines
cat file.txt | sort | uniq  # sort and remove duplicates
ps aux | grep nginx       # find a running process by name
```

### Filter Commands

```bash
grep "pattern" file      # search for pattern in file
grep -i "pattern" file   # case insensitive
grep -r "pattern" dir/   # recursive search in directory
grep -n "pattern" file   # show line numbers

wc file.txt              # count lines, words, bytes
wc -l file.txt           # count lines only
wc -w file.txt           # count words only

sort file.txt            # sort lines alphabetically
sort -n file.txt         # sort numerically
sort -r file.txt         # reverse sort

uniq file.txt            # remove consecutive duplicate lines
sort file.txt | uniq     # remove all duplicate lines
```

---

## Streams & Redirection

```bash
# stdout (fd 1) — normal output
command > file.txt       # redirect stdout to file (overwrite)
command >> file.txt      # redirect stdout to file (append)

# stderr (fd 2) — error output
command 2> errors.txt    # redirect stderr to file
command 2>/dev/null      # discard errors

# both
command > out.txt 2>&1   # redirect both stdout and stderr to file

# stdin (fd 0) — input
command < file.txt       # use file as input instead of keyboard
```

**Rule of thumb:**
- `>` overwrites
- `>>` appends
- `/dev/null` is the trash can — anything sent there disappears

---

## Getting Help

```bash
man command          # full manual for a command
man ls               # manual for ls
man -k "keyword"     # search all manuals for a keyword

command --help       # short help summary (most commands)
command -h           # same (shorter alias, not universal)

whatis command       # one-line description
```

**Inside `man`:**
- `Space` or `f` — page down
- `b` — page up
- `/pattern` — search forward
- `n` — next match
- `q` — quit

---

## Processes

```bash
top                  # live view of processes (CPU/memory)
htop                 # improved top (if installed)
ps                   # your processes in current shell
ps aux               # all processes, all users, detailed

kill PID             # send SIGTERM to process (ask to stop)
kill -9 PID          # send SIGKILL (force stop)
pkill processname    # kill by name

jobs                 # list background jobs
bg %1                # resume job 1 in background
fg %1                # bring job 1 to foreground
Ctrl+Z               # suspend current process
Ctrl+C               # interrupt (kill) current process
```

---

## History & Aliases

```bash
history              # show command history
history | tail -20   # last 20 commands
!!                   # repeat last command
!n                   # repeat command number n
Ctrl+R               # interactive history search

alias ll='ls -la'    # create alias for this session
# To persist: add alias line to ~/.bashrc or ~/.zshrc
unalias ll           # remove alias
alias                # list all current aliases
```

---

## Users & Permissions

```bash
whoami               # current user
id                   # user ID, group ID, groups
groups               # groups current user belongs to

su username          # switch to another user
sudo command         # run command as root
sudo su              # become root

useradd username     # create user
usermod -aG group user  # add user to group
passwd username      # set/change password
```

### Permissions

```bash
chmod 755 file       # set permissions with octal
chmod u+x file       # add execute for owner
chmod go-w file      # remove write from group and others
chown user file      # change owner
chown user:group file  # change owner and group
```

**Octal table:**
```
7 = rwx    (read + write + execute)
6 = rw-    (read + write)
5 = r-x    (read + execute)
4 = r--    (read only)
0 = ---    (no permissions)

chmod 755 = rwxr-xr-x   owner:all  group:read+exec  others:read+exec
chmod 644 = rw-r--r--   owner:rw   group:read        others:read
chmod 600 = rw-------   owner:rw   group:none        others:none
```

**Permission string:** `-rwxr-xr-x`
```
- = file (d = directory, l = symlink)
rwx = owner permissions
r-x = group permissions
r-x = others permissions
```

---

## Files — Info & Search

```bash
file filename        # detect file type
stat filename        # full metadata (size, inode, timestamps)
du -sh dirname/      # disk usage of directory (human readable)
df -h                # disk space on all mounted filesystems
find . -name "*.txt"         # find files by name
find . -type f -name "*.log" # find only files
find . -mtime -7             # modified in last 7 days
```

---

## Links & Inodes

```bash
ls -i file           # show inode number
stat file            # shows inode + all metadata

ln target link       # hard link (same inode, same data)
ln -s target link    # soft/symbolic link (pointer to path)

# Hard link:  both names point to same data — deleting one keeps the other
# Soft link:  pointer to a path — if original is deleted, link breaks
```

---

## Scheduling (Crontab)

```bash
crontab -e           # edit your cron jobs
crontab -l           # list your cron jobs
crontab -r           # remove all your cron jobs
```

**Cron syntax:**
```
* * * * * command
│ │ │ │ │
│ │ │ │ └── day of week (0-7, 0=Sun)
│ │ │ └──── month (1-12)
│ │ └────── day of month (1-31)
│ └──────── hour (0-23)
└────────── minute (0-59)

Examples:
0 * * * *    run every hour (at minute 0)
*/5 * * * *  run every 5 minutes
0 9 * * 1    run at 9am every Monday
0 0 * * *    run at midnight every day
```

---

## Logs

```bash
journalctl           # all system logs (systemd)
journalctl -u nginx  # logs for a specific service
journalctl -f        # follow live logs
journalctl --since "1 hour ago"

tail -f /var/log/syslog       # follow syslog in real time
tail -f /var/log/auth.log     # authentication logs
ls /var/log/                  # see available log files
```

---

## Flags Cheat Sheet

| Flag | Meaning | Common With |
|---|---|---|
| `-r` / `-R` | recursive | `cp`, `rm`, `grep`, `chmod` |
| `-f` | force (no prompts) | `rm`, `cp`, `mv` |
| `-i` | interactive (ask before action) | `rm`, `cp`, `mv` |
| `-v` | verbose (show what's happening) | `cp`, `mv`, `rm`, `tar` |
| `-a` | all (including hidden) | `ls` |
| `-l` | long format | `ls` |
| `-h` | human-readable sizes | `ls`, `du`, `df` |
| `-n` | number of lines | `head`, `tail` |
| `-n` | numeric sort | `sort` |
| `-p` | create parents, no error if exists | `mkdir` |
| `-s` | symbolic link | `ln` |
| `-e` | edit | `crontab` |

---

## TLS / Certificates

```bash
# Inspect a certificate
openssl x509 -in cert.pem -text -noout          # full details
openssl x509 -in cert.pem -noout -dates         # expiry only
openssl x509 -in cert.pem -noout -subject       # CN + SANs

# Check a live server
openssl s_client -connect example.com:443       # TLS handshake
openssl s_client -connect example.com:443 -showcerts  # full chain
echo | openssl s_client -connect host:443 2>/dev/null | openssl x509 -noout -dates

# Generate key + CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr

# Self-signed cert
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# Fix chain
cat server.crt intermediate.crt > fullchain.pem
openssl verify -CAfile ca-bundle.crt fullchain.pem

# Key permissions
chmod 600 server.key
```

---

## I/O Priority

```bash
ionice -c 3 -p <PID>             # set to idle I/O class (lowest — gets disk only when nothing else needs it)
ionice -c 2 -n 7 -p <PID>       # best-effort, lowest within class
ionice -c 1 -n 0 -p <PID>       # realtime (highest, root only)
ionice -c 3 ./backup.sh          # start a new command at idle I/O priority

iotop                            # live I/O monitor (like top for disk)
iotop -o                         # show only processes with active I/O
iotop -b -n 5                    # non-interactive, 5 snapshots
```

---

## lsof

```bash
lsof -p <PID>                    # all files open by a process
lsof +D /var/log                 # what has files open in this directory?
lsof | grep deleted              # files deleted but still held open (disk leak)
lsof -i :80                      # what process has port 80 open?
ls /proc/<PID>/fd | wc -l       # count open file descriptors for a process
```

---

## Disk Quotas

```bash
quota -u username                # check quota for a user
repquota -a                      # quota report for all users
edquota -u username              # edit user's quota limits
quotaon /home                    # enable quotas on filesystem
quotacheck -cug /home            # create quota database (first-time setup)
# fstab needs: UUID=xxx /home ext4 defaults,usrquota,grpquota 0 2
```

---

## Network Namespaces

```bash
ip netns list                    # list namespaces
ip netns add myns                # create namespace
ip netns exec myns ip link list  # run command inside namespace
ip netns del myns                # delete namespace

# Connect two namespaces with veth pair:
ip link add veth0 type veth peer name veth1
ip link set veth1 netns myns
ip addr add 192.168.100.1/24 dev veth0
ip netns exec myns ip addr add 192.168.100.2/24 dev veth1
```

---

## conntrack

```bash
conntrack -L                     # list all tracked connections
conntrack -L | grep ESTABLISHED | wc -l  # count established
cat /proc/sys/net/netfilter/nf_conntrack_count  # current tracked connections
cat /proc/sys/net/netfilter/nf_conntrack_max    # limit
sysctl -w net.netfilter.nf_conntrack_max=131072  # raise limit
```

---

## inotifywait

```bash
inotifywait -m /var/log/app.log              # watch one file
inotifywait -m -r /var/log/                  # recursive directory watch
inotifywait -m -e modify,create /etc/nginx/  # specific events only
inotifywait -e modify file && echo "changed" # one-shot: wait then continue
```

---

## Port & Socket Tuning

```bash
cat /proc/sys/net/ipv4/ip_local_port_range   # current ephemeral port range
sysctl -w net.ipv4.ip_local_port_range="10000 65000"  # widen range

sysctl -w net.ipv4.tcp_fin_timeout=15        # reduce TIME_WAIT hold time
sysctl -w net.ipv4.tcp_tw_reuse=1            # reuse TIME_WAIT sockets

sysctl -w net.ipv4.tcp_syncookies=1          # enable SYN cookie defense

ss -tan | grep TIME-WAIT | wc -l             # count TIME_WAIT sockets
ss -tan state syn-recv | wc -l              # count half-open (SYN flood indicator)
```

---

## User Sessions & Login History

```bash
who                              # who is logged in
w                                # who + what they're doing
last                             # login history (all users)
last reboot                      # reboot history
lastlog                          # last login for every user

loginctl list-sessions           # active sessions (systemd)
loginctl terminate-session <ID>  # kill a session
loginctl terminate-user <user>   # kill all sessions for a user
pkill -u <username>              # kill all processes owned by user
```

---

## Routing

```bash
ip route show                    # routing table
ip route get 8.8.8.8            # which route handles this destination?
ip route add 10.0.0.0/16 via 192.168.1.1   # add route
ip route add default via 192.168.1.1        # set default gateway
ip route del 10.0.0.0/16        # delete route
```

---

## DNS

```bash
dig example.com                  # A record lookup
dig example.com MX               # mail records
dig -x 8.8.8.8                   # reverse lookup (PTR)
dig @8.8.8.8 example.com        # query specific DNS server
dig +short example.com           # just the IP
dig +trace example.com           # full resolution chain from root
dig @<primary> example.com AXFR  # zone transfer test

cat /etc/resolv.conf             # DNS server config
cat /etc/nsswitch.conf | grep hosts  # resolution order
getent hosts example.com         # effective resolution (hosts + DNS)
```

---

## tcpdump

```bash
tcpdump -i eth0 port 80          # capture HTTP on eth0
tcpdump -i any port 80 -A        # any interface, print ASCII (readable HTTP)
tcpdump -i eth0 'tcp port 80 and host 10.0.0.5'  # filter by host + port
tcpdump -w capture.pcap -i eth0  # write to file (open in Wireshark)
tcpdump -nn -c 50 port 80        # no DNS resolution, capture 50 packets
```
