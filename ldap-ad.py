#!/usr/bin/env python2

import sys
import re
import ldap
import json
import ConfigParser
class ADAnsibleInventory():

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('ldap-ad.ini')
        domaindn = config.get('ldap-ad', 'domaindn')
        username = config.get('ldap-ad', 'username')
        password = config.get('ldap-ad', 'password')
        basedn = config.get('ldap-ad', 'basedn')
        ldapuri = config.get('ldap-ad', 'ldapuri') 
        scope = ldap.SCOPE_SUBTREE
        adfilter = "(&(sAMAccountType=805306369))"
        
        self.inventory = {}
        self.ad_connect(ldapuri, username, password)
        self.get_hosts(basedn,scope,adfilter)
        self.org_hosts(basedn)
        print json.dumps(self.inventory, indent=2, encoding='iso-8859-9')
        
    def ad_connect(self, ldapuri, username, password):
        conn = ldap.initialize(ldapuri)
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(username, password)
        self.conn = conn
    
    def get_hosts(self, basedn, scope, adfilter):
        self.results = self.conn.search_s(basedn, scope, adfilter)
   
    def get_groups(self, basedn, scope, adfilter):
        self.groups = self.conn.search_s(basedn, scope, adfilter)

    def org_hosts(self, basedn):

        #Removes CN,OU, and DC and places into a list
        basedn_list = (re.sub(r"..=","", basedn)).split(",")
        for dn,attrs in self.results:
            org_list = (re.sub(r"..=","",dn)).split(",")
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
                    self.add_host(org_list[orgs], attrs['dNSHostName'])
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
