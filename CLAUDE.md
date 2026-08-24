# CLAUDE.md — Working Agreement for This Repo

Entry point for any Claude Code session (Code role) in `blocker-generator`.
This file does not restate policy that already lives elsewhere — it points
to the source and adds only what a fresh session needs before it touches
anything. If something here ever conflicts with the files it points to,
the pointed-to file wins; fix this file instead of trusting the copy.

## Read first, in this order

1. `TEAM_OPERATING_SYSTEM.md` — how PM/Code/PO communicate, GitHub workflow, cadence
2. `DEFINITION_OF_DONE.md` — decision rights, governance rules, done-done criteria
3. `specification/PROJECT.md`, `specification/ARCHITECTURE.md`,
   `specification/BACKLOG.md`, `specification/TESTER.md` — the single source
   of truth for outcomes, domain model, the active Milestone's tasks, and
   verification. `/specification/` always wins over anything else in the repo.

**If a referenced file is missing, renamed, or contradicts another: stop.**
Do not guess, improvise, or build a substitute. Raise the gap per
`DEFINITION_OF_DONE.md`'s decision-rights rules before writing code — this is
exactly the failure that produced three divergent rewrites of Milestone 1.

## Branching — trunk-based development

Full rule: `DEFINITION_OF_DONE.md` Governance Rule 7. Summary for the moment
you're about to run `git checkout -b`:

- **Check for a designated branch first** (added 2026-08-24, after Code
  pushed to a self-invented branch name mid-Iteration-3 instead of the
  session's actual designated branch, then had to reconcile it after the
  fact). If this session's task instructions name a specific branch, use
  that name — don't invent a new one. Only create a fresh short-lived
  branch name when no designated branch applies.
- One branch per task, not per Iteration and not per session.
- Merge it (or delete it, if abandoned) before this session ends. Nothing
  survives unmerged into the next session.
- Task not finished? Land what's safe on `main` behind a clear "incomplete"
  marker (a skipped test, a TODO tied to the BACKLOG task ID) and continue
  next session — don't park it on an island branch.
- **At the end of work on each PBI** (added 2026-08-24, PO's standing
  request from the Iteration 3 retro) — not just at end-of-session or
  end-of-Iteration — give the PO the list of branches that are now safe to
  delete (merged into `main`, no open PR), so branch cleanup never piles
  up into a separate reconciliation task. Code cannot delete branches
  directly (no delete-branch permission via git push or the GitHub API in
  this environment) — deletion is always the PO's action, on this cadence.

## Repo-wide renames and find/replace

A rename or terminology change across the repo isn't done until verified.
After running any rename script or multi-file find/replace, follow it with
a **case-insensitive** grep across the whole repo (`grep -rni`) before
declaring it complete — an exact-case pass missed lowercase/mixed-case
instances during the Business-Partner-to-Product-Owner rename (Issue #10,
2026-08-24) and needed a second pass to catch them. Exclude `_archive/`
and dated Session Log rows (historical narrative is never rewritten) from
the rename itself, but not from the verification grep — confirm what's
left unchanged is only those two categories, not a missed case.

## Three words, three things — don't conflate them

- **Sprint** — the synthetic dataset's own domain concept
  (`Sprint-1..Sprint-12` in `specification/ARCHITECTURE.md`). Never ours.
- **Iteration** — our one-day delivery timebox (PO/PM/Code). See
  `TEAM_OPERATING_SYSTEM.md`'s Terminology note and Daily Iteration Cadence
  section.
- **Milestone** — a vertical-slice grouping of BACKLOG.md tasks (e.g.
  "Milestone 1: Auth Squad + Auth Cluster"), which can span more than one
  Iteration. Milestone 1 took two Iterations to actually land — don't
  assume a 1:1 mapping between the two.

## Decision rights

Don't re-decide something `DEFINITION_OF_DONE.md` already assigns. Hit a
decision outside Code's authority (see its Governance Rules and Decision
Rights sections) — escalate it, don't default and move on.
