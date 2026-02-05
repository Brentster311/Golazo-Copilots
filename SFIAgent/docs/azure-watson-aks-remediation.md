# Azure Watson for AKS/Linux - Step-by-Step Remediation Guide

**Service:** ACCIA Model Hosting Framework  
**KPI:** Azure Watson Not Enabled  
**Status:** Out of SLA (Due: 2025-03-25)

---

## Prerequisites

1. **Geneva Monitoring Agent (MDSD)** - version 1.5.131+ container required
2. **AKS Cluster** with ability to deploy DaemonSets
3. **Geneva managed storage account** for dump uploads

---

## Step 1: Pull the Azure Watson Agent Container

Add to your deployment YAML (AKS handles the pull automatically):

```yaml
image: mcr.microsoft.com/azure-watson/agent/azlinux3:1.23.50.0
```

Or pull manually:
```bash
docker pull mcr.microsoft.com/azure-watson/agent/azlinux3:1.23.50.0
```

---

## Step 2: Configure MDSD Container (Geneva Agent)

In your MDSD DaemonSet/Pod YAML, mount the socket path:

```yaml
volumeMounts:
  - mountPath: /var/run/mdsd
    name: mdsdrun-volume

volumes:
  - name: mdsdrun-volume
    hostPath:
      path: /var/run/mdsd
```

---

## Step 3: Deploy Azure Watson Agent DaemonSet

Create `watsonagent-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: watsonagent
  namespace: <your-namespace>
spec:
  selector:
    matchLabels:
      app: watsonagent
  template:
    metadata:
      labels:
        app: watsonagent
    spec:
      enableServiceLinks: false
      containers:
        - name: watsonagent
          image: mcr.microsoft.com/azure-watson/agent/azlinux3:1.23.50.0
          securityContext:
            privileged: true  # Required for dump access
          env:
            - name: INCOMING_QUEUE
              value: /azure-watson/cores
            - name: REPORT_QUEUE
              value: /azure-watson/queue
            - name: MDSD_ROLE_PREFIX
              value: /var/run/mdsd/
            - name: WA_CORE_PATTERN
              value: /azure-watson/cores/%e.%p.%h.%t
          volumeMounts:
            - mountPath: /azure-watson
              name: aks-host
            - mountPath: /var/run/mdsd
              name: mdsdrun-volume
      volumes:
        - name: aks-host
          hostPath:
            path: /home/docker/azure-watson
        - name: mdsdrun-volume
          hostPath:
            path: /var/run/mdsd
```

Deploy:
```bash
kubectl apply -f watsonagent-daemonset.yaml
```

---

## Step 4: Configure Your Service Container for Crash Dumps

### For .NET Applications (3.1.9+)

Add these environment variables to your service Pod:

```yaml
env:
  - name: COMPlus_DbgEnableMiniDump
    value: "1"
  - name: COMPlus_DbgMiniDumpType
    value: "4"
  - name: COMPlus_DbgMiniDumpName
    value: "/cores/<your-app-name>-%d"
```

Mount the cores directory:
```yaml
volumeMounts:
  - mountPath: /cores
    name: aks-host

volumes:
  - name: aks-host
    hostPath:
      path: /home/docker/azure-watson/cores
```

### For Native (C/C++) Applications

Set core pattern (run on node or in privileged init container):
```bash
sysctl -w kernel.core_pattern='/home/docker/azure-watson/cores/%e-%p-%h-%t'
ulimit -c unlimited
```

---

## Step 5: Configure Geneva (Jarvis) for Watson

1. Go to **Jarvis Portal** → **Manage** → **Logs** → **Configurations**
2. Open your Geneva configuration
3. Add inside `<MonitoringManagement>`:

```xml
<TaggedData name="AzWatsonConfig">
<Data>
{
  "LogLevel": "4",
  "ProcessingThreadSleepTimeSeconds": "80",
  "GroomPeriodSeconds": "150",
  "AgentIdentityString": "watsonagent",
  "ConfigId": "watsonagent.conf.1",
  "AzureWatsonEndpoint": "azurewatsonanalysis-prod.core.windows.net",
  "UseAzureWatsonProtocol": "1",
  "UseStorageToken": "0",
  "MaxAgeSeconds": "3600"
}
</Data>
</TaggedData>
```

> ⚠️ **IMPORTANT:** LogLevel must be 4 (Info) or lower, or S360 will flag you.

---

## Step 6: Verify Deployment

1. Check Watson agent is running on all nodes:
   ```bash
   kubectl get daemonset watsonagent -n <namespace>
   ```

2. Check agent logs:
   ```bash
   kubectl logs -l app=watsonagent -n <namespace>
   ```

3. Generate a test crash (optional):
   ```bash
   sleep 20 &
   kill -SIGSEGV $!
   ```

4. View crashes in [Azure Watson Portal](https://azurewatson.microsoft.com)
   - Search by your MdsMaNamespace or service name
   - Allow a few minutes for upload

---

## Timeline

- **Deploy changes:** ~1-2 hours
- **Data refresh in LENS:** 24 hours after deployment
- **KPI auto-closes** when Watson detects the agent running

---

## Support

- **Email:** supwatson@microsoft.com
- **Office Hours:** Every alternate Tuesday, 9 AM PST
- **DL (join for updates):** [azwlinuxusers@microsoft.com](https://idwebelements.microsoft.com/GroupManagement.aspx?Group=azwlinuxusers&Operation=join)
- **TSG:** https://eng.ms/docs/products/azure-watson/azurewatson/s360kpi

---

## Quick Checklist

- [ ] Geneva MDSD container v1.5.131+ deployed
- [ ] MDSD socket path mounted to host (`/var/run/mdsd`)
- [ ] Watson agent DaemonSet deployed with `privileged: true`
- [ ] Incoming queue and report queue on same mount point
- [ ] Service container configured for dump generation
- [ ] Geneva/Jarvis config updated with AzWatsonConfig
- [ ] LogLevel set to 4 or lower
- [ ] Verified agent running on all nodes
