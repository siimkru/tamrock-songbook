#!/usr/bin/env python3
"""Build the static index for the GitHub Pages PDF songbook."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.parse import quote


TITLE_DIRECTIVE = re.compile(r"^\s*\{title\s*:\s*(.*?)\s*\}\s*$", re.IGNORECASE)
PDF_VARIANTS = (
    ("Kitarr", "Kitarr"),
    ("Ainult sõnad", "Ainult_sonad"),
)


def song_title(song_path: Path) -> str:
    """Return a song's ChordPro title, falling back to its filename."""
    with song_path.open(encoding="utf-8") as song_file:
        for line in song_file:
            match = TITLE_DIRECTIVE.match(line)
            if match and match.group(1):
                return match.group(1)

    return song_path.stem.replace("_", " ").strip().title()


def song_card(song_path: Path, output_dir: Path) -> str:
    title = song_title(song_path)
    links = []
    for label, suffix in PDF_VARIANTS:
        pdf_name = f"{song_path.stem}-{suffix}.pdf"
        if not (output_dir / pdf_name).is_file():
            raise FileNotFoundError(f"Expected generated PDF is missing: {pdf_name}")
        links.append(
            f'<a href="{quote(pdf_name)}">{html.escape(label)}</a>'
        )

    return (
        '      <article class="song">\n'
        f"        <h2>{html.escape(title)}</h2>\n"
        f'        <nav aria-label="PDF-id: {html.escape(title)}">'
        f"{' '.join(links)}</nav>\n"
        "      </article>"
    )


def build_index(songs_dir: Path, output_dir: Path) -> None:
    songs = sorted(songs_dir.glob("*.cho"), key=lambda path: song_title(path).casefold())
    if not songs:
        raise FileNotFoundError(f"No .cho files found in {songs_dir}")

    cards = "\n".join(song_card(song, output_dir) for song in songs)
    page = f"""<!doctype html>
<html lang="et">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="TAMROCK laulik kitarri ja vokaali PDF-idega.">
    <title>TAMROCK laulik</title>
    <style>
      :root {{ color-scheme: light; font-family: system-ui, -apple-system, sans-serif; }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; color: #17202a; background: #f4f6f7; }}
      header {{ padding: 2.5rem 1rem 2rem; color: white; background: #244b3c; text-align: center; }}
      h1 {{ margin: 0 0 .5rem; font-size: clamp(2rem, 7vw, 3.5rem); }}
      main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); gap: 1rem; width: min(70rem, 100%); margin: auto; padding: 1.25rem; }}
      .song {{ padding: 1.25rem; border: 1px solid #d9e0dd; border-radius: .75rem; background: white; box-shadow: 0 2px 8px rgb(0 0 0 / 6%); }}
      h2 {{ margin: 0 0 1rem; font-size: 1.25rem; }}
      nav {{ display: flex; flex-wrap: wrap; gap: .6rem; }}
      a {{ display: inline-block; padding: .65rem .85rem; border-radius: .45rem; color: white; background: #376f5a; font-weight: 650; text-decoration: none; }}
      a:hover, a:focus-visible {{ background: #244b3c; text-decoration: underline; }}
      @media (max-width: 32rem) {{
        header {{ padding-top: 2rem; }}
        main {{ padding: .75rem; }}
        .song {{ padding: 1rem; }}
        nav {{ display: grid; grid-template-columns: 1fr; }}
        a {{ text-align: center; }}
      }}
    </style>
  </head>
  <body>
    <header>
      <h1>TAMROCK laulik</h1>
    </header>
    <main>
{cards}
    </main>
  </body>
</html>
"""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    (output_dir / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("songs_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    build_index(args.songs_dir, args.output_dir)


if __name__ == "__main__":
    main()
