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

- One branch per task, not per Iteration and not per session.
- Merge it (or delete it, if abandoned) before this session ends. Nothing
  survives unmerged into the next session.
- Task not finished? Land what's safe on `main` behind a clear "incomplete"
  marker (a skipped test, a TODO tied to the BACKLOG task ID) and continue
  next session — don't park it on an island branch.

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
