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
