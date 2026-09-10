---
title: 01-Phishing / Social Engineering Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-01
mitre_ttps:
  - T1566.001   # Phishing: Spearphishing Attachment
  - T1566.002   # Phishing: Spearphishing Link
  - T1204        # User Execution
  - T1598        # Phishing for Information
default_severity: Medium
required_data_sources:
  - Email gateway / sandbox
  - Mailbox audit logs
  - Proxy / DNS logs
  - Identity provider sign-in logs
  - EDR
status: draft
---

# 01-Phishing / Social Engineering Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-01 Phishing / Social Engineering` — deception of a person, by email, message, voice or fake software, to obtain access, credentials or an action. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Phishing is usually an entry vector, not the objective: the lure buys the adversary a click, a credential or an execution, and the payoff lands elsewhere. The investigation validates the lure and hunts its consequences downstream.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** a phishing campaign is delivering credential-harvesting links or weaponized attachments to the organization, and one or more recipients have interacted with it.
   * **Benign:** the message is graymail or marketing, a sanctioned phishing-simulation exercise, or a legitimate email a user reported by mistake.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* What do the sender infrastructure and the payload say — authentication posture and alignment, a lookalike or newly registered sender domain, the detonation verdict of the URL or attachment ([Email message](../99-Shared/sub_enrichment_email_message.md))? → `Malicious (High)` when the detonation verdict is malicious or the domain impersonates an owned or partner brand; `Malicious (Medium)` when authentication fails or the domain is newly registered; `Benign (Low)` when authentication passes from a domain with prior legitimate correspondence — a compromised partner mailbox passes every check.
   * *Query 2:* How many mailboxes received the same sender, subject, URL or attachment cluster, and how many reported it? → `Malicious (Medium)` for a cluster across many mailboxes or several independent reports; context for a single recipient — targeted fraud is not less suspicious for being narrow.
   * *Query 3:* Does the message match the sanctioned phishing-simulation platform, an approved marketing sender, or a message the reporter later confirmed as expected? → `Benign (High)` on a match — the explanation of the alert; `Malicious (Low)` when the message claims to be a simulation or a known sender and is not.
   * *Query 4:* Did any recipient click the URL, or did the attachment execute on any recipient's host (proxy, DNS and EDR telemetry)? → `Malicious (High)` on a click that reached the harvesting page or an execution; `Benign (Low)` when no recipient interacted and the gateway held the message.
   * *Query 5:* For recipients who clicked or submitted data, is there a subsequent anomalous sign-in, a new inbox rule, a new MFA method or a consent grant on their account ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (High)` on any of these — and the re-classification trigger below; `Benign (Low)` when the account shows nothing new in the following 24 hours.

**Re-classification pivots:** credentials submitted → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md) or [IC-02 (Business Email Compromise)](02-bec.md); payload executed → [IC-05 (Commodity Malware / Loader)](05-commodity_malware.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-01 (Phishing / Social Engineering)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Quarantine the message cluster in every recipient mailbox (reversed by releasing the messages). Purging the cluster permanently — **requires approval**.
*   Block the sender, the URL host and the domain at the email gateway, the proxy and DNS (reversed by removing the rules).
*   Revoke the active sessions of every recipient who submitted credentials (reversed by signing in again).

### Eradication
*   Reset the credentials of every identity confirmed to have submitted them, and remove any inbox rule, MFA method or consent grant the attacker added. A reset of identities beyond the confirmed ones — **requires approval**.
*   Remove any payload dropped on recipient endpoints; where it executed, the Case is re-classified to IC-05 and its playbook applies.
*   Request the takedown of the phishing infrastructure (hosting provider, registrar) through the organization's external-communications channel.

### Recovery
*   Release any legitimate mail caught by the quarantine.
*   Notify the affected users of the lure and of the actions taken.
*   Feed the lure pattern and indicators (sender infrastructure, subject, URL and hash cluster) to Phase 1 as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-01, the campaign breadth (every affected mailbox) is enumerated and the interaction outcome of every recipient — none, clicked, submitted, executed — is recorded before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 3 executed, or with Query 4 unanswered for any recipient.
*   A confirmed credential submission or payload execution not followed by the session revocation and reset of the affected identity, or not re-classified when the pivot applies.
*   A permanent purge or a reset beyond the confirmed identities applied without approval.
*   Closure while the campaign is still delivering — new recipients of the cluster after the containment actions.

## Hunting Pivots

*   Sweep the mailbox audit logs for the same sender, subject or URL cluster beyond the alerted recipients — a campaign rarely targets one mailbox.
*   Sweep for inbox rules created in the last 7 days that forward or delete mail matching security or finance keywords, across all mailboxes.

## References

*   MITRE ATT&CK: T1566.001, T1566.002, T1204, T1598; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Email message enrichment](../99-Shared/sub_enrichment_email_message.md).
