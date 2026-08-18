---
title: ZeroSOC Framework Index
type: index
last_updated: 2026-08-17
license: Apache-2.0
---

<p align="center">
  <img src="assets/zerosoc_logo.svg" alt="ZeroSOC Logo" width="450">
</p>

# ZeroSOC Framework

![ZeroSOC Framework Infographic](assets/zerosoc_infographic.svg)

The ZeroSOC Framework is a vendor-independent standard for Security Operations, providing an authoritative body of knowledge defining taxonomy, playbooks, performance metrics, and agentic governance.

> **Practitioners — start here →** [Playbook Operating Guide](04-Playbooks/README.md): the operational entry-point that routes any alert through triage → investigation → response.

## Mission

Our mission is to standardize how human analysts, deterministic automation, and AI agents reason about, investigate, and respond to security threats. By formalizing the definitions and providing extensible, hierarchical playbooks, the ZeroSOC Framework aims to build a scalable and mathematically precise approach to modern Detection and Response.

## Core Principles & Philosophy

The ZeroSOC Framework is built upon the strategic mandate of providing a trustworthy foundation for autonomous Security Operations. This philosophy is governed by three core principles detailed in the [Framework Manifest](01-Foundation/framework_manifest.md):

```mermaid
graph TD
    classDef principal fill:#1b2a47,stroke:#3b5998,stroke-width:2px,color:#fff;
    classDef axis fill:#2d3748,stroke:#4a5568,color:#e2e8f0;
    classDef quote fill:#742a2a,stroke:#9b2c2c,color:#fff;

    subgraph Principles ["ZeroSOC Core Philosophy"]
        Mandate["Strategic Mandate: trustworthy, grounded autonomous SecOps"]
        Karpathy["Karpathy's Law: 'You can outsource thinking, but you cannot outsource understanding.'"]
        
        subgraph Neutrality ["Executor Neutrality"]
            TechAxis["Technology Independence<br>(No vendor/query lock-in)"]
            ExecAxis["Executor Independence<br>(Human = Automation = Agent)"]
        end

        Readability["Human Readability & Actionability<br>(Conformance Property)"]
        Transparency["Transparency & Auditability<br>(Glass Box Execution)"]
    end

    Mandate --> Karpathy
    Karpathy --> Readability
    Readability --> Transparency
    Neutrality --> Readability
    TechAxis -.->|Process & Playbook level| ExecAxis
```

1. **Strategic Mandate for Trustworthy Autonomy:** SecOps agents must execute actions based on grounded, mathematically precise playbooks to guarantee consistency and safety.
2. **Executor Neutrality:** Processes are designed to be independent of both technology (vendor-neutral) and executor (human, deterministic automation, or agent — or any blend of the three). Every step must be fully executable by a qualified analyst reading the documentation alone.
3. **Human Readability as a Conformance Property:** Because *"you can outsource thinking, but you cannot outsource understanding,"* every playbook must remain human-readable and actionable. Human comprehension is the ultimate boundary for agent auditability and transparency.

## Operational Architecture & Pipeline

ZeroSOC structures the flow of security observations from raw telemetry through to incident containment and post-hoc metrics review. The operational pipeline governs how alerts pivot into security cases and resolved outcomes:

```mermaid
graph TD
    classDef input fill:#1b2a47,color:#fff,stroke:#3b5998,stroke-width:1.5px;
    classDef process fill:#2d3748,color:#e2e8f0,stroke:#4a5568,stroke-width:1.5px;
    classDef decision fill:#2d3748,color:#e2e8f0,stroke:#4a5568,stroke-width:1.5px;
    classDef gate fill:#b45309,color:#fff,stroke:#d97706,stroke-width:2px;
    classDef deliverable fill:#1e3a5f,color:#90cdf4,stroke:#3182ce,stroke-dasharray: 5 5;
    classDef gov fill:#742a2a,color:#fff,stroke:#9b2c2c;

    subgraph P1 ["Phase 1: Preparation & Detection"]
        Telemetry[Raw Telemetry] -->|Parsed & Normalized| Events[Security Events]
        Events -->|Security Observations| Signals["Signals<br>(Informational Finding)"]
        Signals -->|Correlated & Thresholded| G1["G1: Alert Raised<br>(Detection Finding severity ≥ 2)"]
        Events -->|Direct Detection Rules| G1
    end

    subgraph P2 ["Phase 2: Detection & Analysis"]
        subgraph P21 ["Phase 2.1: Triage (System 1 — Fast Thinking)"]
            G1 --> Triage[Domain Triage Playbook<br>Enrich Context & Validate Priority]
            Triage --> G2{"G2: Triage Decision"}
            G2 -->|Close: FP / Benign| Close1[Close Case & Emit Tuning Signal]
        end

        subgraph P22 ["Phase 2.2: Investigation (System 2 — Slow Thinking)"]
            G2 -->|Promote to Investigation| Investigate[IC Playbook<br>Concurrent A/B Hypothesis Testing]
            Investigate --> G3{"G3: Case Verdict"}
            G3 -->|Close: Benign / FP| Close2[Close Case & Emit Tuning Signal]
        end
    end

    subgraph P3 ["Phase 3: Incident Response"]
        G3 -->|A: Confirmed TP Incident| Respond[CSIRT Containment, Eradication & Recovery]
        Respond --> G4["G4: Containment Confirmed"]
    end

    subgraph P4 ["Phase 4: Post-Incident Activity"]
        Respond -.-> G5["G5: Post-Incident Review / RCA & QA Sampling"]
    end

    subgraph Deliverables ["06-Deliverables"]
        Triage -.->|Produces at G2| TNote[Triage Note]
        Investigate -.->|Produces at G3| INote[Investigation Note]
    end

    subgraph Governance ["07-Governance"]
        Guardrails[Agentic Guardrails & JIT Scoping] -.->|Constrains Execution| Respond
        Supervision[Agentic Supervision & QA] -.->|Audits at G5| TNote
        Supervision -.->|Audits at G5| INote
    end

    subgraph Metrics ["05-Metrics"]
        Gates[Operational Metrics<br>Speed: MTTA / MTTC / MTTR<br>Quality: FP Surface & Promotion Precision<br>Cost: Token Economics]
    end

    P2 -.->|Measured by Gates G1-G5| Gates
    P3 -.->|Measured by Gates G1-G5| Gates

    class Telemetry,Events,Signals input;
    class Triage,Investigate,Respond,Close1,Close2 process;
    class G2,G3 decision;
    class G1,G4,G5 gate;
    class TNote,INote deliverable;
    class Guardrails,Supervision,Gates gov;
```

* **Domain Triage Playbooks (Phase 2.1):** Initial alert ingest (Gate G1) routes to one of 8 telemetry domains (Endpoint, Cloud, Identity, Network, etc.) where entities are enriched and operational priority is recalibrated. Alerts are either closed as False Positive / Benign Positive (emitting tuning feedback) or promoted to active investigation with a candidate Incident Category (Gate G2).
* **Incident Category (IC) Investigation Playbooks (Phase 2.2):** Promoted cases undergo Concurrent A/B Hypothesis Testing (Malicious vs. Benign) to establish a definitive Case Verdict (Gate G3).
* **Incident Response (Phase 3):** Confirmed True Positive incidents trigger active incident response, tactical containment execution (Gate G4), eradication, and recovery.
* **Deliverables & Provenance:** Every Phase produces structured, human-readable documentation (Triage Note, Investigation Note) with mandatory audit trails.
* **Governance & Metrics:** Agent and automation execution is bound by Least Access / JIT guardrails and audited by human supervision QA (Gate G5), with metrics tracking velocity (MTTA/MTTC/MTTR), stage-differentiated false-positive surfaces, and token economics.

## Core Modules Index

The framework is organized into seven foundational modules:

1. **[01-Foundation](01-Foundation/framework_manifest.md)**: The core manifest, roles and responsibilities (Security Analyst, Detection Engineer, Threat Hunter, SOC Manager), design decisions, roadmap, and OCSF-aligned SOC glossary. Standardizes terminology using OCSF `type_id` bands (Scalar primitive types < 20 e.g., Hostname, IP, Hash vs. Full entity objects ≥ 20 e.g., Endpoint, User, File).
2. **[02-Taxonomy](02-Taxonomy/incident_categories.md)**: An incident classification system focusing on Business Impact. Includes telemetry domain-specific [Alert Type Taxonomy](02-Taxonomy/alert_types.md) and 15 business-impact Incident Categories (IC-01 to IC-15) mapped directly to MITRE ATT&CK/ATLAS threat tactics and techniques.
3. **[03-Processes](03-Processes/00-detection_and_response_lifecycle.md)**: Core operational workflows mapped to NIST CSF 2.0, NIST SP 800-61 Rev. 3, ISO/IEC 27035:2023, and ISO/IEC 27001:2022 (A.5.24 - A.5.28). Outlines the operational phases (Preparation, Detection & Analysis, Response, and Post-Incident).
4. **[04-Playbooks](04-Playbooks/README.md)**: Hierarchical playbook standard powered by Concurrent A/B Hypothesis Testing (Malicious vs. Benign). Divided into domain-specific **Triage Playbooks** (normalizing/enriching alerts at Gate G2) and Incident-Category-specific **Investigation & Response Playbooks** (Gate G3).
5. **[05-Metrics](05-Metrics/operational_metrics.md)**: Process-anchored speed metrics (MTTD, MTTA, MTTV, MTTC, MTTR, HITL Dwell Time), stage-differentiated False-Positive Surface (Promotion Precision, Case Noise Rate), paired autonomy-quality metrics, and Token Economics (compute/LLM pricing).
6. **[06-Deliverables](06-Deliverables/README.md)**: Fill-in templates and golden exemplars for the framework's written deliverables (Triage Note and Investigation Note), with mandatory provenance metadata for Glass Box audit trails.
7. **[07-Governance](07-Governance/agentic_guardrails.md)**: Guardrails for autonomous execution (automation and AI agents) in SecOps. Details Least Access identity (JIT Scoping, Time-Boxing), standard HITL containment payloads, autonomous action boundaries, and OSINT data egress restrictions.


## Module & Component Relationships

The diagram below illustrates how standard definitions, governance rules, playbook architectures, operational processes, and metrics interface with each other in the ZeroSOC framework:

```mermaid
graph TD
    subgraph Foundation ["01-Foundation"]
        F1["SOC Glossary (OCSF-aligned)"]
        F2["Framework Manifest & Roles"]
    end

    subgraph Taxonomy ["02-Taxonomy"]
        T1["Alert Types (by domain)"]
        T2["Incident Categories (business impact)"]
        T3["MITRE ATT&CK / ATLAS Mapping"]
    end

    subgraph Processes ["03-Processes"]
        P1["Phase 1: Preparation (DaC)"]
        P2["Phase 2: Detection & Analysis (Triage + Investigation)"]
        P3["Phase 3: Incident Response (C/E/R)"]
        P4["Phase 4: Post-Incident (RCA)"]
    end

    subgraph Playbooks ["04-Playbooks"]
        PB1["Playbook Architecture (standard)"]
        PB2["Triage Playbooks (by domain)"]
        PB3["Investigation & Response Playbooks (by IC)"]
    end

    subgraph Metrics ["05-Metrics"]
        ME1["Funnel & Volume Metrics"]
        ME2["Speed Metrics<br>(MTTD/A/V/C/R, HITL Dwell)"]
        ME3["Disposition Quality<br>(False-Positive Surface)"]
        ME4["Autonomy & Paired Metrics"]
        ME5["Token Economics & Cost"]
    end

    subgraph Deliverables ["06-Deliverables"]
        D1["Triage Note template"]
        D2["Investigation Note template"]
    end

    subgraph Governance ["07-Governance"]
        G1["Agentic Guardrails"]
        G2["Agentic Supervision"]
        G3["Glass Box Protocols"]
    end

    %% Relationships
    F1 -.->|Standardizes Terminology| T1
    F1 -.->|Standardizes Terminology| T2
    F1 -.->|Standardizes Terminology| P2
    T3 -->|Maps techniques to| T1
    T1 -->|Classifies to candidate| T2
    T1 -->|Sourced by| PB2
    T2 -->|Selects| PB3
    PB1 -.->|Governs structure of| PB2
    PB1 -.->|Governs structure of| PB3
    P2 -->|Triage uses| PB2
    P2 -->|Investigation executes A/B| PB3
    PB3 -->|Confirms Incident| P3
    P2 -->|Produces| Deliverables
    P3 -->|Triggers Post-Mortem| P4

    ME2 -->|Measures timelines of| P2
    ME2 -->|Measures timelines of| P3
    ME2 -->|Measures timelines of| P4
    ME3 -->|Measures precision of| P1
    ME3 -->|Measures precision of| P2
    ME3 -->|Measures precision of| P3
    ME5 -->|Tracks compute cost of| P2
    ME5 -->|Tracks compute cost of| P3
    G2 -->|Audits feed QA to| ME3

    G1 -->|Constrains Containment in| P3
    G2 -->|Monitors Agent Actions in| P2
    G2 -->|Monitors Agent Actions in| P3
    G3 -->|Ensures Auditable Reasoning in| PB3
```

## Versioning & Document Status

Every framework document declares a **release status** in its frontmatter — `draft` / `development` / `stable` / `deprecated` — defined, together with the promotion rules and the framework's Semantic Versioning scheme (`MAJOR.MINOR.PATCH`, e.g. `v0.1.0`), in the [Framework Manifest](01-Foundation/framework_manifest.md#versioning--document-release-status). Adopters conform to a tagged release, never to the live repository; [log.md](log.md) doubles as the changelog.

## Standard Alignment

ZeroSOC is designed to interoperate with and build upon the industry's most trusted standards. This section is the **canonical registry of the exact standard/framework versions** ZeroSOC is currently built upon; other documents reference standards by name only and defer to the versions recorded here.

*   **Strategic Governance:** NIST CSF 2.0
*   **Tactical Incident Handling:** NIST SP 800-61 Rev. 3
*   **Process Governance:** ISO/IEC 27035:2023 & ISO/IEC 27001:2022
*   **Data Schema:** Open Cybersecurity Schema Framework (OCSF) v1.8.0
*   **Threat Tactics & Techniques:** MITRE ATT&CK® v19
*   **Cost & Billing Normalization:** FinOps Foundation FOCUS v1.2 (ratified 2025)
*   **Regulatory Compliance:** Designed to support EU NIS2 and DORA auditing requirements and notification timelines.

## License, Trademarks & Contributing

The ZeroSOC Framework is licensed under the **[Apache License 2.0](LICENSE)** (see also [NOTICE](NOTICE) and [DD-15](01-Foundation/design_decisions.md)).

Contributions are welcomed! Before contributing, please review our **[Contributing Guidelines](CONTRIBUTING.md)** and ensure all commits are signed off under the Developer Certificate of Origin (DCO).

The license grants no rights to the "ZeroSOC" name (License §6); naming and commercial-branding rules are defined in the **[Trademark Policy](TRADEMARKS.md)**.

---
*An open standard for the next generation of Security Operations.*
