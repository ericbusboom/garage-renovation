#!/bin/bash
set -euo pipefail
mountpoint=/Volumes/Proj/Buzzkill-Proj
mkdir -p "$mountpoint"
if ! /sbin/mount -t nfs | /usr/bin/grep -Fq " on $mountpoint "; then
  echo 'Connecting Buzzkill /proj. Enter your Mac administrator password when sudo asks.'
  sudo /sbin/mount -t nfs -o vers=3,tcp,resvport,nosuid,nodev,retrycnt=0 192.168.1.23:/proj "$mountpoint"
fi
/usr/bin/python3 - "$mountpoint" <<'PY'
import pathlib,sys,uuid
p=pathlib.Path(sys.argv[1])/('.nfs-check-'+uuid.uuid4().hex)
p.write_text('Mac NFS write/read check\n')
assert p.read_text()=='Mac NFS write/read check\n'
p.unlink()
print('NFS read/write check passed.')
PY
echo "Connected at $mountpoint"
open "$mountpoint"
