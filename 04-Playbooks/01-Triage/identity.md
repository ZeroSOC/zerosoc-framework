---
title: Identity Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Identity
required_data_sources:
  - Identity provider sign-in logs
  - CASB / access-policy evaluation logs
  - Directory audit logs
status: draft
---

# Identity Triage Playbook

Triage knowledge for **Identity** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| Impossible-travel / anomalous sign-in | IdP / CASB | Initial Access | T1078 (Valid Accounts) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| Brute force / password spray | IdP | Credential Access | T1110 (Brute Force) | IC-06 (Identity & Credential Attack) |
| MFA fatigue / push bombing | IdP | Credential Access | T1621 (Multi-Factor Authentication Request Generation) | IC-06 (Identity & Credential Attack) |
| Legacy-auth sign-in | IdP | Initial Access | T1078 (Valid Accounts) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| OAuth app consent / token-session theft | IdP / CASB | Persistence | T1528 (Steal Application Access Token), T1550.001 (Application Access Token) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| Privileged role / group grant | IdP | Privilege Escalation | T1098 (Account Manipulation) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |

## Per-Alert Triage

### Impossible-travel / anomalous sign-in

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP).
- **Checks:**
  1. **Access policy and device compliance.** Did the sign-in pass or fail the identity provider's access policy, and was the device managed and compliant? → `Malicious (Medium)` when the policy failed or the device is unmanaged on an improbable-geography sign-in; `Benign (Low)` when a managed, compliant device passed the policy — routine, but a stolen session replayed through a managed device passes too.
  2. **Baseline deviation.** Is the geography/ASN/device combination genuinely new for this user, or within their established roaming pattern (frequent traveler, known VPN egress)? → `Malicious (Medium)` when the combination is new for the user; `Benign (Medium)` when it matches the user's established pattern. Deviation from the baseline is the core signal, not velocity alone.
  3. **Source reputation.** Does the source IP resolve to a corporate VPN or proxy egress, a consumer ISP, or threat-intelligence-flagged infrastructure? → `Benign (High)` when it is a recognized corporate VPN or proxy egress — the "impossible" travel is an artifact of the egress point; `Malicious (High)` when it is threat-intelligence-flagged or anonymizing infrastructure; context for a consumer ISP.
  4. **Travel confirmation.** Does a travel record, a calendar entry or the user's own confirmation through an independent channel place them at the sign-in location? → `Benign (High)` when it does; `Malicious (High)` when the user denies the sign-in; context when no confirmation is obtainable.
- **False Positive conditions:** corporate VPN or proxy egress producing geo-velocity artifacts; a cloud-hosted mail or sync client signing in on the user's behalf from the provider's region; an IP-geolocation error placing a mobile-carrier address in the wrong country.
- **Benign conditions:** legitimate user travel or roaming; a documented remote-work location or a recorded exception for the user.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-02 (Business Email Compromise) when the account is a mailbox user and the sign-in is followed by mail access.

### Brute force / password spray

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [Network observable](../99-Shared/sub_enrichment_network.md) (source IP).
- **Checks:**
  1. **Failure pattern.** Are failures concentrated on one account (brute force) or spread thin across many accounts from one or few sources (spray)? → `Malicious (Medium)` when the shape is a spray — one attempt per account across many accounts — or a sustained brute force on one account from an external source; `Benign (Medium)` when failures repeat against one service account from the same client at machine-regular intervals, the shape of broken automation.
  2. **Source concentration.** Do failures originate from a small set of IPs/ASNs, especially threat-intelligence-flagged or anonymizing infrastructure, or from a known automation or service endpoint? → `Malicious (High)` when the sources are threat-intelligence-flagged or anonymizing infrastructure; `Benign (High)` when the source is an identified internal automation or application host and its failing credential is confirmed — the failures are explained; `Malicious (Low)` for an unknown external source.
  3. **Outcome.** Did any attempt succeed? → `Malicious (High)` when a sign-in succeeded from an attempting source, especially on an account that failed earlier in the same campaign; context when every attempt failed and lockout held — the outcome changes the severity, not the side.
- **False Positive conditions:** broken automation or a misconfigured service account retrying a stale credential; a lockout storm from a single legitimate application hammering the identity provider; a threshold counting many users behind one NAT egress as a single attacking source.
- **Benign conditions:** an authorized password audit or penetration test whose documented scope covers the accounts and the window.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack).

### MFA fatigue / push bombing

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md), [Network observable](../99-Shared/sub_enrichment_network.md).
- **Checks:**
  1. **Prompt volume and timing.** How many push prompts fired in how short a window, and from how many distinct sign-in attempts? → `Malicious (Medium)` on a rapid burst of prompts from distinct sign-in attempts the user did not initiate; `Benign (Low)` when a handful of prompts repeat from one sign-in attempt at retry-sized intervals.
  2. **Requesting source.** Are the underlying sign-in attempts coming from an unfamiliar geography/ASN/device rather than the user's own client? → `Malicious (High)` when an unfamiliar requester drives the prompts — someone else holds the password; `Benign (High)` when every attempt traces to the user's enrolled device on its usual network — the retries are the user's own.
  3. **Eventual response.** Did the user approve, deny or ignore? → `Malicious (High)` when an approval followed repeated denials from an unfamiliar source — successful coercion; `Malicious (Medium)` when an approval came from an unfamiliar source without prior denials; context when every prompt was denied or ignored — the coercion failed, the credential is still compromised.
  4. **User confirmation.** Does the user, reached through an independent channel, confirm initiating the sign-ins? → `Benign (High)` when they confirm and describe the failing prompt; `Malicious (High)` when they deny initiating them.
- **False Positive conditions:** the user's own client retrying a genuinely failing prompt (network issue, app bug); a detection counting the re-sent prompts of a single sign-in attempt as separate attempts.
- **Benign conditions:** an authorized security-awareness exercise that sends test prompts, recorded for the user and the window; a user enrolling a new authenticator and triggering prompts during setup.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack).

### Legacy-auth sign-in

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md), [Network observable](../99-Shared/sub_enrichment_network.md).
- **Checks:**
  1. **Client identification.** Does the client or user-agent match a known legacy application (an old mail client, a printer or scanner integration), or is it unidentifiable or scripted? → `Benign (Medium)` when it matches a legacy client recorded in the asset inventory; `Malicious (Medium)` when the client is unidentifiable or scripted.
  2. **Baseline recurrence.** Is this a recurring, previously seen legacy client for this user, or a first-time occurrence? → `Benign (Medium)` when the same client has signed in for this user routinely; `Malicious (Medium)` when a legacy client appears for the first time on an established account.
  3. **Source of the sign-in.** Where did it originate? → `Benign (High)` when it comes from the inventoried legacy device's own address on the internal network under a recorded exception — the sign-in is explained; `Malicious (Medium)` when it comes from an external address the device never uses.
  4. **Correlated risk.** Does the sign-in coincide with an impossible-travel, brute-force or MFA alert on the same account? → `Malicious (High)` when it does — legacy authentication is the MFA-bypass path attackers pivot to after credential theft; context when isolated.
- **False Positive conditions:** a parser classifying a modern client as a legacy protocol on a malformed user-agent; a rule that flags a protocol the identity provider already blocks, so the "sign-in" is a rejected attempt with no session.
- **Benign conditions:** an old client (a legacy printer or scanner, an old mail client) that only speaks basic authentication and has done so consistently, with a recorded exception.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-02 (Business Email Compromise) when the legacy protocol is a mail protocol.

### OAuth app consent / token-session theft

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [Network observable](../99-Shared/sub_enrichment_network.md).
- **Checks:**
  1. **App provenance and scope.** Is the application publisher-verified, and does the requested scope (mail read, files, offline access) exceed what the app plausibly needs? → `Malicious (Medium)` on broad scopes from an unverified publisher — the consent-phishing pattern; `Benign (Medium)` when the publisher is verified and the scopes fit the app's stated function.
  2. **Grant or session origin.** Was the grant or token use initiated by the legitimate user session, or does it follow a prior credential or MFA alert on the account? → `Malicious (High)` when the token is used from a different device or IP than the session that obtained it, or the grant follows a credential alert — adversary-in-the-middle token theft; `Benign (Low)` when grant and use come from the user's usual device and network.
  3. **Post-grant activity.** Does the app or session immediately enumerate mail or files, or create inbox rules? → `Malicious (High)` on rapid collection activity after the grant; `Benign (Low)` when activity stays within the app's stated function.
  4. **Sanctioning status.** Is the app on the sanctioned list, or was the grant issued through the approved consent workflow? → `Benign (High)` when it is — the consent is explained; context when the app is unknown to the organization.
- **False Positive conditions:** a rule that flags every consent regardless of publisher verification and scope, with no allowlist; a token-replay detection triggered by a client that legitimately refreshes its token from a changed network (a phone moving between networks).
- **Benign conditions:** sanctioned app onboarding through the approved consent workflow; an administrator's tenant-wide consent for an integration under change control.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-02 (Business Email Compromise) when mail scopes are granted or mail is collected.

### Privileged role / group grant

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (grantor and grantee).
- **Checks:**
  1. **Change-control correlation.** Does the grant tie to an approved access request or change ticket? → `Benign (High)` when a ticket names the grantee and the role — the grant is explained; `Malicious (Medium)` when the grant is untracked.
  2. **Grantor legitimacy.** Was the grant made by an authorized privileged-access administrator, or by an account with no prior role-management activity? → `Benign (Low)` when the grantor routinely manages roles; `Malicious (Medium)` when the grantor is a first-time or anomalous role manager, or the grant was made through an unusual path (a direct API call rather than the access-management workflow).
  3. **Grantee risk.** Is the grantee an existing, active account consistent with the role, or a dormant, recently created or external account? → `Malicious (High)` when privilege is granted to a dormant, new or external account — an escalation or persistence signal; `Benign (Low)` when the grantee is an established account whose function matches the role.
- **False Positive conditions:** a rule that fires on the renewal or re-evaluation of an existing eligible assignment as if it were a new grant; a group the rule lists as privileged that no longer carries privileges.
- **Benign conditions:** an approved access change executed through the standard privileged-access workflow; a time-bound just-in-time activation by an eligible administrator within their approved scope.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack); IC-09 (Insider Threat & Privilege Misuse) when the grantor is a legitimate administrator acting outside process.
