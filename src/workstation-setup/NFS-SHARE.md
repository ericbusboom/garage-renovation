# Buzzkill project share

Server: buzzkill, current address 192.168.1.23. Export: /proj.
Mac client currently 192.168.1.40; only this address is authorized.
Server config: /etc/exports.d/garage-mac.exports.
Options: rw,sync,no_subtree_check,all_squash,anonuid=1002,anongid=1002.
NFS server installed and enabled. exportfs and showmount verified.

Intended Mac mount: /Volumes/Proj/Buzzkill-Proj.
Mount not yet completed: Finder stalled; direct mount requires administrator privileges and sudo needs user password.
Run `Connect Buzzkill.command` to complete TCP NFSv3 mount and test read/write. Re-run after reboot or unmount; no persistent automount configuration installed.
If either LAN address changes, update the export/client mount accordingly; reserve addresses in router if desired.

Existing Mac /Volumes/Proj/proj/CAD/garage has NOT been copied or moved. This share is Buzzkill's separate /proj directory.
