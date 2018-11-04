# Ansible KeePass inventory script
Quick & dirty (just a sysadmin ;) ) Ansible inventory script to read KeePass 2.x (v4) files.

Reads environment variables "KDB_PATH" and "KDB_PASS" to open KeePass file and export JSON inventory for Ansible.

## Details
- Entries are mapped to hosts. "Title" -> hostname.
- Entries named "group_vars" are mapped to vars of the parent group.
- To build up the tree (group_vars, children) the group names contains the uuid.
- "Titles" containing spaces are ignored, as are empty "Titles".
- Tags are mapped to groups. '=' is replaced by '_'.
- Group names and names of vars are converted to lower case.
- Values starting with '---' are parsed as YAML.
 
## Installation
See the playbook "keepass-inventory-install.yml" as example for installation on Ubuntu.

## Examples
- Password of example.kdbx is "example"
- example.kdbx.json is the resulting JSON that is fed to Ansible

