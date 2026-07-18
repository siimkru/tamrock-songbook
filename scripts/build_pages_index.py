#!/usr/bin/env python3
"""Build the static GitHub Pages site for the PDF songbook."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlencode


TITLE_DIRECTIVE = re.compile(r"^\s*\{title\s*:\s*(.*?)\s*\}\s*$", re.IGNORECASE)
PDF_VARIANTS = (
    ("Kitarr", "Kitarr"),
    ("Ainult sõnad", "Ainult_sonad"),
)
DEFAULT_REPOSITORY = "siimkru/tamrock-songbook"
REPORT_MARKER = "<!-- tamrock-song-report -->"

STYLES = """
      :root { color-scheme: light; font-family: system-ui, -apple-system, sans-serif; }
      * { box-sizing: border-box; }
      body { margin: 0; color: #17202a; background: #f4f6f7; }
      header { padding: 2.5rem 1rem 2rem; color: white; background: #244b3c; text-align: center; }
      h1 { margin: 0 0 .5rem; font-size: clamp(2rem, 7vw, 3.5rem); }
      header p { margin: 0; }
      .header-link { margin-top: 1rem; color: white; }
      main { width: min(70rem, 100%); margin: auto; padding: 1.25rem; }
      .song-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); gap: 1rem; }
      .song, .report, .empty-state { padding: 1.25rem; border: 1px solid #d9e0dd; border-radius: .75rem; background: white; box-shadow: 0 2px 8px rgb(0 0 0 / 6%); }
      h2 { margin: 0 0 1rem; font-size: 1.25rem; }
      nav, .actions { display: flex; flex-wrap: wrap; gap: .6rem; }
      .button { display: inline-block; padding: .65rem .85rem; border-radius: .45rem; color: white; background: #376f5a; font-weight: 650; text-decoration: none; }
      .button:hover, .button:focus-visible { background: #244b3c; text-decoration: underline; }
      .button-secondary { color: #244b3c; background: #e4eeea; }
      .button-secondary:hover, .button-secondary:focus-visible { color: white; }
      .reports { display: grid; gap: 1rem; }
      .report h2 a { color: #244b3c; }
      .report-meta { display: flex; flex-wrap: wrap; gap: .5rem 1rem; margin: 0; color: #53635d; }
      .status { display: inline-block; padding: .15rem .5rem; border-radius: 999px; color: #155724; background: #dff2e3; font-size: .875rem; font-weight: 700; }
      .status-closed { color: #633c78; background: #eee1f5; }
      .loading { text-align: center; color: #53635d; }
      @media (max-width: 32rem) {
        header { padding-top: 2rem; }
        main { padding: .75rem; }
        .song, .report { padding: 1rem; }
        .song nav { display: grid; grid-template-columns: 1fr; }
        .song .button { text-align: center; }
      }
"""


def song_title(song_path: Path) -> str:
    """Return a song's ChordPro title, falling back to its filename."""
    with song_path.open(encoding="utf-8") as song_file:
        for line in song_file:
            match = TITLE_DIRECTIVE.match(line)
            if match and match.group(1):
                return match.group(1)

    return song_path.stem.replace("_", " ").strip().title()


def report_url(repository: str, song_path: Path, title: str) -> str:
    body = (
        f"{REPORT_MARKER}\n"
        f"**Laul:** {title}\n"
        f"**Fail:** `songs/{song_path.name}`\n\n"
        "## Mida tuleks parandada?\n\n"
        "Kirjelda viga ja soovitud parandust võimalikult täpselt."
    )
    query = urlencode({"title": f"Parandus: {title}", "body": body})
    return f"https://github.com/{repository}/issues/new?{query}"


def song_card(song_path: Path, output_dir: Path, repository: str) -> str:
    title = song_title(song_path)
    links = []
    for label, suffix in PDF_VARIANTS:
        pdf_name = f"{song_path.stem}-{suffix}.pdf"
        if not (output_dir / pdf_name).is_file():
            raise FileNotFoundError(f"Expected generated PDF is missing: {pdf_name}")
        links.append(
            f'<a class="button" href="{quote(pdf_name)}">{html.escape(label)}</a>'
        )

    links.append(
        '<a class="button button-secondary" '
        f'href="{html.escape(report_url(repository, song_path, title), quote=True)}">'
        "Teata parandusest</a>"
    )
    return (
        '      <article class="song">\n'
        f"        <h2>{html.escape(title)}</h2>\n"
        f'        <nav aria-label="Toimingud: {html.escape(title)}">'
        f"{' '.join(links)}</nav>\n"
        "      </article>"
    )


def index_page(cards: str) -> str:
    return f"""<!doctype html>
<html lang="et">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="TAMROCK laulik kitarri ja vokaali PDF-idega.">
    <title>TAMROCK laulik</title>
    <style>{STYLES}    </style>
  </head>
  <body>
    <header>
      <h1>TAMROCK laulik</h1>
      <a class="header-link" href="reports.html">Vaata parandusteateid</a>
    </header>
    <main class="song-grid">
{cards}
    </main>
  </body>
</html>
"""


def reports_page(repository: str) -> str:
    repository_json = json.dumps(repository)
    marker_json = json.dumps(REPORT_MARKER)
    github_reports_url = (
        f"https://github.com/{repository}/issues?q=is%3Aissue+"
        f'in%3Abody+%22tamrock-song-report%22'
    )
    return f"""<!doctype html>
<html lang="et">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="TAMROCK lauliku parandusteated.">
    <title>Parandusteated – TAMROCK laulik</title>
    <style>{STYLES}    </style>
  </head>
  <body>
    <header>
      <h1>Parandusteated</h1>
      <a class="header-link" href="index.html">Tagasi laulude juurde</a>
    </header>
    <main>
      <p id="loading" class="loading" role="status">Laadin parandusteateid…</p>
      <section id="reports" class="reports" aria-live="polite"></section>
      <noscript>
        <p class="empty-state">Teadete kuvamiseks luba JavaScript või
          <a href="{html.escape(github_reports_url, quote=True)}">vaata neid GitHubis</a>.
        </p>
      </noscript>
    </main>
    <script>
      const repository = {repository_json};
      const reportMarker = {marker_json};
      const reportsElement = document.querySelector("#reports");
      const loadingElement = document.querySelector("#loading");

      function addTextElement(parent, tag, text, className) {{
        const element = document.createElement(tag);
        element.textContent = text;
        if (className) element.className = className;
        parent.append(element);
        return element;
      }}

      function renderReport(issue) {{
        const article = document.createElement("article");
        article.className = "report";
        const heading = document.createElement("h2");
        const link = document.createElement("a");
        link.href = issue.html_url;
        link.textContent = issue.title;
        heading.append(link);
        article.append(heading);

        const metadata = document.createElement("p");
        metadata.className = "report-meta";
        addTextElement(
          metadata,
          "span",
          issue.state === "open" ? "Avatud" : "Suletud",
          issue.state === "open" ? "status" : "status status-closed"
        );
        const date = new Intl.DateTimeFormat("et-EE", {{ dateStyle: "medium" }})
          .format(new Date(issue.created_at));
        addTextElement(metadata, "span", `#${{issue.number}} · ${{date}}`);
        article.append(metadata);
        reportsElement.append(article);
      }}

      async function loadReports() {{
        const reports = [];
        let page = 1;
        while (true) {{
          const apiUrl = `https://api.github.com/repos/${{repository}}/issues` +
            `?state=all&sort=created&direction=desc&per_page=100&page=${{page}}`;
          const response = await fetch(apiUrl, {{
            headers: {{ Accept: "application/vnd.github+json" }}
          }});
          if (!response.ok) throw new Error(`GitHub API: ${{response.status}}`);
          const issues = await response.json();
          reports.push(...issues.filter(issue =>
            !issue.pull_request && issue.body && issue.body.includes(reportMarker)
          ));
          if (issues.length < 100) break;
          page += 1;
        }}
        loadingElement.remove();
        if (reports.length === 0) {{
          addTextElement(reportsElement, "p", "Parandusteateid veel ei ole.", "empty-state");
          return;
        }}
        reports.forEach(renderReport);
      }}

      loadReports().catch(() => {{
        loadingElement.remove();
        const message = addTextElement(
          reportsElement,
          "p",
          "Parandusteadete laadimine ebaõnnestus. ",
          "empty-state"
        );
        const link = document.createElement("a");
        link.href = {json.dumps(github_reports_url)};
        link.textContent = "Vaata teateid GitHubis.";
        message.append(link);
      }});
    </script>
  </body>
</html>
"""


def build_site(songs_dir: Path, output_dir: Path, repository: str) -> None:
    songs = sorted(songs_dir.glob("*.cho"), key=lambda path: song_title(path).casefold())
    if not songs:
        raise FileNotFoundError(f"No .cho files found in {songs_dir}")

    cards = "\n".join(song_card(song, output_dir, repository) for song in songs)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(index_page(cards), encoding="utf-8")
    (output_dir / "reports.html").write_text(
        reports_page(repository), encoding="utf-8"
    )
    (output_dir / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("songs_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    args = parser.parse_args()
    build_site(args.songs_dir, args.output_dir, args.repository)


if __name__ == "__main__":
    main()
