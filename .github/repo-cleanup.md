# Repository Cleanup Plan

**Date:** August 7, 2026  
**Status:** Action Required

## Summary

This repo has accumulated branch and PR clutter. This document tracks cleanup decisions.

---

## Pull Requests — Actions Required

### Merge These PRs
✅ **Do merge these — they're ready and safe**

- **PR #11: Install Vercel Speed Insights**
  - Status: Draft
  - Change: Adds performance monitoring to 4 HTML templates
  - Action: Review, mark ready for review, then merge
  - Safety: Low risk, well-documented

- **PR #9: build(deps): bump fastapi from 0.140.0 to 0.141.1**
  - Status: Open (5 days old)
  - Change: Patch update with bug fixes
  - Action: Merge directly (Dependabot PR)
  - Safety: Low risk, patch-level only

- **PR #4: Bump pydantic-core from 2.46.4 to 2.47.0**
  - Status: Open (11 days old)
  - Change: Dependency patch update
  - Action: Merge directly (Dependabot PR)
  - Safety: Low risk, patch-level only

### Close These PRs
❌ **Do NOT merge these — close them**

- **PR #8: build(deps): bump uvicorn from 0.51.0 to 0.52.0**
  - Status: Open (5 days old)
  - Issue: Contains experimental zttp HTTP/1.1 implementation (not production-ready)
  - Action: Close with comment explaining decision to skip experimental features
  - Reason: Experimental code should not go to production without explicit testing

---

## Branches to Delete

**These feature branches should be deleted** (no associated open PRs):

```
claude/product-docs
codex/mvp-activation
codex/security-foundation
hermes/operations
```

**Also delete Dependabot branches after merging/closing their PRs:**

```
dependabot/pip/fastapi-0.141.1          (delete after PR #9 merge)
dependabot/pip/pydantic-core-2.47.0     (delete after PR #4 merge)
dependabot/pip/uvicorn-0.52.0           (delete after PR #8 close)
vercel/install-vercel-speed-insights-*  (delete after PR #11 merge)
```

---

## Dependabot Configuration

**Current State:** Dependabot is enabled and creating PRs for all Python dependency updates.

**Recommendation:** 
- Keep Dependabot enabled but **batch weekly reviews** on Mondays
- Create a **scheduled workflow** to remind you to review & merge/close PRs
- Set a rule: **All Dependabot PRs must be acted on within 7 days** (merge or explicitly close)

---

## How to Execute

### Step 1: Review & Merge Safe PRs
1. Go to PR #11 → Mark as ready for review → Merge
2. Go to PR #9 → Merge (or use `@dependabot squash and merge`)
3. Go to PR #4 → Merge (or use `@dependabot squash and merge`)

### Step 2: Close the Experimental PR
1. Go to PR #8
2. Close with comment:
   ```
   Closing as the uvicorn 0.52.0 update includes experimental zttp HTTP/1.1 
   implementation. We'll revisit once it's stable. Consider this in future updates.
   ```

### Step 3: Delete Stale Branches
```bash
git push origin --delete claude/product-docs
git push origin --delete codex/mvp-activation
git push origin --delete codex/security-foundation
git push origin --delete hermes/operations
```

### Step 4: Clean Up Dependabot Branches
After each PR is merged/closed, delete its branch via GitHub UI or CLI.

### Step 5: Document Dependabot Policy (Optional)
Create `.github/dependabot.yml` with a weekly schedule and group updates by type.

---

## Result After Cleanup

✅ Zero open, unreviewed PRs  
✅ Only `main` + active feature branches  
✅ Cleaner git history  
✅ Clear policy for dependency updates  

---

## Next Time

- **Set Dependabot alerts:** Review weekly (Mondays)
- **Merge policy:** All Dependabot PRs within 7 days
- **Branch naming:** Delete after merge (automatic in most cases)
- **Protected branches:** Use only for `main` and production releases
