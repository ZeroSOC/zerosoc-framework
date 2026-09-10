---
title: Cloud Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Cloud
required_data_sources:
  - Cloud control-plane audit logs
  - Cloud Security Posture Management (CSPM)
  - CASB / SaaS discovery
  - Cloud billing / cost telemetry
status: draft
---

# Cloud Triage Playbook

Triage knowledge for **Cloud** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| Suspicious IAM policy / role change | Cloud audit logs | Privilege Escalation | T1078.004 (Cloud Accounts), T1098.003 (Additional Cloud Roles) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |
| Resource hijacking / cryptomining | Cloud audit / billing | Impact | T1496 (Resource Hijacking) | IC-12 (Resource Hijacking / Cryptojacking) |
| Cloud storage anomalous access | Cloud audit / CASB | Exfiltration | T1530 (Data from Cloud Storage) | IC-11 (Data Breach / Exfiltration) |
| Logging / guardrail disabled | Cloud audit logs | Defense Impairment | T1685.002 (Disable or Modify Cloud Log) | IC-09 (Insider Threat & Privilege Misuse), IC-05 (Commodity Malware / Loader) |
| New principal / access-key creation | Cloud audit logs | Persistence | T1136.003 (Cloud Account) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |
| Public exposure of a resource | Cloud posture / CSPM | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation), IC-11 (Data Breach / Exfiltration) |
| Unsanctioned SaaS app usage (Shadow IT / Shadow AI discovery) | CASB / SaaS discovery | Exfiltration | T1567 (Exfiltration Over Web Service) | IC-09 (Insider Threat & Privilege Misuse), IC-11 (Data Breach / Exfiltration) |

## Per-Alert Triage

### Suspicious IAM policy / role change

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (principal), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP).
- **Checks:**
  1. **Pipeline provenance.** Was the change deployed through the approved infrastructure-as-code pipeline, or made by a direct console or CLI call outside it? → `Benign (High)` when the pipeline's identity applied it and it matches a reviewed, merged change — the change is explained; `Malicious (Medium)` on an out-of-pipeline change to IAM.
  2. **Privilege delta.** Does the change grant broad or wildcard permissions (`*:*`, administrator-equivalent roles) rather than a scoped, least-privilege addition? → `Malicious (Medium)` on a large privilege jump; `Benign (Low)` on a scoped addition.
  3. **Actor baseline.** Is the change made by a human principal who does not normally touch IAM, or by a service principal acting outside its usual role? → `Malicious (Medium)` on an atypical actor; `Benign (Low)` when the actor routinely manages IAM.
  4. **Source of the call.** Where did the API call originate? → `Malicious (High)` when it came from an unfamiliar region, anonymizing infrastructure, or a credential flagged in a concurrent identity alert; `Benign (Low)` when it came from the corporate network or the pipeline's runners.
- **False Positive conditions:** a rule that flags every IAM write, including the pipeline's own; a detection firing on an idempotent re-apply that changes nothing.
- **Benign conditions:** an approved infrastructure-as-code deployment producing IAM, role or principal changes; a break-glass change under a recorded incident ticket.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-09 (Insider Threat & Privilege Misuse) when a legitimate administrator acts outside process.

### Resource hijacking / cryptomining

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (cloud resource/instance), [User](../99-Shared/sub_enrichment_identity.md) (provisioning principal).
- **Checks:**
  1. **Provisioning legitimacy.** Was the compute or GPU resource provisioned through a tracked change or an autoscaling policy, or does it appear with no corresponding workload or ticket? → `Benign (High)` when it ties to a tracked change, an autoscaling policy or a known workload with an owner — the provisioning is explained; `Malicious (Medium)` on untracked provisioning with no workload behind it.
  2. **Workload signature.** Does the instance show mining-pool connections, known miner process or binary names, or sustained near-100% CPU/GPU with no application logic? → `Malicious (High)` on mining-pool connectivity or a miner fingerprint; `Malicious (Medium)` on sustained saturation with no application logic; `Benign (Medium)` when the processes are the workload's own (a training job, a render, a batch computation).
  3. **Billing anomaly correlation.** Does the resource correlate with an unexplained cost spike in an unexpected region or instance family? → `Malicious (Medium)` — anomalies in atypical regions often indicate a hijacked account; `Benign (Low)` when the spend sits within the account's forecast.
  4. **Provisioning credential.** Was the provisioning principal's credential recently flagged (a leaked key, a key created minutes earlier, an anomalous sign-in)? → `Malicious (High)`; `Benign (Low)` when the normal deployment identity provisioned it.
- **False Positive conditions:** a rule keyed on instance family (GPU) alone; a CPU-utilization heuristic firing on a batch job.
- **Benign conditions:** legitimate autoscaling; a sanctioned GPU or machine-learning workload; a documented burst compute job.
- **Candidate Incident Category(ies):** IC-12 (Resource Hijacking / Cryptojacking).

### Cloud storage anomalous access

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (accessing principal), [Device](../99-Shared/sub_enrichment_asset.md) (storage resource), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP).
- **Checks:**
  1. **Access volume and scope.** Is the principal enumerating or bulk-reading far more objects or containers than its normal pattern, potentially across several sensitive containers? → `Malicious (Medium)` on a volume or scope deviation across sensitive containers; `Benign (Low)` on a modest deviation confined to the principal's usual containers.
  2. **Principal type and authorization.** Is this a new or infrequently used principal accessing data outside its job function or service purpose? → `Malicious (Medium)` on access outside the expected function; `Benign (High)` when the access is a registered workload (a new analytics pipeline) whose owner and purpose are recorded — the access is explained; `Benign (Low)` when an established principal reads within its function.
  3. **Source and destination of the read.** Does the access originate from an unfamiliar IP or region, and is the data then transferred out of the environment? → `Malicious (High)` on an unfamiliar origin followed by egress — the Network "Outbound data spike" subsection applies; `Malicious (Medium)` on an unfamiliar origin alone; `Benign (Low)` when the source is the corporate network or the workload's own compute.
  4. **Data sensitivity.** What classification do the objects read carry? → context: it sets the severity and the notification duties, not the side.
- **False Positive conditions:** a baseline learned before a workload's legitimate growth; a rule counting the listing calls of a backup or lifecycle job; a log-replication artifact double-counting reads.
- **Benign conditions:** a new, sanctioned analytics workload; an approved migration or backup job; a discovery scan by the data-governance function.
- **Candidate Incident Category(ies):** IC-11 (Data Breach / Exfiltration).

### Logging / guardrail disabled

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (principal disabling the control), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP).
- **Checks:**
  1. **Change-control correlation.** Is the disablement tied to an approved maintenance change, or is it undocumented? → `Benign (High)` when an approved change covers the control and the window — the disablement is explained; `Malicious (Medium)` when it is undocumented.
  2. **Scope of impairment.** Does the change blind logging or detection broadly (an organization-wide trail, all regions, a detached guardrail policy) or narrowly (one non-critical log stream)? → `Malicious (High)` on broad impairment; `Malicious (Low)` on a narrow one.
  3. **Surrounding activity.** Does the disablement immediately precede other suspicious IAM or resource changes in the same account? → `Malicious (High)` — guardrail removal followed by privileged changes is a defense-evasion chain; context when isolated.
  4. **Actor baseline.** Has the principal ever managed logging configuration, and is it a human or a workload identity? → `Malicious (Medium)` when it never has, or is a workload identity with no configuration role; `Benign (Low)` when it is a platform administrator who routinely does.
- **False Positive conditions:** a detection firing on a log-destination rotation or on a trail the pipeline deletes and re-creates during a redeploy; a rule matching an update that only changed retention; a sink's transient delivery error reported as disabled logging.
- **Benign conditions:** a sanctioned logging or guardrail change during a maintenance window; a decommissioning of a redundant trail recorded under change control.
- **Candidate Incident Category(ies):** IC-09 (Insider Threat & Privilege Misuse); IC-05 (Commodity Malware / Loader) when malware or automated tooling disables the control.

### New principal / access-key creation

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (new principal and creator), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP of first use).
- **Checks:**
  1. **Creator legitimacy and change-control.** Was the new user, service principal or access key created through the approved provisioning workflow, or by an account with no prior provisioning activity? → `Benign (High)` when a ticket or pipeline run names the principal — the creation is explained; `Malicious (Medium)` on untracked creation by an atypical creator.
  2. **Privilege at birth.** Is the new principal granted broad or administrative privileges immediately on creation rather than a scoped starter role? → `Malicious (Medium)` on high privilege at creation — a backdoor pattern; `Benign (Low)` on a scoped starter role.
  3. **Key usage pattern.** Is a new access key used immediately from an unfamiliar IP or region? → `Malicious (High)` on rapid, geographically inconsistent first use — a pre-staged backdoor; `Benign (Low)` when first use comes from the corporate network or the intended workload's compute.
  4. **Creator's session.** Does the creation follow a credential alert on the creator (a leaked key, an anomalous sign-in, an MFA alert)? → `Malicious (High)`; context otherwise.
- **False Positive conditions:** a detection firing on a scheduled key rotation by the rotation job (a new key replacing an old one); a rule flagging the service principal a managed service creates for itself.
- **Benign conditions:** legitimate provisioning through the standard onboarding process; a scheduled key rotation; a break-glass account created under a recorded ticket.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-09 (Insider Threat & Privilege Misuse) when a legitimate administrator creates it outside process.

### Public exposure of a resource

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (exposed resource), [User](../99-Shared/sub_enrichment_identity.md) (principal who changed the exposure), [Network observable](../99-Shared/sub_enrichment_network.md) (external accessors, if any).
- **Checks:**
  1. **Resource sensitivity.** Does the exposed container, database, VM or secret hold regulated or sensitive data, or is it a resource intended for public content? → context: sensitivity sets the severity, not the side.
  2. **Intent.** Is the resource tagged, named or configured as an intentional public service (a static-website container, a public API), or do its naming and environment (a production database, a secrets store) indicate it should be private? → `Benign (High)` when it is registered as an intentional public service in the inventory — the exposure is explained; `Malicious (Low)` on a mismatch between the resource type and its public state.
  3. **Who exposed it, and when.** Which principal made the change, and under what change? → `Malicious (Medium)` when the change was made outside change control by an atypical principal, or follows an IAM or identity alert — an attacker opening a door; `Benign (Medium)` when the resource owner made it in a tracked change that erred — a misconfiguration to remediate.
  4. **Active exploitation evidence.** Has the exposed resource already seen external access attempts or successful reads? → `Malicious (High)` on successful unrecognized external reads — the "Cloud storage anomalous access" subsection or the Application playbook applies; `Benign (Low)` when access logs show no external access in the exposure window.
- **False Positive conditions:** a posture rule that judges a resource behind a private endpoint or a web application firewall as internet-reachable on its policy text alone; a scan evaluating a stale configuration snapshot; a resource reachable only by the cloud provider's own service.
- **Benign conditions:** an intended public service (a public website container, public documentation, an intentionally open API) recorded in the inventory; a time-boxed public exposure for a documented data-sharing purpose.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation) when the exposed resource is an application; IC-11 (Data Breach / Exfiltration) when it holds data that was read.

### Unsanctioned SaaS app usage (Shadow IT / Shadow AI discovery)

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (principal), [Device](../99-Shared/sub_enrichment_asset.md) (accessing host), [Network observable](../99-Shared/sub_enrichment_network.md) (destination domain).
- **Checks:**
  1. **Content exposure.** Where DLP or CASB content inspection is available (browser upload or API post inspection), was regulated or sensitive data actually submitted into the app, or is this browsing or prompting with no sensitive content? → `Malicious (High)` when inspection confirms regulated or sensitive content submitted; `Benign (Medium)` when inspection shows no sensitive content; context when inspection is unavailable — a Visibility Gap, since the alert alone proves usage, not exposure.
  2. **Role fit and volume.** Does the principal's job function plausibly involve this category of tool, and is usage a one-off or a sustained pattern against the peer group? → `Malicious (Low)` on sustained, role-inconsistent usage; `Benign (Low)` on a one-off consistent with the role.
  3. **Access path.** Was the app reached through the normal corporate network or proxy path, or via a personal device, a VPN bypass or a private-browsing session that evades inspection? → `Malicious (Medium)` on a concealed access path; `Benign (Low)` on the normal corporate path.
  4. **Sanctioning status.** Is the app under a temporary exception or already in the sanctioning pipeline with the user in scope? → `Benign (High)` when it is recorded so — the usage is explained; context when the app is unknown to the organization.
- **False Positive conditions:** a discovery catalog misclassifying a sanctioned app's new domain or a CDN as an unknown app; a rule flagging an app already approved but not yet synchronized to the discovery list.
- **Benign conditions:** a well-known productivity tool used for non-sensitive tasks; an app in the sanctioning pipeline under a temporary exception; an evaluation by the function responsible for tool selection.
- **Candidate Incident Category(ies):** IC-09 (Insider Threat & Privilege Misuse); IC-11 (Data Breach / Exfiltration) when sensitive content is confirmed submitted.
