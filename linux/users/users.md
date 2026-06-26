# Users, Groups, Permissions & Privileges

> Covers lessons 11, 13, 20 — fill in as you complete them

---

## Table of Contents

1. [Users & Groups](#1-users--groups)
2. [Switching Users — su & sudo](#2-switching-users--su--sudo)
3. [Managing Users](#3-managing-users)
4. [Permissions](#4-permissions)
5. [chmod — Change Permissions](#5-chmod--change-permissions)
6. [chown & chgrp — Change Ownership](#6-chown--chgrp--change-ownership)
7. [Inodes & Links](#7-inodes--links)

---

## 1. Users & Groups

Every file and every process is owned by a **user** and a **group**.
Permissions are checked in order: owner → group → others.

```bash
whoami               # print current username
id                   # your UID, GID, and all groups
id username          # info about another user
groups               # groups you belong to
groups username      # groups another user belongs to
```

```bash
# Example output of id:
uid=1000(dor) gid=1000(dor) groups=1000(dor),4(adm),27(sudo),1001(docker)
#    ^user ID     ^primary group    ^all groups you belong to
```

**Key files:**
| File | Content |
|---|---|
| `/etc/passwd` | list of all users (username, UID, home dir, shell) |
| `/etc/shadow` | hashed passwords (only root can read) |
| `/etc/group` | list of all groups and their members |

```bash
cat /etc/passwd | cut -d: -f1    # list all usernames
```

---

## 2. Switching Users — su & sudo

### sudo — run a single command as root

```bash
sudo command          # run command as root
sudo apt update       # typical use: system administration
sudo -u otheruser command   # run as a specific user
sudo !!               # re-run last command with sudo
```

`sudo` uses your own password and checks `/etc/sudoers` to verify you have permission.
Root access is logged.

### su — switch to another user

```bash
su username          # switch to user (keeps current environment)
su - username        # switch user AND load their environment
su                   # switch to root (requires root password)
sudo su              # become root using your sudo password
exit                 # return to your original user
```

**`su` vs `su -`:**
- `su username` — becomes that user but keeps your environment variables
- `su - username` — full login: loads their `$PATH`, `$HOME`, shell config

### /etc/sudoers

Controls who can use `sudo` and for what.
Edit with `visudo` (not directly) — it validates syntax before saving.

```bash
sudo visudo          # safe way to edit sudoers
```

```
# Example sudoers entries:
dor  ALL=(ALL:ALL) ALL          # dor can run anything as anyone
dor  ALL=(ALL) NOPASSWD: ALL    # without password (careful!)
%sudo  ALL=(ALL:ALL) ALL        # everyone in 'sudo' group
```

---

## 3. Managing Users

```bash
useradd username          # create user (minimal setup)
useradd -m username       # create user WITH home directory
useradd -m -s /bin/bash username   # with home dir and bash shell
adduser username          # interactive version (friendlier, Debian/Ubuntu)

passwd username           # set or change password
usermod -aG group user    # add user to a group (-a = append, -G = groups)
usermod -s /bin/bash user # change login shell
userdel username          # delete user (keep home dir)
userdel -r username       # delete user AND their home directory

# Examples:
useradd -m -s /bin/bash alice      # create alice with home and bash
usermod -aG docker alice           # add alice to docker group
usermod -aG sudo alice             # give alice sudo access
passwd alice                        # set alice's password
```

---

## 4. Permissions

Every file has three sets of permissions: **owner**, **group**, **others**.

```
-rwxr-xr-x  1  dor  staff  4096  Jun 10  script.sh
^            ^  ^    ^
│            │  │    └── group
│            │  └───── owner
│            └──────── link count
└─────────────────── type + permissions
```

### The permission string

```
- r w x r - x r - x
│ │ │ │ │ │ │ │ │ │
│ ╰─┴─╯ ╰─┴─╯ ╰─┴─╯
│  owner group others
└── type: - file  d directory  l symlink
```

| Letter | Permission | On files | On directories |
|---|---|---|---|
| `r` | read | read file content | list directory contents (`ls`) |
| `w` | write | modify file | create/delete files inside |
| `x` | execute | run as program | enter directory (`cd`) |
| `-` | denied | — | — |

---

## 5. chmod — Change Permissions

### Octal notation

```bash
chmod 755 file.sh       # rwxr-xr-x
chmod 644 file.txt      # rw-r--r--
chmod 600 secret.txt    # rw-------
chmod 777 file          # rwxrwxrwx (everyone can do everything)
```

**Octal to permissions:**
```
4 = r (read)
2 = w (write)
1 = x (execute)

7 = 4+2+1 = rwx
6 = 4+2   = rw-
5 = 4+1   = r-x
4 = 4     = r--
0 =       = ---
```

**Most common values:**
| Octal | String | Use case |
|---|---|---|
| `755` | `rwxr-xr-x` | scripts, directories |
| `644` | `rw-r--r--` | regular files |
| `600` | `rw-------` | private files (SSH keys) |
| `700` | `rwx------` | private directories |
| `777` | `rwxrwxrwx` | avoid — insecure |

### Symbolic notation

```bash
chmod u+x file       # add execute to owner (u=user/owner)
chmod g-w file       # remove write from group
chmod o-r file       # remove read from others
chmod a+r file       # add read for all (a = all: u+g+o)
chmod u+x,g-w file   # multiple changes at once
chmod -R 755 dir/    # recursive — apply to dir and all contents
```

---

## 6. chown & chgrp — Change Ownership

```bash
chown user file             # change owner
chown user:group file       # change owner and group
chown :group file           # change only group
chown -R user:group dir/    # recursive — change all files inside
chgrp group file            # change group only
```

```bash
# Examples:
chown dor script.sh             # give ownership to dor
chown dor:staff script.sh       # dor owns it, staff group
chown -R www-data /var/www/     # web server owns the web root
```

---

## 7. Inodes & Links

| | Hard link | Soft link |
|---|---|---|
| Same inode | Yes | No |
| Survives original deletion | Yes | No |
| Cross filesystem | No | Yes |
| Can link to directory | No | Yes |

```bash
ln original.txt hardlink.txt      # hard link — same inode, same data
ln -s /path/to/original link.txt  # soft link — pointer to a path
ls -i file                        # show inode number
stat file                         # full inode metadata
```

---

## 8. User Session Cleanup

```bash
who                                    # who is currently logged in and from where
w                                      # who + what command they're running
last | head -20                        # recent login history

# Terminate sessions:
loginctl list-sessions                 # list all active sessions with session IDs
loginctl terminate-session <ID>        # kill a specific session
loginctl terminate-user <username>     # kill all sessions for a user

pkill -u <username>                    # kill all processes owned by a user
pkill -9 -u <username>                 # force kill (if graceful didn't work)

# Check if a user is still logged in after killing their processes:
who | grep <username>
```

---

## 9. Detect Login Time Violations

```bash
last                                   # login/logout history (from /var/log/wtmp)
last username                          # history for one specific user
last -n 20                             # last 20 entries
last reboot                            # system reboot history

lastlog                                # last login for EVERY user (from /var/log/lastlog)
lastlog -u username                    # last login for one user
lastlog | grep "Never logged in"       # accounts that have never been used

# Find logins outside business hours (rough):
last | awk '{print $1, $4, $5, $6, $7}' | grep -v "^$\|wtmp\|reboot"
# Column 4 = day, column 5 = month, column 6 = date, column 7 = time
# Look for weekend days (Sat, Sun) or odd hours (00:, 01:, 02:, 03:)

# PAM time restrictions (enforce login hours):
# /etc/security/time.conf
# *;*;username;Al0800-1800   # allow only 8am-6pm
```

---

## 10. Create Non-Interactive System User

```bash
# System users: run services, have no login shell, no interactive access
useradd -r -s /sbin/nologin appuser              # -r = system (low UID), no login shell
useradd -r -s /sbin/nologin -d /var/lib/myapp appuser  # with home dir for app data
useradd -r -s /bin/false appuser                 # /bin/false also prevents login

# Verify non-interactive:
su - appuser       # should print: "This account is currently not available"
grep appuser /etc/passwd   # shell field should be /sbin/nologin or /bin/false

# Common pattern for a service:
useradd -r -s /sbin/nologin -d /opt/myapp myapp
chown -R myapp:myapp /opt/myapp        # service owns its own directory
```

---

## 11. Find Files Owned by Non-Existent Users

```bash
# Files with no valid UID (owner was deleted, or UID mismatch after migration)
find / -nouser 2>/dev/null             # files with no matching UID
find / -nogroup 2>/dev/null            # files with no matching GID
find / -nouser -o -nogroup 2>/dev/null # either condition

# Restrict to specific filesystems (faster, avoids /proc /sys):
find /home /var /opt -nouser 2>/dev/null

# Take action: reassign ownership
find / -nouser 2>/dev/null -exec chown root:root {} \;

# After a user migration: find files that still belong to old UID numbers
find / -uid 1005 2>/dev/null           # files owned by UID 1005 (even if user is gone)
```

---

## 12. Credential Leak Detection

```bash
# Search config files for hardcoded credentials:
grep -rE "password\s*=" /etc/ 2>/dev/null
grep -rE "(password|passwd|secret|api_key|apikey|token|credential)\s*[=:]" \
  /home/ /opt/ /var/www/ --include="*.conf" --include="*.yaml" --include="*.env" 2>/dev/null

# Find sensitive file types:
find / -name ".env" 2>/dev/null        # .env files (common secret store)
find / -name "*.pem" 2>/dev/null       # private keys
find / -name "id_rsa" 2>/dev/null      # SSH private keys
find / -name "credentials" 2>/dev/null # AWS/cloud credentials

# Check world-readable sensitive files (should NOT be world-readable):
find /etc -name "*.conf" -perm -o+r 2>/dev/null | head -20

# Check git history for accidentally committed secrets:
git log -p | grep -iE "(password|secret|api_key|token)" | head -30
# Or use git-secrets / truffleHog for thorough scanning
```
