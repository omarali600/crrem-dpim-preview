# Handover — Taking this from preview to production

This preview demonstrates the methodology end-to-end on five hand-curated
holdings with illustrative inputs. The production system designed in the
accompanying spec is materially larger:

- 35 tickers, ingested automatically from the issuers' most recent
  sustainability reports.
- Primary + corroborators data model: issuer PDF (LLM extraction with
  page-citation provenance) as the value of record, plus parallel pulls
  from EPRA sBPR XBRL, CDP, GRESB, MSCI ESG, Sustainalytics. Discrepancies
  are surfaced, not hidden.
- A blueprint-compliant compute engine validated bit-exactly against the
  four CRREM worked-example fixtures (CI gate).
- Four audience-specific lenses on the same portfolio model: Investment
  Committee, Regulatory/LP (including NZIF, SFDR PAI 18, Article 8/9
  narratives, TCFD scenario alignment, GRESB-comparable score),
  Engagement, Analyst.
- Authentication (password + TOTP MFA, with SAML/OIDC SSO option),
  four-role RBAC (Admin / Analyst / Viewer / Auditor), and an append-only
  hash-chained audit log.
- A central self-hosted instance for the team, with a follow-on local-first
  desktop build (Tauri) for colleagues — same codebase, additive sync layer.

## The artifacts you have

1. **`docs/superpowers/specs/2026-05-20-crrem-portfolio-tool-design.md`**
   — full specification. Methodology, architecture, error handling,
   testing, NZIF integration, auth, deployment.

2. **`docs/superpowers/plans/2026-05-20-crrem-compute-engine.md`** —
   bite-sized implementation plan for the **compute engine** (the
   foundation library). 16 tasks, each with code and tests written out,
   designed to be executed by a developer or by a coding-agent harness.

   Plans 2–5 (Backend + Auth, Ingestion, Presentation, Tauri packaging)
   are stubbed at the bottom of that plan with explicit scope and
   dependencies. Each gets its own bite-sized plan when its predecessor
   lands.

3. **This preview** (`/crrem-preview/`) — runnable demonstration, in DPIM
   brand styling.

## Two paths to production

### Path A — Engage a developer

The spec and plan are written for a developer who has not spoken to the
author. Hand them over with this README. A capable mid-level developer
should be able to deliver the compute engine in roughly one to two weeks
of focused work; the full system (compute + backend + ingestion + four
lenses + auth + deployment) is a larger engagement.

### Path B — Continue with Claude Code + Superpowers

The spec and plan were authored using **Claude Code** (Anthropic's
official CLI) with the **Superpowers** skill pack. The same setup can
execute the plan directly.

#### Setup

1. Install Node.js (18+) and Python (3.12+).
2. Install Claude Code:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. Authenticate (either an Anthropic API key or a Claude.ai Pro/Max plan).
4. Install the Superpowers plugin pack — follow the install instructions at
   <https://github.com/anthropics/claude-code> for plugin installation,
   then enable the `superpowers` plugin.

#### Run

From an empty project directory:

```bash
claude
```

Then in the Claude Code prompt:

```
Read the spec at <path>/2026-05-20-crrem-portfolio-tool-design.md and the
plan at <path>/2026-05-20-crrem-compute-engine.md, then use
superpowers:subagent-driven-development to execute the plan.
```

Claude Code will run each task with TDD, commit after every step, and
review its own work between tasks. Plans 2–5 get authored when the
preceding plan lands by running `superpowers:writing-plans` against the
spec section for that subsystem.

#### Cost expectations (rough)

The compute-engine plan is mostly mechanical Python and runs in the cheap
tier. The ingestion and presentation plans involve more judgment and run
in the standard tier. Auth + audit log + Tauri packaging are smaller.
Budget on the order of a few tens of dollars in API spend (or a Claude.ai
Pro subscription's monthly allowance) for the compute engine, more for
the full system.

## Help along the way

If you take Path B and hit a wall the agent can't resolve, you have my
contact. The thinking is yours; I'd rather see this run than not. If you
decide you want the production build done at standard, I'm available for
a paid engagement on it.
