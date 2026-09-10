---
title: 06-Identity & Credential Attack Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-06
mitre_ttps:
  - T1110        # Brute Force
  - T1621         # Multi-Factor Authentication Request Generation
  - T1528         # Steal Application Access Token
  - T1550.001     # Use Alternate Authentication Material: Application Access Token
  - T1098         # Account Manipulation
  - T1556         # Modify Authentication Process
default_severity: High
required_data_sources:
  - Identity provider sign-in logs
  - Directory audit logs
  - MFA logs
  - CASB / access-policy logs
  - Mailbox audit logs (pivot)
status: draft
---

# 06-Identity & Credential Attack Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-06 Identity & Credential Attack` — theft, spraying, brute force, MFA fatigue, token or session theft, or SIM swap targeting accounts and identity systems. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

The object of this investigation is the *identity*, not a host: success for the adversary means account takeover, and persistence lives in the identity plane — tokens, MFA methods, application consents, device registrations and role grants — rather than on a machine. The investigation establishes whether the attack succeeded, on how many identities, and what the adversary planted afterwards.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** an adversary is executing a credential attack (password spray, MFA fatigue, adversary-in-the-middle token theft) and has achieved, or is close to achieving, account takeover, with identity-plane persistence being established.
   * **Benign:** a lockout storm from broken automation or a service account with a stale credential, a user retrying a genuinely failing MFA prompt, legitimate travel or VPN geo-velocity, or a sanctioned application onboarding.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Is there a successful sign-in matching the spray or brute-force pattern — the same source, timing and user set as the failed attempts — and how many identities does the pattern target ([Identity](../99-Shared/sub_enrichment_identity.md))? → `Malicious (High)` on a success from the pattern; `Malicious (Medium)` when the failures come from external infrastructure across many identities with no success yet — an attack in progress without takeover; `Benign (Medium)` when the failures come from a single internal source or service identity with a constant stale password — the lockout-storm signature.
   * *Query 2:* Was the MFA prompt approved from a location or device inconsistent with the sign-in's origin, after a burst of repeated prompts, or was a new MFA method or device registered immediately afterward? → `Malicious (High)` on any of these; `Benign (Low)` when the approving device is the user's registered device at the sign-in's origin and no method was added.
   * *Query 3:* Is the same session token being replayed from a new autonomous system or an unmanaged device, indicating adversary-in-the-middle token theft ([Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (High)` on a replay; `Benign (Low)` when the token is used only from the device it was issued to.
   * *Query 4:* Did the account take post-authentication actions — new inbox rules, application consents, privileged role or group grants, device registrations, changes to recovery contacts? → `Malicious (Medium)` on any of these — a mailbox-focused action is the re-classification trigger below; `Benign (Low)` when the account shows nothing new in the following 24 hours.
   * *Query 5:* Does the source infrastructure map to a residential-proxy or known credential-stuffing range, or to the corporate egress or the user's home network? → `Malicious (Medium)` on a residential-proxy or credential-stuffing range; `Benign (Medium)` on the corporate egress or a network the user has used before.
   * *Query 6:* Does the SOC Knowledge Base, a travel record, a service-desk ticket or the automation's owner explain the pattern — a known service account whose password was rotated and now causes the lockouts, a documented trip or VPN egress covering the location, a ticket for the user's MFA re-registration, a sanctioned application onboarding covering the consent? → `Benign (High)` on a record covering the exact identity, event and time — the explanation of the alert; `Malicious (Medium)` when the user denies approving the prompt or registering the method, or the automation's owner does not recognize the source.
   * *Query 7:* Has the identity infrastructure itself been changed — federation or trust configuration, access policies, MFA settings, a new trusted device or tenant, a new credential on an application ([directory audit](../01-Triage/identity.md))? → `Malicious (High)` on a change not tied to a change record — and the infrastructure pivot below; `Benign (Low)` when the configuration is unchanged.

**Re-classification pivots:** mailbox abuse or financial fraud → [IC-02 (Business Email Compromise)](02-bec.md); data access at scale following the takeover → [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); the identity system itself compromised — a federation server, a domain controller, the identity provider's configuration — → [IC-08 (Infrastructure Compromise)](08-infrastructure_compromise.md). The phish that obtained the credential stays recorded as the entry path; [IC-01](01-phishing.md) does not supersede a takeover.

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-06 (Identity & Credential Attack)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Disable the taken-over identity and revoke all its refresh and session tokens (reversed by re-enabling it and signing in again). Disabling a service identity a critical service runs under — **requires approval**.
*   Block the source IP addresses or autonomous system in the identity provider's access policy and at the perimeter (reversed by removing the rule). Blocklisting a partner or customer network — **requires approval**.
*   For a spray in progress, tighten the access policy on the targeted set — require MFA or a compliant device, lower the lockout threshold (reversed by restoring the policy). Resetting the credentials of every targeted identity at once — **requires approval**.
*   Reverting a change to the identity infrastructure configuration — a federation trust, an access policy, tenant-wide MFA settings — **requires approval**.

### Eradication
*   Force a password reset with full MFA re-registration for the identities confirmed taken over. A reset beyond the confirmed identities — **requires approval**.
*   Remove every attacker-registered MFA method, device registration, application consent, application credential and role or group grant, and revoke the tokens issued to the attacker's applications.
*   Close the vector where it is known — the lure per the IC-01 playbook, the exposed legacy authentication endpoint, the weak lockout policy.

### Recovery
*   Restore access through a verified out-of-band channel — never the channel used for the attack.
*   Monitor the identity for re-attack for an extended window after recovery, with the detections that fired kept active on it.
*   Feed the source infrastructure (autonomous system, proxy indicators, device fingerprints) back to Phase 1 as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-06, every identity targeted and every identity taken over is enumerated, access is restored only through a verified out-of-band channel, and the identity is placed under an extended post-recovery monitoring window before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 6 executed, or with Query 2 or Query 3 unanswered for the identity in scope.
*   A confirmed takeover not followed by the session revocation of the identity and the removal of its attacker-registered MFA methods, consents and grants — closure leaving a confirmed foothold — or not re-classified when the pivot applies.
*   A mass credential reset, the disabling of a service identity, the blocklisting of a partner network, or a revert of the identity infrastructure configuration applied without approval.
*   Restoring access through the same channel used for the attack instead of a verified out-of-band channel.
*   A change to the identity infrastructure found (Query 7) and left standing at closure.

## Hunting Pivots

*   Sweep the sign-in logs for the same source autonomous system, device fingerprint or timing pattern across all identities — a spray targets the directory, not one account.
*   Sweep for MFA methods and devices registered in the last 7 days from a location or device different from the identity's usual ones.
*   Sweep the application consents and application credentials granted in the last 30 days against the sanctioned-application list.

## References

*   MITRE ATT&CK: T1110, T1621, T1528, T1550.001, T1098, T1556; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Identity enrichment](../99-Shared/sub_enrichment_identity.md); [Identity triage playbook](../01-Triage/identity.md); [IC-02 BEC](02-bec.md); [IC-08 Infrastructure Compromise](08-infrastructure_compromise.md).
