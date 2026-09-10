---
title: ZeroSOC Security Policy
type: policy
status: draft
last_updated: 2026-09-10
license: Apache-2.0
---

# Security Policy

The ZeroSOC Framework is a documentation standard, not executable software — but a standard that guides security operations can still cause harm if it is wrong. This policy defines what counts as a security report here and how to file one.

## What to report

**In scope:**

1. **Dangerous-guidance defects** — a playbook, process step, or guardrail that, followed *as written* by a human, automation, or AI agent, would cause harm. Examples: a containment action with destructive side effects and no verification gate; guidance that exposes credentials or sensitive data; an OSINT/enrichment step whose egress contradicts the [Agentic Guardrails](07-Governance/agentic_guardrails.md); an handover condition that lets an autonomous agent act where the framework mandates human sign-off.
2. **Malicious or compromised content** — links, assets, or embedded content in this repository that point to malicious destinations or have been tampered with.
3. **CI / supply-chain issues** — vulnerabilities in this repository's GitHub Actions workflows or validation tooling.

**Out of scope:** vulnerabilities in third-party tools, products, or standards that the framework references (report those to their respective projects), and ordinary content errors with no harm potential (open an issue for those).

## How to report

Use **[GitHub Private Vulnerability Reporting](https://github.com/ZeroSOC/zerosoc-framework/security/advisories/new)** on this repository. Do **not** open a public issue for anything you believe could cause harm if exploited before a fix lands.

## What to expect

- **Acknowledgement within 5 business days.**
- Coordinated assessment and fix; for dangerous-guidance defects the interim mitigation may be a warning banner on the affected document while the correction is reviewed.
- **Credited disclosure**: once resolved, the report and fix are recorded in [CHANGELOG.md](CHANGELOG.md) under *Security*, with credit to the reporter (unless you prefer to remain anonymous).
