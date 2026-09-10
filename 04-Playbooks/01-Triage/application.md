---
title: Application Triage Playbook
type: playbook
last_updated: 2026-09-10
license: Apache-2.0
domain: Application
required_data_sources:
  - Web Application Firewall (WAF)
  - Application logs
  - API gateway logs
status: draft
---

# Application Triage Playbook

Triage knowledge for **Application** alerts. The object of triage is the **Alert**; alert types are defined in the [Alert Type taxonomy](../../02-Taxonomy/alert_types.md). The method — enrichment, scope, the coverage rule that closes or promotes a Case — is [Detection & Analysis §1](../../03-Processes/02-detection_and_analysis.md#1-phase-2a--triage-verification-enrichment--prioritization); this playbook says what to look at for each alert type and what each observation is evidence of. Checks and conditions are indicative, not exhaustive.

## Alert Catalog

One row per alert type of this domain; each row is the index into a subsection of [Per-Alert Triage](#per-alert-triage). Tactics and techniques are the candidates an alert type may map to, not a conjunction.

| Alert Type | Log Source | Tactics | Techniques | Candidate Incident Categories |
|---|---|---|---|---|
| Web exploitation / injection | WAF / app logs | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |
| Authentication bypass / broken access control | WAF / app logs | Initial Access | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |
| Web shell upload | WAF / app logs / EDR | Persistence | T1505.003 (Web Shell) | IC-07 (Web App Exploitation), IC-08 (Infrastructure Compromise) |
| API abuse / enumeration / scraping | API gateway / app logs | Discovery | T1595 (Active Scanning), T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation), IC-11 (Data Breach / Exfiltration) |
| Malicious dependency or build-pipeline tampering | Software composition analysis / CI/CD audit logs | Initial Access | T1195.001 (Compromise Software Dependencies and Development Tools), T1195.002 (Compromise Software Supply Chain) | IC-10 (Supply-Chain Compromise) |
| AI application abuse | AI gateway / app logs / API gateway | Initial Access / Exfiltration | AML.T0051 (LLM Prompt Injection), AML.T0024 (Exfiltration via ML Inference API), AML.T0040 (ML Model Inference API Access) | IC-15 (AI/ML System Attack), IC-11 (Data Breach / Exfiltration) |
| Insecure deserialization / RCE | WAF / app logs | Execution | T1190 (Exploit Public-Facing Application) | IC-07 (Web App Exploitation) |

## Per-Alert Triage

### Web exploitation / injection

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (the source), [Device](../99-Shared/sub_enrichment_asset.md) (the targeted application or host), [User](../99-Shared/sub_enrichment_identity.md) (the authenticated session, if any).
- **Checks:**
  1. **Payload validity.** Is the flagged input a syntactically real injection attempt (SQL, script, server-side request) against a live parameter, or ordinary user content that happens to match a signature? → `Malicious (Medium)` when it is a valid attempt against a live parameter; `Benign (Medium)` when it is ordinary content — a SQL fragment in a support ticket, markup in a rich-text field.
  2. **Target response.** Did it land? → `Malicious (High)` when the application returned a database error, unexpected data, a delay matching a time-based payload, or made an outbound request from the server; `Benign (Low)` when every request was blocked or answered normally — an attempt without effect, consistent with untargeted background scanning.
  3. **Source classification.** Who is the source? → `Benign (High)` when it is in the range of an authorized penetration test or DAST scan recorded for this application and this window; `Malicious (Medium)` when it is reputation-flagged infrastructure; `Malicious (Low)` when it is an anonymizing exit or a hosting provider — common for both attackers and scanners.
  4. **Repetition and targeting.** Is the source probing many parameters and endpoints broadly, or refining payloads against one endpoint? → `Malicious (Medium)` on refinement against a single target; `Malicious (Low)` on broad, unrefined probing — internet background noise.
- **False Positive conditions:** a signature matching ordinary user content; a parser artifact on encoded parameters; a stale rule for a vulnerability already patched or a parameter that no longer exists; the application's own synthetic monitoring transactions.
- **Benign conditions:** an authorized penetration test or DAST scan; the vulnerability scanner on its schedule; a bug-bounty researcher within the program's scope.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation).

### Authentication bypass / broken access control

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (the accessed-as identity and the actual identity), [Network observable](../99-Shared/sub_enrichment_network.md) (the source), [Device](../99-Shared/sub_enrichment_asset.md) (the application).
- **Checks:**
  1. **Object reference manipulation.** Is the request manipulating an object reference or identifier to reach data or actions outside the caller's scope? → `Malicious (Medium)` on sequential or out-of-scope identifiers without prior authorization; `Benign (Low)` when the identifiers fall within the caller's own scope — a client retrying or paginating.
  2. **Access outcome.** Did the bypass work? → `Malicious (High)` when out-of-scope data was returned or an unauthorized action was performed; `Malicious (Low)` when the application correctly rejected it — the attempt stands, without effect.
  3. **Session legitimacy.** Where does the request come from? → `Malicious (Medium)` when an anonymous or unauthenticated source reaches a protected resource, or a valid session behaves like automation (rapid identifiers, a scripting user agent); `Benign (Medium)` when a valid session follows the application's usual navigation.
  4. **Intended path.** Is the access path a documented, intended one? → `Benign (High)` when the path is a recorded permissive integration (a service account, an internal tool), an approved impersonation feature used by support under a ticket, or an authorized test covering the application and the window; `Malicious (Low)` when nothing records it.
- **False Positive conditions:** a rule modelling an authorization scheme that changed — a new role, a new sharing feature; a parser artifact treating a shared or public resource identifier as out-of-scope; a delegated-access or act-as feature misread as bypass.
- **Benign conditions:** a misconfigured but intended permissive access path for a specific integration; support staff using an approved impersonation feature under a ticket; an authorized penetration test.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation).

### Web shell upload

- **Enrich entities:** [File](../99-Shared/sub_enrichment_artifact.md) (the uploaded file), [Device](../99-Shared/sub_enrichment_asset.md) (the application host), [Network observable](../99-Shared/sub_enrichment_network.md) (the uploading source), [Process](../99-Shared/sub_enrichment_artifact.md) (the web server process and its children, when host telemetry exists).
- **Checks:**
  1. **File type and location.** Is the file a server-side script type (`.php`, `.jsp`, `.aspx`) landing in a web-servable directory where the upload feature expects only media or documents? → `Malicious (High)` when it is; `Malicious (Medium)` when it is a polyglot — an image or document with embedded script, a double extension; `Benign (Low)` when it is a document or media file in the expected upload directory.
  2. **Upload path.** Did the file arrive through the application's validated upload feature, or through a flaw — path traversal, extension-filter bypass, content-type mismatch? → `Malicious (High)` on a validation bypass; `Benign (Low)` through the normal feature.
  3. **File content.** What is in it? → `Malicious (High)` when the content is a known web shell by signature or hash, or evaluates request parameters as code; `Benign (High)` when the content is inert — a text file or a valid media file with a misclassified extension — which explains the alert on its own.
  4. **Post-upload access.** Was the file requested over HTTP afterwards, and did the web server process then spawn a shell, a command or file-system access? → `Malicious (High)` when it was requested and execution followed; context when it was never requested.
  5. **Deployment channel.** Did the file arrive through the sanctioned deployment pipeline as part of a release? → `Benign (High)` when the release pipeline or configuration management wrote it under a recorded deployment; `Benign (High)` when a security assessment recorded for this host and window placed a test file.
- **False Positive conditions:** a detection firing on scripts deployed by the release pipeline; an inert file with a script extension; a media file whose header triggers a content heuristic; a content-management feature that legitimately accepts server-side templates or plugins.
- **Benign conditions:** a sanctioned plugin, theme or template install by an administrator under change control; a security tool placing a test file during an authorized assessment.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation); IC-08 (Infrastructure Compromise) when the shell has been used to control the host.

### API abuse / enumeration / scraping

- **Enrich entities:** [Network observable](../99-Shared/sub_enrichment_network.md) (the source), [User](../99-Shared/sub_enrichment_identity.md) (the API key or account, if authenticated), [Device](../99-Shared/sub_enrichment_asset.md) (the targeted API).
- **Checks:**
  1. **Request rate and pattern.** Is the traffic far above the per-client limit, sequentially enumerating identifiers or endpoints in a way no ordinary client would? → `Malicious (Medium)` on systematic enumeration at volume; `Benign (Low)` on bursts within the documented limits or a client paginating.
  2. **Client identity.** Who is the client? → `Benign (High)` when the key or user agent belongs to a recognized integration with a documented rate profile in the Knowledge Base; `Malicious (Medium)` when the client is anonymous, rotates credentials, or rotates source addresses across residential or hosting ranges; `Malicious (High)` when the traffic cycles through many distinct credentials — credential stuffing.
  3. **Data sensitivity of responses.** What are the responses returning? → `Malicious (Medium)` when they contain personal records, credentials or proprietary data; `Malicious (Low)` when they contain public catalog data — abuse without a breach.
  4. **Authorization record.** Is a load test, a partner onboarding or a bulk synchronization recorded for this API and this window? → `Benign (High)` when one covers the client and the time; context when none is recorded.
- **False Positive conditions:** a threshold set below a legitimate client's normal rate; the gateway counting retries or pagination as enumeration; the platform's own synthetic health checks; a client version with a retry bug producing a burst.
- **Benign conditions:** a legitimate high-volume integration or partner consumer with a documented rate profile; an authorized load test; a permitted search crawler on public endpoints.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation); IC-11 (Data Breach / Exfiltration) when sensitive records were returned at volume.

### Malicious dependency or build-pipeline tampering

- **Enrich entities:** [File](../99-Shared/sub_enrichment_artifact.md) (the package, artifact or container image, by hash), [Device](../99-Shared/sub_enrichment_asset.md) (the build runner or developer host), [User](../99-Shared/sub_enrichment_identity.md) (the committer, pipeline identity or token), [Network observable](../99-Shared/sub_enrichment_network.md) (destinations contacted during install or build).
- **Checks:**
  1. **Dependency provenance.** Does the flagged package exist in the package registry under the expected name, publisher and version history? → `Malicious (High)` when the name is a lookalike of a package the project uses, or a public package shadows an internal package of the same name — dependency confusion; `Malicious (Medium)` when the package or the version was published minutes to days ago by a publisher with no history; `Benign (Medium)` when it is the long-standing package and the version matches the upstream release and its signed provenance attestation.
  2. **Advisory match.** Is the exact name and version listed in a malicious-package advisory or the registry's takedown list? → `Malicious (High)` when it is; context when only a vulnerability advisory matches — a vulnerable dependency is a vulnerability-management finding, not a supply-chain attack.
  3. **Install-time and build-time behaviour.** Did the dependency's install hooks or the build step run code that reaches the network, reads environment variables or credential files, spawns shells, or writes outside the build workspace? → `Malicious (High)` when install scripts read tokens or environment variables and send them out, or fetch and execute remote content; `Malicious (Medium)` when the build contacts a destination that is not the sanctioned registry or artifact store; `Benign (Low)` when every contact is to the sanctioned registry and artifact store.
  4. **Pipeline change authorization.** Was the pipeline definition, build script or runner configuration changed — by whom, and through which path? → `Benign (High)` when the change is a reviewed and merged change by a maintainer under a recorded change; `Malicious (High)` when the definition was modified outside review — a direct push, a change by a token rather than a person, a pull request from a fork altering the base branch's workflow; `Malicious (Medium)` when the change adds access to a new secret, adds an external action or plugin pinned to a mutable tag, or disables a signing or verification step.
  5. **Artifact integrity.** Do the lockfile and the built artifact match what was declared? → `Malicious (High)` when the lockfile hash changed for an unchanged version, or the artifact or image digest differs from its provenance attestation or reproducible build; `Benign (Medium)` when digests and attestations match.
  6. **Exposure.** How many projects consumed the package or ran the tampered step, and did any artifact reach production? → context for scope and severity.
- **False Positive conditions:** a composition-analysis rule flagging a package on name similarity alone where the publisher is the expected one; a stale advisory for a version already withdrawn and replaced; a detection on install scripts that legitimately compile native code; a rule counting the organization's registry mirror or proxy as an unknown destination.
- **Benign conditions:** an approved dependency upgrade or new dependency by the owning team under review; a sanctioned pipeline refactor or build-hardening change; install-time behaviour documented by the package's maintainers.
- **Candidate Incident Category(ies):** IC-10 (Supply-Chain Compromise).

### AI application abuse

- **Enrich entities:** [User](../99-Shared/sub_enrichment_identity.md) (the API key, account or session), [Network observable](../99-Shared/sub_enrichment_network.md) (the source), [Device](../99-Shared/sub_enrichment_asset.md) (the application or model endpoint), [File](../99-Shared/sub_enrichment_artifact.md) (a retrieved document or uploaded content carrying the injection, if any).
- **Checks:**
  1. **Injection content.** Does the prompt — or a document, web page, email or tool output the application fed to the model — contain instructions to ignore the system prompt, reveal it, assume a role, or invoke tools beyond the task? → `Malicious (Medium)` on a direct instruction override typed by the user; `Malicious (High)` when the instructions arrive indirectly through retrieved content crafted to trigger tool calls or data return — legitimate content does not instruct the model; `Benign (Medium)` when the flagged text is ordinary phrasing a classifier misread.
  2. **Model and tool outcome.** Did the model comply? → `Malicious (High)` when the output contains data the caller is not authorized for, reveals the system prompt or credentials, or a tool call with a side effect — a message sent, a record changed, a URL fetched — ran outside the task; `Benign (Low)` when the guardrail refused and no tool ran — an attempt without effect.
  3. **Query pattern.** Is the client issuing systematic, high-volume queries — sweeping the input space, probing for training-data membership, or extracting the system prompt piece by piece? → `Malicious (Medium)` on a systematic probing pattern from one client; `Malicious (High)` when the same API key is used from rotating sources or from a source its owner never used — a stolen or shared key; `Benign (Low)` on volume within a documented integration's profile.
  4. **Client identity and authorization.** Who is the caller? → `Benign (High)` when the key or account belongs to a recognized integration with a documented profile, or an AI red-team or evaluation engagement recorded for this application covers the window; `Malicious (Medium)` when the caller is anonymous, rotates credentials, or is a consumer account behaving as automation.
  5. **Data in outputs.** Do the responses carry regulated or proprietary data — personal records from the retrieval store, secrets, another tenant's records? → `Malicious (High)` when the outputs contain data outside the caller's scope; context when they contain public content.
  6. **Exfiltration channel in the output.** Does the output contain a rendered link, an image reference or a tool call that encodes data toward an external destination? → `Malicious (High)` when it does — the classic indirect-injection exfiltration path; context otherwise.
- **False Positive conditions:** a guardrail classifier flagging ordinary phrasing, security-training content or the application's own echo of its system prompt; a content filter firing on a benign prompt in another language or on domain jargon; a rate rule set below a legitimate integration's normal volume; a retrieved document that mentions "ignore instructions" in a legitimate context, such as a policy document.
- **Benign conditions:** an authorized AI red-team or evaluation run; prompt engineering by the product team on a staging endpoint; a recognized integration's batch job; a documented internal tool that extracts the system prompt for testing.
- **Candidate Incident Category(ies):** IC-15 (AI/ML System Attack); IC-11 (Data Breach / Exfiltration) when data left through the model's outputs.

### Insecure deserialization / RCE

- **Enrich entities:** [Device](../99-Shared/sub_enrichment_asset.md) (the application host), [Network observable](../99-Shared/sub_enrichment_network.md) (the source), [Process](../99-Shared/sub_enrichment_artifact.md) (any process spawned by the application, when host telemetry exists).
- **Checks:**
  1. **Payload structure.** Does the request carry a recognizable gadget-chain payload or a serialized object with embedded command or class references? → `Malicious (High)` on a gadget chain or a known exploit payload; `Benign (Medium)` when the input is malformed but non-malicious — a truncated body, a wrong content type — that merely raised a parser error.
  2. **Execution evidence.** Did the application host spawn an unexpected child process, write a file or open an outbound connection right after the request? → `Malicious (High)` when it did; context when it did not — the payload may have failed against a patched target.
  3. **Error signature.** What did the application log? → `Malicious (Medium)` on a deserialization or type-confusion exception coinciding with a crafted request; `Benign (Medium)` on a generic application error unrelated to serialization.
  4. **Vulnerability exposure.** Is the targeted component and version known vulnerable and unpatched, and does the endpoint deserialize the input at all? → `Malicious (Medium)` when it is vulnerable and unpatched; `Benign (Medium)` when it is patched or does not deserialize on that path — the exploit cannot land.
  5. **Source authorization.** Who is the source? → `Benign (High)` when it is the authorized penetration test or DAST scanner recorded for this application and this window; `Malicious (Medium)` when it is reputation-flagged or belongs to a mass-exploitation campaign on a threat-intelligence feed.
- **False Positive conditions:** a generic application exception on malformed client input; a signature matching legitimate serialized objects the application exchanges with a trusted client; a stale rule for a vulnerability already patched.
- **Benign conditions:** an authorized penetration test; an exploit validation by the security team in a recorded window.
- **Candidate Incident Category(ies):** IC-07 (Web App Exploitation).
