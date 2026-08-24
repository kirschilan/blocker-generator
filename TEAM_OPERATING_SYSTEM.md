# Team Operating System — Communication & Collaboration

**Status:** Operational agreement  
**Audience:** PM, Code, Product Owner (PO)  
**Purpose:** How we stay synchronized across devices, platforms, and time zones; where work lives; how decisions flow

---

## Principle

One source of truth, lightweight communication, asynchronous-first (you're on iPad, Mac, iPhone, PC—work wherever you are without waiting).

**Terminology:** "Iteration" is our own one-day delivery timebox (PO/PM/Code). "Sprint" is reserved for the synthetic dataset's own domain concept — the fictional squads' 12-sprint quarter (see `specification/ARCHITECTURE.md`). Don't conflate the two.

---

## Source of Truth: GitHub

**All artifacts live here:**
- DEFINITION_OF_DONE.md
- PROJECT.md
- BACKLOG.md
- ARCHITECTURE.md
- TESTER.md
- Generated data files (CSVs for each iteration)
- Code (generate_blocker_data.py, tests)
- Session logs (session_log.md in root)

**Repository structure:**
```
blocker-generator/
├── DEFINITION_OF_DONE.md
├── PROJECT.md
├── BACKLOG.md
├── ARCHITECTURE.md
├── TESTER.md
├── TEAM_OPERATING_SYSTEM.md (this file)
├── session_log.md (append-only; updated at end of each session)
├── src/
│   └── generate_blocker_data.py
├── tests/
│   └── test_blocker_generator.py
├── data/
│   ├── v1_auth_cluster_high_density.csv
│   ├── v1_auth_cluster_test_logs.csv
│   └── ...
├── docs/
│   └── VALIDATION_REPORT_Milestone_1.md
└── README.md
```

**Why GitHub?**
- Version-controlled (you can see what changed, when, by whom)
- Works on all devices (web + git CLI + GitHub mobile app)
- Pull Requests = async code review (PM + PO can review Code's work without real-time meeting)
- Issues = async decision discussion (link to relevant artifacts, no Slack thread history to dig through)
- One truth (not scattered across Slack, email, docs in different clouds)

---

## Communication Channels

### **For Formal Work (Artifacts, Code, Decisions)**
→ **GitHub** (PRs, Issues, commits)

**Workflow:**
1. Code finishes a task → creates Pull Request → links to BACKLOG.md task
2. PR includes: what changed, why, test results, any blockers
3. PM reviews (spot-checks TESTER.md criteria)
4. PO reviews (comments if data matches expectations)
5. PM merges when all approve (or requests changes with feedback)

**Traceability:** Every commit message references the task (e.g., "Task 1.4: Generate features w/ clusters (PR #42)")

---

### **For Real-Time Questions / Blockers**
→ **Slack** (or similar chat; example: "Code: Can you clarify what 'cascade lag' means in ARCHITECTURE.md?")

**Rule:** Slack is for quick clarification, not decisions. Decision outcomes are captured in GitHub (issue comment or PR description).

**Async-friendly:** Don't wait for Slack replies. If question is blocking:
1. Post in Slack (for visibility)
2. Also open GitHub Issue (for record)
3. Continue with best guess; PM + PO will review in GitHub

---

### **For Iteration Kickoff / Sign-Off Gates**
→ **Two short synchronous touchpoints per day** (see Daily Iteration Cadence below)

**Agenda:**
- Iteration kickoff: "Here's what's realistic to reach Done-Done today (BACKLOG); any questions?" (5 min)
- Iteration sign-off: "Here's the data; does it match expectations?" (20 min)
- Blockers / scope changes (if any) (5 min)

**Recording:** PM writes summary in GitHub Issue immediately after (e.g., "Milestone 1 Sign-Off: PO confirmed Auth-cluster cascade matches expectations. Approved to proceed to Milestone 2.")

---

## Session Log: Append-Only Record

**File:** `session_log.md` (in root of repo)

**Updated at end of each work session (before closing this conversation or committing):**

```markdown
# Session Log

## Session: Aug 22, 2026 — PM + Code + PO alignment on DoD

**Date:** 2026-08-22  
**Participants:** Kirschi (PO), PM (Claude), Code (pending Claude Code)  
**Outcome:** Five locked docs (PROJECT, BACKLOG, ARCHITECTURE, TESTER, DEFINITION_OF_DONE); ready for Milestone 1 build

**Decisions Made:**
- GitHub as source of truth; Slack for real-time questions
- Tester.md is shared agreement on verification; execution is collaborative (Code automates, PM spot-checks, PO signs off)
- Decision rights matrix defined in DEFINITION_OF_DONE.md
- Scope change workflow: diagnose → update artifact → session log → confirm all three

**Blockers:** None  
**Next:** Code begins Milestone 1 (Tasks 1.1–1.6)

---

## Session: [Next Date] — Milestone 1 Kickoff

[to be filled in when Code starts]
```

**Why?**
- Asynchronous visibility (PO on iPad can see "where are we?" without asking)
- Traceability (future sessions can replay decisions)
- One artifact per audience (not scattered notes in Slack)

---

## GitHub Workflow (for Code + PM)

### **Code Creates a Task Branch**

```bash
git checkout -b task/1.1-squad-model
# Implements Task 1.1
# Commits with clear messages:
#   "Task 1.1: Create Squad dataclass with adjacency matrix"
#   "Task 1.1: Add JSON serialization for squad config"
```

**Branch lifetime (trunk-based development; see `DEFINITION_OF_DONE.md` Governance Rule 7, and `CLAUDE.md`):** one branch per task, merged or deleted before the session that created it ends. If the task isn't finished, land what's safe on `main` behind a clear "incomplete" marker and continue next session — don't hold the branch open.

### **Code Opens Pull Request**

```
Title: Task 1.1 – Build Squad & Interdependency Data Model

Description:
- Implements Task 1.1 from BACKLOG.md
- Squad dataclass: id, name, domain, depends_on, owns_component
- Adjacency matrix printed for manual verification
- JSON schema for squad config (reusable post-V1)
- All automated checks pass (see TESTER.md)

Checklist:
- [ ] Follows ARCHITECTURE.md squad topology
- [ ] JSON serializable
- [ ] No hardcoded values (config-driven)
- [ ] Tests pass

Blockers / Questions:
- None
```

### **PM Reviews**

- Checks: Does output match Task 1.1 acceptance criteria (BACKLOG.md)?
- Spot-checks: Does adjacency matrix match ARCHITECTURE.md?
- Approves or requests changes

### **PO Optional Review**

- PO doesn't need to review every PR (that's Code + PM's domain)
- PO reviews only when asked or at sign-off gate (after all Milestone 1 tasks are merged)

---

## Tester.md: Agreement, Not a Role

**Important clarification:** There is **no "Tester" persona** on the team. TESTER.md is a **shared agreement on verification responsibilities.**

### **Who Does What?**

| Responsibility | Owner | How |
|---|---|---|
| **Automated checks** | Code | Implement in test suite (pytest, etc.); run before PR |
| **Manual spot-checks** | PM | Load CSVs, spot-check 5 features, verify dates/times |
| **Narrative validation** | PO | Load into viz tool; "Does this match our org?" |
| **Acceptance criteria** | All three | Agreed in TESTER.md before iteration starts |

### **Example: Task 1.4 (Generate Features + Blockers)**

**Code's responsibility (automated):**
```python
def test_blocker_density():
    data = generate_high_density_dataset()
    density = count_blockers(data) / count_features(data)
    assert 0.20 <= density <= 0.30, f"Density {density} not in 20–30%"

def test_cascade_timing():
    data = generate_high_density_dataset()
    auth_blocker = find_blocker(data, "Auth", week=3)
    checkout_blocker = find_blocker(data, "Checkout", week=3)
    assert checkout_blocker.created >= auth_blocker.created + timedelta(days=1)
```

**PM's responsibility (manual):**
1. Load CSV into Pandas
2. Filter to Auth blockers in week 3 (should be 3–5)
3. Filter to Checkout blockers in week 3 (should be 2–3)
4. Verify Checkout blocker dates are 1 day after Auth blocker dates
5. Sample 5 features; check cycle times are 2–14 days (realistic)
6. Record findings: "Spot-checks passed" or "Found issue: [specific example]"

**PO's responsibility (narrative):**
1. Receive CSV + validation report from PM
2. Load into Tableau/Grafana
3. Look at 12-week timeline; filter by "Waiting" status
4. Ask: "Do I recognize this Auth-cluster pattern? Do waiting reasons make sense?"
5. Sign off: "Yes, I recognize this pattern" or "No, something doesn't match reality"

### **It's Collaborative Verification**

```
Code writes automated checks (fast, deterministic)
   ↓
Code runs tests before PR; if fail, Code debugs
   ↓
PM reviews PR + runs manual spot-checks (samples, not exhaustive)
   ↓
Code + PM agree: "Data looks good"
   ↓
PO loads data into viz tool + validates narrative
   ↓
PO signs off: "This matches our org" or escalates to PM
```

**No separate "Tester" person.** The three of you verify together, with clear responsibilities.

---

## Scope Change Process (How It Works In Practice)

### **Scenario: Mid-Iteration, Code Discovers Task Is Too Large**

**Day 1, Thursday:**
1. Code: Opens GitHub Issue titled "Task 1.4 is too large; branching logic needs splitting"
2. Code: Posts in Slack: "Opened #42; needs PM review"
3. PM: Reviews Issue; roots cause
4. PM: Comments in Issue: "Proposal: split into 1.4a (generate features) + 1.4b (inject cascades). Still depends on 1.1–1.3; both complete in parallel. Updates BACKLOG.md with new task breakdown."

**Day 2, Friday:**
1. PO: Sees Issue comment; reviews proposed split
2. PO: Comments: "Split makes sense; no scope change. Approved."
3. PM: Updates BACKLOG.md (adds Task 1.4a, 1.4b; updates session log)
4. Code: Commits backlog change; creates two PRs instead of one

**Record:** GitHub Issue #42 + BACKLOG.md commit + session_log.md entry

---

## Devices & Platforms: How It Works

**You (PO) on iPad:**
- Open GitHub in Safari
- Read PROJECT.md, BACKLOG.md, latest session_log.md
- Review Code's PR (see diffs, leave comments)
- Get Slack notification for quick sync ("Code pushed PR #47")
- All synced across your devices (GitHub web remembers where you left off)

**Later, on Mac:**
- `git pull` to get latest artifacts
- Read ARCHITECTURE.md in local editor
- Write feedback doc for PM
- Commit changes to session_log.md

**Later, on iPhone:**
- GitHub app: check PR status, see if PM needs your sign-off
- Slack: reply to quick question

**No re-downloading, no cloud sync delays, no "which version is current?"** GitHub is the source of truth.

---

## Daily Iteration Cadence

**Our delivery timebox is one day** (an "Iteration" — see Terminology, above), adopted 2026-08-23 so PO, PM, and Code learn actual mutual throughput before committing to larger scope. Iterations replace the earlier weekly cadence; nothing else about decision rights or verification changes.

**Start of day (10–15 min):** Iteration Kickoff
- PM proposes today's slice from BACKLOG.md, sized to what can realistically reach Done-Done today — not what's left on the list
- Code: flags anything blocking before starting
- PO: anything to know for today's narrative validation?

**End of day (20–30 min):** Iteration Sign-Off
- PM: "Here's what shipped today (CSVs + validation report)"
- PO: "Does it match expectations?" — sign-off or escalate
- Code + PM: carry anything unfinished into tomorrow's kickoff — never onto an open branch (see Governance Rule 7, trunk-based development)

**After sign-off (added 2026-08-23, effective Iteration 4):** Backlog Refinement (PBR)
- PM researches/scopes candidate PBIs for a future Iteration (e.g., "what does a real Jira export actually look like") and adds them to the Product Backlog (`BACKLOG.md`)
- This happens *after* the planning conversation closes for the day, not folded into Kickoff — Kickoff is for deciding what today's Iteration pulls from the *existing* Product Backlog, not for generating new candidates on the spot
- Output: new/updated Product Backlog entries, ready for tomorrow's Kickoff to consider — not yet committed to any Iteration

**Async within the day:**
- Code: commits + PRs (PM reviews async)
- PM: session_log.md updated at end of day
- PO: spot-checks any queries in Slack / GitHub

**No mid-day standup.** Trust async workflow within the day; the two synchronous touchpoints are kickoff and sign-off.

---

## Decision Authority in GitHub

**When to use Pull Requests (async, no-rush):**
- Code changes to generate_blocker_data.py
- Updates to ARCHITECTURE.md (when diagram needs clarification)
- Example CSVs committed for reference

**When to use GitHub Issues (discussion, recorded decision):**
- Scope change discussion (Code: "Task too large"; PM + PO: "Agree, split into X + Y")
- Architecture assumption changes (PO: "We learned DataPlatform is weekly, not annual")
- Blocker escalation (Code: "Can't implement without clarifying what 'cascade lag' means")

**When to use Slack (quick, real-time):**
- Questions that resolve in 5 minutes (Code: "Is 'cascade lag' = 1 calendar day or 1 business day?")
- FYI ("I'm about to push Task 1.4; expect PR in 10 min")
- Scheduling ("Can we move sign-off call to Thursday instead?")

**When to use Video Call (30 min, formal):**
- Iteration kickoff (ensure everyone understands what's being built)
- Iteration sign-off (PO validates narrative; decision gate to proceed)
- Escalated disagreements (if GitHub Issue discussion reaches an impasse)

---

## Session Log Template

**Add to `session_log.md` at end of each session:**

```markdown
## Session: [Date] — [Title]

**Date:** [ISO-8601]  
**Participants:** [list]  
**Duration:** [minutes]  
**Mode:** [Async GitHub + Slack | Video call | Code pair-programming]

**Work Completed:**
- Task X.Y: [brief description of what was done]
- Artifact updates: [list of files changed, with commit links]

**Decisions Made:**
- Decision 1: [what was decided, why, who approved]
- Decision 2: [...]

**Scope Changes:**
- Change 1: [what changed, impact on BACKLOG/ARCHITECTURE/TESTER]
- Change 2: [...]

**Blockers / Open Items:**
- Blocker 1: [what's blocked, who's unblocking, ETA]
- Open item 1: [decision pending, who decides, deadline]

**Next Session:**
- [Date if scheduled; or "async until [trigger]"]
- [What to prepare]

**Approvals / Sign-Offs:**
- [ ] PM: Session log reviewed
- [ ] PO: Iteration work acknowledged
- [ ] Code: Ready for next task (if applicable)
```

---

## Backup / Archival

**GitHub is version-controlled, so history is built-in.**

At end of each iteration, PM creates:
- `docs/VALIDATION_REPORT_Iteration_N.md` (auto-generated summary of what passed, what was validated)
- `data/iteration_N_artifacts/` (CSVs, test logs, generated data)

Everything is in git; no risk of losing work.

---

## Session Log (This Document)

| Date | Session | Participants | Key Decisions |
|------|---------|--------------|---------------|
| 2026-08-22 | PM Alignment on DoD | Kirschi (BP), PM, (Code pending) | GitHub as source of truth; Tester.md is shared agreement (not a role); three-party verification (Code automated, PM manual, BP narrative) |
| 2026-08-23 | Iteration 1 Retro | Kirschi (BP), PM, Code | Weekly cadence replaced with one-day Iterations (calibrate throughput before committing scope); "Sprint" renamed to "Iteration" for our own cadence; trunk-based development adopted (branch per task, merged before session ends); `CLAUDE.md` created to enforce branching without duplicating `/specification/` |

