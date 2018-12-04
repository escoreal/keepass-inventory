#!/usr/bin/env python3.6
import sys
import libkeepass
import os
import json
import lxml.etree as ET
import base64
import re
import yaml

def kdb_inventory():
  filename = os.environ["KDB_PATH"]
  credentials = { 'password' : os.environ["KDB_PASS"] }
  vgroups = ['product', 'stage', 'tier', 'type', 'ansible_ssh_host']
  hosts = {}
  inventory = {}
  inventory_vars = {}
  with libkeepass.open(filename, **credentials) as kdb:
    xmldata = ET.fromstring(kdb.pretty_print())
    for history in xmldata.xpath(".//History"):
      history.getparent().remove(history)
    for group in xmldata.findall(".//Group"):
      group_name_raw = group.find("./Name").text
      group_name = re.sub('\s|=','_', group_name_raw, flags=re.IGNORECASE).lower()
      if re.match('^recycle.bin.*',group_name):
        continue
      group_uuid = group.find("./UUID").text
      group_uuid = base64.b16encode(base64.b64decode(group_uuid)).decode('utf-8')
      group_name_uuid = group_name + "_" + group_uuid
      inventory[group_name_uuid] = {}
      inventory[group_name_uuid]["hosts"] = []
      subgroups = []
      for subgroup in group.findall("./Group"):
        subgroup_name_raw = subgroup.find("./Name").text
        subgroup_name = re.sub('\s|=','_', subgroup_name_raw, flags=re.IGNORECASE).lower()
        subgroup_uuid = subgroup.find("./UUID").text
        subgroup_uuid = base64.b16encode(base64.b64decode(subgroup_uuid)).decode('utf-8')
        subgroup_name_uuid = subgroup_name + "_" + subgroup_uuid
        subgroups.append(subgroup_name_uuid)
      if subgroups:
        inventory[group_name_uuid]["children"] = subgroups
      for entry in group.findall("./Entry"):
        hostvars = {}
        hostgroups = []
        hostname = None
        for string in entry.findall("./String"):
          key   = string.findtext("./Key").lower()
          value = string.findtext("./Value")
          if key and value:
            if key == 'title':
              hostname = re.sub('\s|=','_', value, flags=re.IGNORECASE)
            elif key == 'url':
              if re.match('^ssh://', value, flags=re.IGNORECASE):
                hostvars['ansible_host'] = re.sub('^ssh://','',value,flags=re.IGNORECASE)
              else:
                hostname = None      # ignore entry with non-ssh url
            elif key == 'username':
              hostvars['ansible_user'] = value
            elif key == 'password':
              if re.match('^{REF:', value, flags=re.IGNORECASE):    # KeePass can put a reference to another cell - ignore that
                hostname = None
              else:
                hostvars['ansible_ssh_pass']    = value
                hostvars['ansible_become_pass'] = value
            elif re.match('^---\n', value):
              hostvars[key] = yaml.safe_load(value)
            elif value in ['True', 'true']:
              hostvars[key] = True
            elif value in ['False', 'false']:
              hostvars[key] = False
            else:
              hostvars[key] = value
        if hostname == "group_vars":
          inventory[group_name_uuid]["vars"] = hostvars
        elif hostname:
          hosts[hostname] = hostvars
          hostgroups.append(group_name_uuid)
          groups = {
            group.find('Name').text.lower()
            for group in entry.xpath('ancestor::Group')
          }
          for group in groups:
            hostgroups.append(group)
          for vgroup in vgroups:
            if vgroup in hostvars:
              hostgroups.append(hostvars[vgroup])
          tags_raw = entry.findtext("./Tags")
          tags = re.sub('\s|=','_', tags_raw, flags=re.IGNORECASE).split(';')
          for tag in tags:
            if tag:
              hostgroups.append(tag)
          for hostgroup in hostgroups:
            try:
              inventory[hostgroup]["hosts"].append(hostname)
            except KeyError:
              try:
                inventory[hostgroup]["hosts"] = [hostname]
              except KeyError:
                inventory[hostgroup] = {}
                inventory[hostgroup]["hosts"] = [hostname]

    inventory_vars["hostvars"] = hosts
    inventory["_meta"] = inventory_vars
    print(json.dumps(inventory, indent=2, sort_keys=True))

if __name__ == '__main__':
  try:
    os.environ["KDB_PATH"]
  except KeyError:
    print("{}")
    sys.exit(0)
  if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
    kdb_inventory()
  elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
    kdb_inventory()
  else:
    print("Usage: %s --list or --host <hostname>" % sys.argv[0])
    sys.exit(1)
