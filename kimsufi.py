#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find the Kimsufi servers availability.

Usage:
  kimsufi.py [options]
  kimsufi.py <model>... [options]

Options:
  -h, --help     Show this help.
  -v, --version  Show version.
  -m, --mail     Sends a mail when a server is available.

Examples:
  kimsufi.py
  kimsufi.py KS-1 KS-3
  kimsufi.py KS-1 --mail
"""

import json
import os
import smtplib

import requests
from docopt import docopt

VERSION = "1.0"

API_URL = "https://www.ovh.com/engine/api/dedicated/server/availabilities?country=de"

BASE_ORDER_URL = "https://www.kimsufi.com/en/order/kimsufi.xml?reference="

CURRENT_PATH = os.path.dirname(__file__)

with open('references.json', 'r') as ifile:
    REFERENCES = {x['hardware']: x['model'] for x in json.load(ifile)}

with open('zones.json', 'r') as ifile:
    ZONES = {x['zone']: x['location'] for x in json.load(ifile)}


def get_zone_name(zone):
    # rbx-hz to rbx
    zone = zone.split('-')[0]
    if zone in ZONES:
        return ZONES[zone]
    else:
        return zone


def get_servers(models):
    """Get the servers from the OVH API."""

    r = requests.get(API_URL)
    response = r.json()

    search = REFERENCES
    if models:
        search = {k: v for k, v in REFERENCES.items() if v in models}

    return [k for k in response if any(r == k['hardware'] for r in search)]


def get_ref(name):
    """Return the reference based on the server model."""

    return list(REFERENCES.keys())[list(REFERENCES.values()).index(name)]


def send_mail(output, total):
    try:
        with open(os.path.join(CURRENT_PATH, 'config.json')) as data:
            config = json.load(data)
            mail_host = config['email']['host']
            mail_port = config['email']['port']
            mail_username = config['email']['username']
            mail_password = config['email']['password']
            mail_from = config['email']['mail_from']
            mail_to = config['email']['mail_to']

    except IOError:
        print('Rename config.json.sample to config.json and edit it')
        return False
    """Send a mail to <mail_to>."""

    subject = "{0} server{1} {2} available on Kimsufi".format(
        total, "s" [total <= 1:], ["is", "are"][total > 1])
    headers = "From: {}\r\nTo: {}\r\nSubject: {}\r\n\r\n".format(
        mail_from, mail_to, subject)

    try:
        server = smtplib.SMTP(mail_host, mail_port)
    except smtplib.socket.gaierror:
        return False

    server.ehlo()
    server.starttls()
    server.ehlo()

    try:
        server.login(mail_username, mail_password)
    except smtplib.SMTPAuthenticationError:
        print('SMPT Auth Error!')
        return False

    try:
        server.sendmail(mail_from, mail_to, headers + output)
        return True
    except Exception:
        print('Error sending email!')
        return False
    finally:
        server.close()


if __name__ == '__main__':
    arguments = docopt(__doc__, version=VERSION)
    kim = get_servers(arguments['<model>'])

    total = 0
    output = ""

    for k in kim:
        output += "\n{}\n".format(REFERENCES[k['hardware']])
        output += "{}\n".format("=" * len(REFERENCES[k['hardware']]))
        output += "hardware : {}\n".format(k['hardware'])
        output += "order : {}{}\n".format(BASE_ORDER_URL, k['hardware'])

        for z in k['datacenters']:
            invalids = ['unavailable', 'unknown']
            availability = z['availability']
            if availability not in invalids:
                total += 1
            output += '{} : {}\n'.format(
                get_zone_name(z['datacenter']), availability)

    output += "\n=======\nRESULT : {0} server{1} {2} available on Kimsufi\n=======\n".format(
        total, "s" [total <= 1:], ["is", "are"][total > 1])

    print(output)
    if total != 0 and arguments['--mail']:
        send_mail(output, total)
