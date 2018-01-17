#!/usr/bin/python

import re
import time
import argparse
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

parser = argparse.ArgumentParser(description='Pod Health Check Exporter')
parser.add_argument('--api','-ap', type=str, help='K8S API IP', required=True)
parser.add_argument('--interval','-t',type=float, help='Interval between scrapes', required=True)

args = parser.parse_args()
api_server = args.api

class MicroServiceCollector(object):
    def collect(self):

        pod_url = 'http://'+api_server+':8080/api/v1/pods'
        total_Pods = len(requests.get(pod_url).json()['items'])
    
        for pod in range(0, total_Pods):
            svcName = requests.get(pod_url).json()['items'][pod]['metadata']['name']
            svcState = list(requests.get(pod_url).json()['items'][pod]['status']['containerStatuses'][0]['state'])[0]
            if svcState == 'running':
                state = 1
            else:
                state = 0
            svcName = svcName.replace('-','_')
            pod_metric = GaugeMetricFamily('pod_status', 'Micro Service State', labels=['podname'])
            pod_metric.add_metric([svcName], state)
            yield pod_metric


if __name__ == "__main__":
  REGISTRY.register(MicroServiceCollector())
  start_http_server(9115)
  while True: time.sleep(args.interval)
