#/usr/bin/python

import vault_utils
import time
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import argparse

parser = argparse.ArgumentParser(description='Vault Exporter')

parser.add_argument('--cert','-c', help='Client certificate.', required=True)
parser.add_argument('--key','-k', help='Client key.', required=True)
parser.add_argument('--interval','-t', help='Time interval between scrapes.', required=True)
parser.add_argument('--hash','-v', help='Current hash value.', required=True)

args = parser.parse_args()

class VaultCollector(object):
    def collect(self):
        yield GaugeMetricFamily('vault_init', 'Vault init check', value=vault.healthCheck(args.cert, args.key))
        yield GaugeMetricFamily('vault_seal', 'Vault seal check', value=vault.sealCheck(args.cert, args.key))
        yield GaugeMetricFamily('vault_api',  'Vault API check',  value=vault.apiCheck(args.cert, args.key))
        yield GaugeMetricFamily('vault_hash', 'Vault Hash check', value=vault.hashCheck(args.hash))

if __name__ == "__main__":
  REGISTRY.register(VaultCollector())
  start_http_server(9118)
  while True: time.sleep(float(args.interval))
