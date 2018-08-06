#!/usr/bin/env python3

import os
import sys
import re
import ldap3
import json
import configparser
import argparse

parser = argparse.ArgumentParser(description='Script to obtain host inventory from AD')
parser.add_argument('--list', action='store_true')
args = parser.parse_args()

class ADAnsibleInventory():

    def __init__(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        configfile = directory + '/ldap-ad.ini' 
        config = configparser.ConfigParser()
        config.read(configfile)
        domaindn = config.get('ldap-ad', 'domaindn')
        username = config.get('ldap-ad', 'username')
        password = config.get('ldap-ad', 'password')
        basedn = config.get('ldap-ad', 'basedn')
        ldapuri = config.get('ldap-ad', 'ldapuri') 
        port = config.get('ldap-ad', 'port')
        ca_file = config.get('ldap-ad', 'ca_file')
        adfilter = "(&(sAMAccountType=805306369))"
        
        self.inventory = { "_meta": {"hostvars":{}}}
        self.ad_connect(ldapuri, username, password, port, ca_file)
        self.get_hosts(basedn,adfilter)
        self.org_hosts(basedn)
        print(json.dumps(self.inventory, indent=2))
        
    def ad_connect(self, ldapuri, username, password, port, ca_file):
        tls_configuration = ldap3.Tls(ca_certs_path=ca_file)
        conn = ldap3.Connection(ldapuri, 
                                auto_bind=True, 
                                user=username, 
                                password=password, 
                                authentication=ldap3.NTLM)
        self.conn = conn

    def get_hosts(self, basedn, adfilter):
        self.conn.search(search_base=basedn,
                         search_filter=adfilter,
                         attributes=['cn','dnshostname'])
        self.conn.response_to_json
        self.results = self.conn.response
   
    def org_hosts(self, basedn):

        #Removes CN,OU, and DC and places into a list
        basedn_list = (re.sub(r"..=","", basedn)).split(",")
        for computer in self.results:
            org_list = (re.sub(r"..=","",computer['dn'])).split(",")
            #Remove hostname
            del org_list[0]
            
            #Removes all excess OUs and DC
            for count in range(0, (len(basedn_list)-1)):
                del org_list[-1]

            #Reverse list so top group is first
            org_list.reverse()

            org_range = range(0,(len(org_list)))
            for orgs in org_range:
                if orgs == org_range[-1]:
                    self.add_host(org_list[orgs], computer['attributes']['dNSHostName'])
                else:
                    self.add_group(group=org_list[orgs], children=org_list[orgs+1])
    def add_host(self, group, host):
        host = (''.join(host)).lower()
        group = (''.join(group)).lower()
        if group not in self.inventory.keys():
            self.inventory[group] = { 'hosts': [], 'children': [] }    
        self.inventory[group]['hosts'].append(host)
    
    def add_group(self, group, children):
        group = (''.join(group)).lower()
        children = (''.join(children)).lower()
        if group not in self.inventory.keys():
            self.inventory[group] = { 'hosts': [], 'children': [] }    
        if children not in self.inventory[group]['children']:
            self.inventory[group]['children'].append(children)

if __name__ == '__main__':
    ADAnsibleInventory()
