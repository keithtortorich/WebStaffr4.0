# Impeccable Phase 1 Bootstrap

Use this to bootstrap a fresh Phase 1 session from the repo.

## One-Command Start

```bash
npx impeccable install
```

## Phase 1 Runbook

1. Confirm repo state
   - `git status --short`
   - `git log --oneline -5`
2. Verify outputs
   - `ls -la docs/IMPECCABLE*`
   - `ls -la outputs/`
3. Run dry-run
   - `npx impeccable plan --dry-run`
4. Validate gates
   - `npx impeccable validate`
5. Preview site render path
   - `python -m uvicorn webstaffr.app:create_app --reload`
   - Open `/sites/{tenant_id}/web`
6. If Safari shows stale content, rename the affected template file and re-render.

## Exit Criteria

- All quality gates pass
- `/sites/{tenant_id}/web` renders without 5xx
- Angel widget is embedded
- No internal-only fields leak in site_data projection
