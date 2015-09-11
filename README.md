# Ansible KeePass inventory script
Quick & dirty (just a sysadmin ;) ) Ansible inventory script to read KeePass 2.x (v4) files.

Reads environment variables "KDB_PATH" and "KDB_PASS" to open KeePass file and export JSON inventory for Ansible.

## Details
- Entries are mapped to hosts. "Title" -> hostname.
- Entries named "group_vars" are mapped to vars of the parent group
- To build up the tree (group_vars, children) the group names contains the uuid.
- "Titles" with spaces and empty values are ignored.
- tags are mapped to groups. '=' is replaced by '_'.
- group names and names of vars are converted to lower case.
 
## Installation
See the playbook "kdb_inventory_install.yml" as example for installation on Ubuntu.

## Examples
- password of example.kdbx is "example"
- example.kdbx.json is the JSON output

