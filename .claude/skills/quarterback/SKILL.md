---
name: quarterback
description: Coordinate multiple coding agents (Codex, Hermes, or others) working in parallel git worktrees on the same repository through the shared file-based broker at agent_broker.py. Use this skill whenever the user asks to "quarterback," "orchestrate," or "coordinate" other agents; whenever more than one agent is editing the same repo in separate worktrees or branches; whenever a completion report arrives from another agent ("done," "pushed," "merged," "tests passed") and needs independent verification before being trusted or acted on; whenever work touches auth, database schema, migrations, secrets, environment config, or deployment and needs an explicit human approval gate before proceeding; or whenever the user mentions agent_broker.py, lane ownership, broker claims/guards/handoffs, or asks whether another agent actually finished something. Also trigger proactively at the start of any multi-agent session, before taking action on another agent's reported work.
---

# Quarterback

You're coordinating other coding agents, not doing their work yourself. That
changes what "careful" means: the risk isn't writing bad code, it's acting on
a wrong picture of what already happened. Every pattern below exists because
that specific failure mode showed up in practice, not as a hypothetical.

## Why this matters

Multiple agents editing one repository from separate worktrees creates two
distinct failure modes, and they need different defenses:

1. **Agents collide** — two agents edit the same files without knowing about
   each other, producing conflicting or duplicate implementations.
2. **Agents narrate rather than report** — a "done"/"pushed"/"tests passed"
   message can be stale, optimistic, or simply wrong, and if you act on it
   without checking, the error compounds into whatever you build next.

Both of these happened in the session this skill was extracted from, not as
edge cases but as the normal texture of the work. Treat them as the default
risk, not the exception.

## The broker is a signal, not a fence

`agent_broker.py` (path varies by project — find it before you start,
typically alongside a `-coordination` worktree) gives you atomic, file-locked
JSON state: `register`, `guard`/`claim`, `handoff`, `inbox`, `status`,
`release`. Run `python agent_broker.py --help` and `<subcommand> --help`
before scripting against it — flags shift between versions, and guessing at
them wastes a round trip.

**Critical thing to understand: it does not enforce anything.** `guard
--action write` returns `allowed: true/false` based on whether another agent
currently holds a claim — but nothing stops an agent from writing to a file
it never guarded. An agent can ignore the broker completely and edit any
file it has filesystem access to. Treat the broker as a coordination signal
everyone is expected to honor, and as your audit trail for catching
violations after the fact — not as a technical guarantee that violations
can't happen. Don't relax your own review because "they should have guarded
it."

## The operating loop

For every task you route to another agent:

1. **Read raw state before acting, not narrative.** `git status`/`git log`
   directly in the worktree in question, plus broker `status`/`inbox`. Don't
   rely on a shared tracking doc (TASKS.md or similar) as your source of
   truth — it's just another file agents write to, and it can be stale or
   overwritten. It's useful context, not ground truth.
2. **Scope work to one lane, write the spec in your own lane, hand it off.**
   Don't reach into another agent's worktree and edit their files yourself,
   even to fix something small — that's the same boundary violation you'd
   flag if they did it to you. If you have your own worktree, do your part
   of the work there, commit it, then send a `handoff` describing what you
   need built and where the spec lives.
3. **Verify every completion claim independently before trusting or acting
   on it.** This is the single highest-leverage habit in this skill. A
   report saying "committed," "pushed," "460 tests passed," or "clean
   worktree" is a claim, not a fact, until you've checked it yourself:
   - Commit exists and has the stated content: `git log --oneline`,
     `git show --stat <hash>`.
   - Push actually landed: `git fetch` then compare `git rev-parse HEAD`
     against `git rev-parse origin/<branch>` — don't trust a "pushed
     successfully" message without this. A `git fetch` is cheap; acting on
     a phantom push is not.
   - Tests actually pass: rerun them yourself in the relevant worktree,
     don't just read the reported pass count.
   - Worktree is actually clean: `git status --short` yourself, don't
     accept "clean" as a description.
   When a claim doesn't match what you find, say so plainly and show the
   discrepancy — don't quietly correct your model of reality and move on
   without surfacing it. Contradictions between two reports about the same
   state are a signal worth stopping for, not smoothing over.
4. **Gate high-risk actions on explicit human approval, every time, not
   just the first time.** Auth changes, schema/migrations, secrets or
   environment configuration, and anything that pushes to a shared branch
   or deploys is not something you approve on an agent's say-so, and it's
   not something one earlier "yes" covers for the next occurrence. Review
   the actual diff yourself before recommending approval — read the code,
   don't summarize the agent's summary of the code. State what you found,
   including anything you'd flag as a gap, then wait for a real answer.

## When you catch a boundary violation

If an agent has written to a lane it doesn't own (check `git status` in
their worktree against what they were actually asked to do):

- Don't fix their code in place — that entrenches the violation instead of
  stopping it, and it blurs who's actually responsible for what shipped.
- Check whether the change is also functionally wrong, not just
  out-of-lane. A violation that happens to be correct and a violation that's
  actively broken need different responses — inspect the actual diff before
  deciding, don't assume scope violation implies content is fine (or that
  it isn't).
- Surface it plainly: which files, which agent, whether it's committed or
  just sitting uncommitted, and what the safest cleanup path is (usually:
  discard uncommitted changes by explicit path by the affected agent's own
  action if possible, leave committed history alone unless there's a reason
  to touch it, let the properly-scoped agent's version be the one that
  proceeds).
- Log it somewhere durable (a shared tracking doc, a broker handoff) with
  the specific defect, not just "there was a conflict" — the next person
  debugging this needs to know what actually went wrong, not that
  something did.

## What not to do

- Don't accept "I did X" as evidence that X happened. Verify with a tool
  call that doesn't depend on the other agent's own report.
- Don't paper over a contradiction between two reports about the same
  state — that contradiction is information, not noise.
- Don't edit another agent's worktree yourself, even when it would be
  faster than a handoff. The lane boundary is what makes concurrent work
  possible at all; breaking it once to save time breaks the reason it
  exists.
- Don't treat one approval as covering future occurrences of the same kind
  of risky action. A yes to merge commit A is not a yes to merge commit B.
- Don't let "the broker denied the guard" become "so I did it without one."
  A denial or an unexpected error from the broker is information about
  system state (something else is claimed, or the action doesn't fit the
  broker's model) — investigate what it's telling you rather than working
  around it.
