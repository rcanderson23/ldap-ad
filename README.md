ldap-ad
==========

This is written with the purpose of getting an Ansible inventory from an Active Directory domain controller via LDAP. 

Dependencies
==========
* python3
* ldap3

Installation
==========
1. Run `pip3 install -r requirements.txt`
2. Copy `ldap-ad.py` and `ldap-ad.sample.ini` into your `/etc/ansible/inventory` folder
3. Rename `ldap-ad.sample.ini` to `ldap-ad.ini` and fill in variables


Configuration
==========
All configuration options are in `ldap-ad.ini` and is required for this script to run properly.
