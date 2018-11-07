# Ansible KeePass inventory script
Ansible inventory script to read KeePass 2.x (v4) files.

## Install
- Requires Python 3. Tested on Python 3.6.

## Verify (read only)
Password to example.kdbx is "example":

    export KDB_PATH=example.kdbx
    export KDB_PASS=example

    ./keepass-inventory.py --list

The standard output should be a readable JSON. The usual Ansible -i argument can read it:

    ansible all --list-hosts -i keepass-inventory.py

## Standard use
Security: continue on a system where you trust all root users. They can see your KDB_PASS.

    export KDB_PASS=   KDB_PATH=your.kdbx
    read -sp Pass: KDB_PASS
    
    ansible  all   -i keepass-inventory.py    -m shell -a 'wc /etc/shadow'

Instead of "root" passwords inside Keepass you can use "jsmith" accounts with sudo (or similar mechanism):

   ansible all -b -i keepass-inventory.py    -m shell -a 'wc /etc/shadow'

Inside Keepass you can Add Group "devservers1" with some hosts and execute only on these:

    ansible devservers1 -b -i keepass-inventory.py    -m shell -a 'wc /etc/shadow'

This works whether `devservers1` is a top-level group or nested.
 
The whole playbook:

    ansible-playbook /etc/ansible/site.yml -b -i keepass-inventory.py --limit=devservers1

## Advanced use
- Understands an optional Keepass URL field if it starts with "ssh://", for example "ssh://server1.example.com"
- Ignores completely entries that have other URL types, for example it will ignore "https://app.internal.example.com"
- Ignores entries where the password starts with "{REF:"; these are Keepass internal references (like symbolic links)
- Parses any values starting with '---' as YAML
- Auxiliary Ansible groups appear that include the Keepass UUID in their names. You can ignore these
### More grouping - Keepass Tags
- In Keepass GUI go to Edit Entry -> Properties -> Tags -> enter "prod, dbserver, physical" for example
- Keepass tags  map to Ansible groups, very similarly to Keepass groups:
 
      ansible-playbook /etc/ansible/site.yml -b -i keepass-inventory.py --limit=dbserver

  - Within tags, `=` is replaced by `_`

### Group vars
- You can create a Keepass entry with the special title "group_vars"
  - In KeePass GUI go to Edit Entry -> Advanced -> String Fields -> Add
  - These fields will be Ansible vars for this entire group of hosts

