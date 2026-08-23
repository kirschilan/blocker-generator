# Agile Blocker Generator — Backlog

**Status:** Ready for Claude Code (Vertical Slices)  
**Updated:** 2026-08-22  
**Principle:** Each iteration produces a complete, testable vertical slice that can be validated with the business partner. INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.

**Terminology:** "Iteration" is our own delivery timebox (BP/PM/Code); "Sprint" (below) refers only to the synthetic dataset's own domain concept — the fictional squads' 12-sprint quarter. See `TEAM_OPERATING_SYSTEM.md`.

---

## Iteration 1: Auth Squad + Auth Cluster (Minimum Viable Dataset)

**Goal:** Prove the percolation hypothesis works at the smallest scale. Generate Auth squad (SQ-A) + 1 blocker cluster (Auth outage, weeks 3–5) + 2 cascading squads (Checkout, Payments) for 12 sprints. Business partner validates the data correlates to their mental model of how Auth blockers ripple.

**Done-Done Criteria:**
- All tests pass
- Auth cluster is visibly propagated to Checkout + Payments (same root cause, cascading timeline)
- Data loaded into a simple viz (Excel pivot, Grafana, or Tableau) shows the "crime neighborhood"
- Business partner signs off: "Yes, this matches how our squads actually get blocked"

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
**Priority:** P1  
**Size:** Moderate (complete feature generation + blockers for 3 squads only)  
**Acceptance Criteria:**
- 15–20 features per squad per sprint (Auth, Checkout, Payments) = 45–60 features per sprint
- 12 sprints = 540–720 total features
- Auth cluster blockers injected: Auth (3 blockers, week 3), Checkout/Payments (2 blockers each, week 3–4)
- Features in "Waiting" status have correct waiting reason from Task 1.2 taxonomy
- Waiting cycle times realistic (Auth blocker fixed day 3 → downstream clear day 4)
- Blocker density calculable (total blockers / total features × 12 sprints)
- Output: `v1_auth_cluster_high_density.csv` (Jira format)

**Input to Code:** Tasks 1.1–1.3 + ARCHITECTURE.md feature templates for each squad  
**Output:** CSV (~600–750 rows), Jira columns: Issue Key, Summary, Status, Assignee, Waiting Reason, Created, Resolved, Cycle Time, Sprint, Test Automation  
**Verification:**
  - Row count ≈ 600–750
  - All Waiting items have non-null Waiting Reason
  - Dates are monotonic (no time travel)
  - Auth blocker resolves day 3; downstream blockers clear day 4 (visible in Created/Resolved timestamps)
  - Blocker density ~ 20–30% (permissible for high-density slice)
  - All Issue Keys match pattern `SQ-[ABD]-[0-9]+`  
**Test:** Load CSV into Pandas; assert all Waiting rows have Waiting Reason, assert dates monotonic

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

### Task 1.6: Validate & document (for business partner review)
**Priority:** P1  
**Size:** Small (validation + README)  
**Acceptance Criteria:**
- Validation report (text): "Iteration 1 Dataset Summary"
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
**Verification:** Business partner reads report, loads CSVs into a viz tool, confirms: "I see the Auth blocker cascade; matches our mental model"

---

## Iteration 2: Expand to 5 Squads + DataPlatform Cluster + Optimized Scenario

**Goal:** Validate that a second, independent blocker cluster (DataPlatform delay) produces similar cascading behavior. Expand to 5 squads (Auth, Checkout, Payments, Core Banking, Savings), add external dependency (DataPlatform), generate optimized dataset where the DataPlatform cluster is mocked/reduced. Business partner confirms: "If we mock the DataPlatform API, do we see flow improvement?"

**Done-Done Criteria:**
- DataPlatform cluster visible in data (weeks 6–10), cascades to Core Banking → Savings
- Optimized dataset shows blocker reduction when DataPlatform cluster is mocked (P2 Metric B)
- Business partner validates both datasets load + correlate correctly

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

### Task 2.6: Validate & document V2 (for business partner review)
**Priority:** P1  
**Size:** Small  
**Acceptance Criteria:**
- Validation report: "Iteration 2 Dataset Summary"
  - Squads: 5 (Auth, Checkout, Payments, Core Banking, Savings)
  - Clusters: 2 (Auth weeks 3–5, DataPlatform weeks 6–10)
  - High-density: ~1,000 features, ~250–350 blockers, 25–35% density
  - Optimized (with mocking): ~1,000 features, ~150–200 blockers, 15–20% density
  - Flow improvement via mocking: DataPlatform cluster removed → blocker density drops by ~10%, flow resumes
- Updated README.md: mention 2 clusters, mocking scenario, how to load both datasets
- Commit example CSVs (all 4 for review)

**Input to Code:** Tasks 2.1–2.5  
**Output:** Validation report + updated README  
**Verification:** Business partner: "I see Auth + DataPlatform clusters; mocking DataPlatform shows flow improvement. This proves the hypothesis. Ready for full 8-squad dataset."

---

## Iteration 3: Full 8-Squad + 3 Clusters + CLI + Reusability

**Goal:** Merge all squads (Loans, Invoicing, Collections) + all external dependencies (CRM, Loans Rule Engine, BPM, ESB) + 3rd cluster (Checkout instability). Parameterize generator (CLI, config files, reproducibility). Handoff to business partner as reusable tool.

---

### Task 3.1: Extend squad model to all 8 squads + 4 external dependencies
**Priority:** P0  
**Size:** Small (update datastructure; logic reused from Iterations 1–2)  
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
**Verification:** Business partner runs generator, loads CSVs into dashboard, sees "crime neighborhoods," validates hypothesis: "Percolation model holds; interventions reduce density; flow improves."

---

## Post-MVP (Deferred; Triggers Listed)

| Task | Trigger | Priority |
|------|---------|----------|
| **P3 Simulation (what-if engine)** | Business partner validates Iterations 1–2; wants to run scenario: "What if we mock CRM instead of DataPlatform?" | P3 |
| **P4 Prediction (forecasting)** | Simulation works; client wants early-warning system ("Squad X will halt in 3 days") | P3 |
| **Production incident correlation** | Client wants to link blockers to actual prod incidents from their monitoring | P4 |
| **Resource utilization data** | Dashboard recommends "add 2 nodes to Auth service" (requires resource estimates per squad) | P4 |
| **Real Jira/Xray API integration** | Client ready to deploy; sync live data instead of CSV exports | P5 |
| **Multi-domain templating** | 8-squad finance demo succeeds; HR/Sales/Ops want their own generators | P5 |

---

## Key INVEST Principles (Enforced per Iteration)

1. **Independent:** Each iteration produces a complete dataset (tests, docs, validation) independent of downstream iterations
2. **Valuable:** At end of Iteration 1, business partner can load Auth-cluster data and validate hypothesis; at end of Iteration 2, can compare high-density vs. optimized and see flow improvement
3. **Estimable:** Task sizes mapped (P0 = small, P1 = moderate, no task >1 iteration)
4. **Testable:** Each task has explicit verification steps (automated tests + manual validation with business partner)
5. **Small:** No task blocks another; parallelizable (e.g., Task 1.4 and 1.5 can run in parallel once 1.1–1.3 are done)
6. **Negotiable:** If Task 1.6 validation reveals the data doesn't match business expectations, backlog is updated before Iteration 2 (no late surprises)

---

## Blockers & Dependencies

- **None at this point.** Assume each iteration clears its tasks before handoff to business partner.
- **Decision point after Iteration 1:** Business partner signs off on Auth-cluster data before proceeding to Iteration 2.
- **Decision point after Iteration 2:** Business partner confirms mocking scenario (P2 Metric B) works before proceeding to Iteration 3.

---

## Session Log

| Date | Item | Status |
|------|------|--------|
| 2026-08-22 | Backlog restructured as vertical slices (Sprint 1: Auth + 1 cluster; Sprint 2: 5 squads + 2 clusters + mocking; Sprint 3: full 8 squads + all clusters + CLI). Each sprint produces complete, testable data for business partner validation. INVEST principles enforced. | Ready for Code |
| 2026-08-23 | Renamed our delivery timebox from "Sprint" to "Iteration" throughout (headers, sign-off gates, INVEST section) to stop colliding with the dataset's own domain concept (`Sprint-1..Sprint-12` in ARCHITECTURE.md). No scope change — same three vertical slices, same acceptance criteria. | PM + Code + BP (Kirschi) |

