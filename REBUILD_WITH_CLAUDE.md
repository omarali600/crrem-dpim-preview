# Rebuild this with Claude — a copy-paste recipe

This document lets you (or any developer) take the preview from this repo to a
production-grade CRREM Portfolio Assessment tool using **Claude Code**
(Anthropic's official CLI) plus the **Superpowers** skill pack. The same setup
that authored the spec, plan, and preview in this repo.

You will get:

- The full 35-ticker portfolio (not just the 5 in the preview).
- Automated ingestion from each issuer's most recent sustainability report,
  with cross-checks against EPRA sBPR XBRL, CDP, GRESB, MSCI ESG, Sustainalytics.
- Blueprint-validated compute engine (bit-exactly reproduces the CRREM
  worked-example fixtures).
- All four audience lenses fully functional (not preview-illustrative).
- Authentication (password + TOTP MFA, optional SAML/OIDC SSO), four-role
  access control (Admin / Analyst / Viewer / Auditor), and an append-only
  hash-chained audit log.
- Central self-hosted deployment plus a local-first desktop app rollout to
  colleagues.

No prior coding-agent experience required. The recipe below is sequential.

---

## Step 1 — Install prerequisites

You need a Mac, Linux, or Windows (WSL) machine.

1. **Node.js 18+** — <https://nodejs.org/>
2. **Python 3.12+** — <https://python.org/downloads/>
3. **Git** — <https://git-scm.com/downloads>
4. **A code editor** — Cursor, VS Code, or any other.

Open a terminal and verify:

```bash
node --version    # should be v18 or higher
python3 --version # should be 3.12 or higher
git --version
```

## Step 2 — Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Authenticate either with:

- **A Claude.ai Pro or Max subscription** — log in via the browser flow when
  prompted (cheapest if you already have one).
- **An Anthropic API key** — from <https://console.anthropic.com/>. Pay-as-you-go.

Run once to authenticate:

```bash
claude
```

Follow the prompts. Quit with `/exit` once you see the prompt.

## Step 3 — Install Superpowers

Superpowers is the skill pack that includes the brainstorming, planning,
implementation, and review workflows used to build the artifacts in this repo.

From any directory:

```bash
claude
```

Then inside Claude Code:

```
/plugin install superpowers
```

Confirm with `y`. Exit with `/exit`.

## Step 4 — Set up the project directory

```bash
mkdir crrem-production && cd crrem-production
git init -b main
```

Copy the three core artifacts from this preview into your working directory:

```
crrem-production/
├── docs/
│   ├── spec.md      ← from 2026-05-20-crrem-portfolio-tool-design.md
│   └── plan.md      ← from 2026-05-20-crrem-compute-engine.md
├── reference/
│   ├── blueprint.md                       ← CRREM Technical Blueprint v1.0
│   ├── blueprint-schema.json              ← CRREM input schema
│   └── worked-examples-fixtures.json      ← validation fixtures
```

The reference files are open-access from
<https://crrem.org/library/technical-blueprint/> and
<https://crrem.org/library/reference-implementations/>.

## Step 5 — Build the compute engine (the foundation)

Inside the project directory:

```bash
claude
```

Then **paste this prompt verbatim** into Claude Code:

> Read the implementation plan at `docs/plan.md` as the source of truth.
> The spec it implements is at `docs/spec.md`. Reference artifacts
> (CRREM blueprint, input schema, worked-example fixtures) are in
> `reference/`. Use the `superpowers:subagent-driven-development` skill
> to execute the plan task-by-task. Each task gets a fresh subagent for
> implementation, then a spec-compliance review, then a code-quality
> review. Manual prerequisite: when the plan reaches Task 1 Step 6, stop
> and tell me which CRREM reference datasets to download; do not proceed
> past that point without my confirmation. The working directory for the
> Python library is `crrem-compute/`.

Claude Code will work through the 16 tasks. Most are mechanical; some need
your input. When it asks for the CRREM reference datasets (pathways,
emission factors, postal code lookup, HDD/CDD), download them from
<https://crrem.org/library/pathways-and-datasets/> and drop them into
`crrem-compute/data/`, then tell Claude "they're in place, continue."

When the compute engine is done, you will have a Python library that
reproduces all four CRREM worked-example fixtures bit-exactly.

## Step 6 — Author the next plans

The compute engine is the first of five sequenced plans. The remaining four
are stubbed at the bottom of `docs/plan.md`. Author each one as a
full bite-sized plan with this prompt (run inside Claude Code from the
project directory):

> Use the `superpowers:writing-plans` skill to author the implementation plan
> for Plan 2 (Backend + Auth + Audit Log + Data API). Use the spec at
> `docs/spec.md` and the existing plan at `docs/plan.md` as context. Save the
> new plan to `docs/plan-02-backend.md`.

Repeat for Plan 3 (Ingestion), Plan 4 (Presentation — the four lenses),
Plan 5 (Tauri packaging for local rollout). Each plan, once authored, is
executed the same way as Step 5.

## Step 7 — Iterate

You can stop, restart, ask follow-up questions, change scope, and run
adversarial review (`/codex review` or `/codex challenge` if you have OpenAI
Codex CLI installed) at any point. Claude Code commits after every step, so
you can roll back cleanly.

---

## Useful Claude Code commands

| Command | What it does |
|--|--|
| `/help` | Lists every command. |
| `/exit` | Quit. |
| `/clear` | Reset the conversation (use when starting a new sub-task). |
| `/cost` | Show how much you've spent this session. |
| `/plugin list` | Show installed plugins. |
| `/loop 30m <command>` | Run a recurring command. |

---

## Cost ballpark

The compute-engine plan is mostly mechanical Python and runs cheaply
(usually $5–$15 on the API, less if you're on a Claude.ai subscription).
The ingestion plan involves more judgment — budget $20–$50. The presentation
and auth plans land between those. Total end-to-end for the full system:
broadly $80–$200 in API spend on a fresh build, or a single month of a
Claude.ai Max subscription's allowance.

These are rough numbers. Use `/cost` in any Claude Code session to track
spend in real time.

---

## When to ask Omar

You shouldn't need to. The spec and plan are written to be read by a developer
who has never spoken to me. If something is unclear or Claude Code gets stuck
in a loop it can't resolve, an email is fine.

If you want me to build the production version directly rather than
self-rebuilding, the pricing tiers are in the cover email.
