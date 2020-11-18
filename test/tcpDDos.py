from scapy.all import *
import time

while 1:
    t=IP(dst = '10.10.10.134')/TCP(dport=80, sport = 8011, flags='FS')
    send(t)
    time.sleep(2)