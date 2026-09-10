---
title: Asset Entity Enrichment
type: reference
last_updated: 2026-09-10
license: Apache-2.0
status: draft
---

# Asset Entity Enrichment

Enrichment content for **asset** entities: host or device, cloud resource, application. This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both Triage and Investigation ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity concept and its OCSF mapping are defined in the [Entity definitions](../../01-Foundation/definitions.md). What may leave the environment during enrichment is governed by [Data-Handling & OSINT Egress Boundaries](../../07-Governance/agentic_guardrails.md#4-data-handling--osint-egress-boundaries).

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## 1. What the asset is

- Resolve the asset in the CMDB or cloud inventory: type, operating system or platform, owner, business service it belongs to. An asset **without an inventory record** is a finding in itself: an unmanaged or shadow asset.
- Resolve **criticality**: is the asset a **Crown Jewel**, or does it host or serve one ([SOC Knowledge Base](../../01-Foundation/definitions.md#soc-knowledge-base-soc-kb))? A Crown Jewel in the Case scope triggers the human assignee condition of [Agentic Guardrails §3](../../07-Governance/agentic_guardrails.md#3-human-assignee-conditions) and decides which containment actions require approval ([Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)).
- Resolve the network zone, exposure (internet-facing or internal) and the data classification of what it stores or processes.

## 2. What state it is in

- Resolve the **security posture**: EDR or agent coverage and health, patch level, known vulnerabilities, hardening exceptions.
- Resolve **recent changes**: deployments, configuration changes, maintenance windows and scans scheduled on the asset, from change management and the Knowledge Base — the source of most Benign explanations.
- Resolve who is **logged on** and which identities hold sessions on it (pivot to [Identity](sub_enrichment_identity.md)).

## 3. What it talks to

- Resolve the asset's usual peers and destinations over a reference window; note first-seen connections in the Case (pivot to [Network](sub_enrichment_network.md)).

## Produces

- **Asset identity and criticality assessment** — inventory record, owner, business service, Crown Jewel status, zone and exposure.
- **Posture summary** — agent coverage, patch level, vulnerabilities and exceptions.
- **Recent-change summary** — deployments, configuration changes and maintenance in the window, with their authorization.
- **Session and peer inventory** — identities on the asset and its usual and first-seen peers.
