---
title: 03-Ransomware & Digital Extortion Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-03
mitre_ttps:
  - T1486   # Data Encrypted for Impact
  - T1490   # Inhibit System Recovery
  - T1567   # Exfiltration Over Web Service
default_severity: High
required_data_sources:
  - EDR / endpoint process telemetry
  - File system / storage audit logs
  - Backup system logs
  - Network / CASB / firewall logs
status: draft
---

# 03-Ransomware & Digital Extortion Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-03 Ransomware & Digital Extortion` — encryption, data-theft extortion, or both, with a demand; including double and triple extortion and leak-only. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

Ransomware is an objective category: by the time encryption is visible the adversary has held a foothold, moved laterally and often already taken the data. The investigation establishes the impact and its spread while the pre-authorized isolations already run; every hour of delay is more hosts encrypted, so containment does not wait for the last query.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** a threat actor has gained access, moved laterally, potentially exfiltrated data, and is actively encrypting systems — or threatening to leak the data — to demand a ransom.
   * **Benign:** an authorized backup or archiving script, a legitimate mass file rename or migration, or endpoint protection aggressively flagging a legitimate new encryption utility.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Are there signs of lateral movement or mass credential dumping preceding the encryption alerts — remote service creation, administrative shares, credential-access tooling on the affected hosts ([Asset](../99-Shared/sub_enrichment_asset.md))? → `Malicious (Medium)` when present; `Benign (Low)` when the encrypting host shows no prior anomaly in the surrounding window.
   * *Query 2:* Is the encryption process signed by a known, trusted publisher and executed from the authorized software-deployment or backup tool, and does the SOC Knowledge Base or the change calendar record the backup, migration or encryption job covering these hosts and this time? → `Benign (High)` when the job or change covers the hosts, the time and the process — the explanation of the alerts; `Benign (Medium)` when the process is signed and launched by the deployment tool but no record exists; `Malicious (Medium)` when it is unsigned, renamed, or launched from a user-writable path.
   * *Query 3:* Has a ransom-note file (`readme.txt`, `decrypt_instructions.html` and the like) been dropped in multiple directories, or have files been renamed with a uniform new extension? → `Malicious (High)` on a note in multiple directories; `Benign (Low)` when no note exists and the renamed files still open with their original applications.
   * *Query 4:* Did the process delete or disable recovery — shadow copies (`vssadmin.exe Delete Shadows /All /Quiet`, `wmic shadowcopy delete`), boot recovery, backup jobs or backup repositories? → `Malicious (High)` on any of these; `Benign (Low)` when every recovery point is intact.
   * *Query 5:* Was there bulk egress from the affected hosts or file shares before the encryption — to a file-sharing or web service, a newly seen destination or an unusual volume — or a leak-site claim naming the organization? → `Malicious (High)` on bulk egress to unknown infrastructure or a leak-site claim; context when none is found — encryption-only extortion is still IC-03, and the exfiltration status is recorded either way.
   * *Query 6:* How many hosts and file shares show the encryption process, the note or the renamed files, and is the spread still growing? → `Malicious (Medium)` for multiple hosts or a share; context for a single host — this is the scope question, and it is re-run until the spread stops.

**Re-classification pivots:** no functional decryption or ransom path — files destroyed or corrupted with no viable recovery offered, a wiper disguised as ransomware → [IC-13 (Destructive / Wiper Attack)](13-destructive_wiper.md); extortion over stolen data alone, with no encryption → overlaps [IC-11 (Data Breach / Exfiltration)](11-data_breach_exfiltration.md); a loader or precursor found before any encryption ran → [IC-05 (Commodity Malware / Loader)](05-commodity_malware.md) until the objective is established.

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-03 (Ransomware & Digital Extortion)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence.

### Containment
*   Isolate the suspected patient zero and every infected workstation from the network through the EDR or network controls, keeping them powered on for forensics (reversed by reconnecting them). Isolating a production server, file server, hypervisor, domain controller or the backup infrastructure itself — **requires approval**.
*   Halt the ongoing exfiltration: block the identified destinations at the perimeter and apply a temporary egress block on the affected hosts (reversed by removing the rules). Disconnecting a critical data store from the network, or isolating its subnet or cloud network — **requires approval**.
*   Revoke the active sessions and disable the identities confirmed compromised during the intrusion (reversed by re-enabling them). Disabling a service identity a critical service runs under, or resetting many identities at once — **requires approval**.
*   Protect the backups: set the repositories to immutable or read-only and revoke the specific credentials the attacker used against them (reversed by re-issuing them).

### Eradication
*   Identify the initial access vector — an exposed VPN gateway, a phishing message, a stolen credential — and patch or block it.
*   Identify all command-and-control infrastructure and block it at the perimeter.
*   Cleanse the endpoints or, preferably, wipe and re-image every compromised machine — **requires approval**.
*   Rotate the credentials confirmed compromised and the secrets they could reach. A domain-wide reset, including the Active Directory Kerberos service account — **requires approval**.

### Recovery
*   Verify eradication is complete and the environment is clean before restoring: no beaconing to the blocked infrastructure, no encryption activity, no lateral movement from the isolated hosts.
*   Verify the backups are clean and untampered, then restore data from offline, immutable backups taken before T0.
*   A ransom payment, or a commitment to pay, is an executive decision under legal counsel and is never a playbook action; record any such decision in the Case.
*   Lift containment gradually, hosts and identities first, network segments last, each removal recorded in the Case timeline.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-03, the initial access vector, the full host and share scope, and the exfiltration status (with the data categories affected, feeding the breach notification) are recorded, and any ransom-payment decision is recorded as executive-authorized under legal counsel before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 2 executed, or with Query 3 or Query 4 unanswered.
*   Restoring data or lifting containment before eradication — vector closed, command-and-control blocked, hosts cleansed or re-imaged — is verified complete: closure leaving a confirmed foothold.
*   Restoring from backups without first verifying that the backups themselves are clean and untampered.
*   A re-image or wipe, the isolation of a server, domain controller or the backup infrastructure, or a domain-wide credential reset applied without approval.
*   Paying, or committing to pay, the ransom without executive authorization under legal counsel.
*   Files destroyed with no recovery path not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the fleet for pre-encryption staging matching this Incident's initial-access and lateral-movement indicators — the same command-and-control infrastructure, the credential-dumping tooling, the remote-service creation — before encryption triggers elsewhere.
*   Sweep every host for shadow-copy deletion, recovery-disable commands and backup-job changes in the last 7 days: recovery inhibition precedes the encryption by hours to days.
*   Sweep egress logs for bulk transfers to the file-sharing services and destinations found in Query 5 from hosts outside the Case scope.

## References

*   MITRE ATT&CK: T1486, T1490, T1567; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Asset enrichment](../99-Shared/sub_enrichment_asset.md); [IC-13 Destructive / Wiper Attack](13-destructive_wiper.md); [IC-11 Data Breach / Exfiltration](11-data_breach_exfiltration.md).
