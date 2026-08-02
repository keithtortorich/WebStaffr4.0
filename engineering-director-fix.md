# Engineering Director Skill — Repo Verification Fix

**Issue:** Lines 143-144 are stale. Says "As of 2026-07-28, only WS3.3 was cloned locally" but WS4.0 is now production.

**Current text (WRONG):**
```
**At session start, verify which repo is on disk.** Don't assume. Run: `ls /Users/doc/ws33-repo` 
(the stale WS3.3 line) and check GitHub. As of 2026-07-28, only WS3.3 was cloned locally.
```

**Corrected text:**
```
**At session start, verify which repo is on disk.** Don't assume. WS4.0 is production 
(`/Users/doc/Desktop/WebStaffr4`, `github.com/keithtortorich/WebStaffr4.0`). WS3.3 
(`/Users/doc/ws33-repo`, GitHub archive) is stale. Confirm the working directory before building. 
Code on the wrong repo doesn't ship.
```

**Why:**
- WS4.0 moved into production 2026-07-27 (see TASKS.md)
- CLAUDE.md at repo root confirms WS4.0 is canonical
- Site renderer, health check, and all MVP work is in WS4.0
- Stale instruction wastes session time on unnecessary verification

**Additional fix needed (read-only in skill, document for manual update):**

**Line 107** — Remove Lovable from MCP list or clarify it's dead:
- Current: "Supabase... Vercel... GitHub, Netlify, Lovable, Drive..."
- Fix: Remove Lovable OR add note: "Lovable is dead (Site Weaver fallback only, per TASKS.md 2026-08-02). Site renderer (in-repo) is canonical."

**Line 82-87 — Add antipattern for WebStaffr-specific dead-ends:**
- Add: `- ❌ "Which Lovable project should I update?" → ✅ "Lovable is dead per TASKS.md. Site renderer is canonical. Landing page in landing_router.py; updating now."`
