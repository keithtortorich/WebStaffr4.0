---
description: Send a task to Codex or Hermes via agent_broker.py handoff.
---

Delegate a task via the broker. Broker path:
`/Users/doc/Desktop/WebStaffr4-coordination/scripts/agent_broker.py`

1. Parse the request: `$ARGUMENTS$`
2. Pick target agent:
   - `codex` — bulk code generation, unit tests, refactoring, execution
   - `hermes` — webhooks, MCP tool calling, live integration validation
3. Write a one-line subject and a message body containing: clear instructions,
   relevant file paths, and (if applicable) a verification command the target
   agent should run before reporting done.
4. Run:

```bash
python /Users/doc/Desktop/WebStaffr4-coordination/scripts/agent_broker.py handoff \
  --from-agent claude \
  --to-agent <codex|hermes> \
  --subject "<short task slug>" \
  --message "<instructions + context files + verification command>" \
  --priority normal
```

This is a `handoff`, not a task-queue entry — the broker has no `dispatch`
subcommand and no `--task-id` flag. If the target agent needs to claim
write-access to specific files before starting, that's their call to make with
`guard --action write`, not something this command sets up on their behalf.

Output only the broker command's result. No narration.
