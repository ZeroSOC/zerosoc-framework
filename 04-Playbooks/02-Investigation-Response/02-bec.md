---
title: 02-Business Email Compromise (BEC) Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-02
mitre_ttps:
  - T1078       # Valid Accounts
  - T1114       # Email Collection
  - T1564.008   # Email Hiding Rules
default_severity: High
required_data_sources:
  - Identity provider sign-in logs
  - Mailbox audit logs
  - Email gateway logs
  - CASB / access-policy logs
status: draft
---

# 02-Business Email Compromise (BEC) Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-02 Business Email Compromise` — fraud via compromised or spoofed business identities to redirect funds or data, with little or no malware. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

BEC is an objective category: the mailbox is the instrument and the payment or the data is the target. The investigation establishes both halves — that the mailbox is under the adversary's control (or impersonated from a lookalike) and that a redirection of funds or data is being prepared or has happened — and the response runs on two tracks, the identity and the money.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an attacker holds stolen credentials or session tokens, has unauthorized access to a business mailbox, is monitoring communications and hiding them with rules, and is impersonating the mailbox owner — or a lookalike of them — to redirect funds or data.
   * **Benign:** the user set up a legitimate forwarding or delegation rule, the impossible-travel alert was caused by a corporate VPN routing anomaly, or the payment-detail change is a genuine request the counterparty confirmed.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Did the anomalous sign-in come from an unmanaged device combined with an unexpected autonomous system, or from a residential-proxy or anonymizing range ([Identity](../99-Shared/sub_enrichment_identity.md), [Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (Medium)` when unmanaged and unexpected; `Benign (Low)` when from a managed, compliant device on a network the user has used before.
   * *Query 2:* Is there a new inbox rule that forwards or redirects mail to an external domain — a freemail provider in particular — or that moves, marks read or deletes messages matching finance, invoice, payment or security keywords, or a new mailbox delegation? → `Malicious (High)` on any of these; `Benign (Low)` when no rule or delegation changed in the window.
   * *Query 3:* Are there concurrent sign-ins from the user's known, compliant mobile device, and does the corporate VPN egress explain the geo anomaly? → `Benign (Medium)` when the anomalous sign-in is the user's own device through the VPN egress; `Malicious (Medium)` when the anomalous session coexists with the user's legitimate one on a different, unmanaged device holding the same session token — the adversary-in-the-middle pattern.
   * *Query 4:* Was there an immediate attempt to access sensitive files in the collaboration or file-sharing service — finance, HR, contracts, payment instructions? → `Malicious (Medium)` when the access is out of the user's baseline and targets those categories; `Benign (Low)` when the access pattern matches the user's normal work.
   * *Query 5:* Does the user, the SOC Knowledge Base or the service desk confirm the activity — a rule the user created for a documented reason, a travel record covering the location, a delegation requested by ticket, a payment-detail change verified with the counterparty through a known phone number? → `Benign (High)` on a confirmation covering the exact rule, sign-in or request — the explanation of the alert; `Malicious (Medium)` when the user denies creating the rule, or the request fails out-of-band verification.
   * *Query 6:* Are there outbound messages from the mailbox, or from a lookalike domain, to finance staff, customers or suppliers carrying changed bank details, a new invoice or an urgent payment instruction — and has any payment been executed against them ([Email message](../99-Shared/sub_enrichment_email_message.md))? → `Malicious (High)` on a payment-redirection message; context when none exists yet — a takeover without a fraud attempt is the re-classification trigger below, not a weaker IC-02.

**Re-classification pivots:** the investigation is still resolving how the identity was obtained rather than the fraud → the delivery vector, [IC-01 (Phishing / Social Engineering)](01-phishing.md); the confirmed activity is credential or session theft without a fraud attempt → [IC-06 (Identity & Credential Attack)](06-identity_credential_attack.md); mailbox or file access at scale without redirection of funds → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md).

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-02 (Business Email Compromise)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Disable the compromised identity and revoke all its refresh and session tokens (reversed by re-enabling it and signing in again). Disabling a shared or service mailbox identity a critical business process runs under — **requires approval**.
*   Block the malicious IP address or autonomous system at the network boundary and in the identity provider's access policy (reversed by removing the rule). Blocklisting a partner or customer network from which the fraud was relayed — **requires approval**.
*   Quarantine the messages sent from the compromised mailbox — internally and to counterparties — and any lookalike-domain messages in every recipient mailbox (reversed by releasing them). Purging them permanently — **requires approval**.
*   Ask finance to hold any pending payment to the changed details and to freeze the payment instruction under dispute (reversed by releasing the hold).

### Eradication
*   Delete every inbox forwarding, redirection, hiding or delegation rule the attacker created, and any MFA method, device registration or application consent added during the takeover.
*   Force a password reset and full MFA re-registration for the compromised identity; where adversary-in-the-middle token theft is confirmed, re-register every MFA method. A reset of identities beyond the confirmed ones — **requires approval**.
*   Identify and remove the phishing messages the compromised mailbox sent internally, and close the vector that obtained the mailbox where it is known (the lure, per the IC-01 playbook).

### Recovery
*   Restore normal email functionality to the user only after the attacker's rules and delegations are removed.
*   Work with finance to recall any fraudulent transfer made under the impersonation, and notify the deceived counterparties through the organization's external-communications channel using a verified contact — never the thread the attacker used.
*   Feed the sender infrastructure, the lookalike domain and the rule pattern to Phase 1 as a detection-tuning signal, and request the takedown of the lookalike domain through the registrar.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-02, the fraud status — payment attempted, executed, held or recalled, and every deceived counterparty — and any confirmed adversary-in-the-middle session theft are recorded before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 5 executed, or with Query 2 unanswered.
*   A confirmed takeover not followed by the session revocation of the identity and the removal of its attacker rules, or not re-classified when the pivot applies.
*   Restoring normal email functionality to the user before the attacker's forwarding and delegation rules are identified and deleted — closure leaving a confirmed foothold.
*   A confirmed payment-redirection message with no finance hold or recall recorded in the Case timeline.
*   A permanent purge, a reset beyond the confirmed identities, or the blocklisting of a partner network applied without approval.

## Hunting Pivots

*   Sweep all mailboxes for rules created in the last 30 days that forward externally or hide messages matching finance, invoice or payment keywords — the same actor rarely stops at one mailbox.
*   Sweep the sign-in logs for the same source autonomous system, device fingerprint or session pattern across other identities, especially finance and executive accounts.
*   Sweep outbound mail and the gateway for messages carrying changed bank details, and the registrar feeds for lookalikes of the organization's and its suppliers' domains registered in the last 90 days.

## References

*   MITRE ATT&CK: T1078, T1114, T1564.008; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Identity enrichment](../99-Shared/sub_enrichment_identity.md); [Email message enrichment](../99-Shared/sub_enrichment_email_message.md); [IC-01 Phishing](01-phishing.md); [IC-06 Identity & Credential Attack](06-identity_credential_attack.md).
