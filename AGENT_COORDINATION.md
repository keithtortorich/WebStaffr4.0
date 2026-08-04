# AGENT_COORDINATION.md : Multiple Agents, One Working Tree

**Status:** Active rule, effective 2026-08-04. Binding on every AI agent working in this
repository -- Claude, Codex, Hermes, and any other tool added later.
**Why this file exists:** Claude and Codex were both found editing and committing to
`/Users/doc/Desktop/WebStaffr4` at the same time, with no coordination. See TASKS.md's
"Concurrent Agents On One Working Tree" entry (2026-08-04) for the incident log. This file
is the fix. Read it at the start of every session in this repo, before touching git.

---

## The problem, plainly

This repo has one working tree on disk. It does not have one writer. Right now it has at
least two -- Claude and Codex -- and Hermes may run here too. None of them can see what the
others are doing mid-edit. Git does not protect you from this the way you'd expect:

- **A destructive command silently discards the other agent's uncommitted work.**
  `git checkout`, `git restore`, `git stash`, `git reset --hard` all operate on the working
  tree as it exists at that instant. If another agent has an edit in flight that isn't
  committed yet, one of these commands erases it with no warning and no undo.
- **`git add -A` sweeps up whatever the other agent left lying around.** A commit meant to
  ship one feature can end up containing an unrelated agent's half-finished edit, or its
  scratch files, because `-A` doesn't ask.
- **Tests run against a moving target.** If Agent A runs the test suite while Agent B is
  mid-edit on a file A's tests exercise, A's result is meaningless -- pass or fail.
- **Commit messages stop being trustworthy.** This already happened once: a commit titled
  "Revise completion plan with tooling-adjusted estimates" actually contained 295 files and
  139,000 insertions of an unrelated vendored toolchain install, because the message was
  written by one agent and the `git commit` picked up the whole tree, including another
  agent's unrelated uncommitted work.

None of this is a tooling bug. It's what happens when two independent actors share one
mutable directory with no lock and no lane.

---

## The rule (binding on every agent, every session)

### 1. Announce before you start

At the start of any session that will touch this repo, run `git status --short` and
`git log --oneline -3` **before doing anything else.** If either shows changes you didn't
make, another agent is active or was active recently. Slow down.

### 2. Stage only what you wrote

**Never run `git add -A` or `git add .` in this repo.** Stage files by exact path, only
the ones you changed for the task you were given. If `git status` shows files you don't
recognize, leave them alone -- they belong to someone else's in-flight work, not yours to
commit, rename, or delete.

### 3. Write commit messages that match commit contents

Before running `git commit`, run `git diff --cached --stat` and read it. If it lists a
file you don't remember touching, stop and unstage it (`git restore --staged <path>`)
rather than commit it under a message that doesn't describe it. A commit message is a
claim about what changed; make sure it's true.

### 4. Never run a destructive git command without checking the tree is idle first

`git checkout -- <path>`, `git restore`, `git stash`, `git reset --hard`, `git clean -fd`:
all of these can erase another agent's uncommitted work with zero recovery path. Before
running any of them:

- Check `git status --short` for changes you don't recognize.
- If you see any, do not proceed. Commit or explicitly flag what's there first, or ask
  the founder which agent's work takes priority.
- When in doubt, prefer `git stash` over `git reset --hard` if you must clear your own
  tree -- it's recoverable. `reset --hard` is not.

### 5. Treat `.git/index.lock` as a signal, not an obstacle

If a git command fails with `Unable to create '.../.git/index.lock': File exists`, that
almost always means another agent's git process is mid-operation right now, not that a
process crashed. Do not delete the lock file reflexively. Wait a few seconds and retry
first. If it persists past a minute or two, then check for a genuinely stuck process
before removing the lock.

### 6. Never delete or overwrite a file you didn't create, without asking

If you find a file that looks like a duplicate, a stray artifact, or "obviously" wrong
(a second copy of a plan, a leftover scratch file), do not delete it unilaterally even if
you're confident. Another agent may be actively using it. Flag it to the founder in your
response and let a human make the call, or leave a note in TASKS.md and move on.

### 7. Read TASKS.md's active-hazard log before assuming the tree is calm

If TASKS.md has an open "Concurrent Agents" entry (or whatever it's renamed to), treat
every session as shared until that entry is closed. Don't assume you're the only agent
just because your own session doesn't show one running.

---

## What good coordination looks like, concretely

**Before:**
```
git add -A
git commit -m "fix stuff"
```
Sweeps the whole tree, including anything another agent left uncommitted. Message says
nothing verifiable.

**After:**
```
git status --short                       # see what's actually changed, and by whom
git diff --stat webstaffr/site_schema.py # confirm scope of your own edit
git add webstaffr/site_schema.py tests/test_site_schema.py
git diff --cached --stat                 # confirm staged set matches intent
git commit -m "fix: site_schema handles missing optional fields"
```
Stages exactly what was worked on, verifies before committing, message is checkable
against the diff.

---

## Escalation: if lanes keep colliding

The rule above (stage precisely, verify before destructive ops, don't assume an idle
tree) is the first line of defense and should be sufficient for most sessions. If
collisions keep happening despite it -- lost work, more stray files, more mismatched
commit messages -- the next step up is **`git worktree`**: one checkout per agent
(`../WebStaffr4-claude`, `../WebStaffr4-codex`), each with its own working directory,
merging through branches instead of sharing one tree.

That is **not adopted yet**. A second full checkout of this repo on the same machine
risks recreating the WS3.3-vs-WS4.0 confusion this project already paid for once (see
`docs/DECISIONS.md` ADR-019) -- multiple directories claiming to be "the repo," with no
guarantee every agent reads from the one that's actually current. If it comes to that,
it needs a founder decision on directory naming and which one is canonical, not a
unilateral setup by whichever agent hits the problem first.

---

## For the founder

You don't need to referee this day to day. Each agent reading this file is supposed to
self-govern: check before acting, stage narrowly, verify before anything destructive,
flag rather than silently resolve anything ambiguous. Your involvement is needed only if:

- Lost work actually occurs despite the rule (escalation trigger above).
- Two agents genuinely need to work the *same* file at the *same* time on purpose (rare;
  usually a sign the work should be split differently).
- The `git worktree` escalation gets proposed and needs a yes/no plus a naming call.
