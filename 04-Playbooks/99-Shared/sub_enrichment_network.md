---
title: Network Entity Enrichment
type: reference
last_updated: 2026-09-10
license: Apache-2.0
status: draft
---

# Network Entity Enrichment

Enrichment content for **network** entities — the IP address, domain, and URL **observables** (the scalar/primitive band of the OCSF [Observable](https://schema.ocsf.io/1.8.0/objects/observable) object, `type_id` < 20) that pivot an investigation. This is one of the phase-neutral per-entity enrichment sub-playbooks consumed by both the Triage and Investigation methods ([Detection & Analysis](../../03-Processes/02-detection_and_analysis.md)); the entity-vs-observable distinction is defined in the [Entity definitions](../../01-Foundation/definitions.md). Governance policy on egress is canonical in [Data-Handling & OSINT Egress Boundaries §4](../../07-Governance/agentic_guardrails.md); the operative rules are restated inline in [§3](#3-egress-rules-what-may-leave-the-environment) for immediate use at the point of work.

> **Terminology.** *Observable* is the neutral OCSF umbrella for any network scalar. *Indicator* is reserved here for **external** observables — external-facing infrastructure that may carry threat signal. Internal observables (your own IPs, hosts, and services) are **not** indicators and are never treated as such.

Sibling references: [Identity](sub_enrichment_identity.md) · [Asset](sub_enrichment_asset.md) · [Network](sub_enrichment_network.md) · [Artifact](sub_enrichment_artifact.md) · [Email message](sub_enrichment_email_message.md).

## 1. Classify the observable first (internal / external / ambiguous)

Classification decides the entire enrichment path and which tools may touch the observable. **Do it before any lookup.** Classify by **ownership/control, not traffic direction** — the same address can be a source in one event and a destination in the next; what matters is whether it is yours.

| Class | IP | Domain / URL | Enrichment route |
|---|---|---|---|
| **Internal / org-controlled** | RFC1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), CGNAT `100.64.0.0/10`, link-local `169.254.0.0/16` / `fe80::/10`, loopback `127.0.0.0/8` / `::1`, IPv6 ULA `fc00::/7` — **plus org-owned *public* ranges** (allocated CIDRs / ASNs registered to the org, recorded in IPAM) | Internal DNS namespaces (split-horizon corp zones, `.internal` / `.corp` / `.lan` / `.home.arpa`, AD-integrated zones); a host resolving only via internal DNS or to an internal IP | Internal systems of record ([§2.1](#21-internal-observables--resolve-ownership-and-identity-from-internal-systems)) — **never** public TI |
| **External (indicator)** | Publicly routable and **not** in an owned range | Externally registered (public WHOIS/registry); resolves via public DNS to non-owned infrastructure | Threat intelligence + registration + safe content inspection ([§2.2](#22-external-observables-indicators--threat-intelligence-registration-safe-content-inspection)) |
| **Ambiguous** | A public IP that may be **owned-but-not-inventoried** (shadow IT/cloud, M&A assets) | A host with split-horizon ambiguity, or a name resembling an owned brand | **Fail safe: treat as internal** for egress until positively confirmed external ([§3](#3-egress-rules-what-may-leave-the-environment)) |

The subtle case is the **org-owned public range**: a routable, internet-facing IP can still be yours. Resolve ownership from IPAM / ASN allocation and cloud-tenancy records before classifying such an address as external.

## 2. Enrichment by class

### 2.1 Internal observables — resolve ownership and identity from internal systems

The goal is to turn the observable into a **known asset and owner**, not a reputation score. Public TI has nothing authoritative to say about your own address space, and querying it leaks topology (see [§3](#3-egress-rules-what-may-leave-the-environment)).

- **Internal IP →** resolve to a host via IPAM / DHCP lease / reverse DNS (PTR); then CMDB for asset identity, owner, business criticality (Crown-Jewel status), and network zone; NAC / switch-port / AD computer object for the live binding. Pivot to [Asset](sub_enrichment_asset.md) and [Identity](sub_enrichment_identity.md) (owner).
- **Internal domain / hostname →** internal (split-horizon) DNS forward/reverse, AD-integrated zones, and the service/CMDB catalog for the owning application and team.
- **Internal URL →** the internal application/service catalog for the owning app, team, and data classification. **Do not detonate or render** a known internal service — investigate it as an [Asset](sub_enrichment_asset.md), not as a threat indicator.
- **Signal:** an internal IP or host with **no IPAM or CMDB record** is itself notable — an unmanaged, rogue, or shadow asset — and SHOULD be flagged, not dismissed.

### 2.2 External observables (indicators) — threat intelligence, registration, safe content inspection

- **External IP →** multi-source reputation; ASN / hosting provider / geolocation; passive DNS (domains that have historically resolved here). Note whether it is **shared infrastructure** (CDN, cloud, shared hosting): the reputation of a shared host does **not** attribute to the specific tenant, so corroborate before acting. Query the **bare IP** only.
- **External domain →** registration age / WHOIS — a **newly-registered domain** is elevated risk; passive DNS and resolution history (**fast-flux** = many rapidly-rotating IPs); registrar / nameserver patterns and content categorization; and a **lookalike / homoglyph / typosquat** check against owned brands and high-value partners. Query the **registered domain** only.
- **External URL →** reputation and categorization on the **host/domain component only**; retrieve or inspect content **only** via safe rendering or detonation in a **private, isolated sandbox** — never a public one, and never by direct analyst visit.

## 3. Egress rules (what may leave the environment)

These are the operative, immediately-actionable constraints; the governing policy and its NIS2/DORA rationale are canonical in [Data-Handling & OSINT Egress Boundaries §4](../../07-Governance/agentic_guardrails.md). Apply them per the [§1](#1-classify-the-observable-first-internal--external--ambiguous) classification. The keywords are RFC 2119.

- Internal observables (any internal IP, hostname, domain, or URL) **MUST NOT** be sent to any public or third-party service — no public TI or reputation lookup, no public WHOIS on internal names, no public geolocation, no public sandbox. It leaks internal topology, naming, and addressing to attackers and third parties, and returns nothing authoritative. Enrich strictly against internal systems ([§2.1](#21-internal-observables--resolve-ownership-and-identity-from-internal-systems)).
- External indicators **MAY** be queried against public services, but only as **non-attributable, pre-computed scalars** — a bare external IP or a registered domain.
- **Full URLs MUST NOT** be submitted to public services — a URL path or query string may embed session tokens, credentials, PII, or internal hostnames. Send only the **host/domain** component.
- **Dynamic or behavioral analysis** (URL rendering, content detonation) **MUST** use a private, isolated sandbox, never a public one — public submission tips the threat actor that their infrastructure is detected, prompting them to rotate it.
- When class is **ambiguous** ([§1](#1-classify-the-observable-first-internal--external--ambiguous)), apply the **internal** rule (no egress) until ownership is positively confirmed external.

## 4. Cross-entity pivots

- **Internal IP / host →** [Asset](sub_enrichment_asset.md) (identity, criticality, zone) and [Identity](sub_enrichment_identity.md) (owner/operator).
- **External indicator →** the internal [Asset](sub_enrichment_asset.md)s that communicated with it (scope of exposure), and [Artifact](sub_enrichment_artifact.md) for any file or hash it served or received.
- **Sender / URL / domain** observables surfaced from mail flow pivot to and from [Email message](sub_enrichment_email_message.md).

## 5. Risk elevators (quick reference)

| Signal | Applies to | Why it matters |
|---|---|---|
| Newly-registered domain (low WHOIS age) | External domain / URL | Fresh infrastructure is a hallmark of phishing and C2 staged shortly before use. |
| High-entropy / DGA-like name | External domain | Algorithmically-generated names indicate automated C2 infrastructure. |
| Lookalike / homoglyph / typosquat of an owned brand | External domain | Targets your users and partners for impersonation and credential harvesting. |
| Fast-flux (rapidly rotating A records) | External domain | Evasive, resilient hosting typical of botnets and bulletproof providers. |
| Reputation hit on shared hosting / CDN | External IP | Suggestive but **not** attributable to the specific tenant — corroborate before acting. |
| Internal IP / host with no IPAM or CMDB record | Internal IP | Unmanaged, rogue, or shadow asset — a visibility and exposure gap in itself. |
| Owned-public IP exposing an unexpected internal service | Ambiguous / owned-public | Possible shadow-IT exposure or misconfiguration widening the external attack surface. |

## Produces

- **Observable classification verdict** — internal / external / ambiguous determination per [§1](#1-classify-the-observable-first-internal--external--ambiguous), which fixes the enrichment route and egress path taken.
- **Ownership and identity resolution** — for internal observables, the resolved host, asset, owner, and zone ([§2.1](#21-internal-observables--resolve-ownership-and-identity-from-internal-systems)).
- **Reputation and registration findings** — for external observables, multi-source reputation, ASN/hosting/geolocation, passive DNS, and WHOIS/registration-age findings ([§2.2](#22-external-observables-indicators--threat-intelligence-registration-safe-content-inspection)).
- **Risk elevators** — any matched signals (newly-registered domain, DGA-like name, lookalike/typosquat, fast-flux, shared-hosting reputation hit, unmanaged internal host) from [§5](#5-risk-elevators-quick-reference).
