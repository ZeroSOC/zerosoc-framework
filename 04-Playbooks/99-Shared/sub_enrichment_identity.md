---
title: Identity Entity Enrichment
type: reference
last_updated: 2026-09-10
license: Apache-2.0
status: draft
---

# Identity Entity Enrichment

Enrichment content for **identity** entities: user, account, service principal, and the sessions and tokens they hold. This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both Triage and Investigation ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity concept and its OCSF mapping are defined in the [Entity definitions](../../01-Foundation/definitions.md). What may leave the environment during enrichment is governed by [Data-Handling & OSINT Egress Boundaries](../../07-Governance/agentic_guardrails.md#4-data-handling--osint-egress-boundaries).

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## 1. Who the identity is

- Resolve the account to its **type**: a person, a service identity a workload runs under, a shared or emergency account, an external guest, or a machine identity. Each has a different normal.
- Resolve role, department, manager and privilege level; whether the identity holds, or can activate, an administrative role.
- Check the [SOC Knowledge Base](../../01-Foundation/definitions.md#soc-knowledge-base-soc-kb): is the identity a **VIP** or high-risk user, and is there an **approved exception** covering the observed activity? A **privileged identity** in the Case scope triggers the human assignee condition of [Agentic Guardrails §3](../../07-Governance/agentic_guardrails.md#3-human-assignee-conditions).

## 2. What is normal for it

- Baseline the identity's usual sign-in locations, devices, hours and applications over a reference window (30 days); note the first-seen date of any device, location or application in the Case.
- Resolve the identity's **recent changes**: password or MFA method changes, role grants, consent grants, new application registrations, in the days before the alert.
- Resolve **authorization**: is the observed action in scope for this identity's function, and is there a change ticket or request behind it?

## 3. What it can reach

- Enumerate the identity's effective access: group memberships, roles, resource permissions, mailbox delegations — the scope of damage if the identity is compromised.
- Enumerate its **active sessions and tokens** and the hosts they originate from — the scope of containment if a session must be revoked.

## Produces

- **Identity context summary** — type, role, department, privilege level, VIP or high-risk flag.
- **Authorization assessment** — whether the observed action is in scope for this identity and whether an approved exception or change covers it.
- **Baseline deviation assessment** — which locations, devices, hours or applications in the Case are new for the identity.
- **Recent-change summary** — credential, MFA, role and consent changes in the days before the alert.
- **Reach and session inventory** — effective access and active sessions, for scope and containment.
