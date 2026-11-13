---
title: Asset Entity Enrichment
type: reference
last_updated: 2026-11-12
license: Apache-2.0
status: draft
---

# Asset Entity Enrichment

> **Draft.** This enrichment reference has not been verified in detail. Treat it as a proposal open to review rather than as guidance to follow, and expect it to change.

Enrichment content for **asset** entities: host or device, cloud resource, application. This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both Triage and Investigation ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity concept and its OCSF mapping are defined in the [Entity definitions](../../01-Foundation/definitions.md). What may leave the environment during enrichment is governed by [Data-Handling & OSINT Egress Boundaries](../../07-Governance/agentic_guardrails.md#3-data-handling--osint-egress-boundaries).

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## 1. What the asset is

- Resolve the asset in the CMDB or cloud inventory: type, operating system or platform, owner, business service it belongs to. An asset **without an inventory record** is an observation in itself: an unmanaged or shadow asset.
- Resolve **criticality**: what kind of asset is it, is it a **[critical entity](../../01-Foundation/definitions.md#critical-entity)** or does it host or serve one, and on which property is its requirement High ([SOC Knowledge Base](../../01-Foundation/definitions.md#soc-knowledge-base-soc-kb))? The kind and the requirements rate the containment actions on the asset ([Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment)).
- Resolve the network zone, exposure (internet-facing or internal) and the data classification of what it stores or processes.

## 2. What state it is in

- Resolve the **security posture**: EDR or agent coverage and health, patch level, known vulnerabilities, hardening exceptions.
- Resolve **recent changes**: deployments, configuration changes, maintenance windows and scans scheduled on the asset, from change management and the Knowledge Base — the source of most Benign explanations.
- Resolve who is **logged on** and which identities hold sessions on it (pivot to [Identity](sub_enrichment_identity.md)).

## 3. What it talks to

- Resolve the asset's usual peers and destinations over a reference window; note first-seen connections in the Case (pivot to [Network](sub_enrichment_network.md)).

## Produces

- **Asset identity and criticality assessment** — inventory record, owner, business service, kind and requirements (critical entity or not), zone and exposure.
- **Posture summary** — agent coverage, patch level, vulnerabilities and exceptions.
- **Recent-change summary** — deployments, configuration changes and maintenance in the window, with their authorization.
- **Session and peer inventory** — identities on the asset and its usual and first-seen peers.
