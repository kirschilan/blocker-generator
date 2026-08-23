# Blocker Generator — Definition of Done (Verification & Validation)

**Status:** Validation framework  
**Purpose:** Executable checklist for confirming each iteration's dataset is production-ready for business partner review  

**Terminology:** "Iteration" is our own delivery timebox; "Sprint" below refers only to the synthetic dataset's own domain concept (the fictional squads' 12-sprint quarter). See `TEAM_OPERATING_SYSTEM.md`.
**Audience:** Code (automated checks), PM (manual spot-checks), Business Partner (sign-off)

---

## Test Pyramid

1. **Automated Checks** (Code runs these; deterministic, <5 min)
2. **Manual Spot-Checks** (PM runs these; sample-based, ~15 min)
3. **Business Partner Validation** (Decision gate; qualitative, ~30 min)

---

## Iteration 1: Auth Squad + 1 Cluster (Minimum Viable Dataset)

### Automated Checks (Task 1.4 + 1.5 outputs)

**CSV Format & Structure**
- [ ] `v1_auth_cluster_high_density.csv` exists and is valid CSV (can be parsed without errors)
- [ ] Denormalized Sprint columns exist: `Sprint-1`, `Sprint-2`, ..., `Sprint-12`
- [ ] All mandatory columns present: `Issue Key`, `Summary`, `Type`, `Status`, `Assignee`, `Created`, `Resolved`, `Waiting Reason`, `Cycle Time (days)`, `Test Automation`, `External Blocker`, `Cluster Tag`
- [ ] No UTF-8 encoding errors or null bytes
- [ ] All rows have valid Issue Key (format: `SQ-[ABD]-[0-9]+`)

**Row Counts & Data Volume**
- [ ] Total feature rows: 540–720 (15–20 per squad × 3 squads × 12 sprints)
- [ ] Total blocker rows: 7–11 (Auth cluster's own window only — corrected 2026-08-23, see BACKLOG.md Task 1.4 PM ruling; the earlier 15–30 figure assumed weeks 3–5, but the cluster's actual acceptance criteria is a single week)
- [ ] Total rows (features + blockers): 547–731
- [ ] Each row has exactly 12 core columns + 12 Sprint columns (total 24) — corrected 2026-08-23, was miscounted as 13 core columns

**Data Integrity**
- [ ] No duplicate Issue Keys (each key appears once)
- [ ] All `Created` dates are valid ISO-8601 and monotonic (no time travel)
- [ ] All `Resolved` dates are null (blank) if Status = "Waiting"; populated if Status = "Done"
- [ ] All `Resolved` dates >= `Created` dates (no negative cycle times)
- [ ] `Cycle Time (days)` is null if Status = "Waiting"; numeric (float) if Status = "Done"
- [ ] Blocker rows (`Type` = "Sub-task") have non-null `Waiting Reason` regardless of `Status` — it persists after the blocker resolves, so the cluster signal stays retrospectively detectable (corrected 2026-08-23; previously required null once Status = "Done", which erased the signal `PROJECT.md`'s P1 Detection needs); feature rows (`Type` = "Story") have null `Waiting Reason`
- [ ] `Test Automation` is one of: "Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile", or null
- [ ] `External Blocker` is boolean (true/false); false for Auth cluster (internal failure)
- [ ] `Cluster Tag` is one of: "Cluster-1-Auth", null; all Auth-cluster blockers have "Cluster-1-Auth"

**Sprint Column Distribution**
- [ ] Each issue has 1–3 Sprint columns populated (most issues in 1–2 sprints; some span 2–3 if they moved due to blockers)
- [ ] Sprint dates within issue are monotonic (Sprint-1 date < Sprint-2 date < Sprint-3 date, if multiple)
- [ ] No feature appears in Sprint 0 or Sprint 13+
- [ ] Dates in Sprint columns align with actual sprint boundaries (Sprint 1 = Jul 1–14, Sprint 2 = Jul 15–28, etc.)

**Blocker Density** (corrected 2026-08-23 — density is window-scoped, not global; see BACKLOG.md Task 1.4 PM ruling)
- [ ] Window-scoped density = (blocker rows in the cluster's own week / feature rows in that week) × 100 = 20–30%
- [ ] Global density (blockers / all 12 sprints' features) ≈ 1–2% — this is expected, not a failure
- [ ] Auth blockers concentrated in week 3 only
- [ ] No blockers anywhere outside the Auth cluster's own window

**Cascade Validation**
- [ ] Auth blocker count: 3–5 in week 3 (root cause)
- [ ] Checkout blockers: 2–3 appearing in week 3 day 2+ (1-day cascade lag)
- [ ] Payments blockers: 2–3 appearing in week 3 day 2+ (1-day cascade lag)
- [ ] All three squads' blockers have `Waiting Reason` containing "Login service" or "Auth"
- [ ] No orphaned blockers (every blocker has a root cause in `Waiting Reason`)

---

### Automated Checks (Task 1.5 outputs)

**Test Execution Log Format**
- [ ] `v1_auth_cluster_test_logs.csv` exists and is valid CSV
- [ ] All mandatory columns: `Issue Key`, `Sprint`, `Test Type`, `Test Count`, `Pass Count`, `Fail Count`, `Flaky`, `Automation Coverage %`, `Executed Date`
- [ ] No duplicate (Issue Key, Sprint, Test Type) tuples
- [ ] Row count: 1,200–1,500 (roughly 2–3 test types per feature × 3 squads × 12 sprints)

**Test Data Integrity**
- [ ] All Issue Keys match Issue Keys in feature CSV
- [ ] All `Sprint` values are 1–12
- [ ] `Test Type` is one of: "Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile"
- [ ] `Test Count` ≥ `Pass Count` + `Fail Count` (tests are accounted for)
- [ ] `Flaky` is boolean; true only if `Fail Count` > 0 and (Fail Count / Test Count) is 20–30%
- [ ] `Automation Coverage %` is 0–100
- [ ] No issue has 100% automation (all have at least some manual testing)

**Automation Coverage Distribution**
- [ ] ~50% of features have Selenium tests
- [ ] ~10% have Postman API tests
- [ ] ~10% have Perfecto Mobile tests
- [ ] ~5% have Swagger invoker tests
- [ ] 100% have Manual tests
- [ ] Average automation coverage across all features: 40–60%

**Flaky Test Correlation**
- [ ] Flaky tests correlate to Auth-cluster weeks (weeks 3–5): 15–20% of tests are flaky in those weeks
- [ ] Flaky tests appear in Selenium + Perfecto Mobile primarily (automation-heavy)
- [ ] Features with "Waiting on Test Infrastructure" blocker reasons have corresponding flaky tests in same sprint

---

### Manual Spot-Checks (PM; ~10–15 min)

**Sample 5 Features, Verify Cascade:**

1. Pick an Auth-cluster blocker in week 3 (e.g., `SQ-A-25`, Status = "Waiting", Waiting Reason = "Session cache corruption...")
2. Verify:
   - [ ] It has `Cluster Tag` = "Cluster-1-Auth"
   - [ ] It has `External Blocker` = false
   - [ ] Its `Created` date is in week 3 (Jul 17–21, 2026 approximately)
3. Pick a Checkout blocker also in week 3 (e.g., `SQ-B-42`, Status = "Waiting", Waiting Reason = "Waiting on Login service")
4. Verify:
   - [ ] Its `Created` date is ≥ 1 day after the Auth blocker (cascade lag)
   - [ ] Its `Waiting Reason` references Auth or Login service
   - [ ] It has `Cluster Tag` = "Cluster-1-Auth" (same cluster)
5. Pick a feature that resolves before the Auth blocker (e.g., something in week 1–2)
6. Verify:
   - [ ] Its `Resolved` date is before any Auth blocker was created
   - [ ] It has null `Waiting Reason`
   - [ ] Its `Cycle Time (days)` is positive and realistic (2–10 days)

**Sample Test Logs:**

1. Pick a feature from Auth squad (e.g., `SQ-A-15`)
2. In test logs, find all rows with `Issue Key` = `SQ-A-15`
3. Verify:
   - [ ] At least one row has `Test Type` = "Manual"
   - [ ] If feature is blocked in test logs (high fail count), there's a corresponding "Waiting on Test Infrastructure" in Jira CSV
4. Pick a high-automation feature (e.g., Payments, which has ~50% Selenium)
5. Verify:
   - [ ] It has rows with `Test Type` = "Manual", "Selenium", possibly others
   - [ ] `Pass Count` ≥ 80% (tests mostly pass outside of cluster window)

**Timeline Sanity Check:**
- [ ] Spot-check 3 issues' dates: Created dates are all in Jul 2026 (Jul 1–Oct 31 for 12 sprints)
- [ ] Resolved dates are later than Created dates by 2–14 days (realistic cycle times)
- [ ] No dates in 2025 or 2027

---

### Business Partner Validation (Sign-Off Gate; ~20–30 min)

**Narrative Validation:**

> Provide business partner with:
> 1. `v1_auth_cluster_high_density.csv` + `v1_auth_cluster_test_logs.csv`
> 2. VALIDATION_REPORT.md (auto-generated summary: row counts, blocker density, cluster timeline)
> 3. A simple Tableau/Grafana/Excel pivot showing:
>    - X-axis: Sprints (1–12)
>    - Y-axis: Blocker count by squad
>    - Color: Cluster tag or Waiting Reason
> 4. This question: "Does this pattern match how Auth blockers actually cascade through your squads?"

**Sign-Off Criteria (Qualitative):**
- [ ] Business partner recognizes Auth → Checkout/Payments cascade (says "yes, this matches")
- [ ] Waiting reasons are realistic (not random noise)
- [ ] Blocker timeline makes sense (dense in weeks 3–5, sparse elsewhere)
- [ ] Test automation coverage aligns with their reality (50% Selenium, 10% API, rest manual)
- [ ] No "this data looks fake" red flags (cycle times, dates, squad names feel authentic)

**Sign-Off Statement (Required before Iteration 2):**
> "I recognize this Auth-cluster cascading pattern. The data matches how our squads would actually get blocked. Proceed to Iteration 2."

---

## Iteration 2: Expand to 5 Squads + 2 Clusters + Mocking

### Automated Checks (Task 2.3 + 2.4 outputs)

All Iteration 1 checks apply here, plus:

**Row Counts (5 Squads)**
- [ ] Total feature rows: 900–1,200 (15–20 per squad × 5 squads × 12 sprints)
- [ ] Total blocker rows: 30–50 (Auth cluster weeks 3–5 + DataPlatform cluster weeks 6–10)
- [ ] Total rows: 930–1,250

**Two Clusters Present**
- [ ] Auth blockers in weeks 3–5 (unchanged from Iteration 1)
- [ ] DataPlatform blockers in weeks 6–10 (new; 5–10 blockers in Core Banking, 2–3 in Savings)
- [ ] No overlap: Auth weeks 3–5, DataPlatform weeks 6–10
- [ ] All Auth-cluster blockers tagged "Cluster-1-Auth"
- [ ] All DataPlatform-cluster blockers tagged "Cluster-2-DP"

**Cascade for Cluster 2 (DataPlatform → Core Banking → Savings)**
- [ ] Core Banking blockers in week 6 (root)
- [ ] Savings blockers in week 6–7 (1-day cascade lag)
- [ ] All have `Waiting Reason` containing "DataPlatform"
- [ ] `External Blocker` = true for DataPlatform blockers

**Blocker Density**
- [ ] High-density: 25–35% (two overlapping clusters)
- [ ] Weeks 3–5: ~15–20% (Auth cluster only)
- [ ] Weeks 6–10: ~10–15% (DataPlatform cluster only)
- [ ] Weeks 1–2, 11–12: ~5–10% (baseline, no clusters)

---

### Automated Checks (Task 2.4: Optimized Dataset with Mocking)

**Optimized CSV (`v2_two_clusters_optimized_with_mocking.csv`)**
- [ ] Same structure as high-density (same columns, sprint denormalization)
- [ ] Identical feature structure (same 5 squads, same feature count)
- [ ] **DataPlatform cluster removed** (no "Waiting on DataPlatform" rows after week 6)
- [ ] **Auth cluster unchanged** (still weeks 3–5)
- [ ] **Blocker count lower:** 15–20 blockers total (50% reduction via mocking)
- [ ] **Blocker density:** 15–20% (vs. 25–35% in high-density)
- [ ] Row count: 950–1,150 (slightly fewer blocker rows)

**Validation: Mocking Works**
- [ ] High-density CSV has `Waiting Reason` = "Waiting on DataPlatform" rows; optimized has zero such rows
- [ ] High-density blocker density ÷ optimized blocker density ≈ 1.5–2.0× (50–100% improvement)
- [ ] Cycle times for features in weeks 6–10: much lower in optimized (not waiting on DataPlatform)

---

### Manual Spot-Checks (PM; ~20 min)

**Verify Mocking Scenario (P2 Metric B):**

1. Load both high-density and optimized CSVs
2. Filter to weeks 6–10, Core Banking squad (SQ-C)
3. Count "Waiting on DataPlatform" rows in high-density: should be 5–10
4. Count "Waiting on DataPlatform" rows in optimized: should be 0
5. Verify cycle times for SQ-C in weeks 6–10:
   - [ ] High-density: average cycle time 10–15 days (blocked, waiting)
   - [ ] Optimized: average cycle time 3–5 days (not blocked; mocked response)
6. Verify Savings (SQ-E) cascade:
   - [ ] High-density: 2–3 blockers (waiting on Core Banking, which is waiting on DataPlatform)
   - [ ] Optimized: 0 blockers (Core Banking unblocked → Savings unblocked)

**Comparison Table (for business partner):**
| Metric | High-Density | Optimized (w/ Mocking) | Improvement |
|--------|--------------|------------------------|-------------|
| Total Blockers | 40–50 | 20–30 | -40–50% |
| Blocker Density | 25–35% | 15–20% | -33–40% |
| Avg Cycle Time (SQ-C) | 10–15 days | 3–5 days | -66–70% |
| Squads Blocked by DataPlatform | 3 (C, E, F) | 0 | 100% resolved |

---

### Business Partner Validation (Sign-Off Gate; ~30 min)

> Provide:
> 1. High-density + optimized CSVs + test logs (all 4 files)
> 2. Comparison table (above)
> 3. Visualization showing: blocker density over 12 sprints, high-density vs. optimized as overlaid lines
> 4. This question: "If we mocked the DataPlatform API, would your flow improve like this?"

**Sign-Off Criteria:**
- [ ] Business partner sees the mocking scenario and validates: "Yes, mocking DataPlatform would unblock Core Banking, Savings, Loans. This shows how we can improve flow."
- [ ] No objections to the blocker reduction (40–50% feels realistic for that intervention)
- [ ] Agrees that Metric B (mocking reduces blockage) is proven

**Sign-Off Statement (Required before Iteration 3):**
> "I see how mocking DataPlatform improves flow by X%. The two-cluster scenario is credible. Ready for the full 8-squad dataset and all three clusters."

---

## Iteration 3: Full 8-Squad + 3 Clusters + CLI + Reusability

### Automated Checks (Task 3.3 + 3.4 outputs)

All Iteration 1–2 checks apply, plus:

**Row Counts (8 Squads)**
- [ ] Total feature rows: 1,440–1,920 (15–20 per squad × 8 squads × 12 sprints)
- [ ] Total blocker rows: 40–60 (three clusters)
- [ ] Total rows: 1,480–1,980

**Three Clusters All Present**
- [ ] Cluster 1 (Auth): weeks 3–5, affects all 8 squads downstream
- [ ] Cluster 2 (DataPlatform): weeks 6–10, affects Core Banking, Savings, Loans
- [ ] Cluster 3 (Checkout): weeks 10–12, affects Checkout, Payments
- [ ] No time overlaps (except Cluster 3 onset in week 10 avoids Cluster 2 tail)
- [ ] All three tagged correctly ("Cluster-1-Auth", "Cluster-2-DP", "Cluster-3-Checkout")

**Full Cascade Topology**
- [ ] Auth (week 3) → all 8 squads (cascade week 3–4)
- [ ] DataPlatform (week 6) → Core Banking, Savings, Loans (cascade week 6–7)
- [ ] Checkout (week 10) → Payments (cascade week 10–11)
- [ ] No cascades between clusters (independent root causes)

**Blocker Density**
- [ ] Overall: 30–40% (all three clusters; percolation threshold breached)
- [ ] Peak density (weeks with multiple clusters): up to 40–50%

**Optimized Dataset**
- [ ] Auth cluster duration reduced: 3 → 2 days (fewer downstream blockers)
- [ ] DataPlatform: removed/mocked (zero "Waiting on DataPlatform" rows)
- [ ] Checkout cluster duration reduced: 2 → 1 day (infra fix)
- [ ] Blocker density: 15–20% (all interventions applied)
- [ ] Improvement: 30–40% → 15–20% = 50–60% blocker reduction

---

### Automated Checks (Task 3.6: CLI Parameterization)

**CLI Execution**
- [ ] `python generate_blocker_data.py --help` displays all options
- [ ] `python generate_blocker_data.py --density HIGH --seed 42 --output_dir /tmp/test1` runs without error
- [ ] `python generate_blocker_data.py --density HIGH --seed 42 --output_dir /tmp/test2` (second run, same seed) produces identical CSVs
- [ ] `diff /tmp/test1/*.csv /tmp/test2/*.csv` returns no differences (deterministic)
- [ ] `python generate_blocker_data.py --density OPTIMIZED --seed 42` produces lower blocker density (~50% fewer blockers)
- [ ] `python generate_blocker_data.py --automation_coverage 80` produces test logs with 80% automation (vs. default 50%)
- [ ] `python generate_blocker_data.py --sprints 6` produces data for 6 sprints (scaling works)

**Parameter Validation**
- [ ] Invalid `--density` value (e.g., "INVALID") fails with clear error message
- [ ] Invalid `--automation_coverage` (e.g., 150) fails with clear error message
- [ ] Missing required arguments fail gracefully
- [ ] Non-existent output directory is created (or error if `--output_dir` is read-only)

---

### Manual Spot-Checks (PM; ~30 min)

**Cross-Cluster Independence:**
1. Pick a feature in week 9 (overlaps Cluster 2 tail + Cluster 3 onset)
2. Verify:
   - [ ] If it's in Core Banking (SQ-C), it can have "Waiting on DataPlatform" (Cluster 2)
   - [ ] If it's in Checkout (SQ-B), it can have "Waiting on Checkout stability" (Cluster 3)
   - [ ] No feature has *both* DataPlatform and Checkout waiting reasons (clusters are independent)

**Intervention Verification (Optimized Dataset):**
1. Compare Auth cluster (unchanged):
   - [ ] High-density: 3-day duration (weeks 3–5)
   - [ ] Optimized: 2-day duration (weeks 3–4)
   - [ ] Downstream blocker reduction is proportional
2. Compare DataPlatform (removed):
   - [ ] High-density: weeks 6–10, 5+ blockers
   - [ ] Optimized: zero DataPlatform blockers
3. Compare Checkout (reduced):
   - [ ] High-density: 2-day duration, 3–5 blockers
   - [ ] Optimized: 1-day duration, 1–2 blockers

**Reproducibility:**
1. Generate data 3 times with same seed
2. Verify all three outputs are byte-for-byte identical (checksums match)

---

### Business Partner Validation (Final Sign-Off; ~45 min)

> Provide:
> 1. Full 8-squad high-density + optimized CSVs + test logs (all 4 files)
> 2. VALIDATION_REPORT.md (full summary: all squads, all clusters, density %, improvements)
> 3. README.md (how to extend, limitations, next steps)
> 4. Visualization: dashboard showing all 3 clusters + flow comparison
> 5. Questions:
>    - "Do you recognize all three blocker clusters? Do they match how your squads actually get blocked?"
>    - "Does the flow improvement (high-density → optimized) match your expectations for those interventions?"
>    - "Is this dataset credible enough to show in an RFP demo?"

**Sign-Off Criteria:**
- [ ] Business partner recognizes all 3 clusters (Auth, DataPlatform, Checkout)
- [ ] Cascade logic feels authentic (not random)
- [ ] Blocker density targets (30–40% → 15–20%) match their mental model of "percolation threshold"
- [ ] Data is "client-ready" (realistic enough for RFP, not obviously synthetic)
- [ ] No show-stoppers (e.g., "this blocker reason would never happen," "nobody blocks on this for 5 days")

**Sign-Off Statement (Required for completion):**
> "This dataset proves the percolation hypothesis. The 8-squad finance model is credible and ready to demo to clients. I'm confident this is our ROI platform for the dashboard."

**Follow-Up:**
- [ ] Business partner identifies any features/clusters that need adjustment for their specific context
- [ ] Any post-MVP priorities (Simulation, Prediction, etc.) are logged for post-launch roadmap

---

## Known Limitations & Edge Cases

### Accepted Limitations (Not Bugs; DoD allows these)

- **Synthetic Data:** Waiting reasons are templates, not real tickets. Cycle times are statistically realistic, not historically accurate.
- **No Real Incidents:** Data doesn't link blockers to production incidents; post-V1 feature.
- **No Resource Data:** Can't recommend "add 2 nodes to Auth"; that's P3 Simulation layer.
- **Single Scenario Set:** V1 has 1 high-density + 1 optimized path. Multi-variant scenarios (what-if engine) are post-V1.
- **No Machine Learning:** Prediction models deferred; V1 detects, doesn't forecast.
- **Manual Test Coverage:** Perfecto/Selenium coverage is mocked, not real test data.

### Edge Cases Handled

- **Multi-Sprint Issues:** Some features span 2–3 sprints due to blockers; denormalized Sprint columns handle this.
- **Cascading Blockers:** When a root cause resolves, dependent blockers clear 1 day later (propagation lag modeled).
- **Cluster Overlap Windows:** Cluster 3 onset (week 10 day 2) avoids Cluster 2 tail (week 10 day 1); no conflicts.
- **External Dependencies:** DataPlatform, CRM, BPM, ESB blockers have `External Blocker = true` for filtering.
- **Flaky Tests:** Correlated to cluster windows (high-density weeks 10–12 have more flakiness; optimized has less).

### Edge Cases *Not* Handled (Acceptable for V1)

- **Concurrent Root Causes in Same Squad:** Two unrelated blockers for the same squad at the same time (rare; V1 simplifies this away)
- **Circular Dependencies:** Squad A → B → C → A (not modeled; squads have acyclic deps per ARCHITECTURE.md)
- **Priority Interventions:** Can't model "if we prioritize Feature X over Y" (post-V1 simulation layer)
- **Context-Switching Penalty:** Blocker durations don't increase if squad is juggling 10 blockers simultaneously (linear model, not exponential cost)

---

## Verification Workflow (Code + PM + Business Partner)

```
Iteration N Development:
  ↓
Code runs Tasks N.1–N.X
  ↓
Code runs Automated Checks ← All must pass
  ↓
PM runs Manual Spot-Checks (~15 min) ← Sample-based validation
  ↓
Generate VALIDATION_REPORT.md ← Auto-summary of datasets
  ↓
Schedule Business Partner Review (~30 min)
  ↓
Business Partner loads CSVs into viz tool ← Sees "crime neighborhoods"
  ↓
Business Partner validates narrative: "Does this match reality?"
  ↓
Business Partner signs off (statement required) ← Gate to next iteration
  ↓
(If sign-off fails: backlog updated, tasks re-run, cycle repeats)
```

---

## Session Log

| Date | Item | Status |
|------|------|--------|
| 2026-08-22 | TESTER.md created: DoD for Sprint 1–3, automated checks, manual spot-checks, business partner sign-off criteria | Ready for Code |
| 2026-08-23 | Renamed our delivery timebox from "Sprint" to "Iteration" throughout (headers, sign-off gates); domain concept (`Sprint-1..Sprint-12` columns, weekly cluster timing) left unchanged. No scope change. | PM + Code + BP (Kirschi) |

