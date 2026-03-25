# Design Doc Template

Use this template when writing a spec document during the DDD flow.

```markdown
# {Feature Name} — Design Spec

**Date:** YYYY-MM-DD
**Author:** {who drafted this}
**Status:** Draft | In Review | Approved
**Stakeholders:** {who was consulted}

## Goal

{One paragraph: what problem does this solve and why now?}

## Success Criteria

- {Measurable outcome 1}
- {Measurable outcome 2}

## Proposed Approach

### Architecture

{How the pieces fit together. Diagrams welcome.}

### Components

| Component | Responsibility | New/Modified |
|---|---|---|
| {name} | {what it does} | New / Modified |

### Data Flow

{How data moves through the system. Input → processing → output.}

### Error Handling

{What can go wrong and how we handle it.}

### Testing Strategy

{What gets tested, how, and what coverage looks like.}

## Alternatives Considered

### Option A: {name}
{Description and why rejected.}

### Option B: {name}
{Description and why rejected.}

## Open Questions

- {Anything still unresolved}

## Out of Scope (v1)

- {Features explicitly deferred}
```

---

# Project Tracking Template

Use this template when onboarding to a new project channel.

```markdown
# {Project Name} — Project Tracking

**Channel:** #{channel-name}
**Repo:** https://github.com/{org}/{repo}.git
**Product:** {one-line description}

## Team
- **PM:** {name}
- **Dev:** {agent name} (Discord ID: {id})
- **Manager:** {your name}

## Current Status
- PRD: {status}
- Tech Design: {status}
- Sprint/Week: {current}

## Milestones
| # | Description | Status | Branch |
|---|---|---|---|
| M1 | {desc} | ⬜/✅ | feat/{name}/dev-m1 |

## Remaining Gaps
- {item} — {blocker/owner}

## Tech Stack
- Frontend: {x}
- Backend: {x}
- DB: {x}
- Deploy: {x}
```

# Handoff Checklist

When a dev agent changes mid-project:

1. Outgoing agent pushes all WIP to repo
2. Update `USER.md` with new agent's Discord ID
3. Document current state in `memory/{platform}-{id}/notes.md`
4. New agent reads notes + repo before starting
5. Confirm new agent can access all resources
6. Announce handoff in group channel

# Milestone Delivery Checklist

Before marking a milestone complete:

- [ ] All tests passing
- [ ] Code pushed to correct branch (`feat/{name}/dev-{milestone}`)
- [ ] PR opened (if required) with project owner tagged for review
- [ ] Docs updated (PRD status, README, tech notes)
- [ ] Memory files updated in `memory/{platform}-{id}/`
- [ ] Group channel notified of completion
