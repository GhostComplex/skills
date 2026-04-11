---
name: superqa-isotopes
description: "QA and acceptance testing for Isotopes. Activate when: (1) verifying a PR or feature before merge, (2) doing acceptance review after merge, (3) validating UX/UI changes, (4) running E2E smoke tests, (5) reporting test results to GitHub Issues. Triggers on: 'verify isotopes', 'test isotopes', 'acceptance review', 'check dashboard', 'validate webchat', 'QA isotopes'."
---

# SuperQA for Isotopes

You are the QA engineer for Isotopes. Your job is to verify that features work correctly before and after merge.

## Acceptance Review Process

### 1. Pre-Merge Review (PR stage)
- Read the PR diff
- Run `pnpm typecheck && pnpm test` — all must pass
- Check for regressions in existing functionality
- Verify the change matches the Issue description / design doc

### 2. Post-Merge Acceptance (after deploy)

After merging and restarting Isotopes:

#### A. Functional Verification
```bash
# Build + restart
cd ~/_basement/isotopes && git checkout main && git pull origin main
npm run build
kill $(cat ~/.isotopes/isotopes.pid)
LOG_LEVEL=debug nohup node dist/cli.js > ~/.isotopes/logs/isotopes.log 2>&1 &
echo $! > ~/.isotopes/isotopes.pid
sleep 3 && tail -3 ~/.isotopes/logs/isotopes.log  # confirm startup
```

#### B. UX/UI Verification (for frontend changes)

**When a feature has any visual/UX component (Dashboard, WebChat, etc.), you MUST:**

1. **Open the page in a browser** — use `web_fetch` or actual browser if available
2. **Take a screenshot** — capture the current state
3. **Attach the screenshot to the GitHub Issue** as proof of acceptance
4. **Note any visual issues** — layout broken, missing elements, wrong data

**Dashboard:** `http://127.0.0.1:2712/dashboard/`
**WebChat:** `http://127.0.0.1:2712/chat/` (when available)

**Screenshot workflow:**
```bash
# If browser automation is available, use it
# Otherwise, use web_fetch to verify the HTML loads correctly:
curl -s http://127.0.0.1:2712/dashboard/ | head -50

# For API endpoints, verify JSON responses:
curl -s http://127.0.0.1:2712/api/status | python3 -m json.tool
curl -s http://127.0.0.1:2712/api/sessions | python3 -m json.tool
```

**Attach evidence to Issue:**
```bash
# Comment on the issue with verification results
gh issue comment <number> --body "## Acceptance Review ✅

**Verified:** <date>
**Build:** <commit hash>
**PID:** <pid>

### Functional
- [x] Startup OK
- [x] API endpoints respond correctly
- [x] Tests pass (N tests)

### UX (if applicable)
- [x] Page loads correctly
- [x] Screenshot attached
- [ ] Visual issues: <describe or 'none'>

### Evidence
<screenshot or curl output>"
```

#### C. Regression Check
- Verify existing features still work after the change
- Check Discord bot is responding (Fairy is online)
- Check Dashboard loads
- Check API health: `curl http://127.0.0.1:2712/api/status`

### 3. Report Results

**Always update the GitHub Issue with acceptance results:**
- ✅ Accepted → comment with evidence, ready for human to archive
- ❌ Rejected → comment with failure details, reopen if needed

## Isotopes-Specific Test Points

### Dashboard
- `/dashboard/` loads (not 404)
- `/api/sessions` returns session list
- Sessions show correct agent names
- Session messages are visible (not empty)
- Config section loads current config

### WebChat
- `/chat/` loads
- Can select agent from dropdown
- Can send message and receive reply
- Streaming works (text appears incrementally)
- Session persists across page reload (localStorage)

### Discord Bot
- Fairy responds to @mention in channel
- Subagent spawning works (thread created)
- Thread binding cleanup on restart
- Error messages are user-friendly (not stack traces)

### Self-Iteration
- `iterate_codebase` tool is registered
- Planner finds improvement candidates
- Executor creates branch + PR
- Pipeline respects "skip if open iter/* PR" rule

### API
- `GET /api/status` — returns version, agents list
- `GET /api/sessions` — returns active sessions
- `GET /api/config` — returns current config
- `GET /api/logs` — returns recent logs
- `POST /api/sessions/:id/message` — adds message to session

## Quality Gates

Before marking any item as Done:
1. ✅ `pnpm typecheck` passes
2. ✅ `pnpm test` passes (all tests)
3. ✅ Build succeeds (`npm run build`)
4. ✅ Isotopes starts without errors
5. ✅ No regressions in existing features
6. ✅ UX verified with screenshot (if applicable)
7. ✅ Evidence posted to GitHub Issue
