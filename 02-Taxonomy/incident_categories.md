---
title: Incident Categories Taxonomy
type: concept
status: development
last_updated: 2026-09-08
license: Apache-2.0
---

# Incident Categories Taxonomy

The ZeroSOC Framework classifies incidents using the **Incident Category** as the primary high-level classification to represent Business Impact. At the operational level, "the how" is tracked by mapping multiple **MITRE ATT&CK Tactics and Techniques** directly to these categories.

Alert types propose one or more candidate Incident Categories at triage ([Alert Type Taxonomy](alert_types.md)). Investigation confirms a single category from the adversary's observed objective and impact, and the confirmed category selects the [Investigation & Response playbook](../04-Playbooks/README.md). MITRE ATT&CK / ATLAS technique mappings are carried by the alert types and by each playbook, not repeated here; they are indicative, not exhaustive, because the relation between techniques and categories is intentionally loose — a category is decided by objective and impact, not by technique lookup.

**Category shape and precedence.** The categories are of three kinds. **Objective** categories name the realized business impact (IC-02, IC-03, IC-04, IC-11, IC-12, IC-13). **Foothold** categories name what the adversary compromised to get in, before any objective is established (IC-01 a person, IC-05 an endpoint, IC-06 an identity, IC-07 an application, IC-08 infrastructure, IC-10 a trusted supplier). The remaining categories are defined by actor or target (IC-09, IC-14, IC-15). A foothold category holds a Case only until the adversary's objective is established; the objective category then supersedes it. An intrusion stopped before any objective is realized keeps its foothold category as its final classification.

## Categories

### IC-01: Phishing / Social Engineering
*   **Definition:** A user deceived into an action that gives the adversary access or value — credentials entered, an attachment executed, a payment or data handed over — through any channel (email, SMS, voice, chat, fake software or poisoned search results). A foothold category: it is the final classification when the intrusion stops here, and is superseded once an objective is realized.
*   **Distinguish from:** `IC-02 (Business Email Compromise)` — credential phishing is IC-01, not IC-02; IC-02 is the fraud objective conducted through business email identities, which a phish may precede. `IC-06 (Identity & Credential Attack)` — IC-01 is the deception of the person; IC-06 is the attack on the identity or credential system itself, including subsequent use of stolen credentials.

### IC-02: Business Email Compromise
*   **Definition:** Fraud via compromised or spoofed business identities to redirect funds or data; little or no malware.
*   **Distinguish from:** `IC-01 (Phishing / Social Engineering)` — IC-02 is defined by the fraud objective (funds or data redirected through business email identities); the phish that obtained the mailbox is IC-01 until the fraud is attempted.

### IC-03: Ransomware & Digital Extortion
*   **Definition:** Encryption, data-theft extortion, or both, with a demand; includes double/triple extortion and leak-only.
*   **Distinguish from:** `IC-05 (Commodity Malware / Loader)` — IC-03 is realized extortion/impact; IC-05 is generic malware not yet tied to a higher objective. `IC-13 (Destructive / Wiper Attack)` — IC-03 renders data recoverable for a price; IC-13 destroys it with no recovery offered (pseudo-ransomware that cannot decrypt is IC-13).

### IC-04: Denial of Service
*   **Definition:** Deliberate degradation of availability of a service, network, or application by exhausting its resources or flooding it, while systems and data remain intact.
*   **Distinguish from:** `IC-13 (Destructive / Wiper Attack)` — availability returns when a denial-of-service attack stops; IC-13 destroys systems or data, so recovery requires rebuild or restore. A flood against a public website is IC-04; deleting the cloud volumes and their backups is IC-13.

### IC-05: Commodity Malware / Loader
*   **Definition:** Generic malware, loaders, RATs, stealers, botnet agents not yet tied to a specific higher objective.
*   **Distinguish from:** `IC-03 (Ransomware & Digital Extortion)` and other objective-defined categories — IC-05 is the loader/commodity *stage* before a specific objective is established.

### IC-06: Identity & Credential Attack
*   **Definition:** Theft, spraying, brute force, MFA fatigue, token/session theft, SIM-swap targeting accounts and identity systems.

### IC-07: Web App Exploitation
*   **Definition:** Exploitation of internet-facing web apps/APIs (injection, deserialization, auth bypass, RCE).
*   **Distinguish from:** `IC-08 (Infrastructure Compromise)` — IC-07 targets internet-facing application/API logic; IC-08 targets the device or host itself.

### IC-08: Infrastructure Compromise
*   **Definition:** Compromise of systems that other systems depend on — network and edge devices (routers, firewalls, VPN gateways), servers, hypervisors, and identity infrastructure such as domain controllers — used as a foothold, a pivot, or as relay infrastructure for onward attacks, before a business-impact objective is established.
*   **Distinguish from:** `IC-06 (Identity & Credential Attack)` — IC-06 is an attack on accounts and credentials; IC-08 is compromise of the system that hosts them. `IC-07 (Web App Exploitation)` — IC-07 is app-layer exploitation; IC-08 is compromise of the device or host itself.

### IC-09: Insider Threat & Privilege Misuse
*   **Definition:** Authorized users abusing access (malicious, negligent, or compromised-insider).
*   **Distinguish from:** `IC-11 (Data Breach / Exfiltration)` — IC-09 is defined by *abuse of authorized access*; IC-11 is defined by the *unauthorized data removal* as the act, regardless of actor.

### IC-10: Supply-Chain Compromise
*   **Definition:** Intrusion via a trusted third party: software build, update, dependency, MSP, or hardware.

### IC-11: Data Breach / Exfiltration
*   **Definition:** Unauthorized access to and removal of confidential data as the defining act.
*   **Distinguish from:** `IC-09 (Insider Threat & Privilege Misuse)` — IC-11 is defined by the exfiltration itself, regardless of actor; IC-09 is defined by authorized-user abuse (which may or may not exfiltrate data).

### IC-12: Resource Hijacking / Cryptojacking
*   **Definition:** Theft of compute/network resources (crypto mining, proxyjacking, LLM-jacking).

### IC-13: Destructive / Wiper Attack
*   **Definition:** Intent to destroy, corrupt, or render systems/data permanently unavailable — disk wipers, mass deletion, destruction of backups or cloud resources — so that recovery requires rebuild or restore.
*   **Distinguish from:** `IC-04 (Denial of Service)` — IC-04 degrades availability only while the attack lasts and leaves data intact. `IC-03 (Ransomware & Digital Extortion)` — IC-03 offers recovery for payment; IC-13 offers none.

### IC-14: OT/ICS Attack
*   **Definition:** Manipulation or disruption of physical/industrial processes via control systems.

### IC-15: AI/ML System Attack
*   **Definition:** Attacks targeting AI systems: model evasion, poisoning, extraction, prompt injection, AI-infra exploitation.

## Where this taxonomy is used
Candidate categories are attached to a Case during [Triage](../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization), the confirmed category is established during [Investigation](../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation), and playbook selection by category is defined in the [Playbook Architecture](../04-Playbooks/playbook_architecture.md).
