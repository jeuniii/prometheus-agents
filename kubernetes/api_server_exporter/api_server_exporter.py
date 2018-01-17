#!/usr/bin/python

import time
import argparse
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

parser = argparse.ArgumentParser(description='K8S API Server exporter')
parser.add_argument('--master','-ip', type=str, help='K8S API Server IP', required=True)
parser.add_argument('--interval','-t',type=float, help='Interval between scrapes', required=True)
args = parser.parse_args()

class MicroServiceCollector(object):
    def collect(self):
        base_url = 'http://'+args.master+':8080'
        yield GaugeMetricFamily('k8s_nodes', 'Total nodes in K8S cluster', value=getNodes(base_url))
        yield GaugeMetricFamily('k8s_pods', 'Total pods in K8S cluster', value=getPods(base_url))
        yield GaugeMetricFamily('k8s_running_pods' , 'Total pods in Running state' , value=totalRunningPods(base_url))
        yield GaugeMetricFamily('k8s_rc', 'Total replication controllers in K8S cluster', value=getRCs(base_url))
        yield GaugeMetricFamily('k8s_deployments', 'Total deployments in K8S cluster', value=getDeployments(base_url))
        yield GaugeMetricFamily('k8s_version', 'Version of k8s cluster', value=getVersion(base_url))

        nodes = getNodes(base_url)
        node_url = base_url+'/api/v1/nodes'
        for node in range(0,nodes):
            ip = requests.get(node_url).json()['items'][node]['spec']['externalID']

            node_disk_status= requests.get(node_url).json()['items'][node]['status']['conditions'][0]['status']
            if node_disk_status == 'False':
                status = 1
            else:
                status = 0
            sufficient_disk_metric = GaugeMetricFamily('k8s_node_sufficient_disk' , 'Disk Metrics' , labels=['node'])
            sufficient_disk_metric.add_metric([ip], status)
            yield sufficient_disk_metric

            node_memory_status = requests.get(node_url).json()['items'][node]['status']['conditions'][1]['status']
            if node_memory_status == 'False':
                status = 1
            else:
                status = 0
            sufficient_memory_metric = GaugeMetricFamily('k8s_node_sufficient_memory' , 'Node Memory Metrics' , labels=['node'])
            sufficient_memory_metric.add_metric([ip], status)
            yield sufficient_memory_metric

            node_disk_pressure_status = requests.get(node_url).json()['items'][node]['status']['conditions'][2]['status']
            if node_disk_pressure_status == 'False':
                status = 1
            else:
                status = 0
            disk_pressure_metric = GaugeMetricFamily('k8s_node_disk_pressure' , 'Node Disk Pressure Metric' , labels=['node'])
            disk_pressure_metric.add_metric([ip], status)
            yield disk_pressure_metric

            node_ready_status = requests.get(node_url).json()['items'][node]['status']['conditions'][3]['status']
            if node_ready_status == 'False':
                status = 0
            else:
                status = 1
            node_ready_metric = GaugeMetricFamily('k8s_node_ready' , 'Node Ready Metric' , labels=['node'])
            node_ready_metric.add_metric([ip], status)
            yield node_ready_metric



def getNodes(base_url):
    node_url = base_url+'/api/v1/nodes'
    return len(requests.get(node_url).json()['items'])

def getDeployments(base_url):
    dp_url = base_url+'/apis/extensions/v1beta1/deployments'
    return len(requests.get(dp_url).json()['items'])

def getPods(base_url):
    pod_url = base_url+'/api/v1/pods'
    return len(requests.get(pod_url).json()['items'])

def totalRunningPods(base_url):
    pod_url = base_url+'/api/v1/pods'
    total = len(requests.get(pod_url).json()['items'])
    count = 0
    for pod in range(0 , total):
        state = requests.get(pod_url).json()['items'][pod]['status']['phase']
        if state == 'Running':
            count += 1
    return count

def getRCs(base_url):
    rc_url = base_url+'/api/v1/replicationcontrollers'
    return len(requests.get(rc_url).json()['items'])

def getVersion(base_url):
    version_url = base_url+'/version'
    return float(requests.get(version_url).json()['major']+'.'+requests.get(version_url).json()['minor'])


if __name__ == "__main__":
  REGISTRY.register(MicroServiceCollector())
  start_http_server(9116)
  while True: time.sleep(args.interval)
