#!/usr/bin/python

import time
import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


parser = argparse.ArgumentParser(description='Microservices exporter')

parser.add_argument('--vip','-ip', type=str, help='VIP', required=True)
parser.add_argument('--api','-ap', type=str, help='K8S API IP', required=True)
parser.add_argument('--interval','-t',type=float, help='Interval between scrapes', required=True)

args = parser.parse_args()

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MicroServiceCollector(object):
    def collect(self):

        api_url = 'http://'+args.api+':8080/api/v1/services'
        numKubeServices = len(requests.get(api_url).json()['items'])
        microservicesApiPath = []
        for index in range(0, numKubeServices):
            try:
                microservicesApiPath.append(requests.get(api_url).json()['items'][index]['metadata']['labels']['baseApi'])
            except(KeyError):
                pass

        for apiPath in microservicesApiPath:
            url = 'http://'+args.vip+'/'+apiPath+'/health'
            try:
                result = requests.get(url,  verify=False)
                if result.json()['status'] == 'UP':
                    state = 1
                else:
                    state = 0
            except (ValueError):
                state = 0
            apiPath = apiPath.replace('-','_')
            yield GaugeMetricFamily(apiPath+'_service', apiPath+'_check', value=state)


if __name__ == "__main__":
  REGISTRY.register(MicroServiceCollector())
  start_http_server(9117)
  while True: time.sleep(args.interval)
