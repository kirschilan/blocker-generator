# Agile Blocker Generator — Architecture & Data Model

**Version:** 1.0  
**Domain:** Finance (8 squads)  
**Data Horizon:** 12 sprints (1 quarter)

---

## Squad Topology

### Squad Definitions

| Squad ID | Squad Name | Responsibility Area | Dependencies (Squads) | Dependencies (External) | Notes |
|----------|-----------|---------------------|------------------------|--------------------------|-------|
| SQ-A | **Auth** | Secure login, session management, MFA | (none—owned component) | CRM (identity lookups) | Owner of shared "Login" component; high uptime criticality |
| SQ-B | **Checkout** | Shopping cart, order placement, payment processing flow | Auth, Payments | CRM (customer data), ESB (routing) | High volume; test automation is critical bottleneck |
| SQ-C | **Core Banking** | Account balances, ledger integrity, transaction history | Auth, Payments | DataPlatform (40% dependency; annual gates) | Cluster 2 blocker: DataPlatform delays weeks 6–10 |
| SQ-D | **Payments** | Payment media (cards, wallets), fraud detection, settlement | Auth, Checkout | Payment Gateway, ESB | Tight coupling with Checkout; Cluster 3 cascade |
| SQ-E | **Savings** | Savings goals, rates, account opening | Core Banking | DataPlatform (indirect via Core Banking) | Lighter load; ripple effects from DataPlatform delays |
| SQ-F | **Loans** | Loan origination, disbursement, repayment tracking | Core Banking | DataPlatform, Loans Rule Engine (regulatory) | Regulated; rule engine updates block deployments |
| SQ-G | **Invoicing** | Bill generation, delivery, payment tracking | Core Banking, Payments | CRM (customer), BPM (workflow) | Mid-weight; BPM orchestrates invoice lifecycle |
| SQ-H | **Collections** | Overdue management, recovery workflows | Core Banking, Invoicing | BPM (case routing), ESB | Lightest load; depends on Invoicing + BPM coordination |

### Shared Components (Owned)

| Component | Owner Squad | Affected Squads | Typical Failure Impact |
|-----------|-------------|-----------------|------------------------|
| **Login Service** | SQ-A (Auth) | All 8 squads | Complete halt; no one can access system |
| **Checkout Widget** | SQ-B (Checkout) | SQ-B, SQ-D (Payments) | Payment flows broken; transaction processing fails |
| **Transaction Ledger API** | SQ-C (Core Banking) | SQ-C, SQ-E, SQ-F, SQ-G, SQ-H | Data integrity concerns; cascades to all dependent features |
| **Logging & Observability** | Ops (external) | All 8 squads (muted) | Blocker mostly resolved within 1 day; shown for context |

### Interdependency Graph (Adjacency)

```
Auth (SQ-A) ──┬──→ Checkout (SQ-B)
              ├──→ Core Banking (SQ-C)
              ├──→ Payments (SQ-D)
              ├──→ Savings (SQ-E)
              ├──→ Loans (SQ-F)
              ├──→ Invoicing (SQ-G)
              └──→ Collections (SQ-H)

Core Banking (SQ-C) ──┬──→ Payments (SQ-D) [indirect via Checkout]
                      ├──→ Savings (SQ-E)
                      ├──→ Loans (SQ-F)
                      ├──→ Invoicing (SQ-G)
                      └──→ Collections (SQ-H)

Checkout (SQ-B) ──→ Payments (SQ-D) [tight coupling]

Invoicing (SQ-G) ──→ Collections (SQ-H)
```

**External Dependencies**

These are standard finance legacy system integrations; most squads depend on at least one.

| External System | Owner | Affected Squads | Dependency Type | Frequency | Typical Duration | Notes |
|-----------------|-------|-----------------|-----------------|-----------|------------------|-------|
| **DataPlatform** | Data team | SQ-C (Core Banking), SQ-E (Savings), SQ-F (Loans) | Annual release schedule; pre-scheduled data schema updates | Q1, Q2, Q3, Q4 gates | 10–20 days (weeks 6–10 per Cluster 2) | Cannot move; 40% of SQ-C capacity blocked during gates |
| **CRM** | Customer Ops | SQ-A (Auth), SQ-B (Checkout), SQ-G (Invoicing) | Customer data sync, user identity lookups | Intermittent API outages, schema changes | 2–5 days | Low-frequency blockers; when CRM is down, login/checkout slows |
| **Loans Rule Engine** | Loan Services | SQ-F (Loans) | Loan eligibility rules, rate calculations | Annual rule updates + ad-hoc regulatory changes | 5–10 days | SQ-F heavily dependent; rule engine updates block loan origination |
| **BPM** (Business Process Mgmt) | Operations | SQ-G (Invoicing), SQ-H (Collections) | Invoice workflow orchestration, collection case routing | Monthly process updates | 2–3 days | Invoicing/Collections can't deploy without BPM sign-off |
| **ESB** (Enterprise Service Bus) | Integration team | All 8 squads | Message queue, API gateway, inter-service routing | Capacity limits, deployments | 1–2 days | Rare but high-impact blocker; when ESB is slow, all squads feel latency |
| **Payment Gateway** | Payment Processor | SQ-D (Payments) | Rate limits, API changes, PCI compliance | Ad-hoc | 1–2 days | Low frequency; usually quick fixes |

**Realism Check:** In a mature finance firm, these 6 external dependencies are standard. The blockers injected in the generator will reference these systems, making the data realistic for RFP demonstrations.

---

## Blocker Archetypes (Taxonomy)

These are the 6 blocker types the generator will use. Each has a name, typical duration, propagation rule, and waiting-reason template.

| Blocker Type | Typical Duration | Affected Squads | Root Cause Template | Waiting Reason |
|--------------|------------------|-----------------|---------------------|-----------------|
| **SharedCompFailure** | 2–5 days | Multiple (per component) | Auth/Checkout/Ledger service down or broken | Waiting on Login/Checkout/Ledger service |
| **ExternalDelay** | 5–20 days | Dependent squads (2–4) | DataPlatform annual release (10–20 days), Loans Rule Engine update (5–10 days), BPM workflow change (2–3 days), CRM schema change (2–5 days), Payment Gateway API change (1–2 days) | Waiting on DataPlatform / Loans Rule Engine / BPM / CRM / Payment Gateway team |
| **PeerSquadOverload** | 1–3 days | 1–2 squads | Peer squad overloaded; can't review/implement; context-switching | Waiting on [Peer Squad] capacity |
| **TestInfraIssue** | 1–2 days | 1 squad (isolated) | Flaky test automation (Selenium, Perfecto Mobile), missing test env | Waiting on test infrastructure / flaky tests |
| **IntegrationGap** | 2–4 days | 2 squads | Missing API contract (e.g., CRM, ESB), undocumented change in downstream system | Waiting on API integration / contract clarification |
| **KnowledgeGap** | 1–2 days | 1 squad | Undocumented legacy code, domain expert unavailable, complex regulatory rule (Loans, BPM) | Waiting on domain knowledge / legacy code review |

---

## Cluster Topology (Percolation Model)

Three hardcoded blocker clusters injected into high-density dataset. Each cluster has:
- **Root cause:** What triggered it
- **Onset:** Sprint week when it appears
- **Duration:** How long the root cause lasts
- **Affected squads:** Which squads face blockers
- **Cascade:** How blockers propagate downstream
- **Resolution:** When blockers clear (after root cause + propagation lag)

### Cluster 1: Auth Service Outage (Weeks 3–5)

**Timeline:**
- Week 3, Day 1 (Sprint 1, day 15): Auth service has a critical bug (e.g., session cache corruption). SQ-A enters "Waiting on Auth service fix."
- Week 3, Days 1–3: SQ-A blocked internally. Any feature requiring login fails.
- Week 3, Day 2: Dependent squads (B, C, D, E, F, G, H) all place features in "Waiting on Login service" (cascade lag = 1 day).
- Week 4, Day 3: SQ-A resolves (deploy patch). Auth service is stable.
- Week 4, Day 4: Dependent squads' blockers clear (propagation lag = 1 day).

**Affected Squads:**
- SQ-A (root): 3 features stuck (high severity)
- SQ-B, C, D, E, F, G, H (cascade): 2–3 features each waiting on Login

**Blocker Counts:**
- Total: 3 (A) + 7 squads × 2–3 features = 18–24 blockers across 3 days
- Peak density: 20% of weekly capacity blocked

**Waiting Reasons in Data:**
- SQ-A: "Session cache corruption in Auth service; fix in progress"
- SQ-B, C, D, etc: "Waiting on Login service (SQ-A)"

---

### Cluster 2: DataPlatform Annual Release Delay (Weeks 6–10)

**Timeline:**
- Week 6, Day 1: DataPlatform team (external) misses planned release date. SQ-C's features depending on new data schemas are stuck.
- Week 6, Day 1: SQ-C places 4–5 features in "Waiting on DataPlatform release."
- Week 6, Day 2: Downstream squads (SQ-E, SQ-F, dependent on SQ-C) see SQ-C waiting and place their own blockers: "Waiting on Core Banking data" (indirect cascade).
- Week 10, Day 3: DataPlatform finally releases. SQ-C unblocks.
- Week 10, Day 4: SQ-E, SQ-F unblock (propagation lag = 1 day).

**Affected Squads:**
- SQ-C (direct): 4–5 features, 5-day wait
- SQ-E, SQ-F (cascade): 2–3 features each, 5-day wait

**Blocker Counts:**
- Peak: 4 (C) + 2 (E) + 3 (F) = 9 blockers in week 6–10 window
- Density: ~15% during this period

**Waiting Reasons in Data:**
- SQ-C: "Waiting on DataPlatform team annual release (scheduled Q3)"
- SQ-E, SQ-F: "Waiting on Core Banking data updates (DataPlatform delay)"

---

### Cluster 3: Checkout + Test Infrastructure Instability (Weeks 10–12)

**Timeline:**
- Week 10, Day 2: Checkout service has a memory leak under load (performance degrades). Selenium grid becomes flaky.
- Week 10, Days 1–2: SQ-B places 2–3 features in "Waiting on test infrastructure stabilization."
- Week 10, Day 2: SQ-D (Payments) can't test payment flow due to flaky Checkout service. Places 2 features in "Waiting on Checkout stability."
- Week 11, Day 2: SQ-B deploys fix; Checkout stabilizes. Test grid recovers.
- Week 11, Day 3: SQ-D's blockers clear.

**Affected Squads:**
- SQ-B (root): 3 features, 2–3 day wait
- SQ-D (cascade): 2 features, 2–3 day wait

**Blocker Counts:**
- Peak: 3 (B) + 2 (D) = 5 blockers in week 10–11
- Density: ~10% during peak

**Waiting Reasons in Data:**
- SQ-B: "Selenium grid flakiness + Checkout service memory leak; investigating"
- SQ-D: "Waiting on Checkout service stability (SQ-B)"

---

### Blocker Density Targets

**High-Density Dataset (V1):**
- Sprint 1–2: Baseline, ~10% blockers
- Sprint 3–5: Cluster 1 peak, +15% → ~25% total density
- Sprint 6–10: Cluster 2 peak, +10% → ~20% total density
- Sprint 10–12: Cluster 3 peak, +5% → ~15% total density
- **Overall:** ~30–40% blocker density across 12 sprints (percolation threshold breach)

**Optimized Dataset (V2):**
- Same topology, but:
  - Cluster 1 duration: 2 days (instead of 3) → fewer downstream blockers
  - Cluster 2 duration: 3 days (instead of 5) → DataPlatform team adds resources
  - Cluster 3 duration: 1 day (instead of 2) → better observability + quicker triage
  - Reduced cascading via better communication (fewer "waiting on peer" blockers)
- **Overall:** ~15–20% blocker density (below percolation threshold; flow resumes)

---

## Jira CSV Schema

**File:** `high_density.csv` (and `post_optimization.csv`)

**Note on Sprint Columns:** Jira's native CSV export denormalizes Sprint into multiple columns—one for each sprint in the issue's lifecycle. The header row contains column names like `Sprint-1`, `Sprint-2`, ..., `Sprint-12`. Each row has values only in the sprints the issue was planned/worked in; others are blank.

**Example Header:**
```
Issue Key, Summary, Type, Status, Assignee, Created, Resolved, Waiting Reason, Cycle Time (days), Test Automation, External Blocker, Cluster Tag, Sprint-1, Sprint-2, ..., Sprint-12
```

**Example Row:**
```
SQ-A-15, Fix session cache corruption, Story, Done, auth-squad, 2026-07-01T09:00:00Z, 2026-07-15T17:00:00Z, (null), 14.33, Selenium, false, (null), , 2026-07-01, , , , , , , , , , , 
```
*(This feature was planned in Sprint-1; values appear only in Sprint-1 column; others blank.)*

---

**Core Columns:**

| Column | Type | Example | Rules |
|--------|------|---------|-------|
| `Issue Key` | String | `SQ-A-1`, `SQ-B-42` | Format: `SQ-{A..H}-{1..N}` |
| `Summary` | String | "Login session timeout handling" | Feature or blocker description; <100 chars |
| `Type` | String | "Story" or "Sub-task" | Always "Story" for features, "Sub-task" for blockers |
| `Status` | String | "Done" \| "In Progress" \| "Waiting" | Features in Done; blockers in Waiting |
| `Assignee` | String | "auth-squad" | Lowercase squad identifier (e.g., "auth-squad", "payments-squad") |
| `Created` | ISO-8601 | `2026-07-01T09:00:00Z` | Sprint start date + random offset |
| `Resolved` | ISO-8601 | `2026-07-15T17:00:00Z` | Created + Cycle Time; null if in Waiting |
| `Waiting Reason` | String | "Waiting on Login service (SQ-A)" | Only populated if Status = Waiting |
| `Cycle Time (days)` | Float | `14.33` | (Resolved - Created) in days; null if waiting |
| `Test Automation` | String | "Manual" \| "Selenium" \| "Postman" \| "Swagger" \| "Perfecto Mobile" | Primary automation type (if any) |
| `External Blocker` | Boolean | true \| false | true if root cause is external team |
| `Cluster Tag` | String | "Cluster-1-Auth" \| "Cluster-2-DP" \| "Cluster-3-Checkout" \| null | Injected for analysis (can be removed for blind testing) |

---

**Sprint Columns:**

Denormalized; one column per sprint (Sprint-1, Sprint-2, ..., Sprint-12). Each column contains the date the issue was planned in that sprint (or blank if not planned in that sprint).

| Column | Type | Example | Rules |
|--------|------|---------|-------|
| `Sprint-1` | ISO-8601 \| blank | `2026-07-01` | Date issue was planned in Sprint 1; blank if not in Sprint 1 lifecycle |
| `Sprint-2` | ISO-8601 \| blank | `2026-07-15` | Date issue was planned in Sprint 2 |
| ... | ... | ... | ... |
| `Sprint-12` | ISO-8601 \| blank | `2026-10-26` | Date issue was planned in Sprint 12 |

**Example (realistic multi-sprint issue):**
```
Issue Key, Summary, ..., Sprint-1, Sprint-2, Sprint-3, Sprint-4, ...
SQ-B-99, Add payment retry logic, ..., 2026-07-01, 2026-07-15, 2026-07-29, , ...
```
*(Issue SQ-B-99 was planned in Sprints 1, 2, 3 but not 4 onward; cascading blocker moved it across sprints.)*

---

**Row Count:**
- Per sprint: 50–60 features + 2–8 blockers = 52–68 rows
- 12 sprints: ~650–850 rows total (high-density; optimized slightly lower)
- Each row has 1–3 Sprint columns populated (some issues span multiple sprints due to blockers/reprioritization)

---

## Test Execution Log Schema (Xray-like)

**File:** `high_density_test_logs.csv` (and `post_optimization_test_logs.csv`)

| Column | Type | Example | Rules |
|--------|------|---------|-------|
| `Issue Key` | String | `SQ-B-42` | Links to Jira issue |
| `Sprint` | Integer | 1, 2, ..., 12 | Sprint number |
| `Test Type` | String | "Manual" \| "Selenium" \| "Postman" \| "Swagger" \| "Perfecto Mobile" | Automation type |
| `Test Count` | Integer | 5 | Number of test cases |
| `Pass Count` | Integer | 5 | Tests passed |
| `Fail Count` | Integer | 0 | Tests failed |
| `Flaky` | Boolean | false | true if test fails 20–30% of the time |
| `Automation Coverage %` | Float | 50.0 | Cumulative automation % (manual = 0, others = 100) |
| `Executed Date` | ISO-8601 | `2026-07-15T14:00:00Z` | When tests last ran |

**Row Count:**
- Per feature: 1–5 rows (one per test type if present)
- ~1,500–2,000 rows total (aligned with Jira features)

**Automation Coverage Defaults (Parameterizable):**
- Manual testing: 100% (all features have manual tests in-squad)
- Selenium UI: 50% of features (higher for SQ-B, SQ-D; lower for SQ-E, SQ-H)
- Postman API: 10% of features (sparse, homegrown)
- Swagger invoker: 5% of features (emerging)
- **Perfecto Mobile: 15% of features** (higher for Checkout, Payments; mobile-heavy consumers)

**Flaky Test Injection:**
- High-density dataset: 15–20% of tests are flaky (Selenium grid instability in weeks 10–12)
- Optimized dataset: 5% flaky (post-infrastructure fix)

---

## Example: Feature + Blocker Sequence (Cluster 1)

**High-Density Dataset, Weeks 3–5:**

```
Issue Key    | Summary                       | Status     | Created             | Resolved | Waiting Reason
SQ-A-15      | Fix session cache corruption  | Done       | 2026-08-17 09:00:00 | 2026-08-21 17:00:00 | (none)
SQ-A-16      | Validate hotfix in prod       | Done       | 2026-08-21 18:00:00 | 2026-08-22 14:00:00 | (none)
SQ-A-17      | Add session timeout handling  | Waiting    | 2026-08-22 10:00:00 | (null)              | Waiting on Login service (SQ-A)
SQ-B-42      | Add payment retry logic       | Waiting    | 2026-08-22 11:00:00 | (null)              | Waiting on Login service (SQ-A)
SQ-C-88      | Reconcile transaction ledger  | Waiting    | 2026-08-22 10:30:00 | (null)              | Waiting on Login service (SQ-A)
... (5 more squads with "Waiting on Login service")
SQ-A-17      | (same as above)               | Done       | 2026-08-22 10:00:00 | 2026-08-24 16:00:00 | (none)
SQ-B-42      | (same as above)               | Done       | 2026-08-22 11:00:00 | 2026-08-25 09:00:00 | (none)
SQ-C-88      | (same as above)               | Done       | 2026-08-22 10:30:00 | 2026-08-25 10:00:00 | (none)
```

Note: Timestamps show progression (Auth resolves on day 4; dependent squads resolve day 5).

---

## SQL / JSON Serialization (Optional; Code-Internal)

For the generator's internal representation, the following datastructures suffice:

```python
# Pseudocode
@dataclass
class Squad:
    id: str  # "SQ-A"
    name: str  # "Auth"
    domain: str  # "secure-login"
    depends_on: List[str]  # ["SQ-B", "SQ-C"]
    owns_component: str  # "Login Service"

@dataclass
class BlockerArchetype:
    type_id: str  # "SharedCompFailure"
    duration_days: Tuple[int, int]  # (2, 5)
    affected_squads: List[str]
    waiting_reason_template: str

@dataclass
class BlockerCluster:
    cluster_id: str  # "Cluster-1-Auth"
    archetype: str  # "SharedCompFailure"
    onset_sprint: int  # 3
    onset_day: int  # 1
    duration_days: int  # 3
    affected_squads: List[str]
    cascade_lag_days: int  # 1
    propagation_lag_days: int  # 1

# Squads and Clusters are instantiated once, then passed to feature generator
```

---

## Notes for Code Implementation

1. **Randomization:** Use seeded RNG for:
   - Feature titles (randomize within domain, e.g., Auth features involve "session," "token," "timeout")
   - Cycle times (normal distribution around archetype mean)
   - Sprint distribution (features unevenly spread; some sprints busier)

2. **Timestamps:** 
   - Use Pendulum for date arithmetic
   - Sprint 1 = weeks 1–2 (Jul 1–14, 2026)
   - Sprint 2 = weeks 3–4 (Jul 15–28, 2026)
   - ... continuing through Sprint 12 = weeks 23–24 (Oct 19–Nov 1, 2026)

3. **Cascade Logic:**
   - When a cluster root blocker is inserted, query `affects` list and insert downstream blockers with `cascade_lag` delay
   - Downstream blockers reference the root cause in `Waiting Reason`

4. **Verification:**
   - Output CSVs to `/tmp` first
   - Validate: no null keys, dates monotonic, cycle times positive, cluster tags present if applicable
   - Print summary: total features, total blockers, blocker density %, cluster count

---

## Validation Checklist (for Code)

- [ ] All 8 squads instantiated with correct dependencies
- [ ] 3 clusters injected at correct weeks with correct durations
- [ ] Blocker density: high-density ~30–40%, optimized ~15–20%
- [ ] Cascade delays visible in timestamps (root → downstream, 1-day lag)
- [ ] No orphaned blockers (all blockers have valid root causes)
- [ ] Test logs align with features (same issue keys)
- [ ] Flaky test counts higher in high-density, lower in optimized
- [ ] CSVs valid (no weird chars, proper escaping)
- [ ] Regeneration with same seed yields identical data

