#!/usr/bin/env python

from __future__ import print_function

import sys
import getpass
import subprocess
import os
import json


def exit_error(error):
    print(error, file=sys.stderr)
    exit(1)


iniFile = os.path.expanduser(os.path.join("~", ".get-shit-done.ini"))
restartNetworkingCommand = ['systemctl', 'restart', 'systemd-networkd']
hostsFile = '/etc/hosts'
startToken = '## start-gsd'
endToken = '## end-gsd'
siteList = [
    '9gag.com',
    '9gag.tv',
    'facebook.com',
    'instagram.com',
    'reddit.com',
    'slashdot.com',
    'smbc-comics.com',
    'thedailywtf.com',
    'xkcd.com',
    'oglaf.com',
]

if os.path.exists(iniFile):
    ini_file = open(iniFile)
    try:
        ini_content = ini_file.read()
        print(ini_content)
        ini_json = json.loads(ini_content)
        if "sites" in ini_json:
            siteList = siteList + ini_json.get("sites")
        elif "siteList" in ini_json:
            siteList = ini_json.get("siteList")
    finally:
        ini_file.close()


def rehash():
    subprocess.check_call(restartNetworkingCommand)


def work():
    h_file = open(hostsFile, 'a+')
    contents = h_file.read()
    if startToken in contents and endToken in contents:
        exit_error("Work mode already set.")
        h_file.close()
    else:
        h_file.write(startToken + "\n")
        for site in siteList:
            h_file.write("0.0.0.0\t" + site + "\n")
            h_file.write("0.0.0.0\twww." + site + "\n")
        h_file.write(endToken)
    h_file.close()
    rehash()


def play():
    h_file = open(hostsFile, "r+")
    lines = h_file.readlines()
    
    start_index = -1
    
    for index, line in enumerate(lines):
        if line.strip() == startToken:
            start_index = index
    if start_index > -1:
        lines = lines[0:start_index]
        
        h_file.seek(0)
        h_file.write(''.join(lines))
        h_file.truncate()
        
        rehash()


def main():
    if getpass.getuser() != 'root':
        exit_error('Please run script as root.')
    if len(sys.argv) != 2:
        exit_error('usage: ' + sys.argv[0] + ' [work|play]')
    try:
        { "work": work, "play": play }[sys.argv[1]]()
    except Exception as e:
        exit_error(e)


if __name__ == '__main__':
    main()
