#!/usr/bin/python
# _*_ coding=utf8 _*_

import os
import sys
import time
import platform
import commands
import urllib2
import json
import requests

"""
By 2017.10.27.

"""


##  send data to remote server url.
URL = 'http://127.0.0.1:8000/srvstatus/serverapi/'

class LocalSysInfo():
    def __init__(self,sysdisk=None):
        self.sysinfo = {}
        self.__getsysname()
        self.__getsysteminfo()
        self.__getsysmemory()
        self.__getsysfdisk()
        self.__getsyslocalip()
        
        self.sysinfo['hostname'] = self.hostname
        self.sysinfo['disk'] = self.sysdisk
        self.sysinfo['OS'] = self.osinfo
        self.sysinfo['memory'] = self.sysmemory
        self.sysinfo['network'] = self.sysip
        
    
    def __getsysname(self):
        self.hostname = platform.node()
    
    
    def __getsysteminfo(self):
        self.osinfo = platform.platform()
        if 'linux' in self.osinfo.lower():
            self.osinfo = 'linux'
        elif 'windows' in self.osinfo.lower():
            self.osinfo = 'windows'
        
    def __getsysmemory(self):
        self.sysmemory ={}
        if 'linux' == self.osinfo:
            self.sysmem_total = int(commands.getoutput("grep 'MemTotal' /proc/meminfo | awk '{print $2}'"))/1024.0
            self.sysmem_free = int(commands.getoutput("grep 'MemFree' /proc/meminfo | awk '{print $2}'"))/1024.0
            self.sysmem_used = self.sysmem_total - self.sysmem_free
            self.sysmemory ={}
        if 'windows' == self.osinfo:
            pass
        
        self.sysmemory['total'] = self.sysmem_total
        self.sysmemory['free'] = self.sysmem_free
        self.sysmemory['used'] = self.sysmem_used
        
    def __getsysfdisk(self):
        self.sysdisk = {}
        if self.osinfo == 'linux':
            ## exclude partitions 
            parts = """grep -v "^rootfs\|none\|^/proc\|^nfsd\| nfs \|^cgroup\|^tmpfs\|debugfs\|^dev\|^mqu\|^sun\|^sys\|^proc\|^securi\|^fuse\|^seli\|^pstore\|^gvfs\|^syst\|^configfs\|^hugetlbfs\|binf" /proc/self/mounts| awk '{print $1,$2,$3}'"""
            mounts =  commands.getoutput(parts).split('\n')
            
            ## ['/dev/mapper/system-root / xfs',]
            if mounts:
                for d in mounts:
                    tmp = d.split(" ")
                    ##  partitions  
                    self.sysdisk[tmp[0]] = {'mnt':tmp[1],}
                    ##  format
                    self.sysdisk[tmp[0]]['format'] = tmp[2]
                    ##  size/used/free
                    ds = os.statvfs(tmp[1])
                    ##  total  keep .xx 2float 
                    self.sysdisk[tmp[0]]['size'] = round(float(ds.f_bsize * ds.f_blocks)/1024/1024/1024,2)
                    ##  used  keep .xx 2float
                    self.sysdisk[tmp[0]]['used'] = round(float(ds.f_bsize*(ds.f_blocks-ds.f_bfree))/1024/1024/1024,2)
                    ##  free  keep .xx 2float
                    self.sysdisk[tmp[0]]['free'] = round(float(ds.f_bsize * ds.f_bfree)/1024/1024/1024,2)
                    
        elif self.osinfo == 'windows':
            pass
        

            
                    
            
    def __getsyslocalip(self):
        self.sysip = {}
        if self.osinfo == 'linux':
            s = commands.getoutput("ip -o addr ls | grep ' inet ' |grep -v '127.0.0.1'  | awk '{print $2,$4}'").split("\n")
            if s:
                for i in s:
                    ##  remove ip/prefix 
                    si = i.split('/')[0].split(' ')
                    ##  ifname  :  ip
                    self.sysip[si[0]] = si[1] 
                    
        elif self.osinfo == 'windows':
            pass


def sendData(data=None):
    try:
        req = urllib2.Request(URL,data)
        res = urllib2.urlopen(req)
        
    except urllib2.HTTPError,error:
        print "ERROR: ",error.read()
        

if __name__ == "__main__":
    sysinfo = LocalSysInfo()
    print sysinfo.osinfo
    print sysinfo.sysmem_total
    print sysinfo.sysmem_free
    print sysinfo.sysmem_used
    print sysinfo.hostname
    print sysinfo.sysdisk
    print sysinfo.sysip
    print sysinfo.sysinfo
    
    sendData(data=json.dumps(sysinfo.sysinfo))
    #sendData(data=sysinfo.sysinfo)
    
    #r = requests.post('http://127.0.0.1:8000/srvstatus/serverapi/',data=json.dumps(sysinfo.sysinfo),headers={'content-type':'application/json'})
