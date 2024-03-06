#!/usr/bin/python
# -*- coding: utf-8 -*-
import getopt
import json
import os
import subprocess
import sys
import time

from stem import Signal
from stem.control import Controller


def github_link():
    """
for referencing but not initially needed
    """
    git_link = 'https://github.com/quintin2003/torghost.git'
    print(git_link)


def get_ip_from_api():
    """
bingbong, gotta get your ip
    """
    link = "https://api.ipify.org/?format=json"
    cmd = 'curl '
    result = subprocess.run(cmd + link, capture_output=True, text=True, stdout=True)
    ip = json.loads(result.stdout)
    print(ip)


def t():
    """
the time
    :return:
    """
    current_time = time.localtime()
    ctime = time.strftime('%H:%M:%S', current_time)
    return '[' + ctime + ']'


class Bcolors:
    """
    To assign colors for really nothing loooool
    """
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    WHITE = '\033[37m'


def sigint_handler():
    """
signal handler
    """
    print("User interrupt ! shutting down")
    stop_torghost()


def usage():
    """
self-explanatory
    """
    print("""
    Torghost usage:
    -s    --start       Start Torghost
    -r    --switch      Request new tor exit node
    -x    --stop        Stop Torghost
    -h    --help        print(this help and exit)
    """)
    sys.exit()


def check_root():
    """
making sure your root ;)
    """
    if os.geteuid() != 0:
        print("You must be root; Say the magic word")
        sys.exit(0)


TorrcCfgString = \
    ("VirtualAddrNetwork 10.0.0.0/10\n"
     "AutomapHostsOnResolve 1\n"
     "TransPort 9040\n"
     "DNSPort 5353\n"
     "ControlPort 9051\n"
     "RunAsDaemon 1\n")

resolvString = 'nameserver 127.0.0.1'

Torrc = '/etc/tor/torghostrc'
resolv = '/etc/resolv.conf'


def start_torghost():
    """
start torghost
    """
    print(t() + ' Always check for updates using -u option')
    os.system('sudo cp /etc/resolv.conf /etc/resolv.conf.bak')
    if os.path.exists(Torrc) and TorrcCfgString in open(Torrc).read():
        print(t() + ' Torrc file already configured')
    else:

        with open(Torrc, 'w') as myfile:
            print(t() + ' Writing torcc file ')
            myfile.write(TorrcCfgString)
            print(Bcolors.GREEN + 'done' + Bcolors.ENDC)
    if resolvString in open(resolv).read():
        print(t() + ' DNS resolv.conf file already configured')
    else:
        with open(resolv, 'w') as myfile:
            print(t() + ' Configuring DNS resolv.conf file.. '),
            myfile.write(resolvString)
            print(Bcolors.GREEN + 'done' + Bcolors.ENDC)

    print(t() + ' Stopping tor service '),
    os.system('sudo systemctl stop tor')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(Bcolors.GREEN + 'done' + Bcolors.ENDC)
    print(t() + ' Starting new tor daemon '),
    os.system('sudo -u debian-tor tor -f /etc/tor/torghostrc > /dev/null'
              )
    print(Bcolors.GREEN + 'done' + Bcolors.ENDC)
    print(t() + ' setting up iptables rules'),

    iptables_rules = (
            """
NON_TOR="192.168.1.0/24 192.168.0.0/24"
TOR_UID=%s
TRANS_PORT="9040"
            
iptables -F
iptables -t nat -F
iptables -t nat -A OUTPUT -m owner --uid-owner $TOR_UID -j RETURN
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
for NET in $NON_TOR 127.0.0.0/9 127.128.0.0/10; 
do
iptables -t nat -A OUTPUT -d $NET -j RETURN
done
iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $TRANS_PORT

iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
for NET in $NON_TOR 127.0.0.0/8; do
iptables -A OUTPUT -d $NET -j ACCEPT
done
iptables -A OUTPUT -m owner --uid-owner $TOR_UID -j ACCEPT
iptables -A OUTPUT -j REJECT
"""
            % subprocess.getoutput('id -ur debian-tor'))

    os.system(iptables_rules)
    print(Bcolors.GREEN + 'done' + Bcolors.ENDC)
    print(t() + 'Fetching current IP')
    print(t() + 'CURRENT IP:' + Bcolors.GREEN, get_ip_from_api(), Bcolors.ENDC)


def stop_torghost():
    """
poop
    """
    print(Bcolors.RED + t() + 'STOPPING torghost' + Bcolors.ENDC)
    print(t() + ' Flushing iptables, resetting to default'),
    os.system('mv /etc/resolv.conf.bak /etc/resolv.conf')
    ip_flush = \
        """
        iptables -P INPUT ACCEPT
        iptables -P FORWARD ACCEPT
        iptables -P OUTPUT ACCEPT
        iptables -t nat -F
        iptables -t mangle -F
        iptables -F
        iptables -X
        """
    os.system(ip_flush)
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(ip_flush)
    print(Bcolors.GREEN + 'done' + Bcolors.ENDC)
    print(t() + 'Restarting Network manager'),
    os.system('service network-manager restart')
    print(Bcolors.GREEN + '[done]' + Bcolors.ENDC)
    print(t() + 'Fetching current IP...')
    time.sleep(3)
    print(t() + 'CURRENT IP:' + Bcolors.GREEN, get_ip_from_api(), Bcolors.ENDC)


def switch_tor():
    """
pooooop
    """
    print(t() + ' Please wait...')
    time.sleep(7)
    print(t() + ' Requesting new circuit...'),
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    print(Bcolors.GREEN + '[done]' + Bcolors.ENDC)
    print(t() + 'Fetching current IP')
    print(t() + 'CURRENT IP: ', Bcolors.GREEN, get_ip_from_api(), Bcolors.ENDC)


def main():
    """
poop
    """
    check_root()
    if len(sys.argv) <= 1:
        usage()
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'srxhu', [
            'start', 'stop', 'switch', 'help', 'update'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for (o, a) in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-s', '--start'):
            start_torghost()
        elif o in ('-x', '--stop'):
            stop_torghost()
        elif o in ('-r', '--switch'):
            switch_tor()
        elif o in ('-u', '--update'):
            github_link()
        else:
            usage()


if __name__ == '__main__':
    main()
