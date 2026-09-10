---
title: Endpoint Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Endpoint
required_data_sources:
  - EDR / endpoint process telemetry
  - Anti-virus / anti-malware
  - File-integrity monitoring
status: draft
---

# Endpoint Triage Playbook

Triage knowledge for **Endpoint** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| Malware / loader execution | EDR / AV | Execution | T1204 (User Execution), T1059 (Command and Scripting Interpreter) | IC-05 (Commodity Malware / Loader), IC-03 (Ransomware & Digital Extortion) |
| Suspicious script / interpreter execution | EDR | Execution | T1059 (Command and Scripting Interpreter), T1218 (System Binary Proxy Execution) | IC-05 (Commodity Malware / Loader) |
| Credential dumping | EDR | Credential Access | T1003 (OS Credential Dumping) | IC-06 (Identity & Credential Attack) |
| Ransomware mass-encryption | EDR / file-integrity monitoring | Impact | T1486 (Data Encrypted for Impact), T1490 (Inhibit System Recovery) | IC-03 (Ransomware & Digital Extortion) |
| Security-tool / AMSI tampering | EDR | Defense Impairment | T1685 (Disable or Modify Tools) | IC-05 (Commodity Malware / Loader), IC-03 (Ransomware & Digital Extortion) |
| Persistence mechanism created | EDR | Persistence | T1543 (Create or Modify System Process), T1053 (Scheduled Task/Job), T1547 (Boot or Logon Autostart Execution) | IC-05 (Commodity Malware / Loader) |
| Ingress tool transfer to host | EDR | Command and Control | T1105 (Ingress Tool Transfer) | IC-05 (Commodity Malware / Loader) |
| Trusted software / updater anomalous behaviour | EDR | Initial Access | T1195.002 (Compromise Software Supply Chain), T1574.001 (DLL), T1554 (Compromise Host Software Binary) | IC-10 (Supply-Chain Compromise), IC-05 (Commodity Malware / Loader) |
| Mass file destruction / disk wipe | EDR / file-integrity monitoring | Impact | T1485 (Data Destruction), T1561 (Disk Wipe), T1490 (Inhibit System Recovery) | IC-13 (Destructive / Wiper Attack), IC-03 (Ransomware & Digital Extortion) |

## Per-Alert Triage

### Malware / loader execution

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Hash reputation.** Does a multi-engine lookup of the file hash name a known malware family? → `Malicious (High)` on a family consensus; `Benign (Medium)` when the hash is a known, signed vendor release; context when the hash is unknown — an unknown hash is not evidence of either side.
  2. **Payload location.** Where does the executed or dropped file live? → `Malicious (Medium)` when it runs from a world-writable path (`C:\Users\Public\`, `%TEMP%`, `Downloads`); `Benign (Low)` when it runs from a sanctioned install location.
  3. **Execution parent.** What launched it? → `Malicious (High)` when an office document or a script host spawned an execution utility — the macro-delivery chain that business software never produces; `Benign (Low)` when the parent is an installer, a management agent or an interactive shell of an administrator.
  4. **Proxy execution.** Is a trusted, signed system binary (`regsvr32`, `rundll32`, `mshta`) running code from a non-system path? → `Malicious (Medium)`; `Benign (Low)` when the loaded library sits in a sanctioned install location.
- **False Positive conditions:** a heuristic firing on signed vendor software; a detection keyed on a file name that a legitimate product also uses; a packed but legitimate installer.
- **Benign conditions:** an authorized deployment by the endpoint management platform registering a library; a developer or test host building local binaries; a security engineer or tester registering a library as authorized work.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader); IC-03 (Ransomware & Digital Extortion) if ransomware behaviors follow.

### Suspicious script / interpreter execution

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md) ([File](../99-Shared/sub_enrichment_artifact.md) if a script artifact exists).
- **Checks:**
  1. **Command-line intent.** If the command line is encoded or obfuscated (Base64 `-enc`, string concatenation, compression), decode it: what does it do? → `Malicious (Medium)` when the decoded command makes network connections, writes files or modifies the registry; `Benign (Medium)` when it decodes to something inert or to a known administrative script.
  2. **Execution lineage.** What launched the interpreter? → `Malicious (High)` when a document or a script host spawned it; `Benign (Low)` when an administrator's interactive session or a management agent did.
  3. **Download cradle.** Does the script fetch and run remote content (`DownloadString`, `Invoke-WebRequest` to raw content, `IEX`)? → `Malicious (High)` when it fetches from an external host and executes the result; `Benign (Low)` for local-only scripting.
- **False Positive conditions:** a detection firing on obfuscation that a legitimate product's installer or updater uses; an encoded command that decodes to a benign vendor routine.
- **Benign conditions:** authorized IT scripting in an approved change window; a remote-management agent using the interpreter; detection testing by a verified team member on a designated host.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader).

### Credential dumping

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Access target.** What did the process read? → `Malicious (Medium)` on access to LSASS memory, the SAM and SYSTEM hives, or `ntds.dit` on a domain controller — benign software rarely touches these; context for any other target.
  2. **Access technique.** How was it read? → `Malicious (High)` when a minidump of LSASS was written, or `comsvcs.dll MiniDump`, `procdump` or direct system calls were used; context for a routine in-process memory read.
  3. **Accessor identity.** What is the accessing process? → `Benign (High)` when it is a sanctioned, signed security or backup agent that reads protected memory by design on every host; `Malicious (Medium)` when it is unsigned, oddly parented or unknown to the asset inventory.
- **False Positive conditions:** a detection that fires on every handle to LSASS, including the EDR's own; a signed security product not yet on the detection's allowlist.
- **Benign conditions:** sanctioned forensic or incident-response tooling reading LSASS during an authorized engagement; a credential-manager operation by the platform itself.
- **Candidate Incident Category(ies):** IC-06 (Identity & Credential Attack).

### Ransomware mass-encryption

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Modification pattern.** Is a single process rewriting many files across directories with rising entropy or changed extensions in a short window? → `Malicious (High)` on that fan-out pattern; `Benign (Low)` when a few files changed under an editor or a sync client.
  2. **Recovery sabotage.** Did the process delete volume shadow copies or disable recovery (`vssadmin Delete Shadows`, `wmic shadowcopy delete`, `bcdedit /set recoveryenabled no`)? → `Malicious (High)`; there is no business reason to destroy restore points outside a documented decommissioning.
  3. **Ransom-note artifacts.** Were note files dropped into the affected directories? → `Malicious (High)`.
  4. **Encrypting-process provenance.** What is the process? → `Benign (High)` when it is a signed backup, archiving or full-disk-encryption tool running its scheduled job; `Malicious (Medium)` when it is an unsigned binary from a user path.
- **False Positive conditions:** a detection firing on the write pattern of a backup, archiving or compression job; a bulk rename or migration by a signed tool.
- **Benign conditions:** an authorized full-disk-encryption rollout by the endpoint management platform; a scheduled backup job on its usual window.
- **Candidate Incident Category(ies):** IC-03 (Ransomware & Digital Extortion).

### Security-tool / AMSI tampering

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Tampering action.** What control was touched? → `Malicious (High)` for an in-memory AMSI bypass, an event-tracing patch, or the EDR's tamper protection disabled; `Malicious (Medium)` for a stopped AV service or an added exclusion.
  2. **Change authorization.** Was the change made under an approved maintenance or change window by IT or security? → `Benign (High)` when the change ticket covers the host and the action; `Malicious (Medium)` when a standard user or an unexpected process made it.
  3. **Surrounding activity.** Is the tampering chained with execution, persistence or credential alerts on the same host in the same window? → `Malicious (High)` when it clears the way for other suspicious activity; context when isolated.
- **False Positive conditions:** the security product's own upgrade routine stopping and restarting its services; a detection firing on an exclusion added by the product's installer.
- **Benign conditions:** an authorized security-software maintenance or migration window; an administrator adding a documented exclusion under change control.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader); IC-03 (Ransomware & Digital Extortion) if pre-ransomware defense evasion.

### Persistence mechanism created

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Mechanism and target.** What was created (Run key, scheduled task, service, WMI event subscription, startup-folder entry) and what does it launch? → `Malicious (Medium)` when the target is an unsigned binary or a script in a world-writable path; `Benign (Medium)` when it is a signed program in its install location.
  2. **Creating process.** What created it? → `Benign (Medium)` when a known installer or the management agent did; `Malicious (High)` when a document-spawned process or a script host did.
  3. **Timing correlation.** Was it created right after an execution or download alert on the same host? → `Malicious (High)` — the foothold being made durable; context otherwise.
- **False Positive conditions:** a detection firing on the autostart entries every installation of a legitimate product creates.
- **Benign conditions:** a software install or update by the endpoint management platform; a sanctioned administrative scheduled task.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader).

### Ingress tool transfer to host

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [Device](../99-Shared/sub_enrichment_asset.md), [Network observable](../99-Shared/sub_enrichment_network.md).
- **Checks:**
  1. **Downloader identity.** What fetched the file? → `Malicious (Medium)` when a living-off-the-land binary (`certutil`, `bitsadmin`, `curl`, `powershell`) did; `Benign (Low)` when a browser or a package manager did.
  2. **Source reputation.** What is the reputation and registration age of the source? → `Malicious (High)` for a newly registered or reputation-flagged source; `Benign (Medium)` for a well-known vendor or an internal repository.
  3. **Landing and follow-on.** Where did the file land, and was it executed? → `Malicious (High)` when it was written to a world-writable path and run shortly after; `Benign (Low)` when it sits inert in `Downloads`.
- **False Positive conditions:** a detection firing on a package manager or a browser download by command-line shape alone.
- **Benign conditions:** content delivery by the management agent; an administrator fetching tools from a sanctioned internal repository.
- **Candidate Incident Category(ies):** IC-05 (Commodity Malware / Loader).

### Trusted software / updater anomalous behaviour

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [Device](../99-Shared/sub_enrichment_asset.md), [Network observable](../99-Shared/sub_enrichment_network.md).
- **Checks:**
  1. **Child processes.** What did the trusted binary spawn? → `Malicious (High)` when a signed application or updater spawned a shell, a script interpreter or a system utility it has no reason to run; `Benign (Low)` when the children are the product's own components.
  2. **Loaded libraries.** Did the binary load a library from outside its install location, or one whose signer differs from the product's? → `Malicious (High)` on a side-loaded library; `Benign (Low)` when every library is signed by the publisher and sits in place.
  3. **Network behaviour.** Where did the binary connect? → `Malicious (High)` when it beacons to infrastructure that is not the publisher's, especially newly registered; `Benign (Medium)` when it reached only the publisher's update domains.
  4. **Fleet prevalence.** Is the same version behaving the same way on many hosts after the same update? → `Malicious (Medium)` when a supply-chain compromise would explain it and the behaviour is new for the version; `Benign (Medium)` when the publisher's release notes document the new behaviour.
- **False Positive conditions:** a detection baselined on the previous version's behaviour firing on a legitimate update; a product feature newly using a scripting engine.
- **Benign conditions:** a documented product update rolled out by the endpoint management platform whose new behaviour matches the publisher's notes.
- **Candidate Incident Category(ies):** IC-10 (Supply-Chain Compromise); IC-05 (Commodity Malware / Loader) when the trojanized binary is the loader itself.

### Mass file destruction / disk wipe

- **Enrich entities:** [Process](../99-Shared/sub_enrichment_artifact.md), [File](../99-Shared/sub_enrichment_artifact.md), [User](../99-Shared/sub_enrichment_identity.md), [Device](../99-Shared/sub_enrichment_asset.md).
- **Checks:**
  1. **Destruction pattern.** Is a single process deleting or overwriting many files across directories, or writing to the boot record, partition table or volume metadata? → `Malicious (High)` on raw writes to boot or volume structures; `Malicious (Medium)` on a bulk overwrite pattern; `Benign (Low)` for a bulk delete inside a single application's data directory.
  2. **Recovery sabotage.** Were shadow copies, backups or recovery settings destroyed first? → `Malicious (High)`.
  3. **Process provenance and authorization.** What is the process, and is there a decommissioning or re-imaging task for this host? → `Benign (High)` when a signed imaging or disk-management tool runs under a change ticket naming the host; `Malicious (Medium)` when the process is unsigned or the host is not scheduled for decommissioning.
  4. **Scope.** Is the same activity starting on other hosts in the same minutes? → `Malicious (High)` — a wiper propagating; context when confined to one host.
- **False Positive conditions:** a detection firing on a disk-cleanup or storage-reclaim job by a signed tool; a large delete by a sync client after a folder was unshared.
- **Benign conditions:** a sanctioned decommissioning or re-imaging task by the endpoint management platform under change control.
- **Candidate Incident Category(ies):** IC-13 (Destructive / Wiper Attack); IC-03 (Ransomware & Digital Extortion) when the destruction follows an extortion demand.
