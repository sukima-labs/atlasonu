# 04 · Show HN

Antes de publicar: probar la web en un navegador limpio y por el camino público (`/salud` = 200); `maquina` avisada por si hay pico; el asistente disponible las primeras horas. No se pide a nadie que vote ni comente. Publicar entre martes y jueves por la mañana (hora del Este de EE. UU.).

**Título:** Show HN: ATLAS ONU – UN human rights mandates and documents, linked to the source

**URL:** https://sukimalabs.com/atlasonu/

**Primer comentario (del autor):**
Hi HN. This is a free, open-source (AGPL-3.0) static site that maps the UN human rights system for people who don't know it: {{mandatos}} special-procedure mandates, the {{actos}} legal acts that created or renewed them, {{paises}} country profiles, {{tratados}} treaties, an acronym glossary and a timeline. It is Spanish-first (the interface is in all six UN languages; official data is shown as the UN publishes it).

Why: finding the resolution behind a mandate means telling resolutions, reports and drafts apart, and many old ones exist only as scans or inside session reports. Each symbol is checked against the UN Digital Library twice a day; {{localizados}} of {{actos}} are located, and the rest say why not. If an equivalence is inferred, it says so. The update job refuses to publish if the data degrades.

How it's built: no framework, one `index.html` plus generated data files, Python scripts for fetching and verification, Node/Playwright tests (including an accessibility run and emulated phones against the live site). Full-text search and a "ask the documents" box run on a small server: the answer is written only from retrieved paragraphs and cites each one. No tracking, no accounts; the visit counter stores two aggregate numbers.

Limits: only current mandates (extinct ones are missing), translations still need native review, and communications by rapporteurs can't be fetched because the source's robots.txt forbids it.

It is independent and not an official UN product. Code: https://github.com/sukima-labs/atlasonu — I'd love to hear what's missing or wrong.
