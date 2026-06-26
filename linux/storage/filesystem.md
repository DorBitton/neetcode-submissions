# Filesystem — Navigation, Files & Directories

> Covers lessons 1, 3, 4 (completed) and 6, 17 (coming up)

---

## Table of Contents

1. [How the Linux Filesystem is Structured](#1-how-the-linux-filesystem-is-structured)
2. [Navigating](#2-navigating)
3. [Listing Files — ls](#3-listing-files--ls)
4. [Creating & Deleting Directories](#4-creating--deleting-directories)
5. [Creating & Deleting Files](#5-creating--deleting-files)
6. [Copying & Moving](#6-copying--moving)
7. [Reading Files](#7-reading-files)
8. [File Metadata & Search](#8-file-metadata--search)

---

## 1. How the Linux Filesystem is Structured

Everything in Linux is a file (including directories, devices, and network sockets).
The filesystem is one big tree that starts at `/` (root).

```
/                    ← root (top of everything)
├── bin/             ← essential command binaries (ls, cp, etc.)
├── etc/             ← system-wide config files
├── home/            ← user home directories
│   └── dor/         ← your home (~)
├── var/             ← variable data (logs, caches)
│   └── log/         ← log files
├── tmp/             ← temporary files (cleared on reboot)
├── usr/             ← user programs and data
└── proc/            ← virtual filesystem — kernel/process info
```

**Key paths to know:**
| Path | What's there |
|---|---|
| `/` | root of the entire filesystem |
| `~` | your home directory (`/home/yourname`) |
| `.` | current directory |
| `..` | parent directory |
| `/etc` | config files for the system |
| `/var/log` | log files |
| `/tmp` | temp files, wiped on reboot |

---

## 2. Navigating

```bash
pwd         # print working directory — tells you where you are
cd /etc     # go to absolute path (starts from /)
cd logs     # go to relative path (relative to current dir)
cd ..       # go up one level
cd ~        # go home
cd -        # go back to previous location (toggle)
```

**Absolute vs relative:**
```
/home/dor/projects/code.py   ← absolute path (starts with /)
../projects/code.py          ← relative path (starts with . or ..)
projects/code.py             ← relative from current dir
```

---

## 3. Listing Files — ls

```bash
ls               # names only
ls -l            # long format (permissions, owner, size, date)
ls -a            # all files including hidden (dot files)
ls -la           # both — most useful combo
ls -lh           # human-readable sizes
ls -lt           # sorted by time (newest first)
ls -lS           # sorted by size (largest first)
ls /etc          # list a different directory
```

### Reading the long format

```
drwxr-xr-x  2  dor  staff  4096  Jun 10 09:00  projects/
-rw-r--r--  1  dor  staff   512  Jun 10 09:01  notes.txt
lrwxrwxrwx  1  dor  staff    11  Jun 10 09:02  link -> notes.txt
```

| Column | Meaning |
|---|---|
| `d`/`-`/`l` | type: directory / file / symlink |
| `rwxr-xr-x` | permissions (owner, group, others) |
| `2` | hard link count |
| `dor` | owner |
| `staff` | group |
| `4096` | size in bytes |
| `Jun 10 09:00` | last modified |
| `projects/` | name |

### Hidden files

Any file or directory whose name starts with `.` is hidden from `ls` by default.

```bash
ls -a ~          # see all files in your home dir
# You'll see: .bashrc  .zshrc  .gitconfig  .ssh/  etc.
```

---

## 4. Creating & Deleting Directories

```bash
mkdir mydir               # create a directory
mkdir -p a/b/c            # create nested dirs in one command
rmdir mydir               # delete EMPTY directory (fails if not empty)
rm -r mydir               # delete directory and everything inside
rm -rf mydir              # force delete — no confirmation, no errors
                          # ⚠️ dangerous — double-check before using
```

**Why `mkdir -p`?** Without `-p`, if `a/` doesn't exist yet, `mkdir a/b/c` fails.
With `-p` it creates each level as needed, and doesn't error if the dir already exists.

---

## 5. Creating & Deleting Files

```bash
touch file.txt            # create empty file
                          # if file exists: just updates its timestamp
rm file.txt               # delete file
rm -f file.txt            # force delete (no error if file doesn't exist)
rm -i file.txt            # interactive — asks "remove file.txt? [y/N]"
```

**`touch` is also used to:** update the "last modified" timestamp of an existing file
without changing its content. Useful in scripts that check file modification times.

```bash
rm *.log                  # delete all .log files in current dir
rm -r logs/ *.tmp         # remove directory AND temp files
```

---

## 6. Copying & Moving

```bash
cp source dest            # copy file
cp -r source/ dest/       # copy directory recursively
cp -v source dest         # verbose — prints what it's copying
cp -i source dest         # interactive — ask before overwriting

mv source dest            # move file or directory
mv oldname newname        # rename (mv to same dir with new name)
mv -i source dest         # interactive — ask before overwriting
```

**Move vs Rename:** `mv` does both. Moving to a different path = move.
Moving to the same directory with a new name = rename.

```bash
mv file.txt /tmp/         # move to /tmp/
mv file.txt newname.txt   # rename
mv dir/ /tmp/             # move entire directory
```

---

## 7. Reading Files

```bash
cat file.txt              # print entire file to terminal
cat -n file.txt           # with line numbers

less file.txt             # paginated viewer (recommended for large files)
# inside less:
#   Space / f   → page down
#   b           → page up
#   /pattern    → search
#   n           → next match
#   q           → quit

head file.txt             # first 10 lines
head -n 5 file.txt        # first 5 lines
tail file.txt             # last 10 lines
tail -n 5 file.txt        # last 5 lines
tail -f file.txt          # follow — shows new lines as they appear (great for logs)
```

**When to use what:**
| Command | Use when |
|---|---|
| `cat` | file is short, you want to see all of it |
| `less` | file is large, you want to scroll |
| `head` | you only care about the beginning |
| `tail` | you only care about the end |
| `tail -f` | watching a file that's actively being written (logs) |

---

## 8. File Metadata & Search

```bash
file filename             # detect actual file type (not just extension)
stat filename             # full metadata: size, inode, permissions, timestamps
du -sh dirname/           # total disk usage of a directory
du -sh *                  # disk usage of everything in current dir
df -h                     # free disk space on all filesystems
```

```bash
# find — search for files by attributes
find . -name "*.txt"              # by name (in current dir and below)
find /home -name "config*"        # by name, starting at /home
find . -type f                    # only files (not directories)
find . -type d                    # only directories
find . -mtime -7                  # modified in last 7 days
find . -size +1M                  # larger than 1 MB
find . -name "*.log" -delete      # find AND delete
```

**`stat` output explained:**
```
  File: notes.txt
  Size: 512         Blocks: 8    IO Block: 4096  regular file
Device: 10302h      Inode: 1234567  Links: 1
Access: (0644/-rw-r--r--)  Uid: (1000/dor)   Gid: (1000/staff)
Modify: 2024-06-10 09:01:00  ← last content change
Change: 2024-06-10 09:01:05  ← last metadata change
 Birth: 2024-06-10 09:00:00
```
