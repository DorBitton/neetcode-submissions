# Backup and Restore

> tar for archiving, rsync for syncing. The two tools SREs use for backups.

---

## tar — create and extract archives

tar (Tape ARchive) bundles files into one archive, optionally compressed.

### Creating archives
```bash
tar -czf backup.tar.gz /var/www/html        # create compressed archive (.tar.gz)
tar -cjf backup.tar.bz2 /var/www/html       # create with bzip2 compression (smaller, slower)
tar -cf backup.tar /var/www/html            # create without compression

# Flag breakdown:
# -c  create
# -z  gzip compression (.tar.gz)
# -j  bzip2 compression (.tar.bz2)
# -f  filename (always last, immediately before the filename)
# -v  verbose (show files as they're added)
```

### Extracting archives
```bash
tar -xzf backup.tar.gz                     # extract in current directory
tar -xzf backup.tar.gz -C /restore/path    # extract to specific directory
tar -xzf backup.tar.gz var/www/html/index.html  # extract single file

# Flag breakdown:
# -x  extract
# -z  decompress gzip
# -f  filename
# -C  change to directory before extracting
```

### Inspecting archives (without extracting)
```bash
tar -tzf backup.tar.gz                     # list contents
tar -tzf backup.tar.gz | grep "index"      # find specific file in archive
```

**Always verify a backup after creating it:**
```bash
tar -tzf backup.tar.gz > /dev/null && echo "OK" || echo "CORRUPT"
```

### Common tar issues
```bash
# "Cannot open: No such file or directory"
# → wrong path in the tar command, or archive was moved

# "Unexpected EOF in archive" / "Error is not recoverable"
# → archive is corrupted. Check: was the disk full when creating it?

# Extract only specific files
tar -xzf backup.tar.gz --wildcards '*.conf'    # extract all .conf files
```

---

## rsync — sync files between locations

rsync copies only what changed. It's faster than tar for incremental backups and syncing live data.

```bash
rsync -av /source/ /destination/                    # local sync, verbose
rsync -av /var/www/ user@remote:/var/www/           # sync to remote server
rsync -av user@remote:/var/www/ /local/backup/      # pull from remote

# Common flags:
# -a  archive mode (preserves permissions, timestamps, symlinks, etc.)
# -v  verbose
# -z  compress during transfer (good for slow links)
# -n  dry run (show what would be transferred, don't do it)
# --delete  delete files in destination that no longer exist in source
# --exclude  skip certain files/directories
# -P  show progress + allow resume of interrupted transfers
```

**Dry run first — always:**
```bash
rsync -avn /source/ /destination/      # -n = dry run, shows what would change
# Review output, then run without -n
```

**Sync with deletion (mirror):**
```bash
rsync -av --delete /source/ /destination/
# WARNING: files in /destination/ not in /source/ are DELETED
```

**Exclude files:**
```bash
rsync -av --exclude='*.log' --exclude='.git' /source/ /destination/
rsync -av --exclude-from='exclude.txt' /source/ /destination/
```

**Partial/resume interrupted transfer:**
```bash
rsync -avP /large/file user@remote:/backup/   # -P = --partial --progress
```

---

## Backup strategies

**Full backup:** copy everything. Simple, takes most space and time.
```bash
tar -czf full-$(date +%Y%m%d).tar.gz /var/www/
```

**Incremental with rsync:** only sync changes, keep old versions with `--backup`:
```bash
rsync -av --backup --backup-dir=/backup/$(date +%Y%m%d) /source/ /latest/
```

**Rotation — keep last 7 days:**
```bash
find /backup/ -name "*.tar.gz" -mtime +7 -delete
```

---

## Verifying and restoring

**Before restoring, always verify the archive:**
```bash
tar -tzf backup.tar.gz > /dev/null     # can we read the index?
tar -xzf backup.tar.gz --to-stdout | head -c 1000   # can we read the data?
```

**Test restore to a different path first:**
```bash
mkdir /tmp/restore-test
tar -xzf backup.tar.gz -C /tmp/restore-test
ls -la /tmp/restore-test               # verify files are there
```

**Restore to original location:**
```bash
systemctl stop nginx                   # stop the service first
tar -xzf backup.tar.gz -C /            # restore (overwrites existing files)
systemctl start nginx
```

---

## Troubleshooting

**"No space left on device" during backup:**
```bash
df -h                   # which filesystem is full?
# Options: compress more, clean up old backups, add storage
find /backup -name "*.tar.gz" -mtime +30 -delete   # delete old backups
```

**Corrupted archive:**
```bash
tar -tzf backup.tar.gz  # will error with details
# Common causes: disk full during write, network interruption, disk failure
# Prevention: verify immediately after creation
```

**rsync "permission denied":**
```bash
# Source files aren't readable by the running user
ls -la /source/
sudo rsync -av /source/ /destination/   # run as root if needed
```

**rsync "connection refused" to remote:**
```bash
ssh user@remote                         # test SSH first — rsync uses SSH
# Check: sshd running? firewall allows port 22? correct username?
```
