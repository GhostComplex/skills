---
name: teamwork
description: "Full feature lifecycle with agent teams: Lead (PRD + issues), Developer (worktree + PR), Reviewer (code review). /teamwork [feature description or issue#]"
argument-hint: "[feature description to discuss, or issue# to resume]"
---

# Agent Team Feature Lifecycle

You are the **orchestrator**. You manage a 3-agent team that takes a feature from idea to merge-ready PR. The human does the final merge.

## Roles

| Role | Responsibility |
|------|---------------|
| **lead** | Discuss requirements with user → write PRD → create issue (or register feature locally) → manage status |
| **developer** | Pick up issue/feature → create worktree → implement → open PR or push branch |
| **reviewer** | Review PR → post comments → developer fixes → re-review (max 5 rounds) |

## Step 0 — Detect Platform & Parse Input

### 0.1 Platform Detection

Detect the git hosting platform before any other work:

```bash
git remote get-url origin 2>/dev/null
```

| Remote URL contains | Platform | Mode |
|---------------------|----------|------|
| `github.com` | GitHub | Use `gh` CLI for issues, PRs, and reviews |
| Anything else (ADO, GitLab, Bitbucket, etc.) or no remote | Non-GitHub | Use **local mode** — `.teamwork/` folder for tracking |

In **local mode**, create `.teamwork/` at the repo root (add it to `.gitignore`) with this structure:

```
.teamwork/
├── status.json          # overall tracking
└── reviews/
    └── <feature-slug>/
        ├── round-1.md   # review comments per round
        ├── round-2.md
        └── ...
```

`status.json` format:

```json
{
  "features": {
    "<feature-slug>": {
      "status": "Ready|In progress|In review|Done",
      "prd": "docs/prd/<feature-slug>.md",
      "branch": "<feature-slug>",
      "review_round": 0,
      "created_at": "<ISO timestamp>",
      "updated_at": "<ISO timestamp>"
    }
  }
}
```

### 0.2 Parse Input

Parse `$ARGUMENTS`:

| Input | Action |
|-------|--------|
| Feature description (text) | Start from Step 1 — requirements discussion |
| Issue number (`#12`, `12`) or feature slug | Resume — find status and jump to the appropriate step |
| Blank | Ask the user what they want to build |

## Step 1 — Requirements & PRD (Lead)

### 1.1 Discover Project Tracking

**GitHub mode:** Find the GitHub Project associated with this repo:

```bash
gh project list --owner $(gh repo view --json owner -q '.owner.login') --format json
```

- If a project is found, use it for all status management throughout the workflow.
- If no project exists, skip project-based status tracking. Issue state is managed via GitHub issue labels and PR status instead.
- Cache the project ID for later steps.

**Local mode:** Initialize `.teamwork/status.json` if it doesn't exist. All status updates go here.

### 1.2 Discuss with User

The lead engages the user in a focused requirements conversation:

1. Summarize understanding of the feature request
2. Ask clarifying questions (scope, constraints, acceptance criteria)
3. Propose a high-level approach
4. Iterate until the user confirms

**Do NOT proceed to PRD until the user explicitly approves the requirements.**

### 1.3 Write PRD

Create `docs/prd/<feature-slug>.md`:

```markdown
# <Feature Title>

## Overview
<!-- 1-2 sentence summary -->

## Motivation
<!-- Why this feature is needed -->

## Requirements
<!-- Numbered list of functional requirements -->

## Acceptance Criteria
<!-- Testable criteria that define "done" -->

## Technical Approach
<!-- High-level implementation strategy -->

## Out of Scope
<!-- What this feature intentionally does NOT cover -->

## Open Questions
<!-- Unresolved items, if any -->
```

### 1.4 Create Issue / Register Feature

Commit the PRD first so it's available in the repo:

```bash
git checkout -b docs/<feature-slug>-prd main
git add docs/prd/<feature-slug>.md
git commit -m "docs: add PRD for <feature-slug>"
git push -u origin docs/<feature-slug>-prd
```

**GitHub mode:** Create the issue:

```bash
gh issue create --title "<title>" --body "$(cat docs/prd/<feature-slug>.md)"
```

- The issue body IS the PRD content.
- Add relevant labels if the repo has them.
- Move issue to **Ready** in the GitHub Project (if available).

**Local mode:** Register the feature in `.teamwork/status.json` with status `Ready`. The PRD file serves as the source of truth — no external issue is created.

### 1.5 Hand Off

Report the issue number (GitHub mode) or feature slug (local mode) and PRD path to the orchestrator. The lead's active work pauses here until review phase or status updates are needed.

## Step 2 — Implementation (Developer)

### 2.1 Pick Up Issue

- Move issue to **In progress** (GitHub Project, if available).

### 2.2 Create Worktree

The developer MUST work in a worktree — never commit directly to main.

Use the built-in `EnterWorktree` tool with `name: "<feature-slug>"`. This handles CWD switching, cache clearing, and cleanup automatically. Do NOT use raw `git worktree add` commands.

All development happens inside this worktree directory.

### 2.3 Implement

- Read the PRD and issue for requirements.
- Implement the feature in the worktree.
- Write tests as appropriate.
- Run linting, type checking, and tests if the repo has them (check CLAUDE.md for commands).
- Commit with conventional commit style: `feat(<scope>): <description>`.

### 2.4 Open PR

**GitHub mode:**

```bash
git push -u origin <feature-slug>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<bullet points>

Closes #<issue_number>

## Test Plan
<how to verify>

## PRD
See [docs/prd/<feature-slug>.md](docs/prd/<feature-slug>.md)
EOF
)"
```

- The PR body MUST include `Closes #<issue_number>` to link the issue.
- Move issue to **In review** (GitHub Project, if available).

**Local mode:**

```bash
git push -u origin <feature-slug>
```

- Update `.teamwork/status.json` to **In review**.
- The branch itself is the "PR" — the reviewer will review the branch diff against main.

### 2.5 Hand Off

Report the PR number to the orchestrator. Developer pauses until review feedback arrives.

## Step 3 — Code Review (Reviewer)

### 3.1 Review PR

The reviewer reads the diff and the PRD, then posts review comments.

**GitHub mode:**

```bash
gh pr diff <pr_number>
gh pr view <pr_number>
```

**Local mode:**

```bash
git diff main...<feature-slug>
```

Read the PRD from `docs/prd/<feature-slug>.md`.

Review focus areas:
- Does the implementation match the PRD requirements and acceptance criteria?
- Code quality, error handling, edge cases
- Security (OWASP top 10 awareness)
- Test coverage and quality
- Naming, structure, consistency with project conventions

### 3.2 Submit Review

**GitHub mode:**

```bash
gh pr review <pr_number> --comment --body "<review summary>"
```

For specific line comments, use `gh pr review` with `--comment` for general feedback, or use the GitHub API with a JSON input file:

```bash
# Write review payload to a temp file, then submit
jq -n '{
  body: "<summary>",
  event: "REQUEST_CHANGES",
  comments: [{"path":"<file>","line":<line>,"body":"<comment>"}]
}' | gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews --method POST --input -
```

**Local mode:**

Write the review to `.teamwork/reviews/<feature-slug>/round-N.md` with this format:

```markdown
# Review Round N/5 — <feature-slug>

## Verdict: REQUEST_CHANGES | APPROVE

## Comments
- `<file>:<line>` — <comment>
- ...

## Summary
<overall assessment>
```

The review verdict is one of:
- **APPROVE** — no issues found, PR is merge-ready
- **REQUEST_CHANGES** — issues found, developer must fix

### 3.3 Review Loop (Max 5 Rounds)

If REQUEST_CHANGES:

1. Reviewer sends findings to the orchestrator
2. Orchestrator forwards to developer
3. Developer fixes issues in the worktree, pushes new commits
4. Reviewer re-reviews the new changes
5. Repeat until APPROVE or round 5

**Round 5 rule**: If still not approved by round 5, the reviewer must produce a final summary of all remaining issues and escalate to the user for a decision. Do NOT continue beyond round 5.

Track the current round number. Each review message must state: `Review round N/5`.

### 3.4 Approved

When the reviewer approves:

1. **GitHub mode:** Reviewer posts the APPROVE review on GitHub
   **Local mode:** Reviewer writes the final APPROVE review to `.teamwork/reviews/<feature-slug>/`
2. Orchestrator notifies the user: "PR #N (or branch `<feature-slug>`) is approved and ready for merge."
3. **The human merges.** Do NOT merge the PR.

## Step 4 — Cleanup

After the user confirms the PR is merged (or you detect it via `gh pr view` / branch deletion):

1. Move issue to **Done** (GitHub Project, if available) or update `.teamwork/status.json`
2. Use `ExitWorktree` with `action: "remove"` to clean up the worktree.
3. **Local mode:** Keep `.teamwork/` as a historical record — do not delete it.
4. Report completion

## Agent Team Setup

Create a team named `teamwork-<feature-slug>` (derived from the feature description or issue number).

### Spawning

Spawn agents on-demand as each phase begins — do NOT spawn all agents upfront:

1. **lead** — spawn immediately (Step 1)
2. **developer** — spawn when lead hands off the issue number (Step 2)
3. **reviewer** — spawn when developer hands off the PR number (Step 3)

Each teammate receives:
- Their role description and responsibilities from this document
- The current repo's CLAUDE.md (if it exists) for project conventions
- The GitHub project ID (if available)

### Teammate Prompt Template

```
You are the {ROLE} in a feature development team.

## Your Responsibilities
{ROLE_RESPONSIBILITIES from this document}

## Project Conventions
{CLAUDE.md contents, if available}

## GitHub Project
{Project ID and status management instructions, if a GitHub Project was found}

## Current State
{What has been completed so far and what you need to do next}

## Communication
- When your step is complete, send your deliverables to the team lead (orchestrator).
- If you need clarification, ask the orchestrator — they will relay to the user.
- Developer and Reviewer communicate through the orchestrator for review rounds.
```

### Worktree Usage

- Developer MUST use the `EnterWorktree` tool to create an isolated working copy.
- Developer works entirely within the worktree — all edits, commits, and pushes happen there.
- Use `ExitWorktree` with `action: "remove"` in Step 4 after merge for cleanup.

## Status Management Summary

| Event | Status |
|-------|--------|
| Issue created / feature registered | Ready |
| Developer starts | In progress |
| PR opened / branch pushed for review | In review |
| PR merged (by human) | Done |

**GitHub mode** — For GitHub Project, use:
```bash
# Find item ID
gh project item-list <project_number> --owner <owner> --format json | jq '.items[] | select(.content.number == <issue_number>)'

# Update status
gh project item-edit --project-id <project_id> --id <item_id> --field-id <status_field_id> --single-select-option-id <option_id>
```

If the `gh project` commands fail (permissions, no project), fall back to tracking status via GitHub issue labels and PR state.

**Local mode** — Update `.teamwork/status.json` directly. The `status` field tracks the same states.

## Rules

- **Never merge PRs.** The human merges. Always.
- **Never commit to main.** All work goes through worktree + PR.
- **Max 5 review rounds.** Escalate to human after round 5.
- **PRD lives in two places:** `docs/prd/<slug>.md` AND the issue body (GitHub mode) or `.teamwork/status.json` reference (local mode).
- **Lead manages status.** Only the lead (or orchestrator) updates project/issue status.
- **Sequential handoff.** Each role completes before the next begins. No parallel implementation and review.
- **User approval gates:** Requirements must be approved before PRD. PRD must be approved before issue creation.
- **Handle `gh` failures gracefully.** If any `gh` command fails (auth, permissions, branch protection), report the error to the orchestrator instead of proceeding blindly.
