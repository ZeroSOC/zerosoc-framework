---
title: Alert Type Taxonomy
type: concept
status: development
last_updated: 2026-09-08
license: Apache-2.0
---

# Alert Type Taxonomy

This taxonomy defines the common **alert types** a SOC investigates. Alerts are the primary object of **Triage** (Phase 2). It is the vendor-neutral vocabulary the domain triage playbooks in [04-Playbooks/01-Triage](../04-Playbooks/README.md) reference — a clean **definitions vs. procedure** boundary: this taxonomy says *what an alert is and typically represents*; the triage playbooks say *how to handle it*.

Alert types are organized by **telemetry domain**: Endpoint, Identity, Network, Cloud, Email, Data, Application, OT/ICS. Each alert type maps to MITRE ATT&CK tactics/techniques and to one or more **candidate Incident Categories** ([incident_categories.md](incident_categories.md)); the candidate categories are validated during Investigation. An alert may map to more than one category.

**Domain-assignment principle.** An alert type's **home domain is the domain of the primary telemetry that raises it and the entity it is about** — not every sensor that could observe the behavior. The **Log Source** column ([definition](../01-Foundation/definitions.md#log-sources-telemetry-sources)) lists only sources native to that domain. Cross-domain corroboration (e.g., proxy logs confirming a host download) is **enrichment** performed during Triage/Investigation and does not change the home domain. When the same behavior is meaningfully detected from two domains, it is modeled as **two alert types** (one per domain) with overlapping candidate Incident Categories.

**SaaS and Container mapping.** SaaS alerts map to **Identity** (authentication/authorization signals) and/or **Cloud** (configuration/API signals) depending on the telemetry. Container/Kubernetes alerts map to **Cloud**.

**Column contract:** `Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs`. Techniques and Candidate ICs use `ID (Name)` form. The **Description** states the generic meaning, then the two competing readings labelled **Malicious:** and **Benign:**, and — only where an adjacent alert type is easily confused — a **Distinct from** clause naming that type and the single feature that separates them.

## Endpoint

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| Malware / loader execution | Execution of a suspicious binary or loader on a host. **Malicious:** malware or loader payload. **Benign:** a legitimate signed program flagged in error. **Distinct from** Suspicious script / interpreter execution — that runs via a script engine, this is a compiled binary. | EDR / AV | Execution | T1204 (User Execution), T1059 (Command and Scripting Interpreter) | IC-05 (Commodity Malware / Loader), IC-03 (Ransomware & Digital Extortion) |
| Suspicious script / interpreter execution | Abnormal use of scripting engines or living-off-the-land binaries. **Malicious:** hands-on-keyboard activity or a script-based loader. **Benign:** legitimate admin scripting. | EDR | Execution | T1059 (Command and Scripting Interpreter), T1218 (System Binary Proxy Execution) | IC-05 (Commodity Malware / Loader) |
| Credential dumping | Access to OS credential stores (LSASS, registry, SAM). **Malicious:** credential theft. **Benign:** sanctioned IR or forensics tooling. | EDR | Credential Access | T1003 (OS Credential Dumping) | IC-06 (Identity & Credential Attack) |
| Ransomware mass-encryption | Rapid encryption or rename of many files on a host. **Malicious:** ransomware encrypting data. **Benign:** a bulk archive or backup job. **Distinct from** Data "Ransom-note file dropped" — that keys on the note artifact, this on the encryption behaviour. | EDR / file-integrity monitoring | Impact | T1486 (Data Encrypted for Impact), T1490 (Inhibit System Recovery) | IC-03 (Ransomware & Digital Extortion) |
| Security-tool / AMSI tampering | Disabling or tampering with host security tooling (EDR/AV/AMSI/logging). **Malicious:** impairing defences to evade detection. **Benign:** sanctioned maintenance or an approved change. | EDR | Defense Impairment | T1685 (Disable or Modify Tools) | IC-05 (Commodity Malware / Loader), IC-03 (Ransomware & Digital Extortion) |
| Persistence mechanism created | A new service, scheduled task, or autorun that survives reboot. **Malicious:** an attacker foothold. **Benign:** a legitimate software install or update. | EDR | Persistence | T1543 (Create or Modify System Process), T1053 (Scheduled Task/Job), T1547 (Boot or Logon Autostart Execution) | IC-05 (Commodity Malware / Loader) |
| Trusted software / updater anomalous behaviour | A signed vendor binary, installer, or updater behaving unexpectedly: spawning unusual child processes, side-loading a library, or beaconing. **Malicious:** a trojanized or compromised software supply chain. **Benign:** a legitimate update with new behaviour. **Distinct from** Malware / loader execution — the parent here is trusted, signed software. | EDR | Initial Access | T1195.002 (Compromise Software Supply Chain), T1574.001 (DLL), T1554 (Compromise Host Software Binary) | IC-10 (Supply-Chain Compromise), IC-05 (Commodity Malware / Loader) |
| Mass file destruction / disk wipe | Bulk deletion or overwrite of files, or tampering with boot records, volumes, or recovery data. **Malicious:** a wiper or the destructive stage of an extortion attack. **Benign:** a sanctioned decommissioning or disk-reimaging job. **Distinct from** Ransomware mass-encryption — that renders data recoverable for a price, this destroys it. | EDR / file-integrity monitoring | Impact | T1485 (Data Destruction), T1561 (Disk Wipe), T1490 (Inhibit System Recovery) | IC-13 (Destructive / Wiper Attack), IC-03 (Ransomware & Digital Extortion) |
| Ingress tool transfer to host | Host-observed download or write of tooling to the endpoint. **Malicious:** attacker tooling being staged. **Benign:** an approved software deployment. **Distinct from** Network "Download from known-malicious / newly-registered domain" — same act, but seen on the host rather than at the perimeter. | EDR | Command and Control | T1105 (Ingress Tool Transfer) | IC-05 (Commodity Malware / Loader) |

## Identity

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| Impossible-travel / anomalous sign-in | Sign-in from an improbable geography/velocity or atypical context. **Malicious:** credential or session theft. **Benign:** VPN, proxy, or user roaming. | IdP / CASB | Initial Access | T1078 (Valid Accounts) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| Brute force / password spray | High-rate or spread authentication failures. **Malicious:** credential guessing. **Benign:** broken automation or lockout storms. | IdP | Credential Access | T1110 (Brute Force) | IC-06 (Identity & Credential Attack) |
| MFA fatigue / push bombing | Repeated MFA prompts to coerce approval. **Malicious:** push-bombing to hijack a session. **Benign:** a user retrying a failing prompt. | IdP | Credential Access | T1621 (Multi-Factor Authentication Request Generation) | IC-06 (Identity & Credential Attack) |
| Legacy-auth sign-in | Authentication via legacy/basic protocols that bypass MFA. **Malicious:** token or credential abuse via a weak path. **Benign:** an old client that only speaks legacy auth. | IdP | Initial Access | T1078 (Valid Accounts) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| OAuth app consent / token-session theft | A suspicious OAuth grant or use of stolen token/session material. **Malicious:** consent-phishing or adversary-in-the-middle token theft. **Benign:** sanctioned app onboarding. | IdP / CASB | Persistence | T1528 (Steal Application Access Token), T1550.001 (Application Access Token) | IC-06 (Identity & Credential Attack), IC-02 (Business Email Compromise) |
| Privileged role / group grant | Assignment of a privileged role or group membership. **Malicious:** privilege escalation or persistence. **Benign:** an approved access change. | IdP | Privilege Escalation | T1098 (Account Manipulation) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |

## Network

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| C2 beaconing / known-bad destination | Periodic or reputation-flagged outbound connections. **Malicious:** command-and-control traffic. **Benign:** routine telemetry or software updates. | Network / proxy / firewall | Command and Control | T1071 (Application Layer Protocol), T1571 (Non-Standard Port) | IC-05 (Commodity Malware / Loader) |
| Download from known-malicious / newly-registered domain | Perimeter-observed retrieval from suspicious infrastructure. **Malicious:** payload delivery. **Benign:** a legitimate newly-registered site. **Distinct from** Endpoint "Ingress tool transfer to host" — same download, but seen at the perimeter rather than on the host. | Proxy / DNS / firewall | Command and Control | T1105 (Ingress Tool Transfer) | IC-05 (Commodity Malware / Loader) |
| Outbound data spike | An anomalous volume of egress data. **Malicious:** data exfiltration. **Benign:** a legitimate bulk transfer or backup. | Network / CASB / firewall | Exfiltration | T1567 (Exfiltration Over Web Service), T1048 (Exfiltration Over Alternative Protocol) | IC-11 (Data Breach / Exfiltration), IC-03 (Ransomware & Digital Extortion) |
| DoS / DDoS pattern | A traffic flood degrading availability. **Malicious:** a deliberate denial-of-service attack. **Benign:** a legitimate traffic surge. | Network / DDoS appliance | Impact | T1498 (Network Denial of Service), T1499 (Endpoint Denial of Service) | IC-04 (Denial of Service) |
| Internal scan / lateral movement | Flow-observed enumeration or lateral connections across internal hosts. **Malicious:** an intrusion spreading. **Benign:** an authorized vulnerability scanner or asset discovery. | Network / NDR | Discovery | T1046 (Network Service Discovery), T1021 (Remote Services) | IC-06 (Identity & Credential Attack), IC-08 (Infrastructure Compromise) |
| DNS tunneling / suspicious DNS | A covert data or command channel over DNS. **Malicious:** tunnelling or exfiltration. **Benign:** a chatty but legitimate resolver. | DNS / NDR | Command and Control | T1071.004 (DNS), T1572 (Protocol Tunneling) | IC-11 (Data Breach / Exfiltration), IC-05 (Commodity Malware / Loader) |
| Anomalous access / change on network-edge device | Unexpected admin access or a configuration change on a router/VPN/firewall. **Malicious:** edge-device compromise. **Benign:** a sanctioned change. | Network device logs | Persistence | T1133 (External Remote Services) | IC-08 (Infrastructure Compromise) |

## Cloud

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| Suspicious IAM policy / role change | A risky identity or permission change in cloud IAM. **Malicious:** privilege escalation or persistence. **Benign:** an approved infrastructure-as-code change. | Cloud audit logs | Privilege Escalation | T1078.004 (Cloud Accounts), T1098.003 (Additional Cloud Roles) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |
| Resource hijacking / cryptomining | Unusual compute/GPU provisioning or mining signatures. **Malicious:** compute theft for cryptomining. **Benign:** legitimate scaling. | Cloud audit / billing | Impact | T1496 (Resource Hijacking) | IC-12 (Resource Hijacking / Cryptojacking) |
| Cloud storage anomalous access | Abnormal read or enumeration of object storage. **Malicious:** data exfiltration. **Benign:** a new analytics workload. **Distinct from** Public exposure of a resource — that is a misconfiguration, this is active access to the data. | Cloud audit / CASB | Exfiltration | T1530 (Data from Cloud Storage) | IC-11 (Data Breach / Exfiltration) |
| Logging / guardrail disabled | Cloud audit logging or security controls turned off. **Malicious:** impairing defences to evade detection. **Benign:** a sanctioned change. | Cloud audit logs | Defense Impairment | T1685.002 (Disable or Modify Cloud Log) | IC-09 (Insider Threat & Privilege Misuse), IC-05 (Commodity Malware / Loader) |
| New principal / access-key creation | Creation of a new user/service principal or access key. **Malicious:** a persistence backdoor. **Benign:** legitimate provisioning. | Cloud audit logs | Persistence | T1136.003 (Cloud Account) | IC-06 (Identity & Credential Attack), IC-09 (Insider Threat & Privilege Misuse) |
| Public exposure of a resource | A bucket, database, VM, or secret made internet-reachable. **Malicious:** exposure enabling exfiltration or attack. **Benign:** an intended public service. | Cloud posture / CSPM | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation), IC-11 (Data Breach / Exfiltration) |
| Unsanctioned SaaS app usage (Shadow IT / Shadow AI discovery) | A user accessing a SaaS application — including AI assistants — not on the sanctioned list, surfaced from endpoint or network telemetry aggregated into a SaaS discovery catalog. **Malicious:** deliberate routing of company data through an unvetted third party to bypass data-governance controls. **Benign:** ad hoc productivity use with no sensitive content, or an app pending a sanctioning decision. **Distinct from** Data "DLP violation (regulated data)" — that confirms sensitive content in transit, this fires on app usage alone, before content is known. | CASB / SaaS discovery | Exfiltration | T1567 (Exfiltration Over Web Service) | IC-09 (Insider Threat & Privilege Misuse), IC-11 (Data Breach / Exfiltration) |

## Email

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| User-reported phishing | An employee-submitted suspected phishing message. **Malicious:** social engineering. **Benign:** unwanted marketing or a mistaken report. | Email gateway / user report | Initial Access | T1566 (Phishing) | IC-01 (Phishing / Social Engineering), IC-02 (Business Email Compromise) |
| Malicious attachment / URL delivered | An email carrying a weaponized attachment or link. **Malicious:** malware or credential-phishing delivery. **Benign:** a false-positive on a safe file or link. | Email gateway / sandbox | Initial Access | T1566.001 (Spearphishing Attachment), T1566.002 (Spearphishing Link), T1204 (User Execution) | IC-01 (Phishing / Social Engineering), IC-05 (Commodity Malware / Loader) |
| Inbox forwarding / redirect or hide rule | A mailbox rule that forwards mail externally or hides it. **Malicious:** BEC data collection or concealment. **Benign:** a user-created convenience rule. | Mailbox audit | Collection | T1114 (Email Collection), T1564 (Hide Artifacts) | IC-02 (Business Email Compromise) |
| BEC impersonation / display-name spoof | A message impersonating an executive or vendor to induce payment or action. **Malicious:** business-email-compromise fraud. **Benign:** a legitimate lookalike sender. | Email gateway | Initial Access | T1656 (Impersonation), T1566 (Phishing) | IC-02 (Business Email Compromise), IC-01 (Phishing / Social Engineering) |

## Data

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| DLP violation (regulated data) | Movement of regulated or sensitive data against policy. **Malicious:** exfiltration or insider misuse. **Benign:** an approved business transfer. | DLP | Exfiltration | T1567 (Exfiltration Over Web Service) | IC-11 (Data Breach / Exfiltration), IC-09 (Insider Threat & Privilege Misuse) |
| Mass sensitive-file access by one principal | One user or service reading large volumes of sensitive files. **Malicious:** insider collection or exfiltration. **Benign:** a legitimate bulk task. | DLP / file audit | Collection | T1039 (Data from Network Shared Drive), T1005 (Data from Local System) | IC-09 (Insider Threat & Privilege Misuse), IC-11 (Data Breach / Exfiltration) |
| Ransom-note file dropped | An extortion note written across directories. **Malicious:** confirmation of ransomware. **Benign:** a filename false-positive. **Distinct from** Endpoint "Ransomware mass-encryption" — this keys on the note artifact, that on the encryption behaviour. | DLP / EDR | Impact | T1486 (Data Encrypted for Impact) | IC-03 (Ransomware & Digital Extortion) |
| Data staging / archiving for exfil | Collection of data into archives or staging locations before egress. **Malicious:** pre-exfiltration staging. **Benign:** a legitimate backup or packaging job. | DLP / file audit | Collection | T1074 (Data Staged), T1560 (Archive Collected Data) | IC-11 (Data Breach / Exfiltration), IC-09 (Insider Threat & Privilege Misuse) |

## Application

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| Web exploitation / injection | Injection or exploit attempts against a web app (SQLi/XSS/SSRF). **Malicious:** active exploitation. **Benign:** scanner or pen-test noise. | WAF / app logs | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |
| Authentication bypass / broken access control | Access to resources without or around authorization (auth bypass, IDOR). **Malicious:** exploitation of an access flaw. **Benign:** a misconfigured but legitimate access path. | WAF / app logs | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |
| Web shell upload | A server-side script planted for remote control via a web app. **Malicious:** a web shell. **Benign:** a legitimate file upload. | WAF / app logs / EDR | Persistence | T1505.003 (Web Shell) | IC-07 (Web App Exploitation), IC-08 (Infrastructure Compromise) |
| API abuse / enumeration / scraping | Automated high-volume or abusive API access. **Malicious:** credential stuffing, scraping, or enumeration. **Benign:** a legitimate high-volume integration. | API gateway / app logs | Discovery | T1595 (Active Scanning), T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation), IC-11 (Data Breach / Exfiltration) |
| Malicious dependency or build-pipeline tampering | A package, container image, or CI/CD step showing unexpected network or code behaviour, or a dependency flagged as malicious or typosquatted. **Malicious:** a poisoned dependency or a compromised build pipeline. **Benign:** a legitimate new dependency or pipeline change. | Software composition analysis / CI/CD audit logs | Initial Access | T1195.001 (Compromise Software Dependencies and Development Tools), T1195.002 (Compromise Software Supply Chain) | IC-10 (Supply-Chain Compromise) |
| AI application abuse | Prompt injection against an AI-powered application, or abusive use of a model inference API (extraction, enumeration, data exfiltration through model outputs). **Malicious:** manipulation or extraction of an AI system. **Benign:** an unusual but legitimate prompt or integration load. | AI gateway / app logs / API gateway | Initial Access / Exfiltration | AML.T0051 (LLM Prompt Injection), AML.T0024 (Exfiltration via ML Inference API), AML.T0040 (ML Model Inference API Access) | IC-15 (AI/ML System Attack), IC-11 (Data Breach / Exfiltration) |
| Insecure deserialization / RCE | Exploitation yielding remote code execution via an application flaw. **Malicious:** remote code execution. **Benign:** an application error resembling an exploit. | WAF / app logs | Execution | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |

## OT/ICS

| Alert Type | Description | Log Source | Tactics | Techniques | Candidate ICs |
|---|---|---|---|---|---|
| Unauthorized controller / PLC command or logic change | An unsanctioned command or ladder-logic/program change to a controller. **Malicious:** manipulation of the physical process. **Benign:** authorized engineering work. | OT IDS / historian | Impair Process Control | T0855 (Unauthorized Command Message), T0831 (Manipulation of Control) | IC-14 (OT/ICS Attack) |
| Industrial-protocol anomaly | Abnormal Modbus/DNP3/S7 traffic or function codes. **Malicious:** manipulation or reconnaissance. **Benign:** maintenance activity. | OT IDS | Collection | T0801 (Monitor Process State), T0830 (Adversary-in-the-Middle) | IC-14 (OT/ICS Attack) |
| Engineering-workstation / HMI compromise | Compromise of an engineering workstation or HMI that bridges IT and OT. **Malicious:** a pivot toward control systems. **Benign:** normal administrator activity. | OT IDS / EDR | Lateral Movement | T0866 (Exploitation of Remote Services), T0822 (External Remote Services) | IC-14 (OT/ICS Attack), IC-08 (Infrastructure Compromise) |

## Where this taxonomy is used
Alert types are the index of the domain [Triage playbooks](../04-Playbooks/README.md): during [Triage](../03-Processes/02-detection_and_analysis.md#1-triage-verification-enrichment--prioritization) the executor matches the observed alert(s) to the types here and carries the mapped techniques and candidate Incident Categories into [Investigation](../03-Processes/02-detection_and_analysis.md#2-deep-dive-investigation--hypothesis-formulation), where competing hypotheses confirm or refute the classification.
