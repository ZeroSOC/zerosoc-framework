---
title: Data Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Data
required_data_sources:
  - Data Loss Prevention (DLP)
  - File / object access audit logs
  - Data classification labels
status: draft
---

# Data Triage Playbook

Triage knowledge for **Data** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| DLP violation (regulated data) | DLP | Exfiltration | T1567 (Exfiltration Over Web Service) | IC-11 (Data Breach / Exfiltration), IC-09 (Insider Threat & Privilege Misuse) |
| Mass sensitive-file access by one principal | DLP / file audit | Collection | T1039 (Data from Network Shared Drive), T1005 (Data from Local System) | IC-09 (Insider Threat & Privilege Misuse), IC-11 (Data Breach / Exfiltration) |
| Ransom-note file dropped | DLP / EDR | Impact | T1486 (Data Encrypted for Impact) | IC-03 (Ransomware & Digital Extortion) |
| Data staging / archiving for exfil | DLP / file audit | Collection | T1074 (Data Staged), T1560 (Archive Collected Data) | IC-11 (Data Breach / Exfiltration), IC-09 (Insider Threat & Privilege Misuse) |

## Per-Alert Triage

### DLP violation (regulated data)

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (the principal), [File](../99-Shared/sub_enrichment_artifact.md) (the object), [Network observable](../99-Shared/sub_enrichment_network.md) (the destination, if egress), [Device](../99-Shared/sub_enrichment_asset.md) (the originating host).
- **Checks:**
  1. **Data classification match.** Does the flagged content genuinely contain regulated data (personal, payment or health records), or is it a pattern hit on test data, a document template with sample numbers, or numbers that fail their checksum? → `Benign (High)` when the matched content is confirmed not to be regulated data — the detection misfired and the alert is explained; context when the content is confirmed regulated — the alert is real and the destination decides.
  2. **Destination legitimacy.** Where is the data going? → `Benign (High)` when the destination is an approved partner or sanctioned service recorded for this data flow in the Knowledge Base; `Benign (Medium)` when it is an internal system or a sanctioned service not yet recorded for this flow; `Malicious (Medium)` when it is a personal storage or webmail account or an unsanctioned external service; `Malicious (High)` when it is an anonymous file-sharing service or reputation-flagged infrastructure.
  3. **Role fit.** Does the principal's job function require handling this class of regulated data at this volume? → `Benign (Low)` when the function handles this data class routinely; `Malicious (Medium)` when the data class or the volume is outside the function.
  4. **Transfer pattern.** Is this a first-ever transfer or a known recurrence? → `Benign (Medium)` when the same transfer recurs on a schedule with the same parameters (same principal, destination and data class); `Malicious (Medium)` when it is a first-ever bulk transfer, especially one preceded by a mass sensitive-file access alert on the same principal.
- **False Positive conditions:** a pattern hit on test, sample or template data; numbers that match a regulated format but fail validation; a rule keyed on a classification label the file no longer carries; an encrypted or compressed file misread as regulated content.
- **Benign conditions:** an approved business transfer of regulated data to a known partner under a data-sharing agreement; a transfer to a sanctioned destination consistent with the principal's function; a documented exception in the Knowledge Base.
- **Candidate Incident Category(ies):** IC-11 (Data Breach / Exfiltration); IC-09 (Insider Threat & Privilege Misuse) when the principal is an insider moving data outside role.

### Mass sensitive-file access by one principal

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [File](../99-Shared/sub_enrichment_artifact.md), [Device](../99-Shared/sub_enrichment_asset.md) (the accessing host).
- **Checks:**
  1. **Volume against baseline.** Is the access volume a sharp outlier against this principal's own history and against peers in the same function? → `Malicious (Medium)` on a sharp outlier; `Benign (Medium)` when the volume is consistent with a periodic bulk task the principal has performed before (audit, migration, e-discovery review).
  2. **Authorization record.** Is a bulk task recorded for this principal, this file set and this window? → `Benign (High)` when the Knowledge Base or a change ticket names the principal, the file set and the time; context when none is recorded — absence of a record does not establish intent.
  3. **Job-function fit.** Does the file set align with the principal's role (a human-resources analyst reading human-resources files), or does it cross into unrelated data domains? → `Benign (Low)` when the access stays within the role; `Malicious (Medium)` when it spans unrelated domains; `Malicious (Medium)` additionally when the principal is in a notice period or on a leaver list.
  4. **Accessing process.** What performed the reads? → `Benign (High)` when a sanctioned backup, indexing or classification-scanning service account reads files by design on every share; `Malicious (Medium)` when an ad hoc script, an archiving utility or an interactive session outside working hours performed them.
  5. **Follow-on movement.** Did the access precede compression, staging or an outbound transfer? → `Malicious (High)` when it is followed by a staging or egress alert on the same principal or host; context when isolated.
- **False Positive conditions:** a threshold that fires on a service account (backup, indexing, classification scanning) that reads files by design; a rule counting file-listing or metadata reads as content access; a stale baseline that no longer reflects the principal's function after a role change.
- **Benign conditions:** a legitimate bulk task such as a migration, an audit, a backup restore test or an e-discovery review, recorded or confirmed with the data owner; a new team member onboarding onto a large project share.
- **Candidate Incident Category(ies):** IC-09 (Insider Threat & Privilege Misuse); IC-11 (Data Breach / Exfiltration) when staging or egress follows.

### Ransom-note file dropped

- **Enrich entities:** [File](../99-Shared/sub_enrichment_artifact.md) (the note artifact), [Device](../99-Shared/sub_enrichment_asset.md), [User](../99-Shared/sub_enrichment_identity.md), [Process](../99-Shared/sub_enrichment_artifact.md) (the writing process, when host telemetry exists).
- **Checks:**
  1. **Note content.** Does the file content carry ransom language — a payment demand, decryption instructions, a contact channel, threat-actor branding? → `Malicious (High)` when it does; `Benign (High)` when the content is unrelated to extortion — a filename coincidence, which explains the alert on its own.
  2. **Distribution pattern.** Does the same file appear across many directories or shares in a short window, written by one process? → `Malicious (High)` on that fan-out pattern; `Benign (Low)` for a single instance in one location.
  3. **Correlated encryption.** Is mass file modification, rising entropy or extension change happening on the same host or share at the same time? → `Malicious (High)` when it is; context when it is not — a note can precede the encryption stage or be dropped by a separate component.
  4. **Writing process.** What wrote the file? → `Malicious (Medium)` when an unsigned or unknown process from a user-writable path did; `Benign (Medium)` when a user's editor wrote a single file; `Benign (High)` when a sanctioned attack-simulation or detection-testing tool wrote it on a designated host within a recorded exercise window.
- **False Positive conditions:** a filename-only match on a common name (`readme.txt`, `HOW_TO_*`, `RECOVER*`) with unrelated content; a security product's own test artifact; a saved threat-intelligence report or training material describing a ransom note.
- **Benign conditions:** an authorized attack simulation or purple-team exercise dropping sample notes on a designated host in a recorded window.
- **Candidate Incident Category(ies):** IC-03 (Ransomware & Digital Extortion).

### Data staging / archiving for exfil

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md), [File](../99-Shared/sub_enrichment_artifact.md) (the archive or staged files), [Device](../99-Shared/sub_enrichment_asset.md), [Process](../99-Shared/sub_enrichment_artifact.md) (the archiving process), [Network observable](../99-Shared/sub_enrichment_network.md) (if followed by egress).
- **Checks:**
  1. **Staging location.** Where is the data being collected? → `Malicious (Medium)` when it is a non-standard, temporary, world-writable or hidden location, or a recycle bin; `Benign (Medium)` when it is a designated backup or archive path.
  2. **Archive composition.** What does the archive contain? → `Malicious (Medium)` when it pulls sensitive files from many unrelated sources and directories; `Malicious (Medium)` when it is password-protected or split into volumes by a command-line archiver invoked from a script; `Benign (Low)` when it is a coherent single-project or single-directory package.
  3. **Schedule and tooling fit.** What created the archive, and when? → `Benign (High)` when the known backup or packaging tool created it on its recorded schedule; `Malicious (Medium)` when an ad hoc process or script created it at an atypical time for the principal.
  4. **Preceding access.** Was the staging preceded by a mass sensitive-file access alert on the same principal or host? → `Malicious (Medium)` when it was; context otherwise.
  5. **Follow-on egress.** Did the archive leave — an outbound transfer, an upload to personal storage, a copy to removable media — shortly after? → `Malicious (High)` when it did; context when the archive sits in place.
- **False Positive conditions:** a detection firing on the write pattern of a backup, packaging or compression job; an application's own cache, export or log-rotation archive; a sync client compressing files; a developer build packaging its artifacts.
- **Benign conditions:** a scheduled backup or archiving job on its usual window; an authorized migration or e-discovery export under a ticket; an approved transfer of a leaver's files during offboarding.
- **Candidate Incident Category(ies):** IC-11 (Data Breach / Exfiltration); IC-09 (Insider Threat & Privilege Misuse) when the principal is an insider collecting outside role.
