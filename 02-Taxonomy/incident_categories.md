---
title: Incident Categories Taxonomy
type: concept
status: development
last_updated: 2026-09-08
license: Apache-2.0
---

# Incident Categories Taxonomy

The ZeroSOC Framework classifies incidents using the **Incident Category** as the primary high-level classification to represent Business Impact. At the operational level, "the how" is tracked by mapping multiple **MITRE ATT&CK Tactics and Techniques** directly to these categories.

An incident category captures the business impact in simple terms, independent of the execution vector. Triage and investigation rely primarily on identifying MITRE TTPs, which then map to these Incident Categories for playbook selection. Technique references use `ID (Name)` form.

## Categories & MITRE Mappings

### IC-01: Phishing / Social Engineering
*   **Definition:** Deception of a human to obtain access, credentials, or action (email, SMS, voice/vishing, chat, fake software).
*   **Distinguish from:** `IC-02 (Business Email Compromise)` — IC-01 is the social-engineering *delivery/technique* to obtain access; IC-02 is the resulting account/identity *fraud objective*.
*   **Mapped MITRE TTPs:**
    *   T1566 (Phishing)
    *   T1204 (User Execution)

### IC-02: Business Email Compromise
*   **Definition:** Fraud via compromised or spoofed business identities to redirect funds or data; little or no malware.
*   **Distinguish from:** `IC-01 (Phishing / Social Engineering)` — IC-02 is defined by the identity fraud/financial objective; IC-01 is the social-engineering delivery that may precede it.
*   **Mapped MITRE TTPs:**
    *   T1078 (Valid Accounts)
    *   T1114 (Email Collection)
    *   T1564.008 (Email Hiding Rules)

### IC-03: Ransomware & Digital Extortion
*   **Definition:** Encryption, data-theft extortion, or both, with a demand; includes double/triple extortion and leak-only.
*   **Distinguish from:** `IC-05 (Commodity Malware / Loader)` — IC-03 is realized extortion/impact; IC-05 is generic malware not yet tied to a higher objective.
*   **Mapped MITRE TTPs:**
    *   T1486 (Data Encrypted for Impact)
    *   T1490 (Inhibit System Recovery)
    *   T1567 (Exfiltration Over Web Service)

### IC-04: Denial of Service
*   **Definition:** Deliberate degradation of availability of a service, network, or application.
*   **Mapped MITRE TTPs:**
    *   T1499 (Endpoint Denial of Service)
    *   T1498 (Network Denial of Service)

### IC-05: Commodity Malware / Loader
*   **Definition:** Generic malware, loaders, RATs, stealers, botnet agents not yet tied to a specific higher objective.
*   **Distinguish from:** `IC-03 (Ransomware & Digital Extortion)` and other objective-defined categories — IC-05 is the loader/commodity *stage* before a specific objective is established.
*   **Mapped MITRE TTPs:**
    *   T1059 (Command and Scripting Interpreter)
    *   T1105 (Ingress Tool Transfer)

### IC-06: Identity & Credential Attack
*   **Definition:** Theft, spraying, brute force, MFA fatigue, token/session theft, SIM-swap targeting accounts and identity systems.
*   **Mapped MITRE TTPs:**
    *   T1110 (Brute Force)
    *   T1552 (Unsecured Credentials)
    *   T1556 (Modify Authentication Process)

### IC-07: Web App Exploitation
*   **Definition:** Exploitation of internet-facing web apps/APIs (injection, deserialization, auth bypass, RCE).
*   **Distinguish from:** `IC-08 (Infrastructure Compromise)` — IC-07 targets internet-facing application/API logic; IC-08 targets the device or host itself.
*   **Mapped MITRE TTPs:**
    *   T1190 (Exploit Public-Facing Application)

### IC-08: Infrastructure Compromise
*   **Definition:** Compromise of systems that other systems depend on — network and edge devices (routers, firewalls, VPN gateways), servers, hypervisors, and identity infrastructure such as domain controllers — used as a foothold, a pivot, or as relay infrastructure for onward attacks, before a business-impact objective is established.
*   **Distinguish from:** `IC-06 (Identity & Credential Attack)` — IC-06 is an attack on accounts and credentials; IC-08 is compromise of the system that hosts them. `IC-07 (Web App Exploitation)` — IC-07 is app-layer exploitation; IC-08 is compromise of the device or host itself.
*   **Mapped MITRE TTPs:**
    *   T1078 (Valid Accounts)
    *   T1133 (External Remote Services)
    *   T1021 (Remote Services)

### IC-09: Insider Threat & Privilege Misuse
*   **Definition:** Authorized users abusing access (malicious, negligent, or compromised-insider).
*   **Distinguish from:** `IC-11 (Data Breach / Exfiltration)` — IC-09 is defined by *abuse of authorized access*; IC-11 is defined by the *unauthorized data removal* as the act, regardless of actor.
*   **Mapped MITRE TTPs:**
    *   T1078 (Valid Accounts)
    *   T1531 (Account Access Removal)

### IC-10: Supply-Chain Compromise
*   **Definition:** Intrusion via a trusted third party: software build, update, dependency, MSP, or hardware.
*   **Mapped MITRE TTPs:**
    *   T1195 (Supply Chain Compromise)

### IC-11: Data Breach / Exfiltration
*   **Definition:** Unauthorized access to and removal of confidential data as the defining act.
*   **Distinguish from:** `IC-09 (Insider Threat & Privilege Misuse)` — IC-11 is defined by the exfiltration itself, regardless of actor; IC-09 is defined by authorized-user abuse (which may or may not exfiltrate data).
*   **Mapped MITRE TTPs:**
    *   T1048 (Exfiltration Over Alternative Protocol)
    *   T1020 (Automated Exfiltration)

### IC-12: Resource Hijacking / Cryptojacking
*   **Definition:** Theft of compute/network resources (crypto mining, proxyjacking, LLM-jacking).
*   **Mapped MITRE TTPs:**
    *   T1496 (Resource Hijacking)

### IC-13: Destructive / Wiper Attack
*   **Definition:** Intent to destroy, corrupt, or render systems/data permanently unavailable.
*   **Mapped MITRE TTPs:**
    *   T1485 (Data Destruction)
    *   T1561 (Disk Wipe)

### IC-14: OT/ICS Attack
*   **Definition:** Manipulation or disruption of physical/industrial processes via control systems.
*   **Mapped MITRE TTPs:**
    *   T0855 (Unauthorized Command Message)
    *   T0831 (Manipulation of Control)

### IC-15: AI/ML System Attack
*   **Definition:** Attacks targeting AI systems: model evasion, poisoning, extraction, prompt injection, AI-infra exploitation.
*   **Mapped MITRE TTPs:**
    *   AML.T0051 (LLM Prompt Injection)
    *   AML.T0020 (Poison Training Data)
    *   AML.T0043 (Craft Adversarial Data)
    *   AML.T0024 (Exfiltration via ML Inference API)
    *   AML.T0040 (ML Model Inference API Access)

## Usage Guidelines
When triaging a Case, the executor identifies the observed **MITRE ATT&CK TTPs** first. These TTPs map to one or more potential Incident Categories, dictating which candidate Playbooks are selected for Deep-Dive validation and eventual execution.
