# TEAM_OPERATING_SYSTEM.md

How BP, PM, and Code stay in sync on this repo. Async-first — no
assumption that anyone is online at the same time.

## Roles

- **BP (Business Partner)** — owns the *narrative*: does the generated
  dataset tell a plausible, useful blocker story? Validates against
  `docs/validation_report.md` and the CSVs, not the code.
- **PM (Product/Program)** — owns scope, the backlog, and architecture
  decisions. Runs manual spot-checks on merged output. Diagnoses blockers
  raised by Code and updates `BACKLOG.md` / `ARCHITECTURE.md` accordingly.
- **Code** — implements `BACKLOG.md` against `ARCHITECTURE.md`, ships
  automated tests per `TESTER.md`, opens PRs linked to task numbers.

## Source of truth

Everything that matters is a file in this repo or a GitHub PR/Issue —
never a private message. If a decision isn't written down here, it didn't
happen.

## Communication

- **Pull Requests** — all code changes. Title/description reference the
  `BACKLOG.md` task number(s) and cite the relevant `ARCHITECTURE.md`
  section in commit messages.
- **GitHub Issues** — the only channel for "I'm blocked." Code opens an
  issue instead of guessing or going silent; PM triages and either
  unblocks directly or updates `BACKLOG.md` / `ARCHITECTURE.md` and closes
  the loop on the issue.
- **Slack** — quick questions only. Any answer that changes scope or the
  domain model gets written back into the relevant `.md` file, otherwise
  it's lost.

## Cadence

1. PM keeps `BACKLOG.md` current with the next sprint's vertical slices.
2. Code builds against `ARCHITECTURE.md`, opens PRs per task, and never
   silently expands or shrinks scope (see `DEFINITION_OF_DONE.md`).
3. PM runs the manual spot-checks in `TESTER.md` on the merged output.
4. BP validates the narrative from `docs/validation_report.md` and the
   CSVs in `data/`.
5. Anything blocking any of the above becomes a GitHub Issue immediately,
   not at end of sprint.
