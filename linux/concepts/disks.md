# Disks and Filesystems

> Inspecting, partitioning, mounting, and managing storage in Linux.

---

## The mental model

```
Physical disk (sda, sdb, nvme0n1)
  └── Partition (sda1, sda2)
        └── Filesystem (ext4, xfs, btrfs)
              └── Mount point (/mnt/data, /var, /)
```

Linux doesn't use drive letters (C:, D:). Everything is attached somewhere in one directory tree via **mounting**.

---

## Inspecting disks

```bash
lsblk                       # list block devices — disks and partitions (tree view)
lsblk -f                    # also show filesystem type and UUID
fdisk -l                    # detailed partition table (needs root)
fdisk -l /dev/sdb           # specific disk only
blkid                       # show UUIDs and filesystem types for all devices
```

**lsblk output:**
```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0   20G  0 disk
├─sda1   8:1    0   19G  0 part /
└─sda2   8:2    0    1G  0 part [SWAP]
sdb      8:16   0   10G  0 disk          ← unmounted disk
```

---

## Checking disk space

```bash
df -h                       # disk space by filesystem (human readable)
df -h /var                  # space for a specific path
du -sh /var/log             # how much space a directory uses
du -sh /var/log/*           # size of each item inside
du -sh /* 2>/dev/null       # top-level space usage (find the big one)
```

**df output:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        19G   15G  3.2G  83% /
tmpfs           1.9G     0  1.9G   0% /dev/shm
```

**Disk full investigation:**
```bash
df -h                           # 1. which filesystem is full?
du -sh /var/log/* | sort -rh    # 2. what's taking space?
ls -lh /var/log/nginx/          # 3. look at the big files
```

---

## Mounting and unmounting

```bash
# Mount a device
mount /dev/sdb1 /mnt/data          # mount partition to directory
mount -t ext4 /dev/sdb1 /mnt/data  # explicit filesystem type
mount -o ro /dev/sdb1 /mnt/data    # mount read-only

# Unmount
umount /mnt/data                   # unmount by mount point
umount /dev/sdb1                   # unmount by device
umount -l /mnt/data                # lazy umount (when "device is busy")

# See what's currently mounted
mount | grep sdb                   # filter for a specific device
findmnt                            # tree view of all mounts
```

**"device is busy" when unmounting:**
```bash
lsof /mnt/data                     # what processes have files open there?
fuser -m /mnt/data                 # which PIDs are using the mount?
# Kill the process, then umount
```

---

## Creating a filesystem

```bash
mkfs.ext4 /dev/sdb1               # format as ext4
mkfs.xfs /dev/sdb1                # format as xfs
mkfs.ext4 -L "mydata" /dev/sdb1   # with a label
```

**Warning:** `mkfs` destroys all existing data on the partition.

---

## /etc/fstab — persistent mounts

Without fstab, mounts don't survive a reboot. fstab defines what gets mounted at boot.

```
# /etc/fstab
# Device            Mount point   FS type  Options        dump pass
UUID=abc123-...     /mnt/data     ext4     defaults       0    2
/dev/sdb1           /mnt/backup   xfs      defaults,ro    0    0
```

**Use UUID, not /dev/sdb** — device names can change after reboot if disks are added/removed. UUIDs are stable.

```bash
blkid /dev/sdb1     # get the UUID to put in fstab
```

**Test fstab before rebooting:**
```bash
mount -a            # mount everything in fstab that isn't already mounted
                    # if this errors, fix it before rebooting
```

**Bad fstab = system won't boot.** Always test with `mount -a` first.

---

## Swap

```bash
swapon --show               # is swap enabled? how much?
free -h                     # memory + swap usage
swapoff /dev/sda2           # disable swap
swapon /dev/sda2            # enable swap
```

---

## Troubleshooting scenarios

**Disk shows up in lsblk but nothing is there:**
```bash
lsblk -f /dev/sdb           # does it have a filesystem?
# If not: mkfs.ext4 /dev/sdb1 (after partitioning if needed)
# If yes: mount it
```

**Application can't write files — "no space left on device":**
```bash
df -h                       # is a filesystem 100%?
du -sh /var/log/* | sort -rh  # find what's filling it
# Options: delete old files, extend the volume, add another disk
```

**Can't unmount — "target is busy":**
```bash
lsof /mnt/data              # find the process
kill <PID>                  # or:
umount -l /mnt/data         # lazy unmount
```

**Mount survives current session but not reboot:**
```bash
# Add to /etc/fstab using UUID
blkid /dev/sdb1             # get UUID
echo "UUID=xxx /mnt/data ext4 defaults 0 2" >> /etc/fstab
mount -a                    # test it
```
