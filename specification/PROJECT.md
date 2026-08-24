# Agile Blocker Detection Platform — Project Charter

**Status:** Scoping (Aug 22, 2026)  
**Owner:** PM (Claude)  
**Target deadline:** Exploratory (no fixed gate)

---

## Outcomes (Prioritized)

1. **P1: Detection** — Correctly identify blocker *clusters* (2+ squads simultaneously blocked by related root cause) and their density/timing. Dashboard should surface "crime neighborhoods" where blocker density triggers percolation halt.
   - Metric: Can we visually identify 3–5 injected problem clusters in synthetic data that would cause observable flow degradation?
   - Success: When cluster density is HIGH (V1 dataset), flow visibly stalls; when density is REDUCED (V2 dataset), flow resumes.

2. **P2: Actionability** — Correlate cluster signatures to *specific* intervention recommendations and show impact of partial interventions.
   - **Metric A (Diagnosis):** Can the dashboard surface the root cause (shared component, external blocker, peer squad conflict) and suggest where to focus fixing effort?
     - Success: A human PM looking at the cluster can say "I should fix X" without guessing.
   - **Metric B (Mitigation via Mocking):** Can we show that mocking part X of an external dependency reduces blockage and enables flow?
     - Example: "If we mock the DataPlatform API responses, Core Banking unblocks; flow improves by Y days per sprint."
     - Success: Dashboard shows blocker reduction when we simulate a mock integration (V2-variant dataset).

3. **P3: Simulation** — (Deferred to Milestone 2) Forecast flow improvement by simulating resource additions or mocking specific dependencies.
   - **Metric:** If we add N resources to X or mock Y, based on today's cluster data, flow improves by Z%.
   - Success: "Add 2 nodes to Auth service → Auth resolves in 1 day instead of 3 → downstream blockers clear 1 day earlier → 15% velocity gain."
   - Deferred: Requires V1 data to be solid; needs interactive scenario engine (post-backlog).

4. **P4: Prediction** — (Deferred, post-V1) Forecast *when* a squad halts before it happens based on leading indicators.

---

## Scope: What We're Building

### In Scope (V1: Minimum to validate)

**Data generation:**
- 8 finance-domain squads with distinct responsibility areas (see ARCHITECTURE.md)
- 12 sprints of synthetic Jira issues (features, blockers, waiting items)
- Interdependencies modeled as: shared components, peer-squad dependencies, external-team blockers
- **Three "crime neighborhoods"** deliberately injected:
  - Cluster 1: Auth/Login failures cascade to 5+ downstream squads (weeks 3–5)
  - Cluster 2: External DataPlatform annual release delay blocks Analytics + Core Banking (weeks 6–10)
  - Cluster 3: Checkout service flakiness + insufficient test automation creates feedback loop (weeks 10–12)
- Two datasets:
  - `high_density.csv` — blockers dense, cycle times long, flow stalled
  - `post_optimization.csv` — same structure, 40–50% fewer blockers, flow resumed
- **Test execution logs** (Xray-like): pass/fail counts per feature per sprint, automation coverage % (low/medium/high), flaky test flags
- **Output format:** Jira CSV (standard Atlassian export) + test logs CSV
- **Parameterization:** Automation coverage % settable at generation time (e.g., "run with 20% API automation, 50% UI automation, 30% manual")

**Dashboard readiness:**
- Data structure proven for import into any viz tool (Tableau, Grafana, custom React, etc.)
- Clear "waiting" reason taxonomy that correlates to root causes (not random noise)
- Cycle-time data honest (interdependent waiting cascades visible in timestamps)

---

### Deliberately Not Built Yet (With Trigger for Revisit)

| Item | Reason | Revisit If |
|------|--------|-----------|
| **P3 Simulation (what-if engine)** | Requires solid V1 detection first; simulation layer built post-validation | Business partner validates Metric A + B on high-density data |
| **P4 Prediction (forecasting)** | Prediction requires baseline patterns from V1 + V2; not in MVP | Simulation engine works; client wants early-warning system |
| **Production incident data** | Scope creep; blocker flow + test coverage are sufficient to validate hypothesis | Client explicitly requires incident correlation |
| **Resource utilization data** | Adds complexity; we can mock interventions via scenario datasets without CPU/node details | Dashboard needs to recommend *how much* resource to add |
| **Real Jira/Xray API integration** | Out-of-scope for V1; CSV export proves ROI on data alone | Client is ready to deploy to live system |
| **Multi-variant scenario generation** | V1 is one high-density reference; optimized dataset proves mocking hypothesis (Metric B) | Need to A/B test 5+ intervention scenarios |
| **Advanced test metadata** | (flaky test tracking, test-to-code lineage, etc.) | Test root-cause analysis becomes a blocker |

---

## Reusability & ROI Platform

**This is not a one-off.**

- Generator is a **command-line tool** (Python script, parameterized) that produces JIRA/Xray CSVs
- Input: squad config (YAML or JSON), blocker topology, automation coverage %, density target
- Output: reproducible datasets for regression testing the dashboard + client demos
- **Post-V1 roadmap:** Once 8-squad finance demo succeeds, template it for other domains (HR, Sales, Ops) by swapping squad configs and interdependencies

---

## Success Criteria

**V1 is done when:**
1. Generator produces 2 valid datasets (high density + optimized) with no manual editing
2. Blocker clusters are *visibly* correlated across 2+ squads in the data (same root cause → same timeline)
3. Waiting cycle times are realistic and interdependent (Squad A resolves → Squad B's waiting drops next day)
4. Test execution logs correlate to feature complexity + automation coverage (high coverage → fewer manual test blockers)
5. A human (business partner) can load the data, see the "crime neighborhoods," and articulate 1–2 fixes without asking for clarification
6. Datasets are regenerable (same seed → same data for regression testing)

---

## Known Constraints & Assumptions

- **12 sprints is one quarter:** Realistic for spotting seasonal patterns (external teams' annual gates, squad context-switching)
- **CSV over live APIs:** Enough to prove ROI; real data integration comes post-V1
- **Synthetic ≠ real:** We're validating the *hypothesis* (percolation matters), not claiming production fidelity yet
- **Automation coverage is mocked:** Xray logs will show %-based automation; real test execution logic is deferred

---

## Session Log

| Date | Change | By |
|------|--------|-----|
| 2026-08-22 | Charter drafted, outcomes prioritized (Detection → Actionability → Prediction), scope locked | PM |

