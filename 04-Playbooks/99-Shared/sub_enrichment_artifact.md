---
title: Artifact Entity Enrichment
type: reference
last_updated: 2026-09-10
license: Apache-2.0
status: draft
---

# Artifact Entity Enrichment

Enrichment content for **artifact** entities (file, hash, process, registry key; the **email message** artifact has its own [sub-playbook](sub_enrichment_email_message.md)). This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both the Triage and Investigation methods ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity concept and its OCSF mapping are defined in the [Entity definitions](../../01-Foundation/definitions.md). Data-handling and OSINT egress constraints on *how* enrichment is performed are canonical in [Data-Handling & OSINT Egress Boundaries §4](../../07-Governance/agentic_guardrails.md).

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## Process

- Reconstruct parent/child lineage.
- Resolve signer/publisher; flag unsigned or anomalously-parented processes.
- Decode/deobfuscate encoded command lines to reveal the underlying action.

## File

- Resolve multi-engine hash reputation (engine count + family attribution).
- **Query the hash only, never upload the file** — see [Data-Handling & OSINT Egress Boundaries §4](../../07-Governance/agentic_guardrails.md).
- Validate the path (sanctioned install location vs world-writable).

## Produces

- **Process lineage and signer assessment** — reconstructed parent/child lineage plus signer/publisher status, flagging unsigned or anomalously-parented processes.
- **Hash reputation and family attribution** — multi-engine reputation verdict and malware family attribution for the file hash.
- **Path legitimacy assessment** — whether the file resides in a sanctioned install location or a world-writable/anomalous path.
