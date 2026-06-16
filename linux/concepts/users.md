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

### What is an inode?

Every file is stored in two parts:
1. **The data** — actual content on disk
2. **The inode** — metadata: size, permissions, timestamps, owner, where data blocks are

The filename is just a **directory entry** pointing to an inode.
The inode doesn't store the filename — the directory does.

```bash
ls -i file.txt          # show inode number
stat file.txt           # full inode info
```

### Hard links

A hard link is another directory entry pointing to the **same inode**.

```bash
ln original.txt hardlink.txt     # create hard link
ls -i original.txt hardlink.txt  # same inode number!
```

```
directory entry "original.txt" ─┐
                                  ├→ inode 1234 → data on disk
directory entry "hardlink.txt" ─┘
```

- Deleting `original.txt` does NOT delete the data — inode still has a reference from `hardlink.txt`
- Hard links can't cross filesystems
- Hard links can't point to directories

### Soft (symbolic) links

A soft link is a file that contains a **path** pointing to another file.

```bash
ln -s /path/to/original link.txt   # create symbolic link
ls -la link.txt                     # shows link.txt -> /path/to/original
```

```
directory entry "link.txt" → inode 5678 → "/path/to/original"
                                                      ↓
directory entry "original.txt" → inode 1234 → data on disk
```

- If `original.txt` is deleted, the link is **broken** (dangling symlink)
- Soft links can cross filesystems
- Soft links can point to directories

### Hard vs Soft comparison

| | Hard link | Soft link |
|---|---|---|
| Same inode | Yes | No |
| Survives original deletion | Yes | No |
| Cross filesystem | No | Yes |
| Can link to directory | No | Yes |
| `ls -la` shows it as | regular file | `link -> target` |
