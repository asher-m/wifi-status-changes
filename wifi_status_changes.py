#!/usr/bin/env python3
""" Simple script to check wifi protocol, and write to log if it's different.
"""


import subprocess
import time


LOGFILE = 'wifi_status_changes.log'


def query():
    """ Get the protocol that the wireless card is opperating in. """
    while True:
        try: # It's possible to fail if not connected:
            response, _ = launch_without_console(['netsh', 'wlan',
                                                    'show', 'interfaces']).\
                                                    communicate()
            response = [i.strip() for i in response.decode('utf-8').lower()\
                        .splitlines()]
            protocol = [i for i in response if 'radio type'
                        in i][0].split()[-1]
            ap = [i for i in response if 'bssid' in i][0].split()[-1]
            return protocol, ap
        except:
            time.sleep(10)

def write_change(protocol_old, ap_old, protocol_new, ap_new):
    """ Write change to log. """
    with open(LOGFILE, 'a') as fp:
        fp.write('{:<28s} {:>10} {:<12} {:<8} @ {} --> {:<8} @ {}\n'.\
                 format(time.ctime(), 'EVENT:', 'CHANGE',\
                        protocol_old, ap_old, protocol_new, ap_new))

def main():
    """ Query the wifi status every 5 seconds to see if there's been a change.
    """
    global LAST_PROTOCOL, LAST_AP
    while True:
        # Check if old protocol is what's still being used:
        protocol, ap = query()
        if protocol != LAST_PROTOCOL[-1] or ap != LAST_AP[-1]:
            # Write the log, then add to lists:
            write_change(LAST_PROTOCOL[-1], LAST_AP[-1], protocol, ap)
            LAST_PROTOCOL.append(protocol)
            LAST_AP.append(ap)
        time.sleep(5)

def launch_without_console(args):
    """ Launches windowless subprocess... """
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(args, startupinfo=startupinfo,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        
# Wait 30 seconds for the system to catch up...
time.sleep(30)
protocol, ap = query()
LAST_PROTOCOL = [protocol]
LAST_AP = [ap]


with open(LOGFILE, 'a') as fp:
    # Write new line to log indicating system start:
    fp.write('{:<28s} {:>10} {:<12}\n'.format(time.ctime(),
             'SYSTEM:', 'LOG STARTED'))
    fp.write('{:<28s} {:>10} {:<12} {:<8} @ {}\n'.\
             format(time.ctime(), 'EVENT:', 'INIT',
                    LAST_PROTOCOL[0], LAST_AP[0]))

if __name__ == '__main__':
    main()
    