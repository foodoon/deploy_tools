#!/usr/bin/env python
# encoding: utf-8
#安装python  paramiko fabric
#https://github.com/paramiko/paramiko.git
#https://github.com/fabric/fabric.git

from fabric.api import *
from fabric.contrib.files import *
import os
import time
import tarfile
import urllib2


#define args
tomcat_home='/usr/tomcat-ball'
code_dir='/alidata/code-git/ball'
backup_dir='/alidata/backup'
check_url='http://blog.foodoon.com/api/list.htm'
package_cmd='git pull & mvn clean package -Dmaven.test.skip=true -Ppro'
war_dir='/target/'
war_name='ball-1.0-SNAPSHOT.war'
war_listen_port="8080"


env.roledefs = {
            'test-server': ['user1@host1:port1',],  
            'pro-server': ['root@ums365.com:22', ]
            }

env.passwords = {
   'root@ums365.com:22':'gavin1217',
}
#env.key_filename = "~/.ssh/id_rsa"

@roles('pro-server')
def test():
#    backup()
#    stop_tomcat()
#    package()
#    deploy()
#    start_tomcat()
    check()
    

def backup():
    if exists(tomcat_home + '/webapps/ROOT'):
       today = time.strftime('%Y%m%d')
       now = time.strftime('%H%M%S') 
       run('mkdir -p ' + backup_dir + os.sep + today)
       print 'backup ---- mk backup dir success,dir=',today
       target = backup_dir + os.sep + today + os.sep + now + '.tar.gz'
       tar = 'tar -cvzf ' + target + ' ' + tomcat_home+'/webapps/ROOT/'
       run(tar)
       print 'backup ---- tar code success'
    
def stop_tomcat():
    run('sh ' + tomcat_home+'/bin/shutdown.sh && sleep 3')

def start_tomcat():
    run('sh ' + tomcat_home + '/bin/startup.sh &',pty=False)
#    sudo('tail -f ' + tomcat_home + '/logs/catalina.out')
    sec=0
    while(check_listen_port() == 'bad'):
       print 'wait server start up ',sec
       sec=sec+1
       time.sleep(1)
    print 'server start up success'

def package():
    with cd(code_dir):
        run(package_cmd)
        
def deploy():
    code_war_dir = code_dir + war_dir
    run('mv ' + code_war_dir + war_name + ' ' + code_war_dir+'/ROOT.war')
    run('rm -rf ' + tomcat_home + '/webapps/ROOT.war')
    run('rm -rf ' + tomcat_home + '/webapps/ROOT')
    run('cp ' + code_war_dir + '/ROOT.war ' + tomcat_home + '/webapps')
   
def check():
    print 'start check app url:',check_url
    try:
      response=urllib2.urlopen(check_url,timeout=8)
      print response.getcode()
    except urllib2.URLError,e:
      print e.code
    
def check_listen_port():
    std=run('netstat -nlt |grep ' + war_listen_port,shell=True, pty=True, quiet=True,combine_stderr=True)
    print std
    if std is None:
       return 'bad'
    if war_listen_port in std:
            return 'ok'
    else:
            return 'bad' 
