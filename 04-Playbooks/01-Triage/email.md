---
title: Email Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Email
required_data_sources:
  - Email gateway / secure email gateway
  - Mailbox audit logs
  - Email detonation / sandbox
  - User-reported phishing mailbox
status: draft
---

# Email Triage Playbook

Triage knowledge for **Email** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| User-reported phishing | Email gateway / user report | Initial Access | T1566 (Phishing) | IC-01 (Phishing / Social Engineering), IC-02 (Business Email Compromise) |
| Malicious attachment / URL delivered | Email gateway / sandbox | Initial Access | T1566.001 (Spearphishing Attachment), T1566.002 (Spearphishing Link), T1204 (User Execution) | IC-01 (Phishing / Social Engineering), IC-05 (Commodity Malware / Loader) |
| Inbox forwarding / redirect or hide rule | Mailbox audit | Collection | T1114 (Email Collection), T1564 (Hide Artifacts) | IC-02 (Business Email Compromise) |
| BEC impersonation / display-name spoof | Email gateway | Initial Access | T1656 (Impersonation), T1566 (Phishing) | IC-02 (Business Email Compromise), IC-01 (Phishing / Social Engineering) |

## Per-Alert Triage

### User-reported phishing

- **Enrich entities:** [Email message](../99-Shared/sub_enrichment_email_message.md), [Network observable](../99-Shared/sub_enrichment_network.md) (sender domain, URLs), [User](../99-Shared/sub_enrichment_identity.md) (reporter and recipient).
- **Checks:**
  1. **Sender authentication.** Does the message pass SPF/DKIM/DMARC, and is the sending domain a lookalike or newly registered? → `Malicious (Medium)` on failed authentication or a lookalike or newly registered domain; `Benign (Low)` on aligned authentication from an established domain — a compromised legitimate account passes authentication too.
  2. **Content intent.** Does the message solicit credentials, payment or urgent action, or is it unsolicited but harmless (marketing, a newsletter)? → `Malicious (Medium)` on a lure that induces action; `Benign (Medium)` on graymail with no ask.
  3. **Link/attachment verdict.** Does sandbox detonation or reputation on any embedded link or attachment return malicious? → `Malicious (High)` on a malicious verdict (a credential-harvesting page, a malware payload); `Benign (Medium)` on a clean verdict — a clean detonation does not clear a text-only social-engineering lure.
  4. **Known campaign or sender.** Does the message belong to a recorded phishing-awareness simulation, or does a known internal or vendor sender confirm through an independent channel that they sent it? → `Benign (High)` when either holds — the report is explained; `Malicious (High)` when the purported sender denies sending it.
  5. **Reach and interaction.** How many mailboxes received the same message, sender or URL, and did the reporter or any recipient click or submit credentials? → `Malicious (Medium)` when a wave reached many recipients; context on interaction — it drives urgency and opens the Identity and Endpoint pivots, it does not change the side.
- **False Positive conditions:** unwanted marketing or graymail reported as phishing; a mistaken report on a legitimate internal or vendor email.
- **Benign conditions:** a recorded phishing-awareness simulation by the training provider; an authorized penetration-test phishing exercise with a documented window.
- **Candidate Incident Category(ies):** IC-01 (Phishing / Social Engineering); IC-02 (Business Email Compromise) when the lure impersonates a business counterpart to obtain payment.

### Malicious attachment / URL delivered

- **Enrich entities:** [Email message](../99-Shared/sub_enrichment_email_message.md), [Network observable](../99-Shared/sub_enrichment_network.md) (URL/domain), [File](../99-Shared/sub_enrichment_artifact.md) (attachment hash), [User](../99-Shared/sub_enrichment_identity.md) (recipient).
- **Checks:**
  1. **Detonation/reputation verdict.** Does sandbox detonation or threat intelligence flag the attachment hash or URL as malicious? → `Malicious (High)` on a confirmed-bad verdict; `Benign (Medium)` when a re-detonation and reputation come back clean — a sandbox-evading sample also looks clean.
  2. **Delivery mechanics.** Is the attachment a macro-enabled document, a password-protected archive, a disk image or shortcut file, or an executable disguised as a document — file types with no ordinary business use from external senders? → `Malicious (Medium)` on a weaponizable file type from an external sender; `Benign (Low)` on an ordinary document with no active content.
  3. **Sender relationship.** Is the sender a known vendor or partner, an unknown party, or a lookalike of a known contact? → `Benign (High)` when a known sender confirms through an independent channel that they sent the file and it matches its stated purpose — the alert is explained; `Malicious (Medium)` when the sender is unknown, a lookalike, or a known contact whose account shows signs of compromise.
  4. **Recipient interaction.** Did the recipient open the attachment or click the link? → context: it sets the urgency and opens the Endpoint pivot; when host telemetry shows the document spawning a process, that is an Endpoint "Malware / loader execution" alert to add to the Case.
  5. **Campaign scope.** How many mailboxes received the same attachment hash or URL? → `Malicious (Medium)` when a wave hit many recipients; context for a single delivery.
- **False Positive conditions:** a sandbox false positive on a safe file or link; a legitimate vendor document flagged by heuristics (a signed macro template); a URL reputation lookup flagging a link shortener or a shared-hosting domain.
- **Benign conditions:** an authorized phishing-awareness simulation; samples received into a designated analysis mailbox by the security function; an internal tool distributing a signed macro template under a recorded exception.
- **Candidate Incident Category(ies):** IC-01 (Phishing / Social Engineering); IC-05 (Commodity Malware / Loader) when the payload executes.

### Inbox forwarding / redirect or hide rule

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (mailbox owner), [Network observable](../99-Shared/sub_enrichment_network.md) (forwarding destination domain, if external).
- **Checks:**
  1. **Forwarding destination.** Does the rule forward to an external, personal or unrecognized domain, or to an internal or approved address? → `Malicious (High)` when the destination is a newly registered lookalike domain or one tied to a known fraud campaign; `Malicious (Medium)` on an external, personal or unrecognized destination; `Benign (Low)` on an internal or approved address.
  2. **Rule creation context.** Was the rule created shortly after a sign-in anomaly or an OAuth-grant alert on the same account, or from a session that is not the user's? → `Malicious (High)` when it follows a credential-risk alert or was created from an unfamiliar device or IP — data collection after account takeover; `Benign (Low)` when it was created from the user's usual device and network.
  3. **Concealment behavior.** Does the rule also hide or delete matching mail (auto-delete, move to an obscure folder, mark as read), typically keyed on words such as invoice, payment or password? → `Malicious (High)` on concealment paired with forwarding — deliberate hiding of the compromise; `Benign (Low)` on a plain forward with no hiding.
  4. **User confirmation.** Does the user, reached through an independent channel rather than the mailbox itself, confirm creating the rule and its purpose? → `Benign (High)` when they do; `Malicious (High)` when they deny creating it.
- **False Positive conditions:** an internal shared mailbox or an alias domain classified as external by a parsing error; a migration tool's temporary forwarding; an out-of-office or delegation setting misread as a rule.
- **Benign conditions:** a user-created convenience rule forwarding to a personal account, recorded as a policy matter rather than a compromise; an approved delegation or forward during leave; a departing employee's mailbox forward set by IT under the leaver process.
- **Candidate Incident Category(ies):** IC-02 (Business Email Compromise).

### BEC impersonation / display-name spoof

- **Enrich entities:** [Email message](../99-Shared/sub_enrichment_email_message.md), [Network observable](../99-Shared/sub_enrichment_network.md) (sender domain), [User](../99-Shared/sub_enrichment_identity.md) (impersonated party and recipient).
- **Checks:**
  1. **Display-name vs. address mismatch.** Does the display name match a known executive or vendor while the underlying address is external or a lookalike? → `Malicious (Medium)` on a mismatch — the core impersonation signal; `Benign (Low)` when the address matches the party's known domain — a compromised counterpart also matches.
  2. **Request type.** Does the message request a wire transfer, a gift-card purchase, a payroll or banking-detail change, or an urgent confidential action? → `Malicious (Medium)` on these canonical asks; `Benign (Low)` when nothing of value or urgency is requested.
  3. **Domain lookalike analysis.** Is the sending domain a homoglyph or slight variant of the impersonated organization's real domain? → `Malicious (High)` on a lookalike registration, especially a recent one; `Benign (High)` when the sending domain is a verified subsidiary or partner domain recorded in the SOC Knowledge Base — the resemblance is explained.
  4. **Counterpart verification.** Does the impersonated party, reached through an independently known contact channel (not the details in the message), confirm the message and the request? → `Benign (High)` when they confirm; `Malicious (High)` when they deny it, or when the message continues a real thread from a lookalike domain — a hijacked thread after the counterpart's compromise.
  5. **Recipient action.** Did the recipient act on the request (a payment initiated, details changed)? → context: it sets the impact and starts the financial-recovery clock, it does not change the side.
- **False Positive conditions:** a legitimate sender who is a namesake of an executive; a rule matching on common first names; a mailing list or ticketing system rewriting the display name.
- **Benign conditions:** a legitimate lookalike vendor domain (a real subsidiary or an authorized partner domain resembling but distinct from the primary domain); an authorized fraud-awareness simulation.
- **Candidate Incident Category(ies):** IC-02 (Business Email Compromise); IC-01 (Phishing / Social Engineering) when the lure seeks credentials rather than payment.
