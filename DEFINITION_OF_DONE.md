# Definition of Done — PM Contract

**Status:** Locked (project governance)  
**Principle:** Marty Cagan (outcome-driven), LeSS (one team, one definition), Melissa Perri (shared mental model), Fowler (trunk-based development)  
**Audience:** PM, Code, Product Owner (all three are one team)

---

## The Contract

This document defines what "done" means at each level of this project, and what happens when scope changes. **It is a working agreement, not a static rulebook.** It evolves only by explicit negotiation between PM, Code, and Product Owner—never silently.

---

## Artifact-Level Definition of Done

### 1. PROJECT.md — "Outcomes and Scope Are Locked"

**This artifact is DONE when:**
- [ ] Outcomes (P1, P2, P3, P4) are stated, prioritized, and measurable (traceable to business hypothesis)
- [ ] Success criteria are explicit (e.g., "Detection = visually identify 3 clusters in synthetic data")
- [ ] Scope is defined: what's IN, what's DELIBERATELY OUT (with triggers for revisit)
- [ ] Product Owner has read it and agrees: "Yes, these are the right outcomes"
- [ ] No outcome can be misinterpreted (e.g., "P2 Actionability" has Metric A and Metric B; not vague)

**Who owns it:** PM  
**When it changes:** Only when business hypothesis, outcomes, or success metrics change (not when implementation details shift). Changes require PM + Product Owner re-negotiation.  
**Impact on Backlog/Tester:** Major changes cascade (backlog tasks may be added/removed; tester sign-off gates may shift)

**Current Status:** DONE (locked Aug 22, 2026)

---

### 2. BACKLOG.md — "Work Is Vertical Slices, Each Independently Valuable"

**This artifact is DONE when:**
- [ ] Work is organized into iterations (not a monolithic task list)
- [ ] Each iteration produces a complete, independently testable deliverable (vertical slice)
- [ ] Each task is INVEST-compliant: Independent, Negotiable, Valuable, Estimable, Small, Testable
- [ ] No task is blocked by a later task (precedence is clear; parallelizable where possible)
- [ ] Acceptance criteria are concrete and testable (not "build a feature"; "generate 600–750 rows with blocker density 20–30%")
- [ ] Post-MVP items are explicitly deferred with triggers (not silently dropped)
- [ ] Product Owner has read it and agrees: "This breakdown makes sense; I can validate each iteration"

**Who owns it:** PM  
**When it changes:** When scope changes (outcomes shift, or implementation strategy evolves). Changes are triggered by:
  - **Code discovers a task is too large:** PM breaks it down (backlog updated before iteration runs)
  - **Product Owner requests new feature:** PM assesses against outcomes, re-prioritizes, updates backlog
  - **New dependency discovered:** PM updates precedence and task order
  - Changes require PM re-assessment and Product Owner acknowledgment (not silent)

**Impact on Tester:** Task-level changes affect TESTER.md acceptance criteria (if backlog task size changes, verification scope changes)

**Current Status:** DONE (locked Aug 22, 2026; vertical slices enforced)

---

### 3. ARCHITECTURE.md — "Data Model Is Unambiguous and Implementable"

**This artifact is DONE when:**
- [ ] Squad topology is defined: all 8 squads, all dependencies, all external systems
- [ ] Blocker archetypes are specified: 6 types, durations, propagation rules
- [ ] 3 blocker clusters are defined: exact weeks, affected squads, cascade timing, root causes
- [ ] CSV schemas are unambiguous (columns, types, examples, rules for each cell)
- [ ] Code can implement without asking "what does this mean?"
- [ ] All examples are realistic (not obviously fake; finance domain-authentic)
- [ ] Product Owner has read it and agrees: "Yes, this topology matches our organization"

**Who owns it:** PM  
**When it changes:** Only when understood domain assumptions change (new squad, new external dependency, new blocker type). Changes require:
  - Root-cause diagnosis (why does domain understanding need to shift?)
  - PM + Product Owner negotiation (impact assessment)
  - Backlog update (if architecture changes, implementation tasks may change)
  - Tester update (if cluster specs change, verification thresholds change)

**Example change scenario (hypothetical):**
- **Current:** CRM is external dependency affecting Auth, Checkout, Invoicing
- **Change request:** "CRM is now in-scope; we own it"
- **Response:** 
  1. PM diagnoses: "If we own CRM, blocker durations drop from 2–5 days to <1 day"
  2. PM assesses impact: "This affects Cluster scenarios; Metric B (mocking) changes"
  3. PM + Product Owner decide: "This changes our Actionability story; worth 1–2 tasks in Milestone 2"
  4. PM updates ARCHITECTURE.md (CRM no longer external)
  5. PM updates BACKLOG.md (new task: "reduce Cluster 2 blocker durations")
  6. PM updates TESTER.md (sign-off gate for updated cluster specs)

**Current Status:** DONE (locked Aug 22, 2026; all domains and clusters defined)

---

### 4. TESTER.md — "Verification Is Reproducible and Unambiguous"

**This artifact is DONE when:**
- [ ] Automated checks are written (code can run them; pass/fail is binary)
- [ ] Manual spot-checks are defined (PM knows exactly what to verify; ~10–20 min per iteration)
- [ ] Product Owner sign-off criteria are explicit (what must partner confirm before gate opens?)
- [ ] Acceptance thresholds are quantified (not "blocker density should be high"; "20–30%")
- [ ] Each milestone has its own TESTER section (Milestone 1 ≠ Milestone 2; verification scope evolves)

**Who owns it:** PM (with Code input on what's automatable)  
**When it changes:** When tasks or acceptance criteria in BACKLOG.md change. Changes are always:
  - Linked to BACKLOG.md changes (never independent)
  - Documented in TESTER.md session log (traceability)
  - Reviewed by Code (is the new check automatable? Is the new threshold realistic?)

**Example change scenario:**
- **Backlog change:** "Cluster 1 duration reduced from 3 days to 2 days (monitoring added)"
- **Impact on Tester:** 
  - Old check: "Auth blockers in weeks 3–5" → New check: "Auth blockers in weeks 3–4.5"
  - Old threshold: "downstream blockers = 15–20" → New threshold: "downstream blockers = 10–15" (fewer due to faster resolution)
  - TESTER.md updated with new thresholds and timeline

**Current Status:** DONE (locked Aug 22, 2026; three-layer verification defined: automated + manual + sign-off)

---

### 5. Code & Generated Data — "Meets Acceptance Criteria and Passes All Tester Checks"

**This artifact is DONE when:**
- [ ] All automated checks in TESTER.md pass (binary: green/red)
- [ ] All manual spot-checks pass (PM has verified 5–10 samples)
- [ ] Product Owner has signed off (explicit statement required; not just "looks good")
- [ ] Code is committed with clear commit message linking to BACKLOG task
- [ ] Example CSVs are in version control (reproducible; same seed = same data)

**Who owns it:** Code (with PM verification and Product Owner sign-off)  
**When it changes:** When bugs are discovered post-sign-off. Changes require:
  - Root-cause diagnosis (why did verification miss this?)
  - Code fix + re-run all TESTER checks
  - PM re-spot-checks if fix impacts acceptance criteria
  - Product Owner notified (may need re-sign-off if change is significant)

**Current Status:** PENDING (waiting for Claude Code to build Milestone 1)

---

## Decision Rights: How Scope Changes Flow

### Scenario 1: Product Owner Requests New Feature

**Example:** "Can you add scenario data showing incident correlation?"

**Process:**

1. **PM assesses against outcomes:**
   - Is "incident correlation" aligned with P1 (Detection), P2 (Actionability), P3 (Simulation), or P4 (Prediction)?
   - If not aligned: "This is out of scope for the current hypothesis. Worth revisiting post-V1."
   - If aligned: "This could strengthen P2 Actionability. Let's scope it."

2. **If in scope: PM re-scopes:**
   - What's the smallest version? (MVP: link 1 blocker to 1 incident; not all incidents)
   - Does it fit in current iterations, or does it require a new iteration?
   - What's the effort? (Code estimates)
   - Trigger: What outcome makes this worth revisiting post-V1?

3. **PM updates backlog:**
   - Adds task to BACKLOG.md with clear acceptance criteria
   - Updates TESTER.md with new verification checks
   - Adjusts backlog priority and iteration if needed

4. **PM + Product Owner confirm:**
   - "Does this change still meet your definition of success for V1?"
   - If yes: proceed; if no: defer to post-MVP with explicit trigger

**Decision is PM's, but requires Product Owner acknowledgment (not approval; acknowledgment that we're aware of the impact).**

---

### Scenario 2: Code Discovers Task Is Too Large

**Example:** "Task 1.4 says generate 12-sprint features, but the branching logic for cascades is too complex; I need to split this into 2 tasks."

**Process:**

1. **Code brings to PM:** "Here's the blocker and my proposed split."

2. **PM assesses:**
   - Does split violate vertical-slice principle (each iteration independently valuable)?
   - Can the split maintain INVEST? (small, independent, testable)
   - What's the impact on timeline?

3. **PM updates backlog:**
   - Splits task into two (e.g., Task 1.4a: Generate features w/o cascades; Task 1.4b: Inject cascading blockers)
   - Verifies split doesn't break precedence (both tasks still depend on Tasks 1.1–1.3)
   - Updates TESTER.md acceptance criteria for both sub-tasks

4. **PM confirms with Product Owner:**
   - "Implementation strategy changed, but output is the same; no scope change."
   - Product Owner acknowledges; no re-sign-off needed (implementation detail)

**Decision is Code's + PM's (not Product Owner's unless it impacts outcomes).**

---

### Scenario 3: Tester Validation Fails (Product Owner Says "Data Looks Fake")

**Example:** Cycle times show features resolving in 1 day; Product Owner says "Nobody ships features in our org in 1 day."

**Process:**

1. **PM diagnoses root cause:**
   - Is the threshold wrong (data is fine, but acceptance criteria are off)?
   - Or is the data generation wrong (blocker cascade durations are too short)?

2. **PM proposes fix:**
   - If threshold is wrong: update TESTER.md and re-sign-off
   - If data is wrong: task goes back to Code with diagnosis (e.g., "Cluster 1 duration should be 3 days, not 1 day")

3. **Code re-runs:**
   - Fixes architecture (e.g., ARCHITECTURE.md cluster duration updated)
   - Regenerates data
   - Re-runs all TESTER checks
   - If still failing: escalate to PM + Product Owner jointly

4. **If escalation needed:**
   - PM + Product Owner + Code meet to align on what "realistic" means
   - ARCHITECTURE.md is updated with agreed durations
   - Data is regenerated
   - New sign-off

**Decision is PM's + Code's, with Product Owner veto authority (can say "this doesn't match reality").**

---

### Scenario 4: Architecture Assumption Changes Mid-Iteration

**Example:** "We just learned that DataPlatform releases weekly, not annually. How does this affect Cluster 2?"

**Process:**

1. **PM diagnoses impact:**
   - Cluster 2 (weeks 6–10, 5-day duration) assumes annual gate
   - If weekly: blocker duration becomes 1–2 days instead of 5
   - Impact: Blocker density drops; percolation hypothesis weaker

2. **PM brings to team:**
   - "This changes our cluster topology. Resets current iteration; let's reassess."

3. **PM + Product Owner + Code jointly decide:**
   - **Option A:** Adjust cluster to match new reality (weekly gate, shorter duration) → regenerate data, adjust TESTER
   - **Option B:** Keep annual assumption as "what-if" scenario (for demo purposes) → add note to ARCHITECTURE.md
   - **Option C:** Make two datasets (one annual, one weekly) → adds complexity

4. **Update artifacts:**
   - ARCHITECTURE.md updated with agreed assumption
   - BACKLOG.md adjusted if scope shifts (additional scenarios, etc.)
   - TESTER.md updated with new thresholds
   - Code regenerates data

**Decision is PM + Product Owner (shared; not PM alone).**

---

## Governance Rules (Non-Negotiable)

### 1. No Silent Scope Creep

- **Rule:** Every change to PROJECT.md, BACKLOG.md, or ARCHITECTURE.md must be documented in a session log with date, what changed, and why.
- **Enforcement:** Before closing a session, PM updates artifacts. If change list is empty, state explicitly "No changes; artifacts remain locked."
- **Rationale (pm-playbook):** "The failure mode to actively avoid is two docs both claiming to track 'what's open'—they will drift."

### 2. Changes Require Root-Cause Diagnosis

- **Rule:** Don't change scope because "it would be nice to have." Diagnose why (business need, domain misunderstanding, implementation complexity).
- **Enforcement:** PM asks "Why?" before updating backlog. If answer is unclear, escalate to Product Owner.
- **Rationale (pm-playbook):** "Find the actual cause before proposing a fix."

### 3. Deferred Items Have Explicit Triggers

- **Rule:** Every item in "Deliberately Not Built Yet" must have a clear trigger (e.g., "Prediction models: revisit when detection is validated on 3+ real client datasets").
- **Enforcement:** If someone asks "should we build X?", PM checks if X is in the deferred list and evaluates trigger. If trigger is met, re-scope; if not, defer again with acknowledgment.
- **Rationale (pm-playbook):** "A running 'deliberately not built yet' list stops the same debate from recurring every session."

### 4. Decision Rights Are Specific

**Role note (per Issue #10, resolved 2026-08-24):** "Product Owner" here is the Scrum/Nexus/LeSS PO — a single role with full backlog ownership (prioritization, acceptance, and domain rulings) — not the SAFe/Scrum@Scale PO, which is narrower and layered under Product Management. Concretely: the PO can *originate* architecture and backlog-structure decisions, not just veto PM/Code proposals. Iteration 3 already worked this way in practice (the PO ruled directly on Cluster Tag → Labels, dropping Cycle Time, folding External Blocker into Waiting Reason, and the Iteration Log / Product Backlog restructuring); this rule catches the table up to that practice.

- **Rule:** Different decisions have different owners:
  - **Outcomes (P1–P4):** PM + Product Owner (joint; veto = project reset)
  - **Backlog prioritization:** Product Owner owns it (PM assesses against outcomes and scopes; Code estimates effort)
  - **Architecture assumptions:** Product Owner can originate a domain ruling directly; PM incorporates it into ARCHITECTURE.md and assesses downstream impact; Code flags implementability concerns before it's locked
  - **Task breakdown:** Code + PM (implementation detail; doesn't require Product Owner sign-off) — distinct from backlog *structure* (e.g., Iteration Log vs. Product Backlog shape), which the PO can direct
  - **Verification thresholds:** PM + Code (must be automatable and defensible; Product Owner sign-off on final data)

**Enforcement:** If someone makes a decision outside their authority, PM flags it. Decisions are documented with owner and date.

### 5. Incomplete States Are Honest

- **Rule:** If an iteration's data is "mostly done" but verification failed, don't hide it. Document explicitly: what passed, what failed, and what's next.
- **Enforcement:** TESTER.md sign-off includes a "blockers" section if anything is incomplete.
- **Rationale (pm-playbook):** "Make incomplete states honest, not hidden."

### 6. One Team, One Definition of Done

- **Rule:** DoD is negotiated once, then held constant. No separate "Code's DoD" vs "PM's DoD" vs "Product Owner's DoD."
- **Enforcement:** This document (DEFINITION_OF_DONE.md) is the contract. Changes require all three parties.
- **Rationale (pm-playbook):** "Treat the team (human + any coding agent involved) as one whole unit with one definition of done."

### 7. Trunk-Based Development (Not Long-Lived Branches)

- **Rule:** One branch per task, not per Iteration and not per session. A branch is merged — or deleted, if abandoned — before the session that created it ends. Nothing survives unmerged into the next session.
- **If a task isn't finished:** land what's safe on `main` behind a clear "incomplete" marker (a skipped test, a TODO tied to the BACKLOG task ID) and continue next session. Don't park it on an island branch.
- **Enforcement:** Encoded in `CLAUDE.md` so it's loaded automatically every session, not left to be discovered in prose.
- **Rationale (Fowler, Trunk-Based Development):** Session-scoped branches with no lifetime limit are what produced three divergent, never-merged rewrites of Milestone 1 (see `session_log.md`, 2026-08-23). A rule stated only in a document that may or may not be read is not a rule; this one is enforced by branch lifetime, not by trust.

---

## How This Document Evolves

**This DEFINITION_OF_DONE.md is DONE now.** But it can change. Changes require:

1. **Trigger:** A recurring misunderstanding (e.g., "We keep debating what 'independent task' means") or a process that broke down (e.g., "Code didn't know who decides this")
2. **Proposal:** PM proposes a clarification or rule update
3. **Discussion:** PM + Code + Product Owner discuss; aim for consensus
4. **Update:** PM updates this document with new rule + rationale + date
5. **Acknowledgment:** All three parties confirm "Yes, this is our new agreement"

**Session Log:**

| Date | Change | Reason | Approver |
|------|--------|--------|----------|
| 2026-08-22 | Created DEFINITION_OF_DONE.md; locked 1-level DoD (artifact + decision rights + governance rules) | Explicit working agreement required; supports Cagan (outcomes-driven), LeSS (one team), Perri (shared mental model) | Kirschi (PO) + PM + Code (pending) |
| 2026-08-23 | Fixed citation spelling (Marty Cagan, Melissa Perri). Added Governance Rule 7 (Trunk-Based Development, Fowler). Renamed our delivery timebox "Sprint" → "Iteration" throughout (kept "Sprint" for the dataset's own domain concept). | Iteration 1 retro surfaced three unmerged, divergent branches — policy without enforcement or a bounded branch lifetime doesn't prevent drift; "Sprint" collided with ARCHITECTURE.md's domain concept | Kirschi (BP) + PM + Code |
| 2026-08-23 | Fixed citation spelling (Marty Cagan, Melissa Perri). Added Governance Rule 7 (Trunk-Based Development). Renamed our delivery timebox "Sprint" → "Iteration" throughout (kept "Sprint" for the dataset's own domain concept). | Iteration 1 retro surfaced three unmerged, divergent branches — policy without enforcement or a bounded branch lifetime doesn't prevent drift; "Sprint" collided with ARCHITECTURE.md's domain concept | Kirschi (BP) + PM + Code |
| 2026-08-24 | Renamed "Business Partner"/"BP" → "Product Owner"/"PO" throughout (dropped the proposed dual BP/PO hat from Issue #10 — simplified to a single PO role). Rewrote Governance Rule 4's Decision Rights table: PO owns backlog prioritization and can originate architecture/backlog-structure rulings, not just veto PM/Code proposals — catching the table up to how Iteration 3 actually ran. Noted this is the Scrum/Nexus/LeSS PO (single, full backlog authority), not the SAFe/Scrum@Scale PO (narrower, team-level). | Issue #10 retro: table under-documented rights already being exercised. Kirschi: "I concur with PO as my role, noting that this is the Scrum, Nexus and LeSS PO, not the SAFe or Scrum@Scale PO. For simplicity, drop the BP definition. PO is easier." | Kirschi (PO) + PM + Code |

---

## Relationship to Other Docs

```
DEFINITION_OF_DONE.md (this document)
  ↓ defines standards for
  ├─ PROJECT.md (outcomes, deliberately-not-done)
  ├─ BACKLOG.md (vertical slices, INVEST)
  ├─ ARCHITECTURE.md (unambiguous domain model)
  └─ TESTER.md (reproducible verification)

When scope changes:
  1. Root-cause diagnosis (pm-playbook: "diagnose before proposing fix")
  2. Update relevant artifact (PROJECT, BACKLOG, ARCHITECTURE, or TESTER)
  3. Session log entry (what changed, why, approver)
  4. Confirm all three parties acknowledge (PM + Code + Product Owner)
```

---

## Reference: Principles Applied

**Marty Cagan (Inspired):**
- Outcomes over features (PROJECT.md defines outcomes, not features)
- Clear vision (ARCHITECTURE.md is unambiguous; no "figure it out" phases)
- Product discovery (DEFINITION_OF_DONE.md treats Code as team, not vendor; feedback loops built in)

**LeSS (Large-Scale Scrum):**
- One team, one definition of done (this document)
- Simplicity (three-layer TESTER, not five; minimal docs, not a forest of specs)
- Emergent design (ARCHITECTURE.md is detailed where needed, sparse where flexible)

**Melissa Perri (Organizational):**
- Shared mental model (explicit working agreements, not assumptions)
- Role clarity (who decides what; GOVERNANCE RULES section)
- Psychological safety (Code can escalate blocker without blame; Product Owner can say "data looks fake" without offending PM)

**Martin Fowler (Trunk-Based Development):**
- Branches are short-lived and integrate to `main` frequently, not held open across sessions (Governance Rule 7)
- Incomplete work is merged behind a marker (skipped test, TODO tied to a task ID) rather than isolated on a branch
- Prevents the divergence that produced three un-reconciled versions of Milestone 1

---

## Who This Is For

- **PM:** Your contract with Code and Product Owner. Refer to this when scope changes or decisions are ambiguous.
- **Code:** Your accountability framework. Know your decision authority; know when to escalate.
- **Product Owner:** Full backlog ownership (Scrum/Nexus/LeSS PO, not the SAFe/Scrum@Scale PO) — you originate architecture and backlog-structure calls, not just veto; you don't need to approve implementation details (task breakdown, task-splitting mechanics).

**One team. One DoD. Clear decisions.**

