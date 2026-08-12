<!--
Sync Impact Report
- Version change: unratified template → 1.0.0
- Modified principles: none (initial ratification replacing template placeholders)
- Added sections:
  - Core Principles (10 principles with Rationale / Rule / How To Apply)
  - Domain Coverage
  - Review & Compliance
  - Governance
- Removed sections: template placeholder sections ([SECTION_2_NAME], [SECTION_3_NAME] placeholders)
- Follow-up TODOs: none
-->

# alptraining20260812-2 Constitution

## Core Principles

### I. Do Not Distribute by Default

**Domain**: Distributed Systems

**Rationale**: Coordination is a cost measured in round trips, not milliseconds. Every
additional process, service, or queue introduces failure modes, latency, and operational
surface area that compound faster than they scale.

**Rule**: Vertical scaling and a single deployable is the starting point. A new process,
service, or queue MUST NOT be introduced without a written justification tied to exactly one
of: (1) working-set overflow that cannot be addressed by vertical scaling, (2) genuinely
independent compute with no shared working set, (3) geographic latency requirements, or (4)
organizational independence with separate ownership and release cadence.

**How To Apply**:
- A PR that adds a new service, background worker, message queue, or separate deployable
  MUST include a justification section naming the applicable category above.
- A PR that splits an existing monolith without documented overflow, latency, or org
  justification violates this principle.
- Reviewers reject distribution without justification; they do not negotiate category fit
  without written evidence.

### II. Optimize for Deletion, Not Extension

**Domain**: Software Design

**Rationale**: Speculative abstractions ossify faster than duplicated code. A module that
cannot be deleted in a day becomes a permanent liability; duplication below three
occurrences is cheaper than the wrong abstraction.

**Rule**: A module MUST be small enough that one engineer can delete and rewrite it in a
day. Speculative abstractions (interfaces, base classes, generic frameworks without
concrete callers) MUST be rejected. Code MUST be inlined until duplication hurts, then
extracted only when the same pattern appears three or more times.

**How To Apply**:
- A PR introducing a new abstraction layer (shared utility, base class, generic handler)
  without three existing concrete use cases violates this principle.
- A PR adding a module whose scope exceeds one-day rewrite (measured by file count,
  dependency fan-out, or cross-cutting touch points) MUST be split or reduced before merge.
- Reviewers ask: "Can one engineer delete this module tomorrow?" If no, reject or refactor.

### III. Make Dependencies Explicit

**Domain**: Software Design

**Rationale**: Hidden coupling and implicit global state make every change a discovery
exercise. A reader who cannot see dependencies at the function signature or file header
cannot safely modify or delete code.

**Rule**: Hidden coupling, implicit global state, and import-time side effects MUST NOT
exist in new code. Every dependency of a function MUST be visible in its signature or at
the top of its file. Dependency injection MUST be used over singletons. Module-level
mutable state MUST NOT be introduced.

**How To Apply**:
- A PR adding a singleton, global registry, or `getInstance()` pattern violates this
  principle unless replacing an existing singleton with an explicit injection path.
- A PR with import-time side effects (network calls, file writes, config loading at module
  import) violates this principle.
- A PR where a function reaches for ambient context (thread-local, implicit request
  scope, hidden `context` globals) without declaring it in the signature violates this
  principle.

### IV. Contract at the Boundary, Not in the Middle

**Domain**: Data Engineering

**Rationale**: Shared mutable schemas between layers create silent coupling. Semantic
reconciliation belongs at the boundary, owned by the side that understands both producer
and consumer context.

**Rule**: Every producer/consumer boundary (HTTP endpoint, queue message, file format,
database table) MUST have a versioned schema. Semantic reconciliation MUST happen at the
boundary. The owning side MUST be the one that understands both contexts. Shared mutable
schema objects passed between layers MUST NOT exist.

**How To Apply**:
- A PR touching an API, queue, file, or database boundary MUST include or update a
  versioned schema (OpenAPI, JSON Schema, Avro, migration file, etc.).
- A PR passing a mutable domain object across a boundary without conversion violates this
  principle.
- A PR with schema logic embedded in business logic (not at ingress/egress) violates this
  principle.

### V. Test the Transformation, Not the Plumbing

**Domain**: Software Design / Quality

**Rationale**: Mocking owned code tests the mock, not the system. Integration tests at
boundaries and unit tests on pure transformations give signal; plumbing tests give false
confidence.

**Rule**: Unit tests MUST cover pure transformation logic. Integration tests MUST cover
boundaries. Code you own MUST NOT be mocked in unit tests. External systems you do not own
MAY be mocked. A bug fix MUST include a failing test that reproduces the bug before the
fix. CI that passes without a test for the fixed bug is not green.

**How To Apply**:
- A bug-fix PR without a test that fails on the pre-fix code violates this principle.
- A unit test that mocks an internal module, repository, or service you own violates this
  principle (use integration tests for boundary behavior instead).
- Reviewers reject "green CI" on bug fixes when no new test demonstrates the failure mode.

### VI. Emit Structured Events, Derive Everything Else

**Domain**: Observability

**Rationale**: Logs, metrics, and traces are projections of one primitive. Unstructured
log lines cannot be queried, correlated, or alerted on. High-cardinality context is
required for diagnosis, not optional decoration.

**Rule**: Logs, metrics, and traces MUST be derived from structured events. New code MUST
NOT emit unstructured log lines (printf-style, string concatenation without fields).
Structured events MUST include high-cardinality fields where applicable: `user_id`,
`request_id`, `tenant_id`, `feature_flag_state`. These fields MUST NOT be optional when
the context is available.

**How To Apply**:
- A PR adding `console.log`, `print`, or unstructured logger calls in new code violates
  this principle.
- A PR emitting structured events without available correlation IDs (request_id, tenant_id)
  when the calling context has them violates this principle.
- Reviewers check: can this log line be filtered by user, request, or tenant? If not,
  reject.

### VII. Recovery Over Prevention

**Domain**: DevOps

**Rationale**: Prevention without tested recovery creates false confidence. Deployments
that cannot be reverted in minutes become incidents measured in hours.

**Rule**: Every change MUST be revertible in under five minutes without a code change.
Risky code paths MUST be gated by feature flags. Database migrations MUST follow
expand-then-contract. Rollback MUST be tested as part of the deploy process, not assumed.

**How To Apply**:
- A PR with a destructive migration (drop column, rename without expand phase) violates
  this principle.
- A PR deploying risky behavior without a feature flag or kill switch violates this
  principle.
- A deploy without a documented and tested rollback path violates this principle.
- Reviewers require: "How do we revert this in 5 minutes?" before approving risky changes.

### VIII. Attention Is Finite

**Domain**: Observability

**Rationale**: Alerts without runbooks waste on-call attention. Dashboards without saved
queries are decoration. Signals that never page usefully consume review time and create
alert fatigue.

**Rule**: Every alert MUST correspond to a user-visible symptom and MUST link to a
runbook. Dashboards MUST be saved queries, not manually assembled views. Signals that have
not fired a useful page in 90 days MUST be deleted.

**How To Apply**:
- A PR adding an alert without a runbook URL and symptom description violates this
  principle.
- A PR adding a dashboard panel that is not a saved, reproducible query violates this
  principle.
- Quarterly review: alerts with zero useful pages in 90 days MUST be removed; PRs
  retaining them without justification violate this principle.

### IX. Value Is Realized at the User, Not at Merge

**Domain**: DevOps

**Rationale**: Merged code in a branch delivers zero user value. A PR marked "done" at
merge without deploy, instrumentation, and monitoring creates invisible debt.

**Rule**: A PR is NOT done until the change is in the hands of users, observable, and
revertible. "Shipped" means deployed, instrumented, and monitored—not merged. Closing a
ticket or marking work complete at merge without production deployment violates this
principle.

**How To Apply**:
- Work items closed at merge without deploy confirmation violate this principle.
- A PR merging risky behavior without corresponding observability (structured events,
  alerts per Principle VIII) violates this principle.
- Definition of done checklist: deployed → instrumented → monitored → revertible.

### X. Commands Are Discoverable; Local Dev Matches CI

**Domain**: DevOps / Developer Experience

**Rationale**: Hidden commands and CI-only steps create "works on my machine" gaps. If a
new contributor cannot list every repeatable action in 30 seconds, the interface is
broken.

**Rule**: Every repeatable action (build, test, lint, migrate, deploy, seed) MUST be a
single named command listed in one place and runnable with no hidden arguments. The command
a developer runs locally MUST be the same command CI runs. CI-only shell steps, undocumented
makefile targets, and implicit environment assumptions MUST NOT exist.

**How To Apply**:
- A PR adding a build, test, or deploy step that runs only in CI (not locally via a named
  command) violates this principle.
- A PR adding a makefile target, script, or npm script not listed in the project's command
  index violates this principle.
- A PR where local `npm test` (or equivalent) differs from CI test invocation violates
  this principle.
- Reviewers ask: "What command do I run?" If it is not in the single command index,
  reject.

## Domain Coverage

| Domain | Principles |
|--------|-------------|
| Distributed Systems | I. Do Not Distribute by Default |
| Software Design | II. Optimize for Deletion; III. Make Dependencies Explicit; V. Test the Transformation |
| Data Engineering | IV. Contract at the Boundary |
| DevOps | VII. Recovery Over Prevention; IX. Value at the User; X. Commands Discoverable |
| Observability | VI. Emit Structured Events; VIII. Attention Is Finite |

## Review & Compliance

Every PR MUST be reviewed against the ten principles above. Reviewers MUST cite the
specific principle number when requesting changes (e.g., "violates Principle III: hidden
singleton introduced").

Compliance checklist for reviewers:
1. Distribution justified? (Principle I)
2. Module deletable in a day? No speculative abstraction? (Principle II)
3. Dependencies explicit in signature or file header? (Principle III)
4. Boundary has versioned schema? No shared mutable schemas? (Principle IV)
5. Bug fix has failing test? No mocking owned code? (Principle V)
6. Structured events with required cardinality fields? (Principle VI)
7. Revertible in 5 min? Feature flag for risky paths? Expand-then-contract? (Principle VII)
8. Alert has symptom + runbook? (Principle VIII)
9. Deployed, instrumented, monitored—not just merged? (Principle IX)
10. Command in index? Local matches CI? (Principle X)

## Governance

This constitution supersedes ad-hoc engineering practices. All PRs and design reviews MUST
verify compliance with the principles above.

**Amendment procedure**:
1. Propose change in a PR modifying this file with version bump rationale.
2. MAJOR: backward-incompatible principle removal or redefinition.
3. MINOR: new principle or materially expanded guidance.
4. PATCH: clarifications, wording, typo fixes.
5. Amendment PR MUST update `LAST_AMENDED_DATE` and `CONSTITUTION_VERSION`.

**Compliance review**: Quarterly audit of alerts (Principle VIII), command index
(Principle X), and any open distribution justifications (Principle I).

**Version**: 1.0.0 | **Ratified**: 2026-08-12 | **Last Amended**: 2026-08-12
