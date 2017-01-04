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


ini_file_path = os.path.expanduser(os.path.join("~", ".get-shit-done.ini"))
restart_networking_command = ['systemctl', 'restart', 'systemd-networkd']
hosts_file = '/etc/hosts'
start_token = '## start-gsd'
end_token = '## end-gsd'
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

if os.path.exists(ini_file_path):
    ini_file = open(ini_file_path)
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
    subprocess.check_call(restart_networking_command)


def get_status():
    h_file = open(hosts_file, 'r+')
    content = h_file.read()
    if start_token in content and end_token in content and len(content.split('\n')) > 2:
        curr_status = 'work'
    elif start_token not in content and end_token not in content:
        curr_status = 'play'
    else:
        exit_error('There are some problems with "%s" file' % hosts_file)
    h_file.close()
    return curr_status


def status():
    curr_status = get_status()
    if 'work' in curr_status:
        print("Work mode")
    elif 'play' in curr_status:
        print("Play mode")
    

def work():
    curr_status = get_status()
    h_file = open(hosts_file, 'a+')
    if 'work' in curr_status:
        exit_error("Work mode already set.")
        h_file.close()
    elif 'play' in curr_status:
        h_file.write(start_token + "\n")
        for site in siteList:
            h_file.write("0.0.0.0\t" + site + "\n")
            h_file.write("0.0.0.0\twww." + site + "\n")
        h_file.write(end_token)
    h_file.close()
    rehash()


def play():
    h_file = open(hosts_file, "r+")
    lines = h_file.readlines()
    
    start_index = -1
    
    for index, line in enumerate(lines):
        if line.strip() == start_token:
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
        exit_error('usage: ' + sys.argv[0] + ' [work|play|status]')
    try:
        { "work": work, "play": play, "status": status }[sys.argv[1]]()
    except Exception as e:
        exit_error(e)


if __name__ == '__main__':
    main()
