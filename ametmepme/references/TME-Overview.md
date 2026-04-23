# TME Tenant Overview

**Source URL:** https://microsoft.sharepoint-df.com/:w:/r/teams/fido-hub/_layouts/15/Doc.aspx?sourcedoc=%7B07DE4B22-C1BA-4A4A-9BC3-02EB5012F9F2%7D&file=TME%20Overview.docx&action=default&mobileredirect=true&share=cQoiS94HusFKSpvDAutQEvnyEgUCHkX5t7LYaYgK2qn-KZFpFA

---

## FAQ for Onboarding to the TME tenant

### What is happening?

The Production Tenants are being locked down and all resources in those tenants are treated as "Production". All access to Azure Portal from Corpnet Machines to resources hosted in Production tenants is blocked. All Application access from Microsoft Corporate IPs are blocked. Non-Production scenarios and associated resources must move to a non-production tenant. This includes test & validation scenarios. New non-production tenants are being stood up and will serve as the homes for non-production activities. The new non-production tenants, including TME, aim to offer a high security bar close to what is provisioned in AME/PME, but with some policies turned off, like the SAW requirement and allowing the guesting of Corp identities.

### What is the Test Managed Environment (TME) meant to do?

The purpose of the TME tenant is to have a managed tenant where teams can host Azure resources that are impacted by the lockdown of our production tenants. The TME tenant will be accessible via Microsoft-managed devices without the need to use a SAW device. Think of the non-production TME tenant as an environment that is purposefully isolated from the production tenants to avoid co-mingling of production and non-production identities and resources to avoid the security risk of a threat actor gaining access to production resources through a test identity.

### What will I as a developer need to do differently? Will I need new credentials?

To access Resources in the TME Tenant you can do so from the standard tooling. It's available via the "Switch Directory" menu option in AAD.

### When will I need to make the necessary changes by?

Production Environments will be locked down on 7/22 to SAW only; any access from a corpnet machine will be blocked unless there is an approved exception.

### How will this affect my developer experience?

If your developer experience requires access to resources hosted in Production then it will be impacted. If not, then the lockdown will not impact you.

### How will the non-production tenant interact with other tenants?

The tenant itself does not directly interact with other tenants. Applications within the Tenant won't be consentable into other tenants.

### How do we handle secrets and certs?

Secrets can be created and stored in KeyVault.

### Can we download certs from dev/test?

Certificates from KeyVaults in the TME Tenant can be downloaded to Developer machines.

### Is Corp access to these resources allowed?

- Access to Microsoft CorpNet is **not allowed** from this tenant.
- Access to Microsoft Tenant is **not allowed** from the Resources in this Tenant.

### Is standing access allowed?

Yes — Standing access is allowed based on Security Group.

### How will the environment be deployed/configured/maintained?

The Environment will be monitored and managed just like the other Microsoft Tenants.

### Will it be required to create new eligibilities for the test tenant?

Yes. You will need to create an eligibility to have your corp identity guested to the TME01 tenant.
