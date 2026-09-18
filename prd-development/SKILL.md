---
name: prd-development
description: Create a structured product requirements document that connects the problem, target users, proposed solution, scope, dependencies, and success metrics. Use when turning discovery notes, stakeholder input, or scattered product context into an engineering-ready PRD for a significant feature or initiative.
---

# PRD Development

Create a complete PRD that is clear enough for product, design, engineering, and stakeholders to align on the same initiative.

Use [template.md](template.md) as the output skeleton. Use [examples/sample.md](examples/sample.md) when you need a quick quality bar for good and bad PRD patterns.

## Workflow

Work through the document in this order:

1. Write an executive summary that states the user, problem, solution, and expected impact.
2. Define the problem with evidence such as interviews, analytics, support tickets, or market signals.
3. Identify the primary persona and any meaningful secondary personas.
4. Explain the strategic context, including business goals, urgency, and optional market or competitive framing.
5. Describe the solution at a high level without turning the PRD into a pixel-perfect design spec.
6. Define one primary success metric, then add secondary and guardrail metrics.
7. Convert the solution into user stories with acceptance criteria, constraints, and edge cases.
8. Close with out-of-scope items, dependencies, risks, and open questions.

## Writing Rules

- Keep the document evidence-based. If the problem statement has no proof, call that out and ask for it.
- Prefer one clear primary persona over a vague "all users" audience.
- State why this work matters now; do not leave the business case implicit.
- Keep the solution section high level. Leave detailed UI decisions to design and implementation details to engineering docs.
- Make success measurable. Every important initiative should have a target, baseline, or explicit measurement gap.
- Document what is not being built. This is one of the easiest ways to prevent scope creep.
- Surface missing decisions explicitly in `Open Questions` instead of guessing silently.

## Suggested Facilitation Sequence

If the user wants a guided conversation, gather inputs in this order:

1. What initiative or feature is this PRD for?
2. Who has the problem, and what evidence shows it is real?
3. What business goal or strategic objective does this support?
4. What is the proposed solution in one or two paragraphs?
5. How will success be measured?
6. What user stories and acceptance criteria are already known?
7. What is out of scope?
8. What dependencies, risks, and open questions remain?

If the user provides only fragments, draft the PRD structure anyway and clearly label assumptions and missing evidence.

## Section Guidance

### Executive Summary

Draft a short paragraph in this format:

`We are building [solution] for [persona] to solve [problem], which should result in [impact].`

Write an early draft to force clarity, then revise it after the rest of the PRD is complete.

### Problem Statement

Cover:

- Who has the problem
- What the problem is
- Why it hurts
- What evidence supports it

Good evidence includes customer quotes, discovery findings, analytics, support patterns, churn signals, and operational pain.

### Target Users

For each meaningful persona, describe:

- Role or context
- Goals
- Pain points
- Relevant behaviors or constraints

If there is a primary persona, optimize the PRD for that persona instead of flattening priorities across many audiences.

### Strategic Context

Tie the initiative to a real business outcome such as retention, activation, revenue, cost reduction, or market expansion. Include `Why now` so the prioritization is understandable later.

### Solution Overview

Describe how the solution works, what core user flow it supports, and the most important features. Keep this section product-level rather than implementation-level.

### Success Metrics

Define:

- One primary metric
- Supporting secondary metrics
- Guardrail metrics that should not regress

Whenever possible, include current state, target state, and timing.

### User Stories And Requirements

Translate the initiative into testable stories and acceptance criteria. Capture constraints and edge cases that materially affect delivery or UX.

### Out Of Scope, Dependencies, Risks

Use these sections to prevent ambiguity:

- `Out of Scope`: explicitly excluded items
- `Dependencies`: teams, systems, designs, integrations, or decisions required first
- `Risks`: likely failure modes and mitigations
- `Open Questions`: unresolved choices that still need answers

## Quality Checks

Before finishing, verify that the PRD:

- explains the problem with evidence instead of opinions alone
- names the primary user clearly
- links the work to business value
- describes the solution without over-specifying implementation
- includes measurable success criteria
- contains acceptance criteria for important stories
- states what is out of scope
- lists dependencies, risks, and open questions

## Common Pitfalls

- Writing a PRD in isolation and presenting it as a finished contract
- Using generic problem statements like "users want better onboarding"
- Skipping metrics, which makes success impossible to validate
- Turning the PRD into a detailed design or engineering spec
- Leaving out `Out of Scope`, which invites scope creep

## Resources

- Use [template.md](template.md) to generate the PRD structure.
- Use [examples/sample.md](examples/sample.md) to compare strong and weak examples.
