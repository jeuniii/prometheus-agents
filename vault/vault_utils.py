#/usr/bin/python
import os
import hvac
import requests
import subprocess
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def establishConnection(crt, key):
    client = hvac.Client(url='https://127.0.0.1:8200',
                         verify=False,
                         cert=(crt, key))
    try:
        client.auth_tls()
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.ProtocolError, hvac.exceptions.VaultDown):
        print("establishConnection() failed.")
    return client

def healthCheck(crt, key):
    client = establishConnection(crt, key)
    try:
        result = client.read('/sys/init')
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.ProtocolError, hvac.exceptions.VaultDown):
        return 0
    if result['initialized'] == True:
        return 1
    else:
        return 0

def sealCheck(crt, key):
    client = establishConnection(crt, key)
    try:
        result = client.read('/sys/seal-status')
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.ProtocolError, hvac.exceptions.VaultDown):
        return 0
    if result['sealed'] == True:
        return 0
    else:
        return 1

def apiCheck(crt, key):
    client = establishConnection(crt, key)
    try:
        result = client.read('secret/prometheus')['data']['password']
        if result == 'prometheus':
            return 1
        else:
            return 0
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, requests.packages.urllib3.exceptions.ProtocolError, hvac.exceptions.VaultDown):
        return 0

def hashCheck(hash):
    currentHash = subprocess.check_output('find /opt/vault/var/store/logical  -type f -exec md5sum {} + | md5sum | awk \'{print $1}\'', shell=True).decode('utf-8').strip()
    if hash == currentHash:
        return 1
    else:
        return 0
