# session_log.md

## 2026-08-22 — Sprint 1 build

**Context.** This repo started with only a `LICENSE` and a two-line
`README.md`; no team docs, backlog, architecture, or code existed yet, and
no separate BP/PM session was reachable. Built the full Sprint 1 loop
(BP/PM/Code artifacts + implementation) in one pass, playing all three
roles as needed per `TEAM_OPERATING_SYSTEM.md`.

**What shipped**

- Process docs: `TEAM_OPERATING_SYSTEM.md`, `DEFINITION_OF_DONE.md`,
  `PROJECT.md`, `BACKLOG.md` (Tasks 1.1–1.6), `ARCHITECTURE.md`,
  `TESTER.md`.
- `src/generate_blocker_data.py` — stdlib-only generator implementing the
  full domain model in `ARCHITECTURE.md`: teams (internal/external),
  Jira-style issues, Xray-style blocker links with derived category, and
  a tunable percolation-style random-graph process for the blocker edges.
- `tests/test_blocker_generator.py` — 21 automated tests covering every
  item in `TESTER.md` §Automated checks: schema, referential integrity,
  invariants (no self-blocking, no duplicate pairs, category always
  derived not chosen), determinism (same seed → byte-identical CSVs),
  percolation-stats correctness against a hand-built graph, and a CLI
  smoke test. All 21 pass (`pytest tests/ -v`).
- Generated artifacts: `data/teams.csv`, `data/issues.csv`,
  `data/blockers.csv`, `docs/validation_report.md` (default params:
  5 internal + 3 external teams, 25 issues/team, seed 42).

**PM manual spot-check (TESTER.md §Manual spot-checks)** — performed as
part of this session:

- `teams.csv`: 5 internal (Atlas, Nimbus, Forge, Vector, Halcyon) clearly
  distinguishable from 3 external vendors (`Vendor-*`, `Partner-*`). Pass.
- `issues.csv`: spot-checked several rows — `created <= updated` holds,
  `resolved` is set only when `status == Done` and always `>= updated`.
  Pass.
- `blockers.csv`: manually cross-checked several `External` and
  `Inter-Team` rows against the referenced issues' teams in `issues.csv`
  — category always matches the derivation rule. Pass.
- Density sweep (`--blocker-density` 0.1 / 0.35 / 0.8 / 2.0, same seed):
  largest-component fraction moved 2.5% → 2.0% → 24.0% → 77.5% — a clear
  percolation transition as density rises (minor noise at the low end is
  expected sampling variance, not a defect). Pass.

**Sign-off:** Sprint 1 (Tasks 1.1–1.6) meets `DEFINITION_OF_DONE.md`.
CSVs and `docs/validation_report.md` are ready for BP's narrative
validation.

**Open follow-ups for BP:** review whether the default parameters
(25 issues/team, density 0.35) tell a strong enough "vendor is the
bottleneck" story for a dashboard demo, or whether Sprint 2 should ship a
demo-tuned parameter preset alongside the general-purpose defaults.

## Model & Ethics Checkpoint (2026-08-22)

Models used:
- PM (Claude Haiku 4.5): Sufficient for well-scoped Sprint 1; reassess at Sprint 2 if architecture complexity rises
- Code (Claude Sonnet 5): Appropriate for implementation; no escalation needed yet

Ethics:
- ETHICS_AGREEMENT.md locked in repo, governs all decisions
- Specification-first principle enforced: Code given /specification/ as source of truth
- Single source of truth achieved: archived Code's generic versions, consolidated to /specification/

Observations:
- Miscommunication resolved by consolidation, not conversation
- Model selection deferred to post-Sprint 1 assessment
- Dr. Agile standards repo TBD (post-project action)

## Iteration 1 Retro (2026-08-23)

**Participants:** Kirschi (BP), PM, Code

**Finding:** `git fetch --all` revealed three unmerged branches, each an
independent, divergent rewrite of Milestone 1
(`claude/blocker-generator-pm-ffutq6`, `claude/sprint-1-blocker-generator-qpnb1i`,
`claude/sprint1-backlog-xray-mismatch-8io8es`), none reconciled with `main`.
Root cause: policies written into `TEAM_OPERATING_SYSTEM.md` (single source
of truth, branch-per-task) were never enforced or bounded — nothing stopped
a session from opening a branch and never coming back to it.

**Decisions made:**
1. Fixed citation spelling in `DEFINITION_OF_DONE.md`: Marty Cagan, Melissa Perri.
2. Adopted trunk-based development (Fowler) — one branch per task, merged or
   deleted before the session that created it ends. Codified as
   `DEFINITION_OF_DONE.md` Governance Rule 7.
3. Created `CLAUDE.md` as the enforcement point (loaded automatically every
   session), constrained to be DRY with `/specification/` — it points, it
   doesn't restate.
4. Replaced the weekly kickoff/sign-off cadence with a one-day timebox, so
   BP/PM/Code calibrate real throughput before committing to larger scope.
5. Renamed our delivery timebox from "Sprint" to "Iteration" throughout
   `BACKLOG.md`, `TESTER.md`, `PROJECT.md`, `DEFINITION_OF_DONE.md`, and
   `TEAM_OPERATING_SYSTEM.md` — "Sprint" is now reserved for the synthetic
   dataset's own domain concept (`Sprint-1..Sprint-12`, ARCHITECTURE.md),
   which was never renamed.
6. Iteration 1 declared closed (as of yesterday); Iteration 2 begins now.

**Not yet resolved (first item for Iteration 2 planning):** the three
orphaned branches above, and the spec-vs-build gap they each independently
attempted to close (the locked 8-squad finance/3-cluster spec in
`/specification/` vs. the generic random-graph generator on `main`).

## Iteration 2 (2026-08-23)

**Goal:** resolve the branch conflicts into trunk-based dev; complete
Milestone 1 (Auth Squad + Auth cluster, 12 sprints) to Done-Done.

**Discovery:** `claude/blocker-generator-pm-ffutq6` (one of the three
orphaned branches) turned out to hold a PM ruling from 2026-08-22, already
"confirmed with Business Partner," that was never merged to `main`:
`TESTER.md`'s "20–30% global blocker density" was copied from the full
8-squad/3-cluster model without rescaling, and is mathematically impossible
for the 3-squad/1-cluster slice (caps at ~1–2% globally). Ruling: density is
window-scoped (within the cluster's own week), `Waiting Reason` persists
after a blocker resolves, external-dependency deferral stands. That branch
also named `claude/sprint-1-blocker-generator-qpnb1i` as the correct base
implementation and explicitly rejected `claude/sprint1-backlog-xray-mismatch-8io8es`'s
baseline-blocker approach. Folded this ruling into `specification/BACKLOG.md`
(Task 1.4) and `specification/TESTER.md` today, formalizing what was already
agreed but undocumented in `/specification/`.

**Also corrected:** `ARCHITECTURE.md`'s Cluster 1 timeline said "Week 4, Day
3" for root resolution, contradicting its own stated 3-day duration and
`BACKLOG.md` Task 1.3's verification text. Corrected to Week 3, Day 3 (PM
call, per Decision Rights — architecture assumptions are PM's, BP veto
after).

**Landed:** `qpnb1i`'s package (`src/blocker_generator/`: squads,
archetypes, clusters, features, xray_logs, csv_io) plus its test suite (59
tests), `ETHICS_AGREEMENT.md` (previously referenced in this log as "locked
in repo" on 2026-08-22 but actually lost across the branch divergence — this
restores it), and added the one real gap the PM ruling flagged: cluster
blocker rows now resolve to `Status = Done` with a populated `Resolved`
timestamp while `Waiting Reason` persists (previously they stayed
permanently `Waiting`, which the branch's own tests had encoded as
correct — updated `test_features.py` to match the ruling instead). Added
`src/blocker_generator/__main__.py` as the CLI entry point neither original
branch had committed (the branch's committed CSVs had been generated by an
uncommitted, ad-hoc script — regenerability, a `PROJECT.md` Success
Criterion, was not actually satisfiable from either branch as merged).

**PM manual spot-check (TESTER.md Milestone 1 §Manual Spot-Checks) —
performed against the regenerated `data/v1_auth_cluster_high_density.csv`
and `data/v1_auth_cluster_test_logs.csv` (seed 42):**
- 653 total rows (644 features + 9 blockers), within the corrected 547–731
  range. Pass.
- All 9 blocker rows: `Status = Done`, `Resolved` populated (Created + 1
  day), `Waiting Reason` non-empty, `Cluster Tag = Cluster-1-Auth`. Auth
  (SQ-A) blockers on Jul 15–17 (week 3, days 1–3); Checkout/Payments
  blockers on Jul 16–18 (1-day cascade lag). No blockers outside week 3.
  Pass.
- Window-scoped density (blockers ÷ week-3 features): 28.1%, within
  20–30%. Global density: 1.4%, within the expected ~1–2%. Pass.
- Spot-checked 3 early features (created before Jul 15): `Resolved` well
  before the Auth blocker's onset, `Waiting Reason` empty, cycle times
  3.1–11.8 days (realistic). Pass.
- Test logs: 1,235 rows, within 1,200–1,500. Payments squad Selenium
  presence 108/218 (~49.5%, matches the ~50% target). Average automation
  coverage 48.1%, within the 40–60% band. Flaky-test rate for
  Selenium/Perfecto Mobile tests inside the cluster's week: 21.2%, vs. 1.4%
  baseline elsewhere — clearly concentrated in the cluster window as
  required, though the raw in-window rate across all test types (8.7%) reads
  lower than TESTER.md's "15–20%" text, which appears to describe the
  automation-heavy subset specifically (matches ARCHITECTURE.md's flaky-test
  note). Pass, with that reading noted for whoever revisits the wording.
- Determinism: two independent runs at seed 42 produced byte-identical
  CSVs. Pass.
- `pytest tests/ -v`: 59/59 pass.

**Status:** Code + PM verification complete; all `TESTER.md` Milestone 1
automated checks and manual spot-checks pass. **Business Partner narrative
sign-off is still outstanding** — per `TEAM_OPERATING_SYSTEM.md`, that step
is BP's, not PM's or Code's, to perform.

**Branch disposition (pending BP confirmation, not yet executed):**
- `claude/sprint-1-blocker-generator-qpnb1i` — merged into this Iteration's
  work; safe to delete once this lands on `main`.
- `claude/sprint1-backlog-xray-mismatch-8io8es` — superseded per the PM
  ruling above (explicitly rejected, not merged); safe to delete.
- `claude/blocker-generator-pm-ffutq6` — its analysis is now captured here
  and in `/specification/`; safe to delete once confirmed nothing else on
  it is needed.

**Update:** PR #6 (open on `claude/blocker-generator-pm-ffutq6`) reviewed and
closed without merging — its ruling was already independently landed in
`a195769`; the one thing it caught that the independent fix missed
(`TESTER.md`'s stale "13 core columns" vs. the actual 12) was ported to
`main` directly (`014b571`). PM + Code confirm all three orphaned branches
are safe to delete from GitHub (branch deletion isn't available from this
session — git push --delete returned 403, no delete-branch tool on the
GitHub MCP server — so BP needs to do this step).

**BP review of the delivered CSVs surfaced a real defect:** researched real
Jira CSV export behavior (see Issue #7) and confirmed BP is right —
`ARCHITECTURE.md`'s Sprint-column schema (`Sprint-1`..`Sprint-12` as
distinct headers holding dates) doesn't match how Jira actually exports a
multi-value field (repeated `Sprint` header per occupied slot, sprint
*name* as the value, not a date). Filed as Issue #7 with a proposed fix,
pending PM/BP confirmation before Code implements — this touches
`ARCHITECTURE.md`, `TESTER.md`, the generator, and the committed CSV
together. BP's second point ("External Dependency column, which should be
a Waiting Reason") doesn't match any column that actually exists in either
delivered CSV or in the spec — filed as Issue #8 asking BP to clarify which
file/column was meant rather than guessing and changing the schema again.

**Update:** Issue #7 fixed and merged to `main` (`c52e041`) — `Sprint`
header now repeats once per occupied slot (sized to the dataset's actual
widest span, 3), cell values are sprint names, not dates.
`ARCHITECTURE.md`/`BACKLOG.md`/`TESTER.md` corrected to match;
`data/v1_auth_cluster_high_density.csv` regenerated; 59/59 tests pass;
determinism reconfirmed. Closed with a note that BP's "Ready For Sprint"
placeholder value wasn't modeled (reads as a workflow-status artifact of
BP's specific Jira instance, not universal Jira export behavior) — reopen
if that's actually expected here.

Issue #8 ("External Dependency column") remains open — still needs BP's
clarification on which file/column was meant before Code touches the
schema again on a guess.

**Update — terminology correction, round 2:** "Iteration" had silently come
to mean two different things: our one-day daily timebox (correct, per
`TEAM_OPERATING_SYSTEM.md`'s Daily Iteration Cadence) and `BACKLOG.md`/
`TESTER.md`'s multi-task vertical-slice groupings (the former "Sprint
1/2/3," renamed to "Iteration 1/2/3" earlier today) — the exact same
collision class as the original Sprint-vs-Iteration problem, one layer up.
Evidence it was live: BP asked "what goes in Iteration 3" meaning the next
*day*, but `BACKLOG.md`'s "Iteration 3" meant the full 8-squad/CLI epic —
answering literally would have proposed multiple days of work for a
one-day question. Introduced a third term, **Milestone**, for the
vertical-slice groupings; "Iteration" now means only the daily timebox.
Milestone 1 (Auth Squad + Cluster) took two Iterations (1 and 2) to land —
Milestones and Iterations are not 1:1. Renamed across `BACKLOG.md`,
`TESTER.md`, `PROJECT.md`, `DEFINITION_OF_DONE.md`, `TEAM_OPERATING_SYSTEM.md`,
`CLAUDE.md`, and the generator itself (`VALIDATION_REPORT_Milestone_1.md`,
regenerated).

**PBR (2026-08-23):** BP identified that `Test Automation`, `External
Blocker`, and `Cluster Tag` aren't out-of-the-box Jira fields. Researched
real Atlassian CSV export behavior (confirmed: custom fields export as
`Custom field (<Name>)`, a documented convention — Atlassian
JRASERVER-62216/JRACLOUD-62216). Classified every current schema column as
native vs. custom (native: Issue Key, Summary, Type, Status, Assignee,
Created, Resolved, Sprint — the last is technically a plugin-added field
but Jira exports it plain; custom: Waiting Reason, Test Automation,
External Blocker). Two open design questions surfaced, not decided
unilaterally: whether `Cluster Tag` should be a custom field or Jira's
native `Labels` field, and whether `Cycle Time (days)` (not a real
exportable Jira field at all) should be kept as a generator convenience or
dropped in favor of letting a downstream dashboard compute it. Written up
as Task 2.0 in `specification/BACKLOG.md`, gating Milestone 2's 5-squad
scope. Code assessed it as too large for one Iteration as scoped and split
it into four independent sub-tasks (2.0a ready now; 2.0b blocked on Issue
#8; 2.0c blocked on the Labels-format check; 2.0d blocked on a keep/drop
decision) — for PM/BP/Code review before Iteration 3 starts, not yet
implemented.

**BP feedback on planning structure:** BACKLOG.md's Milestone-N-as-Iteration-N
framing was itself a predetermined-scope pitfall — pre-bucketing tasks into
named multi-day sections reads as a schedule even when it isn't one (see
the Milestone-vs-Iteration collision above). Restructured `BACKLOG.md`
around two new sections: an **Iteration Log** (status index: which PBIs
each Iteration pulled and their outcome) and a **Product Backlog** (flat,
prioritized PBI list, tagged with a Milestone for narrative context only —
not scheduled to any Iteration in advance). The `Milestone N` sections
remain as reference detail (acceptance criteria, schemas) for whenever a
PBI drawn from them actually gets pulled — they no longer imply a
schedule.

**Process note for tomorrow (Iteration 4):** BP clarified that PBR
(backlog refinement — researching and drafting new candidate PBIs) should
happen *after* the day's planning conversation closes, not folded into
Kickoff. Added to `TEAM_OPERATING_SYSTEM.md`'s Daily Iteration Cadence as
a new "After sign-off: Backlog Refinement" step, effective Iteration 4.
(Today's Jira-field PBR happened mid-conversation, before this was
clarified — the output stands, just noting the cadence going forward.)

## Iteration 3 (2026-08-24)

**Goal (per Product Backlog, pulled at Kickoff):** PBI 2.0a (rename
`Waiting Reason`/`Test Automation` to native `Custom field (...)` format)
+ resolve Issue #8.

**Issue #8 resolved:** BP's follow-up ("Test Automation, External
Blocker, Cluster Tag are not out of the box Jira fields... they should be
custom fields") confirmed the column in question is `External Blocker`,
and the disposition is to correctly label it (PBI 2.0b), not fold it into
`Waiting Reason` as the original report's wording suggested. Closed on
GitHub with that reading; reopen if wrong.

**PBI 2.0a landed** (`66e0e64`): `Waiting Reason` → `Custom field (Waiting
Reason)`, `Test Automation` → `Custom field (Test Automation)`. Also fixed
`ARCHITECTURE.md`'s Core Columns table, which still had pre-persistence-fix
language ("Only populated if Status = Waiting") that this session's
earlier Waiting-Reason-persistence correction had missed. Regenerated CSV,
spot-checked the real output, 60/60 tests pass, determinism reconfirmed.

**Deliberately not pulled into today's scope:** PBI 2.0b (`External
Blocker` rename), even though Issue #8's resolution unblocks it — staying
disciplined to what was actually planned at Kickoff rather than quietly
expanding scope mid-Iteration. Flagged to BP as ready for Iteration 4 or
sooner if wanted today.

**Status:** Iteration 3 complete. Both planned items done. Product
Backlog and Iteration Log in `BACKLOG.md` updated to match.

**Follow-up, same day — BP's rulings on PBI 2.0b/c/d:**
- **External Blocker:** not a Jira field. My earlier Issue #8 resolution
  (just relabel it) was incomplete — BP's correction: drop the column
  entirely, the internal-vs-external signal belongs to which blocker
  archetype produced the `Waiting Reason`, not a separate flag. Corrected
  the GitHub issue comment accordingly.
- **Cluster Tag → Labels:** confirmed via research that Jira's native
  `Labels` field exports as repeated columns (one per occupied label
  slot, like `Sprint`), not a comma-joined cell (Atlassian
  JRACLOUD-85433/JRASERVER-63747).
- **Cycle Time (days):** confirmed not a real Jira field either way;
  dropped from the CSV, kept internally (still used by `xray_logs.py` and
  the validation report).

Implemented all three: `IssueRow.cluster_tag: str` → `labels: List[str]`;
`external_blocker` field removed entirely; `cycle_time_days` no longer
written to CSV. CSV writer now handles two independent repeated-column
groups (`Labels`, `Sprint`). Header shrank from 12 core columns to 9 (+
repeated `Labels` + repeated `Sprint`). Updated `ARCHITECTURE.md`,
`TESTER.md`, and the test suite to match; regenerated CSV; 59/59 tests
pass; determinism reconfirmed.

**BP's separate PM-directed observation:** every row in the dataset is
`Status = Done` — the generator has no "as-of" reference point within the
12-sprint timeline, so it can't show a live, actionable snapshot (some
items currently blocked, some previously blocked with history, some aging
toward risk). Diagnosed as a real gap: `ARCHITECTURE.md` already lists
`"In Progress"` as a valid Status, but the generator never uses it.
Written up as **PBI 2.1** in `BACKLOG.md`'s Product Backlog — not
implemented today (this was addressed to PM as something to account for
before Milestone 2, not an execution go-ahead like PBI 2.0b/c/d was for
Code). Flagged as should-land before Milestone 2 scales the schema
further, since 5 squads on top of a still-fully-retrospective dataset
just repeats the same gap at larger scale.

**Follow-up, same day — Xray CSV research (Issue #9), PBI 2.1 implemented,
and BP's other rulings:**

**Xray research (mirroring Issue #7's Jira research):** confirmed via
Atlassian/Xray docs that real Xray `Test Type` values are Manual/
Cucumber/Generic (a test's *authoring method*), not the tool names our
schema uses (Selenium/Postman/Swagger/Perfecto Mobile) — foundational to
`xray_logs.py`'s whole model, flagged for a design decision, not touched.
Also confirmed `Automation Coverage %` and `Flaky` aren't raw Xray
fields — coverage is a computed report metric, flakiness is inferred from
run history — same pattern as `Cycle Time` in the Jira CSV. Dropped both
from the CSV (kept internally), no BP input needed for that part.

**BP's aging ruling:** the dashboard computes age as NOW()-`Created` at
report time — not something we pre-compute. This simplified PBI 2.1 to
just: leave some issues genuinely unresolved.

**PBI 2.1 implemented** (rejected the global as-of-date design floated
earlier — it would have excluded most of the 12-sprint feature population
from the export, conflicting with `TESTER.md`'s existing row-count
baseline). Smaller design instead: each cascade squad's final blocker day
stays `Waiting` (root always fully resolves — "downstream clears day 4" is
a lag relative to root's "resolves day 3," so the last step hasn't cleared
yet); ~8% of ordinary features stay `In Progress`. Caught and fixed a real
bug during implementation: the in-progress decision initially drew from
the shared feature-generation RNG, which perturbed every later feature's
created-date draw and broke the window-density and flaky-correlation
tests for this seed — fixed by deciding via an independent per-issue RNG
instead, leaving the original draw sequence untouched. 61/61 tests pass,
determinism reconfirmed, real output spot-checked (including catching and
fixing stale example issue keys in `TESTER.md` left over from the broken
intermediate state).

**Status:** Iteration 3 (extended) complete. `BACKLOG.md`'s Iteration Log
and Product Backlog updated. Xray's bigger gaps (`Test Type` values, and
real exports being one-row-per-Test-Run rather than aggregated counts)
remain open, tracked as future Milestone 2+ items needing BP/design
input.


---

**Same day, continued — role clarification: Product Owner, not Business
Partner (Issue #10):**

Retro question from BP: given they've been *originating* architecture and
backlog-structure rulings this iteration (Cluster Tag → Labels, dropping
Cycle Time, folding External Blocker into Waiting Reason, the aging
ruling, the Iteration Log / Product Backlog restructuring) rather than
just vetoing PM/Code proposals, does "Business Partner" still describe
the role, and if not, what should?

Opened Issue #10 proposing a dual BP/PO hat (keep "Business Partner" for
the `ETHICS_AGREEMENT.md` stakeholder-hierarchy meaning, add explicit
"Product Owner" decision rights alongside it). BP rejected the dual-hat
compromise and simplified instead:

> "I concur with PO as my role, noting that this is the Scrum, Nexus and
> LeSS PO, not the SAFe or Scrum@Scale PO. For simplicity, drop the BP
> definition. PO is easier."

Implemented as a single-role rename, not a relabeling exercise:
- Mechanical rename "Business Partner"/"BP" → "Product Owner"/"PO" across
  `CLAUDE.md`, `DEFINITION_OF_DONE.md`, `TEAM_OPERATING_SYSTEM.md`,
  `ETHICS_AGREEMENT.md`, `README.md`, and all three live `specification/`
  files — excluding dated Session Log rows (historical narrative is never
  rewritten) and `_archive/` (out of scope, already retired).
- Substantive follow-through, not just the label: rewrote
  `DEFINITION_OF_DONE.md` Governance Rule 4's Decision Rights table so the
  PO *owns* backlog prioritization and can *originate* architecture/
  backlog-structure rulings, rather than only holding veto power — this
  was the actual gap Issue #10 flagged, and the label change alone
  would have left it undocumented.
- Recorded the Scrum/Nexus/LeSS-PO-vs-SAFe/Scrum@Scale-PO distinction in
  both `DEFINITION_OF_DONE.md` (Governance Rule 4) and
  `ETHICS_AGREEMENT.md` (stakeholder hierarchy) so it isn't lost to a
  single chat message.
- Added Session Log rows to both `DEFINITION_OF_DONE.md` and
  `ETHICS_AGREEMENT.md` per each document's own "changes require explicit
  written agreement" rule, citing Issue #10 and BP's approval verbatim.

61/61 tests pass (prose-only change; no generator code touched).

**Status:** Issue #10 resolved — closing with a confirming comment. Going
forward this log (and all docs) uses "Product Owner (PO)"; "BP" is
retired except where it appears inside untouched historical rows above.

---

**Same day — Iteration 3 retrospective, closed with working-agreement changes,
not just talk:**

PM proposed 9 retro candidates (research-before-guessing paying off,
independent-RNG pattern, trunk-based development working, the Issue #8
wrong-then-corrected resolution, the rename script's case-sensitivity gap,
pushing to the wrong branch mid-session, the "merged ≠ deleted" branch
confusion, Backlog Refinement placement, and the BP→PO role churn). PO
responded to each:

1. Asked what needs to change to make vendor-format validation (Atlassian,
   and future vendors) the norm, not an ad hoc save each time.
2. Asked what the architecture improvement is (re: the independent-RNG bug).
3. Good work acknowledged, all three parties.
4. Explicit no-blame framing: "I am human, I make mistakes. You are AI,
   you make mistakes. That's why we improve our agreements" — re: Issue #8's
   wrong-then-corrected resolution.
5. Asked whether there's an action item on the rename script's
   case-sensitivity gap.
6. No-blame (as #4) on the wrong-branch push; asked what changes in the
   working agreements.
7. New standing practice proposed directly: at the end of work on each
   PBI, Code gives PO the list of branches safe to delete.
8. Backlog Refinement placement: still work in progress, no ruling yet.
9. BP→PO role churn: also work in progress — explicitly deferred to revisit
   after 2–3 additional Iterations, not decided now.

**Converted into actual working-agreement changes today (items 1, 2, 5, 6,
7 — not left as retro notes):**
- `DEFINITION_OF_DONE.md` Governance Rule 8 (new): Vendor Format
  Verification — every schema column cites a vendor-doc source or is
  marked internal; code and `ARCHITECTURE.md` must agree, enforced via a
  new Schema Authenticity Check in `TESTER.md`.
- Fixed a real instance of the gap Rule 8 targets while writing it:
  `ARCHITECTURE.md`'s Xray schema table still listed `Flaky`/`Automation
  Coverage %` as columns after Issue #9 had already dropped them from
  `xray_logs.py` — spec and code had drifted. Corrected the table and
  flagged `Test Type`'s non-authentic values inline, still open pending
  client feedback (Issue #9 stays open for that reason alone).
- `ARCHITECTURE.md` "Notes for Code Implementation" now documents the
  independent-RNG-streams rule as a standing design principle, not just a
  one-off fix buried in `features.py`'s docstring.
- `DEFINITION_OF_DONE.md` Governance Rule 7 amended with two practices:
  check for a session's designated branch before inventing one; Code
  posts a branch-deletion list to the PO at the end of each PBI (Code has
  no delete-branch permission via git or the GitHub API in this
  environment — confirmed today by two separate 403s — so deletion stays
  the PO's action, just on a tighter, PBI-level cadence instead of
  end-of-session).
- `CLAUDE.md` updated to match both Rule 7 amendments, plus a new
  "Repo-wide renames and find/replace" section requiring a
  case-insensitive verification grep after any rename — the exact gap
  that let lowercase "business partner" instances survive the first
  BP→PO rename pass this session.

**Left open, explicitly not ruled on today (items 8–9):** Backlog
Refinement placement and the PO role definition both stay "work in
progress" — PO's own words — revisit after 2–3 more Iterations rather than
forcing a premature ruling.

**Status:** Iteration 3 fully closed — single trunk (`main`), retro
converted to concrete doc changes where the PO gave a clear direction,
explicitly parked where it didn't.

---

**Iteration 4 (2026-08-25) — Task 2.1: 5-squad + DataPlatform squad model:**

PM/Code proposed pulling only Task 2.1 into today's Iteration (PO explicitly
asked for a realistic, Done-able-today proposal, not a development session —
"recall that I am human"). PO approved as proposed: "I like this plan. Go
ahead. We'll examine the resulting artifacts and decide afterwards if
there's capacity for more Done-able work."

Before starting, merged Iteration 3's retro follow-through branch
(`claude/blocker-generator-meeting-8ogayj`, commit `37910ab`) into `main`
so today's work forked from a clean trunk.

**Implemented:** `build_five_squad_subgraph()` in `squads.py` — Auth,
Checkout, Payments (unchanged from Task 1.1) + Core Banking, Savings.
Added a new `Squad.external_depends_on` field rather than following
BACKLOG.md's literal Task 2.1 test line (`CoreBanking.depends_on ==
[Auth, DataPlatform]`) exactly — that line mixes a squad id and an
external system name in one list, which would have broken the existing
invariant (`depends_on` is squad-ids-only) that Task 1.1's own tests
already rely on. `CoreBanking.depends_on == [Auth]`,
`CoreBanking.external_depends_on == [DataPlatform]` — same fact, cleaner
types. Documented as a Code implementation-detail decision (no PO
sign-off needed per `DEFINITION_OF_DONE.md`'s Decision Rights) directly
in BACKLOG.md's Task 2.1 resolution note.

Scope held deliberately narrow, matching Task 1.1's own precedent: Core
Banking's squad-level dependency on Payments (present in `ARCHITECTURE.md`'s
full Interdependency Graph) is not modeled in this slice. Not wired into
`__main__.py` or feature/cluster generation — that starts at Task 2.2.

6 new tests added (`tests/test_squads.py`); 67/67 pass. Spot-checked
`print_adjacency(build_five_squad_subgraph())` output by hand, matches
`ARCHITECTURE.md`'s topology for this slice exactly.

**Status:** Task 2.1 Done-Done. Awaiting PO's review of the artifacts
before deciding whether today has capacity for more (per PO's own framing
of how today would proceed).

---

**Iteration 4, continued — Task 2.2: DataPlatform cluster injection,
verified against a real CSV:**

PO pushed on the Agile Manifesto principle directly: "Working software is
the primary measure of progress. What is Done today that can be measured
in working progress?" Honest answer at that point: nothing — Task 2.1's
5-squad model was reachable from precisely nowhere the CLI actually runs;
`python3 -m blocker_generator --seed 42` produced byte-identical output to
the day before (verified by diff, not assumed). PO then directed: "Pull
Task 2.2, test the resulting CSV files meet the criteria."

**Implemented:**
- `CLUSTER_2_DATAPLATFORM` in `clusters.py`: root Core Banking, cascade
  Savings, onset week 6 day 1, 5-day duration (BACKLOG.md Task 2.2's own
  stated figure — same "duration vs. ARCHITECTURE.md's day-by-day
  narrative" mismatch as Cluster 1, resolved the same way: the
  BACKLOG-stated, testable number wins).
- `generate_dataset()` extended to take a list of clusters (was a single
  cluster) sharing one issue-key counter, so Auth + DataPlatform coexist
  in one dataset without key collisions. Updated all 4 existing call
  sites (`__main__.py`, `test_features.py` x3, `test_test_logs.py`) --
  Milestone 1's actual CLI output reconfirmed byte-identical afterward
  (diffed against `data/v1_auth_cluster_high_density.csv`).
- Generated and committed a real artifact:
  `data/task_2.2_five_squad_two_clusters.csv` (1,075 rows) -- not proven
  only in a test's temp directory, an actual file in the repo.

**Real bug caught by testing the CSV itself, not just aggregate counts:**
`generate_cluster_blockers` hardcoded Cluster 1's "Session cache
corruption in Auth service" / "Feature blocked pending Auth service fix"
summary text unconditionally -- harmless with one cluster, silently wrong
with two (every DataPlatform blocker's `Summary` column read "...Auth
service"). Found by eyeballing the actual generated CSV rows after
writing them, which is exactly what the PO's "test the resulting CSV
files" instruction was for -- an in-memory-only check of counts/labels
would not have caught it. Fixed by adding `root_summary`/`cascade_summary`
to `BlockerCluster`, threaded through `BlockerDay`. Added regression tests
at both the injection level and the CSV level so this can't quietly
reappear.

13 new tests (5 `test_clusters.py`, 8 `test_cluster2_dataplatform.py`);
80/80 total pass.

**Status:** Task 2.2 Done-Done, with an actual working-software delta
this time: a new, regenerable CSV in `data/` that didn't exist before
today, verified against Task 2.2's own acceptance criteria via the real
file. Task 2.3 (tuned combined density, official `v2_...` naming, row-
count range, optimized variant, test logs, validation report) remains
unstarted and out of today's scope.

---

**Iteration 4, continued — 3 new Product Backlog items from reading the
actual CSV (no work commenced, per PO's explicit instruction):**

PO, examining `data/task_2.2_five_squad_two_clusters.csv` directly: "I see
that all Waiting issues are towards the bottom of the CSV. Is that
deliberate?" Investigated (read-only, no code changes) and confirmed via
the real file:

**Root cause 1 -- CSV row order isn't sorted by anything.** Not deliberate:
`generate_dataset()` returns `features + blockers` (every Story row, then
every Sub-task row appended as one block); `write_jira_csv` writes rows in
exactly that order with zero sorting anywhere in the pipeline. Since
`Status = "Waiting"` only ever occurs on blocker rows, and blockers are
100% of the tail block, every Waiting row is structurally guaranteed to
land near the bottom. Confirmed on the actual file: all 3 Waiting rows sit
at positions 1061, 1064, 1074 of 1075 total rows. Confirmed the CSV isn't
sorted by `Created` date either (checked programmatically) -- this is a
Governance-Rule-8 (Vendor Format Verification) miss: nobody checked our
row order against what a real Jira CSV export actually looks like.

**Root cause 2 -- Issue Key numbers don't track chronological creation
order.** A squad's blocker rows (created week 3 or week 6) get *higher*
key numbers than that squad's features spanning all 12 weeks, because keys
are assigned in generation order (all of a squad's features first, then
its blockers) not creation-date order. Sorting the CSV by `Created` alone
would leave Issue Keys jumping backward and forward -- a real Jira
project's keys are assigned in the order tickets are actually opened.
Deeper than root cause 1: fixing it touches Issue Key assignment, which
ripples into existing tests and the specific example keys already
documented in `TESTER.md` (e.g. `SQ-A-214`).

**Also raised, not a bug but a design gap:** only 3 Waiting rows exist
across 1,075 total rows (the last cascade-tail day per cluster, per PBI
2.1's design). Thin for a 5-squad, 2-cluster dataset meant to give a
dashboard actionable "currently blocked" signal -- worth a PBI to revisit
the generation logic now that there's more than one cluster to draw from,
not just a same-day fix to root cause 1.

PO's explicit instruction: add all three to the Product Backlog, do NOT
commence work on any of them -- next Iteration's decision. Added to
`specification/BACKLOG.md`'s Product Backlog table:
1. Bug -- CSV row order isn't sorted (Waiting rows cluster at the bottom)
2. Bug -- Issue Key numbering doesn't reflect chronological creation order
3. PBI -- Improve Waiting-issue generation logic

No code touched. No tests added or changed. Today's CSV
(`data/task_2.2_five_squad_two_clusters.csv`) is left exactly as Task 2.2
produced it.

**Status:** Iteration 4 remains Task 2.1 + Task 2.2, both Done-Done. Three
new backlog items logged for Iteration 5 planning; none started.

---

**Iteration 4, continued — closing today's documentation gaps (PO
instruction: complete gaps now; sort-order fix must include research;
agreement changes wait for the retro):**

Three concrete gaps closed:

1. **`ARCHITECTURE.md`'s Cluster 2 section was stale.** It still described
   the pre-Task-2.2 ~30-day timeline (Week 6 Day 1 through Week 10 Day
   3/4), contradicting Task 2.2's actual 5-day implementation -- the same
   narrative-vs-quantified-criteria mismatch Cluster 1 had, which *did*
   get a corrective note (2026-08-23) that Cluster 2 never received.
   Corrected the timeline, Affected Squads, and Blocker Counts to match
   what `clusters.py` actually implements (5 (Core Banking) + 5 (Savings)
   = 10 blockers, entirely within week 6; SQ-F/Loans dropped from the
   narrative since it isn't part of the 5-squad slice), with an inline
   note explaining the correction, mirroring Cluster 1's precedent.
2. **Housekeeping note added to Task 2.3** in `BACKLOG.md`: whoever
   starts Task 2.3 must explicitly decide whether to delete or keep
   `data/task_2.2_five_squad_two_clusters.csv` once the official
   `v2_two_clusters_high_density.csv` lands -- not leave both sitting in
   `data/` indefinitely with no stated relationship between them.
3. **Sort-order bug's backlog entry tightened** per PO's explicit
   instruction: it now requires researching real Jira's default CSV
   export row ordering (Governance Rule 8) *before* implementing a fix,
   not just applying "sort by Created date" as an assumption -- same
   research-before-fix discipline as Issues #7/#8/#9.

**Explicitly deferred, not decided now (PO's instruction):** the two
working-agreement proposals from earlier today --
(a) flagging at Kickoff whether a proposed task produces a PO-facing
artifact, and
(b) a standing Kickoff-sizing check that a solo-task Iteration must
produce a measurable working-software delta --
are queued for the retrospective after this sprint closes, not decided
mid-Iteration. Recorded here so they aren't lost between now and then.

No source or test files touched this round; 80/80 tests still pass
(unaffected, doc-only change).

---

**Iteration 4 Retrospective — closed 2026-08-25:**

Seven candidate topics (working software, architecture improvement, no
work commenced on findings, dependent-artifact drift, trunk-based
development vs. Done, terminology mixups, velocity) — PO's rulings on
each, and what actually changed:

**1 & 2 — Working software as the default outcome of Done.** PO: "Working
software should be the normal and implicit outcome of a Done PBI. The
exception... should be stated so explicitly." Added `DEFINITION_OF_DONE.md`
Governance Rule 9 (Working Software Is the Default Outcome of Done) and a
matching checklist line on Artifact 5 (Code & Generated Data). A PBI's
Done statement must now say explicitly which case applies: behavior
changed (show it), or deliberately unchanged (show how "unchanged" was
verified).

**3 — Testing philosophy.** PO: "That is normal for software development.
As long as our TESTER is robust enough to catch what we already did, we
should be OK. Surprises will keep happening." Explicitly closed with NO
rule change -- declined the "manually eyeball CSV rows" standing practice
I'd proposed. The actual bar: regression coverage for bug classes already
found (already true -- both today's bugs got regression tests), not a
blanket promise to prevent all future surprises.

**4 — Dependent artifacts move together.** PO asked what should happen so
downstream docs (e.g. `ARCHITECTURE.md`) update before a PBI is Done, when
upstream artifacts (code) change. Added `DEFINITION_OF_DONE.md` Governance
Rule 10 (Dependent Artifacts Move Together): before Done, Code greps
`specification/*.md` for the domain concept being changed, not just
re-reads the file already being edited -- a mechanism, not a promise,
matching the style of `CLAUDE.md`'s rename-verification rule.

**5 — Trunk-based development vs. Done.** PO: "This should be implicit by
definition of Trunk Based Development. Do you forecast conditions when a
branch should remain open and the PBI would be considered Done?" Answer:
no -- this project's own DoD already requires PO sign-off before Done, and
in a trunk-based, single-day-Iteration, few-participant flow, sign-off and
merge are the same event. No external review queue, staged-rollout gate,
or compliance hold exists in this project's actual operating model that
would justify a gap between the two. Made this explicit in Rule 7 rather
than leaving it merely implicit, since implicit cross-document consistency
is exactly the failure mode Rule 10 (above) exists to close.

**6 — Terminology mixups, symmetrically.** PO: "Call me (PO) out when I
make a terminology mixup. Ours is a product laden with potential for
confusion over terminology." Added to `TEAM_OPERATING_SYSTEM.md`'s
Terminology note: PM/Code flag a mixup the moment it appears, including
the PO's own (e.g. "close the sprint" for "close the Iteration," this
same conversation) -- not just correct other parties' slips.

**7 — Velocity, visualized:**

```
Velocity -- PBIs Done per Iteration (specification/BACKLOG.md, verified count)

Iteration 1 (Aug 22) |                        0
Iteration 2 (Aug 23) |######                  2
Iteration 3 (Aug 24) |###################     7
Iteration 4 (Aug 25) |######                  2
                      +--+--+--+--+--+--+--+--+
                      0  1  2  3  4  5  6  7  8
```

Caveat, per this team's own "no inflated numbers" standard (Iteration 3
retro): Iteration 3's "7" bundles PBI 2.0b/c/d -- three mechanical outputs
from a single PO ruling made in one exchange -- alongside Issue #8, PBI
2.0a, PBI 2.1, and the Xray Issue #9 fix. Iteration 4's "2" required more
rigor per item (a real generated CSV, a bug caught by reading actual rows
and fixed with regression tests, stale-doc correction). Raw PBI count is
not an apples-to-apples throughput measure across Iterations -- read as a
rough shape (Iteration 1's honest zero, a big Iteration 3, a smaller but
more rigor-heavy Iteration 4), not a precise rate.

**Status:** Iteration 4 retro closed. Two Governance Rules added (9, 10),
one amended (7), one terminology-symmetry instruction added to
`TEAM_OPERATING_SYSTEM.md`, one item explicitly closed with no change,
one velocity chart produced. All logged in `DEFINITION_OF_DONE.md`'s and
`TEAM_OPERATING_SYSTEM.md`'s own Session Log tables per their respective
change-approval rules.
