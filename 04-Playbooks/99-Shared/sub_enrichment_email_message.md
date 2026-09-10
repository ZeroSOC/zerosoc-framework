---
title: Email Message Entity Enrichment
type: reference
last_updated: 2026-09-10
license: Apache-2.0
status: draft
---

# Email Message Entity Enrichment

Enrichment content for the **email message** entity, an artifact given its own sub-playbook. This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both Triage and Investigation ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity concept and its OCSF mapping are defined in the [Entity definitions](../../01-Foundation/definitions.md). What may leave the environment during enrichment is governed by [Data-Handling & OSINT Egress Boundaries](../../07-Governance/agentic_guardrails.md#4-data-handling--osint-egress-boundaries).

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## 1. Who sent it

- Resolve the **sender authentication posture**: SPF, DKIM and DMARC results and alignment between the envelope sender, the header From and the signing domain.
- Resolve the sending domain and infrastructure: registration age, lookalike or homoglyph relation to an owned or partner brand, reputation (pivot to [Network](sub_enrichment_network.md)); whether it is a known partner or vendor domain, and whether the mailbox shows prior legitimate correspondence with it.
- Resolve the **reply chain**: is the message a reply inside an existing thread, and does the thread history sit in the recipient's mailbox? A genuine thread from a compromised partner mailbox passes every authentication check.

## 2. What it carries

- Resolve the disposition of every URL and attachment: gateway and sandbox verdicts, the host component's reputation. Content is inspected only in a private sandbox, never by visiting the link or submitting the file to a public service.
- Resolve the **request**: what the message asks the recipient to do — sign in, open, pay, change banking details, buy gift cards, call a number. The request type is often the strongest signal when the infrastructure is clean.

## 3. Who else got it and what happened

- Resolve the **campaign breadth**: mailboxes that received the same sender, subject, URL or attachment cluster, and how many reported or interacted.
- Resolve **interaction**: clicks, credential submissions, attachment execution, replies (pivot to [Identity](sub_enrichment_identity.md) and [Asset](sub_enrichment_asset.md) for the recipients who did).

## Produces

- **Sender authenticity verdict** — authentication results and alignment, sender domain assessment, prior-correspondence and thread context.
- **Payload disposition** — the verdict on every URL and attachment.
- **Request assessment** — what the message asks for and whether it matches a known fraud pattern.
- **Campaign breadth and interaction summary** — recipients, reports, clicks, submissions and executions.
