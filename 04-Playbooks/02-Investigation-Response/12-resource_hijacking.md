---
title: 12-Resource Hijacking / Cryptojacking Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-12
mitre_ttps:
  - T1496       # Resource Hijacking
  - T1078.004   # Valid Accounts: Cloud Accounts
  - T1136.003   # Create Account: Cloud Account
  - T1190       # Exploit Public-Facing Application
default_severity: Medium
required_data_sources:
  - Cloud audit + billing/cost telemetry
  - Compute/GPU utilization metrics
  - Container / Kubernetes logs
  - Netflow (mining-pool destinations)
  - Model-API usage logs
status: draft
---

# 12-Resource Hijacking / Cryptojacking Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-12 Resource Hijacking / Cryptojacking` — theft of compute or network resources for crypto mining, proxyjacking or LLM-jacking. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Resource theft is usually the symptom of a credential compromise: the spend anomaly is the alert, but the entry vector is the incident. The investigation validates the workload and hunts the credential or the exploited workload that provisioned it.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary holding stolen credentials, or controlling an exploited workload, is provisioning compute — instances, containers, serverless functions or inference-API capacity — for cryptomining, proxyjacking or LLM-jacking.
   * **Benign:** legitimate autoscaling, a newly sanctioned ML or analytics workload, or a cost anomaly from approved use.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Who or what created the resources — does the creating principal show a first-time API-call pattern, an unusual geography or ASN, or a dormant key suddenly active ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (Medium)` when the principal never provisioned compute before, or a dormant key wakes from an unfamiliar location; `Benign (Low)` when the creator is the usual pipeline identity acting from its usual location — a stolen pipeline credential looks the same.
   * *Query 2:* Does the workload connect to known mining-pool or stratum endpoints, run a known miner image or process name, or sustain flat-out CPU or GPU utilization with no application process to account for it ([Network](../99-Shared/sub_enrichment_network.md), [Artifact](../99-Shared/sub_enrichment_artifact.md))? → `Malicious (High)` on a mining-pool destination or a known miner; `Malicious (Medium)` on sustained flat-out utilization the application cannot explain; `Benign (Low)` when the destinations and processes are the approved application's own.
   * *Query 3:* Does the workload map to an approved project, an existing quota request or a change ticket covering the provisioning — cost-allocation tags, the cloud tagging policy, the SOC Knowledge Base? → `Benign (High)` when an approved project or quota request covers the exact resources and time — the explanation of the alert; `Malicious (Medium)` when the resources carry no owner, an unfamiliar tag, or a project nobody claims.
   * *Query 4:* Were new keys, principals, roles, functions or auto-restart mechanisms — scheduled jobs, container restart policies, instance templates, autoscaling groups — created alongside the compute, by the same session? → `Malicious (High)` on new principals or persistence created with the compute; `Benign (Low)` when nothing besides the compute changed.
   * *Query 5:* Is there anomalous inference-API token spend from unfamiliar clients, keys or regions — the LLM-jacking variant — and do the prompts belong to the organization's applications? → `Malicious (Medium)` on spend from a client or key with no prior usage, or on prompts unrelated to any application of the organization; `Benign (Low)` when the spend tracks a known client's baseline.
   * *Query 6:* What else did the principal do in the same session — did it read data, list or read secrets, or enumerate other accounts, regions or subscriptions? → `Malicious (High)` on data access or secret enumeration — and the re-classification trigger below; context when the session is confined to provisioning compute, and the list of accounts and regions it touched scopes the eradication.

**Re-classification pivots:** the compromised credential is the real objective, not the resource theft → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); data is accessed alongside the hijacked compute → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); the entry was an exploited internet-facing application and no compute was provisioned yet → [IC-07 (Web App Exploitation)](07-web_app_exploitation.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-12 (Resource Hijacking / Cryptojacking)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Revoke the compromised keys and disable the compromised principals (reversed by issuing new keys or re-enabling the principal). Disabling a service identity a critical service runs under — **requires approval**.
*   Stop or quarantine the offending instances, containers and functions, snapshotting them first for forensics (reversed by restarting them). Stopping a workload a production service runs on — **requires approval**.
*   Block the mining-pool, stratum and proxy destinations at egress (reversed by removing the rule), and kill the miner process on hosts that must keep serving.
*   Clamp the provisioning quotas of the affected account to stop further provisioning (reversed by restoring them). Clamping a quota that production workloads share — **requires approval**.

### Eradication
*   Remove the attacker's identity artifacts — principals, keys, roles, functions, instance templates, restart mechanisms — across **all** regions and accounts the principal could reach (Query 6), not only the affected one.
*   Rotate the leaked credential and the secrets it could reach. A rotation beyond the confirmed scope — **requires approval**.
*   Close the entry vector: the exposed key, the exploited workload or application, the permissive role.
*   Delete the rogue compute, images and snapshots once the forensic copies are preserved — **requires approval**.

### Recovery
*   Restore quotas and egress rules to normal operating levels, each removal recorded in the Case timeline.
*   Reconcile billing and claim provider credits where available.
*   Feed the re-provisioning pattern — principal, image, destination, utilization shape — to Phase 1 as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-12, the compromised credential or entry vector is identified and its privilege level recorded, and every account and region the principal reached is enumerated before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 3 executed, or with Query 2 unanswered for the alerted workload.
*   Data access or secret enumeration by the compromised principal (Query 6) not re-classified when the pivot applies.
*   Attacker artifacts removed in only the affected account or region, or closure leaving a persistence mechanism from Query 4 in place — a confirmed foothold.
*   A production workload stopped, a service identity disabled, a shared quota clamped or resources deleted without approval.

## Hunting Pivots

*   Sweep every account and region for compute created by the same principal, from the same source, or from the same image in the last 30 days — a hijacker rarely stops at one region.
*   Sweep egress flows fleet-wide for stratum and mining-pool destinations, and for sustained high utilization on hosts with no matching workload.
*   Sweep the inference-API logs for keys whose first use is within the last 30 days and whose spend exceeds their baseline.

## References

*   MITRE ATT&CK: T1496, T1078.004, T1136.003, T1190; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Identity enrichment](../99-Shared/sub_enrichment_identity.md); [Network enrichment](../99-Shared/sub_enrichment_network.md).
