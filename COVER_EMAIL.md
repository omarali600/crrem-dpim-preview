# Cover email — draft

**Subject:** CRREM portfolio tool — preview + handover

---

Hi [name],

Following our call, here is what I promised: a working preview of the CRREM
portfolio assessment tool we discussed, along with the full specification
and implementation plan so you can take it as far as you'd like.

**The preview.** A single-page web app that takes a portfolio of five
listed REITs (Land Securities, Unibail-Rodamco-Westfield, Prologis,
Vonovia, Segro), models each as a CRREM-compliant mini-portfolio of
pseudo-assets, and shows the portfolio's trajectory against the 1.5°C
pathway through 2050, with NZIF classification per holding. Styled in DPIM
brand. Runs locally with one `streamlit run` command — instructions in the
README.

The numbers in the preview are illustrative placeholders chosen for
plausible magnitudes; the real version pulls inputs from each issuer's
most recent sustainability report. The methodology — pseudo-asset
modelling, CRREM compute, NZIF classification, GIA-weighted portfolio
rollup — is real and the same logic the production system would use.

**The handover.** Three files, all in the attached folder:

- `README.md` — what the preview shows and how to run it.
- `HANDOVER.md` — what production looks like (35 tickers, primary +
  corroborator ingestion from issuer PDFs / EPRA / CDP / GRESB / MSCI /
  Sustainalytics, four audience lenses including a regulatory lens with
  NZIF + SFDR + TCFD, auth + audit log, central deployment with a
  follow-on local-first build), and two paths to get there — hiring a
  developer, or continuing with Claude Code + Superpowers using the spec
  and plan I've written.
- The full **spec** and **implementation plan** for the compute engine
  (16 bite-sized tasks with code and tests written out, designed so a
  developer or coding agent can run them straight through).

I've put this together because I genuinely believe AI-enabled tools are
how we close the gap between climate methodology and the people who need
to use it. The thinking and the preview are yours to keep regardless of
what you decide next. If your uncle or any developer picks it up, the
spec and plan are written so they don't need to talk to me first.

If you do want the production build done at standard — the 35-ticker
scale-up, the ingestion pipeline, the four lenses, the auth and audit
trail — that's real engineering work and I'd want to do it as a paid
engagement. Happy to scope it if and when that's useful.

Either way, looking forward to seeing this run.

Best,
Omar

---

## Attachments

- `crrem-preview/` (preview app + README + HANDOVER)
- `2026-05-20-crrem-portfolio-tool-design.md` (spec)
- `2026-05-20-crrem-compute-engine.md` (implementation plan)
