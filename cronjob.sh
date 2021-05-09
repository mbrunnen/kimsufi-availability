#!/bin/sh

set -eu

cd $(dirname "$0") && pwd

. env/bin/activate
REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt ./kimsufi.py --mail KS-2
