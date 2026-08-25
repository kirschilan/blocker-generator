# Agile Blocker Generator — Backlog

**Status:** Ready for Claude Code (Vertical Slices)  
**Updated:** 2026-08-22  
**Principle:** Each iteration produces a complete, testable vertical slice that can be validated with the Product Owner. INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.

**Terminology (corrected 2026-08-23 — see session_log.md):** three words, three distinct things, don't conflate them:
- **Sprint** — the synthetic dataset's own domain concept (the fictional squads' 12-sprint quarter). Never ours.
- **Iteration** — our one-day delivery timebox (PO/PM/Code). See `TEAM_OPERATING_SYSTEM.md`'s Daily Iteration Cadence. Iteration 1 = the first day worked (2026-08-22, timeboxed out); Iteration 2 = the second day (2026-08-23); etc.
- **Milestone** (below) — a vertical-slice grouping of backlog tasks, potentially spanning several Iterations. Milestone 1 took two Iterations (1 and 2) to actually land. Don't assume one Milestone = one Iteration.

**Planning structure (restructured 2026-08-23 — PO's call, to stop pre-determining scope):** what actually happens each day lives in the **Iteration Log** and **Product Backlog** below — a PBI moves between them, not between "Milestone N" sections. The **Milestone** sections further down are reference detail (domain-accurate acceptance criteria, CSV schemas, etc.) for when a PBI drawn from them gets pulled into an Iteration — they are not a pre-scheduled Iteration-by-Iteration plan. Only the Iteration Log/Product Backlog say what's actually next; a Milestone section being written doesn't mean its scope is committed to any particular Iteration.

---

## Iteration Log

| Iteration | Date | Status | PBI(s) |
|---|---|---|---|
| 1 | 2026-08-22 | Complete (timeboxed out) | Land Milestone 1 (Auth Squad + Cluster) to Done-Done — **Not Done** |
| 2 | 2026-08-23 | Complete | Land Milestone 1 to Done-Done — **Done**; Fix Issue #7 (Sprint CSV format) — **Done**; PBR — Task 2.0 candidate PBIs drafted |
| 3 | 2026-08-24 | Complete | PBI 2.0a — **Done**; Issue #8 — **Done**; PBI 2.0b/c/d — **Done**; Xray Issue #9 research + fix (Flaky/Automation Coverage % dropped) — **Done**; PBI 2.1 (live Status distribution: Waiting/Done/In Progress) — **Done**; Xray `Test Type` gap and row-shape gap — flagged, not started (need design input) |
| 4 | 2026-08-25 | Complete | Task 2.1 — 5-squad + DataPlatform external dependency — **Done**; Task 2.2 — inject DataPlatform cluster, verified against a real CSV — **Done** |

Full narrative for each Iteration (root causes, decisions, rationale) lives in `session_log.md` — this table is a status index, not a replacement for it.

---

## Product Backlog

Flat, prioritized list. A PBI's `Milestone` tag is for narrative context (which vertical slice it belongs to) — it does **not** imply which Iteration it's scheduled into. Pulling a PBI into an Iteration is a planning-conversation decision, made fresh each day against actual capacity.

| PBI | Milestone | Status |
|---|---|---|
| Land Auth Squad + Cluster MVP to Done-Done | Milestone 1 | Done (Iterations 1–2) |
| Fix Issue #7 — Sprint CSV column format | Milestone 1 | Done (Iteration 2) |
| PBI 2.0a — Rename `Waiting Reason`/`Test Automation` to `Custom field (...)` | Milestone 2 (prerequisite) | Done (Iteration 3) |
| Issue #8 — Clarify & resolve `External Blocker` column | Milestone 1 (hardening) | Done (Iteration 3) |
| PBI 2.0b — `External Blocker` dropped; signal folded into `Waiting Reason` archetype | Milestone 2 (prerequisite) | Done (Iteration 3) — PO's ruling: not a real field, remove rather than relabel |
| PBI 2.0c — `Cluster Tag` → native, repeated `Labels` field | Milestone 2 (prerequisite) | Done (Iteration 3) — confirmed Jira exports `Labels` as repeated columns, same convention as `Sprint` |
| PBI 2.0d — `Cycle Time (days)` dropped from CSV (kept internally) | Milestone 2 (prerequisite) | Done (Iteration 3) — PO's ruling: not a real field, dashboard computes it |
| PBI 2.1 — Live/actionable Status distribution | Milestone 1 (hardening) | Done (Iteration 3) — see resolution note below |
| Xray Issue #9 — drop `Flaky`/`Automation Coverage %` (not real Xray fields) | Milestone 1 (hardening) | Done (Iteration 3) |
| Xray gap — `Test Type` values (tool names vs. Manual/Cucumber/Generic) | Milestone 2 (prerequisite) | Not started — needs a design decision, Issue #9 |
| Xray gap — real exports are one row per Test Run, not aggregated counts | Milestone 2+ (future) | Not started — noted, not attempted; bigger structural change |
| Task 2.1 — Extend squad model to 5 squads + DataPlatform external dependency | Milestone 2 | Done (Iteration 4) — see resolution note below |
| Task 2.2 — Inject DataPlatform cluster (weeks 6–10) | Milestone 2 | Done (Iteration 4) — see resolution note below |
| Bug — CSV row order isn't sorted (Waiting rows cluster at the bottom) | Milestone 2 (hardening) | Not started — found in Task 2.2 (PO's question), deferred to Iteration 5 per PO. Do not commence. Detail: session_log.md, Iteration 4. |
| Bug — Issue Key numbering doesn't reflect chronological creation order | Milestone 2 (hardening) | Not started — found alongside the row-sort bug in Task 2.2, deferred to Iteration 5 per PO. Do not commence. Detail: session_log.md, Iteration 4. |
| PBI — Improve Waiting-issue generation logic | Milestone 2 | Not started — deferred to Iteration 5 per PO. Do not commence. Detail: session_log.md, Iteration 4. |
| Milestone 2 scope: 5-Squad + DataPlatform cluster + optimized scenario | Milestone 2 | Tasks 2.1–2.2 done; Tasks 2.3–2.6 not yet started |
| Milestone 3 scope: Full 8-Squad + 3 clusters + CLI | Milestone 3 | Not started — not yet broken into individual PBIs |

---

## Milestone 1: Auth Squad + Auth Cluster (Minimum Viable Dataset)

**Goal:** Prove the percolation hypothesis works at the smallest scale. Generate Auth squad (SQ-A) + 1 blocker cluster (Auth outage, weeks 3–5) + 2 cascading squads (Checkout, Payments) for 12 sprints. Product Owner validates the data correlates to their mental model of how Auth blockers ripple.

**Done-Done Criteria:**
- All tests pass
- Auth cluster is visibly propagated to Checkout + Payments (same root cause, cascading timeline)
- Data loaded into a simple viz (Excel pivot, Grafana, or Tableau) shows the "crime neighborhood"
- Product Owner signs off: "Yes, this matches how our squads actually get blocked"

---

### Task 1.1: Build minimal data model (Auth + dependent squads only)
**Priority:** P0 (unblocks all)  
**Size:** Small (1 squad graph, not 8)  
**Acceptance Criteria:**
- 3 squads instantiated: Auth (SQ-A), Checkout (SQ-B), Payments (SQ-D)
- Adjacency defined: Auth → Checkout, Auth → Payments
- Shared component: Login Service (owned by Auth)
- External dependency: (none for this slice; deferred)
- Datastructure serializable to JSON

**Input to Code:** ARCHITECTURE.md section "Squad Topology" (extract Auth-centric subgraph)  
**Output:** Python `Squad` dataclass instances (3 squads)  
**Verification:** Print adjacency; confirm Auth blocks the other two  
**Test:** Instantiate, verify `Auth.depends_on == []` and `Checkout.depends_on == [Auth]`

---

### Task 1.2: Define blocker archetype taxonomy
**Priority:** P0  
**Size:** Small (6–8 types; code once, reuse across all sprints)  
**Acceptance Criteria:**
- Blocker types: SharedCompFailure (2–5 days), ExternalDelay (10–20 days), PeerSquadOverload (1–3 days), TestInfraIssue (1–2 days), IntegrationGap (2–4 days), KnowledgeGap (1–2 days)
- Each has: type_id, duration_days (min, max), waiting_reason_template
- No hardcoded squad names in templates (allow substitution)

**Input to Code:** ARCHITECTURE.md section "Blocker Archetypes"  
**Output:** Python enum/dataclass  
**Verification:** Instantiate all 6, verify waiting_reason_template is generalized (e.g., "Waiting on {component} {reason}")  
**Test:** `blocker_type = BlockerArchetype.SharedCompFailure; assert blocker_type.duration_days == (2, 5)`

---

### Task 1.3: Implement cluster injection (Auth cluster only, weeks 3–5)
**Priority:** P0  
**Size:** Small (1 cluster, hardcoded)  
**Acceptance Criteria:**
- Auth cluster: root cause "Session cache corruption in Auth service," onset week 3 day 1, duration 3 days, affects Auth (root) + Checkout, Payments (cascade with 1-day lag)
- When cluster is injected into timeline, all 3 squads have blockers at correct days
- Propagation lag is explicit: root blocker day X, downstream day X+1

**Input to Code:** ARCHITECTURE.md section "Cluster Topology" (Cluster 1 only)  
**Output:** Python `BlockerCluster` dataclass + injection method  
**Verification:**
  - Generate timeline, count blockers: Auth on days 1–3 (week 3), Checkout/Payments on days 2–4 (1-day lag)
  - Print cluster impact: "Auth blocker x1, Checkout blocker x1, Payments blocker x1" for each day
  - Verify resolution order: Auth resolves first, then cascade clears  
**Test:** Run injection on empty 12-sprint timeline; assert Auth has 3 blockers in week 3

---

### Task 1.4: Generate 12-sprint features + Auth cluster (high-density)
**Status:** Corrected 2026-08-23 — see PM ruling below. Original criteria asked for global blocker density of 20–30%, which is mathematically impossible at this slice's scale (a single cluster producing 7–11 blocker rows across 540–720 feature rows caps global density at ~1–2%, not 20–30%). That 20–30% figure was written for the full 8-squad/3-cluster model (`ARCHITECTURE.md` "Blocker Density Targets") and copied into this 3-squad/1-cluster slice without rescaling.  
**PM ruling:** density is **window-scoped**, not global — measured within the cluster's own active week, not across all 12 sprints. No blockers exist anywhere outside the Auth cluster's own window; this slice is single-cluster by design. Additionally, `Waiting Reason` persists on a blocker row after it resolves (`Status` still reflects current state) — clearing it on resolve would erase the historical cluster signal `PROJECT.md`'s P1 (Detection) needs to identify clusters retrospectively. External-dependency deferral (Task 1.1) stands as originally written.  
**Priority:** P1  
**Size:** Moderate (complete feature generation + blockers for 3 squads only)  
**Acceptance Criteria:**
- 15–20 features per squad per sprint (Auth, Checkout, Payments) = 45–60 features per sprint
- 12 sprints = 540–720 total features
- Auth cluster blockers injected: Auth (3 blockers, week 3), Checkout/Payments (2–3 blockers each, week 3, 1-day cascade lag) = 7–11 blocker rows total
- No blockers anywhere outside the Auth cluster's own window
- Features in "Waiting" status have correct waiting reason from Task 1.2 taxonomy
- `Waiting Reason` persists on a blocker row after it resolves (Status still reflects current state)
- Waiting cycle times realistic (Auth blocker fixed day 3 → downstream clear day 4)
- **Blocker density is window-scoped, not global:** (blockers in the cluster's own week ÷ features in that week) × 100 = 20–30%. Global density (all 12 sprints) is expected to be ~1–2%.
- Output: `v1_auth_cluster_high_density.csv` (Jira format)

**Input to Code:** Tasks 1.1–1.3 + ARCHITECTURE.md feature templates for each squad  
**Output:** CSV (547–731 rows: 540–720 features + 7–11 blockers), Jira columns: Issue Key, Summary, Type, Status, Assignee, Created, Resolved, Custom field (Waiting Reason), Custom field (Test Automation), then repeated `Labels` columns and repeated `Sprint` columns holding sprint names (corrected 2026-08-24, PBI 2.0a/b/c/d — `Cycle Time`/`External Blocker`/`Cluster Tag` were never real Jira fields; see Task 2.0 below)  
**Verification:**
  - Row count ≈ 547–731
  - All blocker rows (Type = Sub-task) have non-null Waiting Reason regardless of Status; feature rows (Type = Story) have null Waiting Reason
  - Dates are monotonic (no time travel)
  - Auth blocker resolves day 3; downstream blockers clear day 4 (visible in Created/Resolved timestamps)
  - Window-scoped blocker density ~ 20–30%; global density ~1–2%; zero blocker rows outside the cluster window
  - All Issue Keys match pattern `SQ-[ABD]-[0-9]+`  
**Test:** Load CSV into Pandas; assert all blocker rows have Waiting Reason regardless of Status, assert dates monotonic, assert window-scoped density is 20–30%, assert zero blockers outside the cluster window

---

### Task 1.5: Generate test execution logs (Xray-like) for Auth cluster dataset
**Priority:** P1  
**Size:** Moderate (one log row per feature × test type)  
**Acceptance Criteria:**
- One row per feature per test type (Manual always; Selenium 50%, Postman 10%, Swagger 5%, Perfecto Mobile 10%)
- Test counts: if feature is in "Waiting on Test Infrastructure" blocker, that feature has flaky tests (fail count > 0)
- Automation coverage % calculated per feature (sum of automated / sum of all tests)
- Output: `v1_auth_cluster_test_logs.csv` (Xray format)

**Input to Code:** `v1_auth_cluster_high_density.csv` from Task 1.4  
**Output:** CSV (~1,200–1,500 rows, 6 features per sprint × 12 sprints × 3 squads × 3–4 test types avg)  
**Verification:**
  - Row count ~ 1,200–1,500
  - Flaky tests correlate to "Test Infrastructure" waiting reasons
  - Automation coverage % makes sense (high coverage = fewer manual test blockers)  
**Test:** Load CSV; assert for each Issue Key, at least one test type row exists; assert Automation % is between 0–100

---

### Task 1.6: Validate & document (for Product Owner review)
**Priority:** P1  
**Size:** Small (validation + README)  
**Acceptance Criteria:**
- Validation report (text): "Milestone 1 Dataset Summary"
  - Total features: 600–750
  - Blocker count: 20–30
  - Blocker density: 20–30%
  - Cluster signature: Auth cluster weeks 3–5, cascades to Checkout/Payments with 1-day lag
  - Peak waiting cycle time: 3 days (Auth), 4 days (Checkout/Payments)
  - Test coverage: ~50% automation across squads
- README.md (minimal):
  - What is this? (1 para): "Synthetic Jira + Xray data for 3 squads, 12 sprints, 1 blocker cluster"
  - How to load? (example): "Import .csv into Tableau; filter Sprint column"
  - What's the hypothesis? (1 para): Percolation theory; Auth blocker halts dependent squads
  - Limitations: "Synthetic; only Auth cluster; 3 squads only; ready for feedback"
- Example CSVs committed (not generated at runtime)

**Input to Code:** Tasks 1.1–1.5  
**Output:** `VALIDATION_REPORT.md` + updated `README.md`  
**Verification:** Product Owner reads report, loads CSVs into a viz tool, confirms: "I see the Auth blocker cascade; matches our mental model"

---

## Milestone 2: Expand to 5 Squads + DataPlatform Cluster + Optimized Scenario

**Prerequisite (PBR, 2026-08-23 — for Iteration 3 review, not yet started):** correct the Jira CSV schema's native-vs-custom-field provenance before scaling the schema to 5 squads — scaling up a schema with unrealistic field labeling just compounds the authenticity gap. See Task 2.0 below.

### Task 2.0: Correct Jira field provenance (native vs. custom fields)

**Priority:** P0 (blocks Milestone 2's schema work — see rationale above)
**Origin:** PO review, 2026-08-23. PO correctly identified that `Test Automation`, `External Blocker`, and `Cluster Tag` are not out-of-the-box Jira fields.

**PM research (confirmed via Atlassian sources — see session_log.md):**
- Real Jira "Export CSV, All Fields" labels every **custom field** column as literally `Custom field (<Field Name>)` — this is documented, known Jira export behavior (Atlassian issues JRASERVER-62216 / JRACLOUD-62216), not optional or configurable.
- **Native/system fields** (keep plain names, no prefix): `Issue Key`, `Summary`, `Type`, `Status`, `Assignee`, `Created`, `Resolved`.
- **`Sprint`** is a special case: technically implemented as a custom field under the hood by the Jira Software plugin, but Jira's own CSV export prints it as plain `Sprint` (not `Custom field (Sprint)`) because Jira Software treats it as a first-party feature field. No change needed — already correct (Issue #7).
- **Not native — need the `Custom field (...)` treatment:**
  - `Waiting Reason` → `Custom field (Waiting Reason)`
  - `Test Automation` → `Custom field (Test Automation)`
  - `External Blocker` → `Custom field (External Blocker)` — pending Issue #8's resolution, since PO flagged this column's meaning is unclear anyway
- **Open design questions (need PM+PO decision, not Code's to default):**
  1. `Cluster Tag` — model as a bespoke `Custom field (Cluster Tag)`, or as Jira's **native** `Labels` field (built for exactly this kind of tagging)? Needs verifying Jira's actual `Labels` CSV export convention (single cell, multi-value how?) before deciding — not yet confirmed.
  2. `Cycle Time (days)` — this isn't a native Jira field *or* a typical custom field; real Jira doesn't export a computed cycle-time value directly (a reporting app would compute it from `Created`/`Resolved`, or a specific "time in status" app might add its own custom field for it). Decide: keep as a generator convenience value (clearly labeled as derived, not a real exported field), or drop it from the CSV and let a downstream dashboard compute it, matching real-world practice more closely?

**Acceptance Criteria (draft — confirm with PO/PM before Code starts):**
- Header renamed per the classification above
- `Cluster Tag` and `Cycle Time (days)` open questions resolved by PM+PO before implementation (not decided unilaterally by Code)
- `specification/ARCHITECTURE.md`'s Jira CSV Schema table updated to show native vs. custom provenance per column
- Regenerated CSV + updated tests
- Issue #8 resolved as part of, or before, `External Blocker`'s renaming

**Code's INVEST assessment (2026-08-23):** Not a single one-day-Iteration slice as scoped above — it bundles a confirmed rename (small), an unresolved external dependency on PO's Issue #8 answer, and two open design decisions that could go either way and change the diff shape. Recommend splitting:
- **Task 2.0a (Small, Independent, ready now):** rename `Waiting Reason` and `Test Automation` to `Custom field (...)` — no open questions block these two. Doable in well under a day.
- **Task 2.0b (Small, blocked on Issue #8):** rename/rework `External Blocker` once PO clarifies its intended meaning.
- **Task 2.0c (Small, blocked on a `Labels`-vs-custom-field decision):** `Cluster Tag`'s real modeling — needs the `Labels` export-format check first.
- **Task 2.0d (Small, blocked on a keep-vs-drop decision):** `Cycle Time (days)`'s fate.
Each is independently mergeable; 2.0a can land in Iteration 3 regardless of what happens with 2.0b–d.

**Resolved 2026-08-24 (PO's ruling on each, ahead of Code starting):**
- **2.0b:** `External Blocker` isn't a Jira field. Not relabeled — dropped. The internal-vs-external signal belongs to which blocker archetype produced the `Waiting Reason` (e.g. `ExternalDelay`'s template vs. `SharedCompFailure`'s), not a separate column.
- **2.0c:** `Cluster Tag` → Jira's native `Labels` field, confirmed to export as repeated columns (one per occupied label slot), the same convention as `Sprint` (Issue #7) — not a single comma-joined cell.
- **2.0d:** `Cycle Time (days)` isn't a Jira field. Dropped from the CSV; a real dashboard computes it from `Created`/`Resolved`. Kept internally since `xray_logs.py` and the validation report still use it.

All three landed same-day as 2.0a (see `session_log.md`, Iteration 3).

---

### PBI 2.1: Live/actionable Status distribution (as-of reference date)

**Priority:** P1 (blocks Milestone 1 fully satisfying `PROJECT.md`'s P1 Detection outcome as a *live* dashboard input, not just a retrospective one)
**Origin:** PO, 2026-08-24 — "all lines in the CSV are in Status Done. We should have multiple stati, so the dashboard can point to actionable data, such as aging items."

**Root cause:** the generator has no "as-of" reference point within the 12-sprint timeline — it always generates as if the entire quarter has already concluded. `generate_features` hardcodes every feature row to `Status = "Done"` regardless of where it falls in the timeline, and (after today's persistence fix) every blocker row also resolves to `Done`. Real dashboards need a live snapshot: some items still open now, some resolved with history, some at risk of becoming a problem soon. `ARCHITECTURE.md`'s own schema already lists `"In Progress"` as a valid `Status` value — the generator has just never used it.

**What PO is asking for, restated as three concrete row categories at some reference point in time ("as of" a chosen sprint/day within the quarter, not after it):**
1. **Currently blocked** — a cluster blocker whose active window straddles the as-of date: `Status = "Waiting"`, `Resolved` still null, `Waiting Reason` populated. (Today, every cluster blocker resolves — none are left genuinely open.)
2. **Previously blocked, now resolved** — already implemented (today's persistence fix): `Status = "Done"`, `Waiting Reason` still populated.
3. **Aging / at-risk candidates** — a feature still open (`Status = "In Progress"`, no `Resolved`) that's been open unusually long relative to typical cycle time for its squad — an early-warning signal, not yet an actual blocker.

**Resolved 2026-08-24 (PO's ruling, then implemented same day):**
- **Aging is dashboard-computed** — "NOW()-Created at the time of the report," not a stored field. Simplifies category 3 to just: leave some features genuinely unresolved; nothing to pre-compute.
- **Rejected a global as-of-date/truncation design** (would have cut most of the 12-sprint feature population, since a single as-of point early enough to catch the Auth cluster live would exclude sprints 2–12 entirely — conflicting with `TESTER.md`'s existing 540–720 feature row-count baseline). Implemented a smaller, narratively-consistent design instead:
  1. **Currently blocked:** each cascade squad's (Checkout, Payments) *final* blocker day stays `Status = "Waiting"`, `Resolved` null — the root's "resolves day 3" is a completed fact per `BACKLOG.md`; "downstream clears day 4" is a *lag* relative to that, so the last step of propagation hasn't happened yet as of the report. The root (Auth) itself always fully resolves.
  2. **Previously blocked, now resolved:** unchanged — already implemented (Waiting-Reason-persistence fix, Iteration 2).
  3. **Aging candidates:** ~8% of ordinary feature rows across all 12 sprints stay `Status = "In Progress"`, `Resolved` null — realistic WIP, not tied to any calendar cutoff.
- Implemented in `src/blocker_generator/features.py` (`IN_PROGRESS_PROBABILITY`, cascade-tail logic in `generate_cluster_blockers`); the in-progress decision uses an independent per-issue RNG so it doesn't perturb the existing created-date distribution (and with it, `TESTER.md`'s density/flaky-correlation numbers) — verified via test failures caught and fixed before landing.
- `TESTER.md`'s row-count/density baselines are unaffected — Status changed, row existence didn't.
- Regenerated CSV; 61/61 tests pass; determinism reconfirmed; PM spot-checked the real output.

---

## Milestone 2 (continued): 5-Squad + DataPlatform Scope

**Goal:** Validate that a second, independent blocker cluster (DataPlatform delay) produces similar cascading behavior. Expand to 5 squads (Auth, Checkout, Payments, Core Banking, Savings), add external dependency (DataPlatform), generate optimized dataset where the DataPlatform cluster is mocked/reduced. Product Owner confirms: "If we mock the DataPlatform API, do we see flow improvement?"

**Done-Done Criteria:**
- DataPlatform cluster visible in data (weeks 6–10), cascades to Core Banking → Savings
- Optimized dataset shows blocker reduction when DataPlatform cluster is mocked (P2 Metric B)
- Product Owner validates both datasets load + correlate correctly

---

### Task 2.1: Extend squad model to 5 squads + DataPlatform external dependency
**Priority:** P0  
**Size:** Small (3 new squads + external dep)  
**Acceptance Criteria:**
- Add squads: Core Banking (SQ-C), Savings (SQ-E), + keep Auth, Checkout, Payments
- Add external dependency: DataPlatform (affects Core Banking, Savings; 40% dependency)
- Adjacency: DataPlatform → Core Banking → Savings (indirect)
- Extend Task 1.1 datastructure (no breaking changes)

**Input to Code:** ARCHITECTURE.md "Squad Topology" + "External Dependencies"  
**Output:** Updated Python dataclass instantiation (5 squads + DataPlatform)  
**Test:** `assert CoreBanking.depends_on == [Auth, DataPlatform]`

**Resolved 2026-08-25 (Iteration 4), Code's implementation note:** the literal test above mixes a squad id and an external system name in one list; implemented instead with a new, separate `Squad.external_depends_on` field so `depends_on` keeps its existing invariant (squad ids only — every Task 1.1 test relies on this). `CoreBanking.depends_on == [Auth]` and `CoreBanking.external_depends_on == [DataPlatform]` — same fact the literal test was reaching for, without overloading one field with two types. Like Task 1.1, this slice is still narrower than the full topology: Core Banking's squad-level dependency on Payments (`ARCHITECTURE.md`'s Interdependency Graph) isn't modeled yet — out of this task's stated scope. `build_five_squad_subgraph()` added alongside (not replacing) `build_auth_subgraph()`; Milestone 1's dataset generation (`__main__.py`) is untouched. 6 new tests added (`tests/test_squads.py`), 67/67 pass. Not yet wired into feature/cluster generation — that's Task 2.2 onward.

---

### Task 2.2: Inject DataPlatform cluster (weeks 6–10)
**Priority:** P0  
**Size:** Small (1 new cluster, reuse injection logic from Task 1.3)  
**Acceptance Criteria:**
- DataPlatform cluster: root cause "Annual release delay (Q3)," onset week 6 day 1, duration 5 days, affects Core Banking (root) + Savings (cascade)
- Inject alongside Auth cluster (both clusters in same dataset, different weeks)
- No overlap (Auth weeks 3–5, DataPlatform weeks 6–10)

**Input to Code:** ARCHITECTURE.md Cluster 2 + Task 1.3 cluster injection method  
**Output:** Updated injection logic (handle 2+ clusters)  
**Test:** Inject both clusters; assert Auth blockers in week 3, DataPlatform blockers in week 6; no conflicts

**Resolved 2026-08-25 (Iteration 4):** PO explicitly directed this be verified against an actual CSV file, not just in-memory assertions, after Task 2.1 shipped with no data artifact ("Working software is the primary measure of progress" — what's Done today that's measurable in working software?). Implemented:
- `CLUSTER_2_DATAPLATFORM` added to `clusters.py` (root: Core Banking, 5-day duration per this task's own acceptance criteria — same "stated duration vs. ARCHITECTURE.md's day-by-day narrative" inconsistency as Cluster 1, resolved the same way: BACKLOG's stated figure wins; cascade: Savings only, 1-day lag, matching ARCHITECTURE.md's Cluster 2 timeline).
- `generate_dataset()` extended to accept a list of clusters (was a single cluster) sharing one issue-key counter, so two clusters coexist in one dataset without key collisions.
- A real CSV (`data/task_2.2_five_squad_two_clusters.csv`, 1,075 rows) generated and committed — not just proven in a test's temp directory — so there's an actual artifact to open, per the PO's standard from this same conversation.
- **Bug caught by testing the real CSV, not just aggregate counts:** `generate_cluster_blockers` hardcoded Cluster 1's "Session cache corruption in Auth service" / "Feature blocked pending Auth service fix" summary text for *every* cluster — harmless with one cluster, silently wrong with two (DataPlatform blockers were labeled as Auth blockers). Caught by eyeballing the generated CSV's actual rows, not by any existing test (none checked `summary` content before). Fixed by adding `root_summary`/`cascade_summary` fields to `BlockerCluster` and threading them through `BlockerDay`, with regression tests added at both the injection level (`test_clusters.py`) and the CSV level (`test_cluster2_dataplatform.py`) so it can't silently regress.
- Milestone 1's output reconfirmed byte-identical (`v1_auth_cluster_high_density.csv` unchanged) — the fix only affected Cluster 2's values.
- 13 new tests (5 in `test_clusters.py`, 8 in `test_cluster2_dataplatform.py`), 80/80 total pass.

Scope explicitly NOT included (Task 2.3's job): tuned combined blocker density (25–35%), the official `v2_two_clusters_high_density.csv` name/row-count range, the optimized/mocked variant, test logs, validation report.

---

### Task 2.3: Generate 12-sprint features + 2 clusters (high-density V2)
**Priority:** P1  
**Size:** Moderate (5 squads × 12 sprints)  
**Acceptance Criteria:**
- 15–20 features per squad per sprint = 75–100 features per sprint
- 12 sprints = 900–1,200 total features
- Both Auth + DataPlatform clusters injected
- Blocker density ~ 25–35% (2 clusters, overlapping impact)
- Output: `v2_two_clusters_high_density.csv`

**Input to Code:** Tasks 2.1–2.2 + feature generation  
**Output:** CSV (~1,000–1,250 rows)  
**Verification:**
  - Row count ~ 1,000–1,250
  - Auth blockers in week 3, DataPlatform blockers in week 6 (both visible in data)
  - Cascade: Core Banking blocker resolves day after DataPlatform cluster resolves
  - Blocker density ~ 25–35%  
**Test:** Load CSV; filter by Waiting Reason; count "Waiting on Login" (week 3) vs "Waiting on DataPlatform" (week 6)

---

### Task 2.4: Generate optimized dataset with DataPlatform mocking
**Priority:** P1  
**Size:** Moderate (variant of Task 2.3)  
**Acceptance Criteria:**
- Same squads + feature structure as high-density V2
- **Mocking rule:** DataPlatform cluster removed or duration reduced to 1 day (mocked responses)
- Auth cluster: unchanged (we can't mock external Auth failures; focus on DataPlatform)
- Result: blocker density drops to ~15–20% (P2 Metric B: "mocking DataPlatform improves flow")
- Output: `v2_two_clusters_optimized_with_mocking.csv`

**Input to Code:** Task 2.3 + mocking parameter  
**Output:** CSV (~950–1,150 rows, slightly fewer blockers)  
**Verification:**
  - DataPlatform cluster removed (no "Waiting on DataPlatform" after week 6)
  - Blocker density ~ 15–20% (confirmed lower)
  - Auth cluster unchanged  
**Test:** Count "Waiting on DataPlatform" rows; assert count == 0 in optimized dataset

---

### Task 2.5: Generate test logs for both V2 datasets
**Priority:** P1  
**Size:** Moderate (Task 1.5 applied to 5 squads)  
**Acceptance Criteria:**
- Test logs for high-density V2 + optimized V2
- Same automation coverage % as V1 (50% Selenium, 10% Postman, 10% Perfecto Mobile, rest manual)
- Flaky tests correlate to blockers in high-density; fewer flaky tests in optimized
- Output: `v2_two_clusters_high_density_test_logs.csv` + `v2_two_clusters_optimized_test_logs.csv`

**Input to Code:** Task 2.3–2.4 feature CSVs  
**Output:** Two CSVs (~1,500–2,000 rows each)  
**Test:** Assert flaky test count higher in high-density than optimized

---

### Task 2.6: Validate & document V2 (for Product Owner review)
**Priority:** P1  
**Size:** Small  
**Acceptance Criteria:**
- Validation report: "Milestone 2 Dataset Summary"
  - Squads: 5 (Auth, Checkout, Payments, Core Banking, Savings)
  - Clusters: 2 (Auth weeks 3–5, DataPlatform weeks 6–10)
  - High-density: ~1,000 features, ~250–350 blockers, 25–35% density
  - Optimized (with mocking): ~1,000 features, ~150–200 blockers, 15–20% density
  - Flow improvement via mocking: DataPlatform cluster removed → blocker density drops by ~10%, flow resumes
- Updated README.md: mention 2 clusters, mocking scenario, how to load both datasets
- Commit example CSVs (all 4 for review)

**Input to Code:** Tasks 2.1–2.5  
**Output:** Validation report + updated README  
**Verification:** Product Owner: "I see Auth + DataPlatform clusters; mocking DataPlatform shows flow improvement. This proves the hypothesis. Ready for full 8-squad dataset."

---

## Milestone 3: Full 8-Squad + 3 Clusters + CLI + Reusability

**Goal:** Merge all squads (Loans, Invoicing, Collections) + all external dependencies (CRM, Loans Rule Engine, BPM, ESB) + 3rd cluster (Checkout instability). Parameterize generator (CLI, config files, reproducibility). Handoff to Product Owner as reusable tool.

---

### Task 3.1: Extend squad model to all 8 squads + 4 external dependencies
**Priority:** P0  
**Size:** Small (update datastructure; logic reused from Milestones 1–2)  
**Acceptance Criteria:**
- 8 squads: Auth, Checkout, Payments, Core Banking, Savings, Loans, Invoicing, Collections
- 4 external deps: DataPlatform, CRM, Loans Rule Engine, BPM, ESB
- Full adjacency per ARCHITECTURE.md
- Datastructure parameterizable (squad config in JSON; can swap for other domains post-V1)

**Input to Code:** Updated ARCHITECTURE.md (full topology)  
**Output:** Python dataclass + JSON schema for squad config  
**Test:** Load full config; assert all 8 squads + 4 external deps instantiate

---

### Task 3.2: Inject Checkout cluster (weeks 10–12) + validate all 3 clusters together
**Priority:** P0  
**Size:** Small (reuse cluster injection logic)  
**Acceptance Criteria:**
- Checkout cluster: weeks 10–12, affects Checkout (root) + Payments (cascade)
- All 3 clusters coexist in same dataset without conflicts
- No overlaps (Auth weeks 3–5, DataPlatform weeks 6–10, Checkout weeks 10–12; Checkout onset day 2 week 10 avoids DataPlatform tail)

**Input to Code:** ARCHITECTURE.md Cluster 3 + cluster injection method  
**Output:** Injection logic handling 3+ clusters  
**Test:** Generate 12-sprint timeline with all 3 clusters; verify no blockers appear on same day at same squad (except cascades)

---

### Task 3.3: Generate full 8-squad high-density dataset (all 3 clusters)
**Priority:** P1  
**Size:** Large (complete dataset generation)  
**Acceptance Criteria:**
- 15–20 features per squad per sprint = 120–160 features per sprint
- 12 sprints = 1,440–1,920 total features
- All 3 clusters injected + cascading
- Blocker density ~ 30–40% (percolation threshold breached)
- Output: `full_8squad_high_density.csv`

**Input to Code:** Tasks 3.1–3.2 + ARCHITECTURE.md feature templates  
**Output:** CSV (~1,800–2,400 rows)  
**Verification:**
  - Blocker density ~ 30–40%
  - All 3 clusters visible
  - Cascades to dependent squads (Auth → all 8; DataPlatform → Core Banking, Savings, Loans; Checkout → Payments)  
**Test:** Query blockers by root cause (Auth, DataPlatform, Checkout); confirm counts align with ARCHITECTURE.md

---

### Task 3.4: Generate full 8-squad optimized dataset (mocked interventions)
**Priority:** P1  
**Size:** Large  
**Acceptance Criteria:**
- Same structure as high-density
- **Intervention model:**
  - Auth cluster: duration reduced 3→2 days (added monitoring, faster triage)
  - DataPlatform: removed/mocked (API responses mocked; Core Banking doesn't wait)
  - Checkout: duration reduced 2→1 day (infra fix)
- Result: blocker density ~ 15–20% (below percolation; flow resumes)
- Output: `full_8squad_optimized.csv`

**Input to Code:** Task 3.3 + intervention params  
**Output:** CSV (~1,200–1,600 rows)  
**Verification:**
  - Blocker density ~ 15–20%
  - Auth cluster shorter; DataPlatform removed; Checkout shorter
  - Flow improvement visible (fewer waiting reasons, faster cycle times)

---

### Task 3.5: Generate test logs for full 8-squad datasets
**Priority:** P1  
**Size:** Large  
**Acceptance Criteria:**
- Test logs for high-density + optimized
- Automation coverage parameterizable (CLI flag `--automation_coverage 50` for 50% avg)
- Flaky tests higher in high-density (Selenium grid issues weeks 10–12), lower in optimized
- Output: 2 CSVs (~2,000–3,000 rows each)

**Input to Code:** Tasks 3.3–3.4 + test template logic  
**Output:** Two CSVs  
**Verification:** Assert flaky test density higher in high-density; test automation counts reflect parameter

---

### Task 3.6: CLI + parameterization
**Priority:** P1  
**Size:** Small (wraps all logic)  
**Acceptance Criteria:**
- Script: `python generate_blocker_data.py [OPTIONS]`
- Options:
  - `--squads <path>` (JSON config; default: finance config)
  - `--sprints <N>` (default: 12)
  - `--density <HIGH|OPTIMIZED>` (default: HIGH)
  - `--automation_coverage <percent>` (default: 50)
  - `--seed <N>` (default: random; set for reproducibility)
  - `--output_dir <path>` (default: `./output`)
- Same seed → identical data (deterministic)
- Help text clear, examples provided

**Input to Code:** All tasks 3.1–3.5  
**Output:** Python script + help text  
**Verification:**
  - Run with `--seed 42` twice; outputs identical
  - Run with different `--density`; blocker counts differ as expected
  - Run with `--automation_coverage 80`; test logs show 80% automation
  - `--help` works

---

### Task 3.7: Documentation & final handoff
**Priority:** P1  
**Size:** Small  
**Acceptance Criteria:**
- README.md:
  - What is the generator? (percolation hypothesis, blocker clusters, ROI platform)
  - Quick start (1–2 examples)
  - CSV schema (Jira + Xray columns explained)
  - How to extend (add squads, new clusters, new domains)
  - Limitations (synthetic, no real incidents, no ML)
- ARCHITECTURE.md kept current (reflects full topology + all clusters)
- Example CSVs: `full_8squad_high_density.csv` + `full_8squad_optimized.csv` (for dashboard loading)
- VALIDATION_REPORT.md: final summary (all 3 clusters, density %, cascade proofs, ready for client)

**Input to Code:** All tasks + ARCHITECTURE.md  
**Output:** README + updated docs + example CSVs  
**Verification:** Product Owner runs generator, loads CSVs into dashboard, sees "crime neighborhoods," validates hypothesis: "Percolation model holds; interventions reduce density; flow improves."

---

## Post-MVP (Deferred; Triggers Listed)

| Task | Trigger | Priority |
|------|---------|----------|
| **P3 Simulation (what-if engine)** | Product Owner validates Milestones 1–2; wants to run scenario: "What if we mock CRM instead of DataPlatform?" | P3 |
| **P4 Prediction (forecasting)** | Simulation works; client wants early-warning system ("Squad X will halt in 3 days") | P3 |
| **Production incident correlation** | Client wants to link blockers to actual prod incidents from their monitoring | P4 |
| **Resource utilization data** | Dashboard recommends "add 2 nodes to Auth service" (requires resource estimates per squad) | P4 |
| **Real Jira/Xray API integration** | Client ready to deploy; sync live data instead of CSV exports | P5 |
| **Multi-domain templating** | 8-squad finance demo succeeds; HR/Sales/Ops want their own generators | P5 |

---

## Key INVEST Principles (Enforced per Milestone)

1. **Independent:** Each iteration produces a complete dataset (tests, docs, validation) independent of downstream iterations
2. **Valuable:** At end of Milestone 1, Product Owner can load Auth-cluster data and validate hypothesis; at end of Milestone 2, can compare high-density vs. optimized and see flow improvement
3. **Estimable:** Task sizes mapped (P0 = small, P1 = moderate, no task >1 iteration)
4. **Testable:** Each task has explicit verification steps (automated tests + manual validation with Product Owner)
5. **Small:** No task blocks another; parallelizable (e.g., Task 1.4 and 1.5 can run in parallel once 1.1–1.3 are done)
6. **Negotiable:** If Task 1.6 validation reveals the data doesn't match business expectations, backlog is updated before Milestone 2 (no late surprises)

---

## Blockers & Dependencies

- **None at this point.** Assume each iteration clears its tasks before handoff to Product Owner.
- **Decision point after Milestone 1:** Product Owner signs off on Auth-cluster data before proceeding to Milestone 2.
- **Decision point after Milestone 2:** Product Owner confirms mocking scenario (P2 Metric B) works before proceeding to Milestone 3.

---

## Session Log

| Date | Item | Status |
|------|------|--------|
| 2026-08-22 | Backlog restructured as vertical slices (Sprint 1: Auth + 1 cluster; Sprint 2: 5 squads + 2 clusters + mocking; Sprint 3: full 8 squads + all clusters + CLI). Each sprint produces complete, testable data for business partner validation. INVEST principles enforced. | Ready for Code |
| 2026-08-23 | Renamed our delivery timebox from "Sprint" to "Iteration" throughout (headers, sign-off gates, INVEST section) to stop colliding with the dataset's own domain concept (`Sprint-1..Sprint-12` in ARCHITECTURE.md). No scope change — same three vertical slices, same acceptance criteria. | PM + Code + BP (Kirschi) |
| 2026-08-23 | Task 1.4 corrected: original "20–30% global blocker density" was mathematically impossible for the 3-squad/1-cluster slice (copied from the full 8-squad/3-cluster model without rescaling — see `pm-ffutq6` branch's diagnosis). Ruling: density is window-scoped (within the cluster's own week), not global. `Waiting Reason` now persists after a blocker resolves (needed for retrospective cluster detection, PROJECT.md P1). External-dependency deferral (Task 1.1) confirmed standing. | PM + Code + BP (Kirschi), formalizing a ruling first made 2026-08-22 |
| 2026-08-25 | Task 2.1 done: 5-squad + DataPlatform squad model, `Squad.external_depends_on` added as a separate field rather than overloading `depends_on`. Iteration 4 kickoff deliberately scoped to this one task only (PO: focus on what's realistically Done-Done today). | PO + PM + Code |
| 2026-08-25 | Task 2.2 done, same Iteration: PO pushed back that Task 2.1 alone had no measurable working-software delta ("Working software is the primary measure of progress" — what's Done today?). Pulled Task 2.2, generated and committed a real CSV, and caught a real bug (Cluster 2's summary text hardcoded to Cluster 1's) by testing that actual file instead of only aggregate assertions. | PO + PM + Code |
| 2026-08-25 | PO spotted a second real issue by reading the committed CSV directly (all Waiting rows clustered at the bottom): traced to two root causes, not fixed today — added as 3 new Product Backlog items (2 bugs + 1 improvement PBI), explicitly deferred to Iteration 5, no work commenced. | PO + PM + Code |

