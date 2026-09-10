---
title: 10-Supply-Chain Compromise Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-10
mitre_ttps:
  - T1195.001    # Compromise Software Dependencies and Development Tools
  - T1195.002    # Compromise Software Supply Chain
  - T1554        # Compromise Host Software Binary
  - T1105        # Ingress Tool Transfer
  - T1078        # Valid Accounts
default_severity: High
required_data_sources:
  - Software inventory / SBOM
  - EDR
  - Update-infrastructure logs
  - Vendor advisories / threat intelligence
  - Cloud & remote-access audit for vendor/MSP accounts
status: draft
---

# 10-Supply-Chain Compromise Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-10 Supply-Chain Compromise` — intrusion via a trusted third party: a software build, update, dependency, managed service provider or hardware component. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

This is a trust inversion: the malicious artifact arrives through a channel the organization deliberately trusts — a vendor, an update feed, a dependency from the package registry, a provider's remote access. Everything is gated on exposure confirmation first: an advisory or indicator that does not match the deployed footprint is not an Incident.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** a trusted vendor, software update or dependency has been compromised and is delivering malicious code — or a vendor's or provider's access into the environment is being abused.
   * **Benign:** a legitimate vendor update flagged on novelty, or a published advisory that does not apply to the deployed version or configuration.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Exposure confirmation — is the affected component and version actually deployed, per the software inventory or SBOM sweep, and are the advisory's exploitation conditions met (the feature enabled, the component reachable)? → `Benign (High)` when the component or version is absent from the deployed footprint — the explanation of an advisory-driven alert; `Malicious (Medium)` when it is deployed and the conditions hold. Every other query is gated on this one.
   * *Query 2:* Does the post-update behavior delta show new child processes or new network destinations against the same software's pre-update baseline ([Asset](../99-Shared/sub_enrichment_asset.md), [Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (High)` on a new process tree or destination the release does not document; `Benign (Medium)` when the process tree and destinations match the pre-update baseline or the vendor's documented changes.
   * *Query 3:* Does the artifact's signature or hash validate against the vendor-published values ([Artifact](../99-Shared/sub_enrichment_artifact.md))? → `Malicious (High)` on a mismatch; `Benign (Medium)` on a match — a compromised build pipeline signs its own output.
   * *Query 4:* Does a sweep of the advisory's indicators across the fleet return hits? → `Malicious (Medium)` on any hit; `Benign (Low)` when none.
   * *Query 5:* Is the vendor's or provider's account activity occurring outside its contracted scope or maintenance windows, or from addresses other than the provider's declared ones ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (Medium)` on either; `Benign (High)` when the provider's maintenance ticket covers the exact action, on these systems, in this window — the explanation of a provider-access alert.
   * *Query 6:* Did the update arrive through the sanctioned update channel, at the scheduled time, as a version the vendor published and whose release notes account for the change observed? → `Benign (High)` when all hold — the explanation of a novelty alert; `Malicious (Medium)` when the update arrived outside the channel or schedule, or is a version the vendor never published.

**Re-classification pivots:** the delivered code establishes an objective — encryption or extortion → [IC-03 (Ransomware & Digital Extortion)](03-ransomware.md), data moved → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md), mining → [IC-12 (Resource Hijacking / Cryptojacking)](12-resource_hijacking.md); the provider's credentials are used as a plain credential attack rather than through its contracted access → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); the compromised component is the image of an edge device or core infrastructure → [IC-08 (Infrastructure Compromise)](08-infrastructure_compromise.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-10 (Supply-Chain Compromise)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Quarantine the affected package version on hosts where a prior version or an alternative keeps the service running (reversed by releasing it). Blocking or removing it fleet-wide, or where the removal stops a critical service — **requires approval**.
*   Disable the implicated vendor's or provider's remote-access identities and revoke their sessions and keys (reversed by re-enabling them). Disabling a provider service identity a critical service runs under — **requires approval**. Blocklisting the provider's network — **requires approval**.
*   Block the update channel and the advisory's indicators at the perimeter, the proxy and DNS (reversed by removing the rules).

### Eradication
*   Remove or roll back the compromised software versions. Where the rollback requires re-imaging hosts — **requires approval**.
*   Rotate every credential and key the affected software or the provider's access could reach; a reset of many identities at once — **requires approval**.
*   Deploy the vendor-fixed build only after integrity verification against the published hashes and, where available, a build provenance attestation.

### Recovery
*   Redeploy in stages with monitoring, watching for the behavior delta of Query 2 on each stage.
*   Reassess the vendor's risk posture before restoring full trust; restore the provider's access only under a renewed, narrower scope and window.
*   Track the advisory for new indicators as the vendor's investigation continues, and re-run the fleet sweep of Query 4 on each update.
*   Conduct vendor coordination, contractual notification and any public disclosure through the organization's external-communications channel ([Detection & Analysis §3.2](../../03-Processes/02-detection_and_analysis.md#32-stakeholder--regulatory-notification)); where the organization itself redistributes the affected software, its customer-notification and disclosure obligations apply.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-10, exposure confirmation (Query 1) is recorded even on a Benign resolution, since it gates every other finding, and, where the organization redistributes the affected software, the customer-notification decision is recorded.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   The Incident declared or acted on before Query 1 confirms the affected component and version are deployed.
*   A Benign close without Query 1 executed, or with Query 2 unanswered on any exposed host.
*   A fleet-wide block or removal, a re-imaging, a mass credential reset or a provider-network blocklisting applied without approval.
*   The vendor-fixed build deployed without integrity verification against the published hashes.
*   Vendor, customer or public communication issued outside the organization's external-communications channel.
*   Closure leaving a confirmed foothold: the compromised version still present on a host, or the provider's access restored under its old scope.
*   An objective established by the delivered code and the Case not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the fleet for the full advisory indicator set, and for anomalous egress from every host running the affected software family.
*   Sweep other products from the same vendor or the same build pipeline for the behavior delta of Query 2 — a compromised pipeline rarely taints one release.
*   Sweep every vendor and provider account for sessions outside their contracted windows in the last 90 days.

## References

*   MITRE ATT&CK: T1195.001, T1195.002, T1554, T1105, T1078; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Artifact enrichment](../99-Shared/sub_enrichment_artifact.md).
