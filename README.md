# prometheus-agents

The agents are all developed using Python3.4.

# kubernetes_api_exporter.py

The script requires the following arguments:
  1) IP address of Kubernetes Master.
  2) Scrape interval.
  
  python3.4 kubernetes_api_exporter.py --master <MASTER-IP> -t <SCRAPE-INTERVAL>
  
# vault_exporter.py

The vault_exporter.py utilizes vault_utils.py. It needs to be placed locally onto the Vault server and run.
The agent monitors the following:
  1) Vault Init check.
  2) Vault Seal check.
  3) Vault API  check.
  4) Vault Hash check.

For the Vault API check, I have created a dummy entry using the below command.
```
vault write secret/prometheus password=prometheus username=prometheus
```

The script requires the following arguments:
  1) Client certificate of vault server.
  2) Client decrypted key of vault server.
  3) Scrape interval.
  4) Current hash value.
