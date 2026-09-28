---
name: "paper-pdf-hunter"
description: "Drive a real web browser like a human to find and download PDFs for a list of research papers given in a markdown file (Google Scholar, publisher pages, preprint servers, repositories)."
---

# Paper PDF hunter (browser-driven)

Invoke as:
    /paper-pdf-hunter <PAPER-LIST> <OUTPUT-FOLDER>

You are going to act like a diligent research assistant sitting at the user's browser: read a markdown list of papers, then for each one search, click, follow links and download the PDF — the way a person would. Do NOT call scholarly REST APIs; the user already has an API-based tool. The point of this skill is the human-style browsing that APIs miss (Scholar's [PDF] side-links, "All versions", author homepages, institutional access via the user's logged-in browser).

## 0. Tools and setup

Use whichever browser-automation tools are present, in this order of preference:

1. **Claude in Chrome** (tools like `navigate`, `read_page`, `find`, `get_page_text`, `computer`, `javascript_tool`, `tabs_context`) — best, because it is the user's real Chrome with their cookies, institutional/SSO logins and a human-looking fingerprint.
2. **Playwright MCP** (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_wait_for`, …) — fine, but headless/fresh profiles get CAPTCHA'd by Google Scholar much sooner.

If neither is available, stop and tell the user which one to connect; do not silently fall back to APIs.

Before starting:

- Ask (once) for the <PAPER-LIST> if not given; offer the option to search for a markdown file which looks like a list of papers; if you cannot find the markdown file exit and say why.
- Ask (once) for the <OUTPUT-FOLDER> if not given; default `./papers/` next to the markdown file.
- For Chrome: PDFs download cleanly only if Chrome is set to download rather than preview them. Check with the user or navigate to `chrome://settings/content/pdfDocuments` and ask them to pick "Download PDFs". Otherwise, when a PDF opens in the viewer, the viewer's URL is the PDF URL — record it and download it with `curl -L` (see §4).
- Note the browser's download directory (usually `~/Downloads`) so you can find and move files afterwards.

## 1. Parse the markdown

Extract one record per paper. Accept any shape: bullet lists, numbered references, tables, APA/Vancouver/BibTeX-ish strings, bare DOIs/arXiv IDs/URLs. For each record capture what is present: `title`, `authors` (first author surname is the most useful), `year`, `venue`, `doi` (regex `10\.\d{4,9}/[^\s"<>]+`, strip trailing punctuation), `arxiv` (`\d{4}\.\d{4,5}(v\d+)?` or old-style `[a-z\-]+/\d{7}`), any URL. Show the user the parsed list count (and anything ambiguous) before you start browsing; don't wait for confirmation unless parsing was genuinely unclear.

Keep a working table (in memory or a scratch file) with columns: `#, short title, status, source, file, notes`.

## 2. Search strategy per paper (stop at the first verified PDF)

Work through the ladder in order. Spend at most ~6–8 browser actions per rung, and move on.

**a. Direct identifiers (fast path)**

- arXiv ID → `https://arxiv.org/abs/<id>` → click "View PDF".
- DOI → `https://doi.org/<doi>` → on the publisher landing page look for a "PDF" / "Download PDF" / "View PDF" button. Also read the `citation_pdf_url` meta tag (via `javascript_tool`: `document.querySelector('meta[name="citation_pdf_url"]')?.content`, or from the page snapshot). The user's browser may have institutional access, so try it even for paywalled journals. If a cookie/consent banner blocks the page, dismiss it like a human would ("Accept necessary only" where offered).

**b. Google Scholar** (`https://scholar.google.com/scholar?q=<"exact title">` — quote the title; add the first author's surname if the title is generic)

- Confirm the top hit matches title/author/year.
- Look at the right-hand column of that result for a `[PDF] domain.tld` link (or `[HTML]`). Click the [PDF] link.
- If none, click **"All N versions"** under the result and scan every version for a [PDF] side-link; prefer, in order: publisher, PubMed Central / Europe PMC, university repositories (`*.edu`, `*.ac.uk`, `hal.science`, `repository.*`, `dspace`, `eprints`), preprint servers, author homepages, then ResearchGate/Academia.
- Pace yourself like a person: a few seconds between Scholar queries, no rapid-fire searches, reuse one tab.
- **CAPTCHA / "unusual traffic"**: never try to solve or bypass it programmatically. Pause and ask the user to solve it in the browser (message them), then continue. If it recurs or the user is away, skip Scholar for the remaining papers and rely on the other rungs.

**c. Preprint and repository sites** (use their own search boxes)

- arXiv (`arxiv.org/a` / search), bioRxiv/medRxiv, PsyArXiv & other OSF preprints (`osf.io/preprints`), SSRN, RePEc/IDEAS, PhilPapers, HAL, Zenodo.
- Europe PMC (`europepmc.org/search?query=`) → if a PMCID exists, `https://europepmc.org/articles/<PMCID>?pdf=render`. PubMed Central article pages have a "PDF" link in the sidebar.
- Semantic Scholar web page (`semanticscholar.org/search?q=`) — use its "PDF" / "View via Publisher" buttons.

**d. General web search, human style**

- Search `"<exact title>" filetype:pdf`, then `"<exact title>" <first-author surname> pdf`. Look for author homepages, lab pages, course pages, conference proceedings, institutional repositories.
- If you find the first author's homepage, check its Publications page.

**e. ResearchGate / Academia.edu** — download only if a public full-text PDF is offered without logging in as someone else. If only "Request full-text" exists, record it as an option for the user rather than clicking it.

**Out of scope:** shadow libraries (Sci-Hub, LibGen, Anna's Archive, etc.) and anything that bypasses a paywall or login. If the only route is paywalled and the user's browser has no access, mark it `paywalled` and move on.

## 3. Verify every download

A link labelled PDF is often an HTML interstitial, a login page or the wrong paper. For each candidate:

- Confirm the file starts with `%PDF` (`head -c 5 file`) and is > ~20 KB.
- `pdfinfo` for page count; `pdftotext -l 2 file - | head -60` and check the title (case/punctuation-insensitive, allow minor differences) and ideally the first author appear on page 1–2.
- Watch for: supplementary-material PDFs, book front matter only, a different paper with a similar title, a review/commentary *on* the paper, cover-sheet-only files. Treat these as failures and keep looking.
- Note the version when you can tell (published / accepted manuscript / preprint) — prefer the published version if you found multiple.

## 4. Getting the file onto disk

- Browser download (preferred — it carries the user's cookies): trigger it, then find the newest `.pdf` in the download directory (`ls -t ~/Downloads/*.pdf | head`), verify, and move it.
- If a PDF opened in the viewer or you have a clean direct PDF URL that isn't behind a login: `curl -L --fail -A "Mozilla/5.0" -o <tmp> "<url>"`, then verify.
- Filename: `<FirstAuthorSurname>_<Year>_<first-5-title-words>.pdf`, ASCII, spaces→`_`, no punctuation; append `_preprint` / `_accepted` when not the published version. Never overwrite an existing file — add `_2`.

## 5. Report

When done, write `download_report.md` in the output folder (and summarise in chat) with a table:

| # | Paper (short) | Status | Source (URL) | File | Notes |
|---|---|---|---|---|---|

Status is one of `downloaded`, `downloaded (preprint)`, `paywalled`, `not found`, `ambiguous`, `skipped (captcha)`. For every miss, list the concrete next options you saw: ResearchGate "request full-text" link, the corresponding author's email from the landing page, interlibrary loan via the user's library, or a DOI to try later. Finish with counts (e.g. "23/30 downloaded, 4 paywalled, 3 not found").

## Working style

- Process papers sequentially in a single tab; don't open dozens of tabs.
- Post a one-line progress update every ~5 papers.
- If a page asks you to log in, sign up, pay, or accept terms on the user's behalf, don't — note it and move on (or ask the user if it's their institutional SSO and they want to log in themselves).
- Stop and ask only when genuinely blocked (CAPTCHA, output folder unknown, the markdown can't be parsed). Otherwise keep going and let the report carry the details.
