#!/bin/sh

set -eu

cd $(dirname "$0") && pwd

python3 -m venv env
. env/bin/activate
pip3 install -r requirements.txt
REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt ./kimsufi.py --mail KS-2
