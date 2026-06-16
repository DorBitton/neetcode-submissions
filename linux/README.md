# Linux Notes

## Start Here

> **Open [`CHEATSHEET.md`](./CHEATSHEET.md) when you need a command fast.**
> Use the `concepts/` files to understand the *why* behind commands.

---

## Lesson Progress

| # | Lesson | Status | Concepts |
|---|--------|--------|---------|
| 1 | List files | ✅ | `ls`, flags, hidden files |
| 2 | Your best friend — man | ✅ | `man`, `--help`, searching manual |
| 3 | Work with directories | ✅ | `pwd`, `cd`, `mkdir`, `rmdir` |
| 4 | Create and delete files | ✅ | `touch`, `rm`, `cp`, `mv` |
| 5 | Pipes | ✅ | `\|`, `head`, `tail`, `grep`, `wc` |
| 6 | Reading the file | ⬜ | `cat`, `less`, `more`, `nano`, `vi` |
| 7 | Copy and move files | ⬜ | `cp -r`, `mv`, renaming |
| 8 | The top command | ⬜ | `top`, `htop`, system monitoring |
| 9 | The ps command | ⬜ | `ps`, `ps aux`, process listing |
| 10 | Create aliases | ⬜ | `alias`, `.bashrc`, `.zshrc` |
| 11 | Work with users | ⬜ | `useradd`, `usermod`, `passwd`, `groups` |
| 12 | Your work history | ⬜ | `history`, `!!`, `!n`, Ctrl+R |
| 13 | Elevate privileges | ⬜ | `sudo`, `su`, `/etc/sudoers` |
| 14 | Work with logs | ⬜ | `journalctl`, `/var/log/`, `tail -f` |
| 15 | Streams | ⬜ | stdin/stdout/stderr, `>`, `>>`, `2>` |
| 16 | Crontab | ⬜ | `crontab -e`, cron syntax, scheduling |
| 17 | Know your files | ⬜ | `file`, `stat`, `du`, `df`, `find` |
| 18 | Soft and hard links | ⬜ | `ln`, `ln -s`, inode sharing |
| 19 | Inodes | ⬜ | what an inode is, `ls -i`, `stat` |
| 20 | Permissions | ⬜ | `chmod`, `chown`, `chgrp`, octal notation |
| — | Test your knowledge | ⬜ | — |

---

## File Map

### Reference (open while working)

| File | What's in it |
|---|---|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | Every command, flag, and example on one page |

### Deep-Dive Concepts (read to understand)

| File | Lessons | What's in it |
|---|---|---|
| [`concepts/filesystem.md`](./concepts/filesystem.md) | 1, 3, 4, 6, 17 | Navigating, listing, creating, deleting files and dirs |
| [`concepts/streams.md`](./concepts/streams.md) | 5, 15 | Pipes, stdin/stdout/stderr, redirections |
| [`concepts/processes.md`](./concepts/processes.md) | 8, 9, 16 | top, ps, cron, process management |
| [`concepts/users.md`](./concepts/users.md) | 11, 13, 20 | Users, groups, sudo, permissions |

### Interview Prep

| File | What's in it |
|---|---|
| [`interview-questions.md`](./interview-questions.md) | 25 common Linux interview questions with answers |
