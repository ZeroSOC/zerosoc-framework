---
title: 04-Denial of Service Investigation & Response
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
incident_category: IC-04
mitre_ttps:
  - T1498        # Network Denial of Service
  - T1498.001    # Direct Network Flood
  - T1499        # Endpoint Denial of Service
default_severity: High
required_data_sources:
  - Netflow / DDoS appliance telemetry
  - CDN / WAF logs
  - Application & API gateway logs
  - Upstream ISP / scrubbing-provider telemetry
status: draft
---

# 04-Denial of Service Investigation & Response

Investigation and Incident Response knowledge for Cases whose candidate category is `IC-04 Denial of Service` — deliberate degradation of the availability of a service, network or application by exhausting its resources or flooding it, while systems and data remain intact. Consumes the Triage → Investigation phase transition contract ([Playbook Architecture §5](../playbook_architecture.md#5-phase-transition-contracts)). The method — verify or retract the triage findings, run the queries, resolve by score and coverage — is [Detection & Analysis §2](../../03-Processes/02-detection_and_analysis.md#2-phase-2b--investigation); the containment autonomy matrix is [Incident Response §2.1](../../03-Processes/03-response.md#21-risk-based-autonomy-matrix-for-containment). Hypotheses and queries are indicative, not exhaustive.

IC-04 is the one Incident Category where the Containment, Eradication and Recovery semantics shift: there is no host, payload or account to remediate. **Containment means mitigation** (absorb or shed the traffic), **Eradication means attrition and hardening** (outlast the attacker and close the abused vector), and **Recovery** has no artifact cleanup step at all — only staged de-mitigation and a capacity postmortem.

## Investigation

1. **Hypotheses** (seeded by the candidate category):
   * **Malicious:** a deliberate volumetric, protocol or application-layer flood is degrading the availability of a targeted service.
   * **Benign:** a legitimate traffic surge (a product launch, a marketing event), a misbehaving client retry storm, or an internal capacity or deployment problem.
2. **Validation queries** — each stated as a question; the executor translates it to its query language.
   * *Query 1:* Does the source distribution show spoofed or botnet-like autonomous-system and geographic spread inconsistent with the service's organic client mix ([Network](../99-Shared/sub_enrichment_network.md))? → `Malicious (Medium)` when the spread is inconsistent with the client mix; `Benign (Medium)` when the sources are the known client networks and geographies, with returning clients among them.
   * *Query 2:* Do the offending requests show a uniform signature — identical URI, user agent or packet structure, SYN-only floods, incomplete handshakes — rather than the session diversity of organic traffic? → `Malicious (Medium)` on a uniform signature; `Benign (Medium)` when sessions are diverse and complete as organic ones do.
   * *Query 3:* Does the surge correlate with a business event, marketing campaign, release or deployment window recorded in the SOC Knowledge Base or the business calendar, or does it trace to a single identified client or partner integration retrying? → `Benign (High)` when the record covers the service and the time, or the surge is one identified integration's retry storm — the explanation of the alert; `Malicious (Low)` when no event exists and the surge began abruptly at full volume.
   * *Query 4:* Has a ransom-DoS extortion demand been received through any channel referencing this outage? → `Malicious (High)` on a demand; context when none has been received — most floods carry no demand.
   * *Query 5:* Is the flood concentrated on a single business-critical or computationally expensive endpoint — login, checkout, search, a specific API — rather than spread undirected across the service? → `Malicious (Medium)` on a concentrated flood; `Benign (Low)` when the load spreads across the service the way organic traffic does.
   * *Query 6:* Is the inbound request rate within its baseline while the degradation traces to an internal cause — a deployment, a saturated dependency, a resource limit? → `Benign (High)` when inbound volume is normal and the internal cause is identified — an availability problem, not an attack; `Malicious (Medium)` when inbound volume is many times the baseline.

**Re-classification pivots:** systems, volumes or backups deleted or corrupted so that availability does not return when the traffic stops → [IC-13 (Destructive / Wiper Attack)](13-destructive_wiper.md); the outage caused by an exploit against the application rather than by volume → [IC-07 (Web App Exploitation)](07-web_app_exploitation.md); a flood used as cover for an intrusion elsewhere → the category of that intrusion.

## Incident Response

Once the Malicious hypothesis is proven, the Case is an `IC-04 (Denial of Service)` Incident. Actions marked **requires approval** fall in the approval tier of the autonomy matrix; every other action is pre-authorized, subject to the Case confidence. Containment means traffic mitigation, Eradication means attrition and hardening of the abused vector, and Recovery means staged de-mitigation.

### Containment
*   Apply rate limiting, geographic and autonomous-system blocks, and WAF and CDN filtering rules against the identified flood signature and sources (reversed by removing the rules). Blocklisting a partner or customer network found among the sources — **requires approval**.
*   Activate the scrubbing or anycast mitigation of the CDN or DDoS-mitigation provider for volumetric floods beyond local absorption capacity (reversed by deactivating it). Requesting upstream filtering from the ISP, or changing the network's routing or route announcements to divert the traffic — **requires approval**.
*   Fail over to alternate capacity to preserve service for legitimate users (reversed by failing back). Replacing a revenue-critical service with a maintenance or static page — **requires approval**.

### Eradication
*   Sustain the upstream filtering for the duration of the attack; there is no artifact to remove, only pressure to outlast.
*   Close the abused vector — harden or authenticate the expensive unauthenticated endpoint the flood targeted, cache or throttle it, and fix the capacity or architecture weakness the attack exposed.
*   Where an extortion demand was received, preserve it as evidence and route it through the organization's external-communications channel; a payment is an executive decision under legal counsel, never a playbook action.

### Recovery
*   Lift mitigations in stages, watching for resumption before each next step, each removal recorded in the Case timeline.
*   Feed a capacity and response postmortem back to [Post-Incident Activity](../../03-Processes/04-post_incident_activity.md), and the flood signature and source set to Phase 1 as a detection-tuning signal.

## Completion Criteria & Critical Failures

**Complete when:** the Case is resolved per [Detection & Analysis §2.4](../../03-Processes/02-detection_and_analysis.md#24-hypothesis-resolution-verdict-and-confidence), the Investigation Note is produced and the phase transition contract (or the closure verdict) is emitted; for IC-04, the duration of the impact against the service's availability objective is recorded (it feeds the regulatory notification), mitigations are lifted in stages with resumption monitored at each step, and the capacity and response postmortem is fed back to Post-Incident Activity before closure.

**Critical failures** (auto-fail conditions for [QA sampling](../../07-Governance/agentic_supervision.md)):
*   A Benign close without Query 3 or Query 6 executed.
*   An upstream ISP engagement, a routing change, the blocklisting of a partner or customer network, or the replacement of a revenue-critical service with a maintenance page applied without approval.
*   Lifting mitigation in a single step rather than in stages, without monitoring for resumption before each next step.
*   A received extortion demand not preserved and not recorded in the Investigation Note.
*   Systems or data found destroyed not re-classified when the pivot applies.

## Hunting Pivots

*   Sweep the other public services and the API gateway for the same source set or request signature: a flood aimed at one service usually probes its neighbours.
*   Sweep the 7 days before T0 for short, low-volume floods from the same sources — the calibration runs that precede a full attack.
*   Sweep the application inventory for other expensive unauthenticated endpoints of the kind the flood targeted, before they are found by the same actor.

## References

*   MITRE ATT&CK: T1498, T1498.001, T1499; NIST SP 800-61 Rev. 3.
*   [Playbook Architecture](../playbook_architecture.md); [Incident Categories](../../02-Taxonomy/incident_categories.md); [Network enrichment](../99-Shared/sub_enrichment_network.md); [Post-Incident Activity](../../03-Processes/04-post_incident_activity.md); [IC-13 Destructive / Wiper Attack](13-destructive_wiper.md).
