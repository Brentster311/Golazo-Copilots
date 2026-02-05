# [USGov] 1.05 Azure Tenant Security - Remediation Guide

## Summary

**KPI:** [USGov] 1.05 Azure Tenant Security  
**Domain:** Security  
**Owner:** AZTB-ISEG (AZTB-ISG@microsoft.com)  
**SLA:** 30 days (Red = Past Due)

You have **4 out-of-SLA action items** for **Azure Core Platform and Decision Infrastructure** service on **FairFax (USGov) cloud**. All are due **2025-12-09** (significantly overdue).

---

## 🚨 Your Action Items

All 4 items relate to **SFI-SM2.1.2**: Turn on Microsoft Defender for Cloud plans.

| # | Control ID | Issue |
|---|------------|-------|
| 1 | `Azure_Subscription_Config_Enable_MicrosoftDefender_Servers` | Enable Defender for Servers |
| 2 | `Azure_Subscription_Config_Enable_MicrosoftDefender_Databases` | Enable Defender for Databases |
| 3 | `Azure_Subscription_Config_Enable_MicrosoftDefender_Container` | Enable Defender for Containers |
| 4 | `Azure_Subscription_Config_Enable_MicrosoftDefender_Storage` | Enable Defender for Storage |

---

## 📋 What's the Problem?

The Azure Resources Core Security Baseline requires **Microsoft Defender for Cloud** to be enabled on your subscription for:
- Servers (VMs)
- Databases (SQL, CosmosDB, etc.)
- Containers (AKS, ACR)
- Storage Accounts

These controls are part of the Azure Tenant Baseline (TBv12) and are mandated by the **Secure Future Initiative (SFI)** goal SM2.1.2.

---

## 🔧 Step-by-Step Remediation

### Prerequisites
1. You need **Owner** or **Security Admin** role on the affected subscription
2. Access to **Azure Portal** or **Azure CLI** in the FairFax cloud
3. Subscription ID from the [aggregated findings](https://aka.ms/MSFAzureUSBNonCompliant) report

### Option 1: Azure Portal (Recommended)

#### Step 1: Navigate to Microsoft Defender for Cloud
1. Go to [Azure Portal (FairFax)](https://portal.azure.us)
2. Search for **"Microsoft Defender for Cloud"**
3. Select **Environment settings** from the left menu
4. Find and select your subscription

#### Step 2: Enable Defender Plans
1. Under **Defender plans**, enable the following:
   - **Servers** → Turn **On**
   - **Databases** → Turn **On** (includes SQL, Cosmos DB, etc.)
   - **Containers** → Turn **On**
   - **Storage** → Turn **On**
2. Click **Save**

#### Step 3: Verify Configuration
1. Wait 15-30 minutes for initial scan
2. Return to Defender for Cloud → **Recommendations**
3. Verify the controls show as "Healthy"

### Option 2: Azure CLI

```bash
# Login to FairFax cloud
az cloud set --name AzureUSGovernment
az login

# Set your subscription
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Enable Defender for Servers
az security pricing create -n VirtualMachines --tier Standard

# Enable Defender for Databases (SQL)
az security pricing create -n SqlServers --tier Standard
az security pricing create -n SqlServerVirtualMachines --tier Standard

# Enable Defender for Containers
az security pricing create -n Containers --tier Standard

# Enable Defender for Storage
az security pricing create -n StorageAccounts --tier Standard
```

### Option 3: Azure PowerShell

```powershell
# Connect to Azure US Government
Connect-AzAccount -Environment AzureUSGovernment

# Set subscription
Set-AzContext -SubscriptionId "<YOUR_SUBSCRIPTION_ID>"

# Enable all Defender plans
Set-AzSecurityPricing -Name "VirtualMachines" -PricingTier "Standard"
Set-AzSecurityPricing -Name "SqlServers" -PricingTier "Standard"
Set-AzSecurityPricing -Name "SqlServerVirtualMachines" -PricingTier "Standard"
Set-AzSecurityPricing -Name "Containers" -PricingTier "Standard"
Set-AzSecurityPricing -Name "StorageAccounts" -PricingTier "Standard"
```

---

## 🔍 Finding Your Resources

1. **View Aggregated Findings:** Use the Power BI links from S360:
   - [Servers](https://aka.ms/MSFAzureUSBNonCompliant?experience=power-bi&filter=USB_NonCompliant_Results%2FBaseline_x0020_Control_x0020_Id%20eq%20%27Azure_Subscription_Config_Enable_MicrosoftDefender_Servers%27)
   - [Databases](https://aka.ms/MSFAzureUSBNonCompliant?experience=power-bi&filter=USB_NonCompliant_Results%2FBaseline_x0020_Control_x0020_Id%20eq%20%27Azure_Subscription_Config_Enable_MicrosoftDefender_Databases%27)
   - [Containers](https://aka.ms/MSFAzureUSBNonCompliant?experience=power-bi&filter=USB_NonCompliant_Results%2FBaseline_x0020_Control_x0020_Id%20eq%20%27Azure_Subscription_Config_Enable_MicrosoftDefender_Container%27)
   - [Storage](https://aka.ms/MSFAzureUSBNonCompliant?experience=power-bi&filter=USB_NonCompliant_Results%2FBaseline_x0020_Control_x0020_Id%20eq%20%27Azure_Subscription_Config_Enable_MicrosoftDefender_Storage%27)

2. **Self-Service Portal:** https://aka.ms/aztsui-prodtenants
   - View non-compliant resources
   - Trigger on-demand scans
   - Track remediation progress

---

## ⏱️ After Remediation

### Important Timing Notes
- **S360 refresh:** Action items will clear within **72 hours** of successful remediation
- **On-demand scan:** Use [AzTS-UI](https://aka.ms/aztsui-prodtenants) to validate remediation immediately
- **Don't submit tickets** until at least 72 hours have passed

### Verify Remediation
1. Go to [AzTS-UI](https://aka.ms/aztsui-prodtenants)
2. Navigate to your subscription
3. Click **Scan** to trigger an on-demand scan
4. Wait for scan to complete (5-15 minutes)
5. Check that control status shows **"Passed"**

---

## 💰 Cost Considerations

Microsoft Defender for Cloud plans have associated costs:

| Plan | Approximate Cost |
|------|-----------------|
| Servers | ~$15/server/month |
| Databases | ~$15/server/month |
| Containers | ~$7/vCore/month |
| Storage | ~$10/storage account/month |

**Note:** Costs are estimates and vary by region and usage. Check [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/) for exact pricing in USGov.

---

## 🆘 Support Resources

| Resource | Link |
|----------|------|
| **Program Overview** | https://eng.ms/docs/microsoft-security/digital-security-and-resilience/sr-risk-management/infra-security-engineering/infra-security-guidance/azure-resources-core-security-baseline/program_information/program_overview |
| **Support Portal** | https://aka.ms/ATB_Support |
| **Self-Service Portal** | https://aka.ms/aztsui-prodtenants |
| **KPI Owner** | AZTB-ISG@microsoft.com |

### Remediation Guides per Control
- [Defender for Servers](https://aka.ms/Azure_Subscription_Config_Enable_MicrosoftDefender_Servers)
- [Defender for Databases](https://aka.ms/Azure_Subscription_Config_Enable_MicrosoftDefender_Databases)
- [Defender for Containers](https://aka.ms/Azure_Subscription_Config_Enable_MicrosoftDefender_Container)
- [Defender for Storage](https://aka.ms/Azure_Subscription_Config_Enable_MicrosoftDefender_Storage)

---

## ❓ FAQs

### Can I get an exception?
**No.** No exceptions are granted for this KPI. If you're unable to remediate due to platform limitations, submit a **Blocker** request at https://aka.ms/ATB_Support.

### I just remediated, why is the action item still showing?
S360 syncs with AzTS every 24-72 hours. Use the [AzTS-UI](https://aka.ms/aztsui-prodtenants) to trigger an on-demand scan to verify remediation was successful.

### What if I don't have permissions?
Contact your subscription owner or submit a request at https://aka.ms/ATB_Support to get the necessary permissions.

### What if the subscription doesn't belong to my service?
Check ServiceTree to verify service ownership. If the mapping is incorrect, update it in ServiceTree.

---

*Last updated: 2026-02-03*
