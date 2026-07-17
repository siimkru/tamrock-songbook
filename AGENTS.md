# Repository Guidelines

## Project Structure & Module Organization

This repository is a ChordPro songbook for Rattalaagri band. Song sources live in `songs/` as `*.cho`; use lowercase, underscore-separated filenames such as `oma_laulu_ei_leia_ma_ules.cho`. The three instrument-specific ChordPro configurations live in `config/`. Google Drive integration lives in `scripts/`, while CI build and upload behavior is defined in `.github/workflows/main.yml`. Generated PDFs belong in the ignored `build/` directory.

## Build, Test, and Development Commands

Generate a PDF locally with Docker (replace the config and output name as needed):

```bash
docker run --rm -v "$(pwd):/app" -w /app chordpro/chordpro \
  chordpro --config=config/guitar.json \
  -o build/song-Kitarr.pdf songs/song.cho
```

On macOS with ChordPro installed, use:

```bash
/Applications/ChordPro.app/Contents/Resources/cli/chordpro \
  --config config/lyrics.json --output build/vocals.pdf songs/*.cho
```

Install Drive dependencies with `python -m pip install -r requirements.txt`, then upload using `python3 scripts/upload_to_drive.py <pdf> <folder-id>`. Run `python3 scripts/generate_token.py` only when provisioning credentials.

## Coding Style & Naming Conventions

Keep ChordPro directives consistent with existing files: begin with `{title: ...}`, add `{artist: ...}` when known, place chords inline as `[Am]`, and label sections with `{comment: Intro}` or paired verse/chorus directives. Preserve Estonian spelling and UTF-8 text. Use four-space indentation, snake_case names, and PEP 8 conventions in Python. Keep configuration formatting aligned with the surrounding JSON-like ChordPro syntax.

## Testing Guidelines

There is no automated test suite or coverage target. Before submitting a song or configuration change, render it with all three configurations and inspect the PDFs for clipped text, incorrect page breaks, misplaced chords, and unwanted diagrams. For Python-only edits, run `python3 -m py_compile scripts/upload_to_drive.py scripts/generate_token.py`. Do not perform a real Drive upload unless explicitly testing integration credentials.

## Commit & Pull Request Guidelines

Recent history mainly uses short messages such as `update`; no formal convention is established. Prefer specific imperative subjects, for example `Add chords for Kõnõtraat` or `Fix keyboard diagram layout`. Pull requests should summarize changed songs/configurations, list the render commands used, and attach sample PDF pages or screenshots when layout changes. Note any Drive workflow impact and link the relevant issue when one exists.

## Security & Configuration

Never commit OAuth client secrets, refresh tokens, folder IDs, or generated PDFs. Supply `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET`, and `GDRIVE_REFRESH_TOKEN` through environment variables or GitHub Actions secrets. Treat `client_secret.json` as local sensitive material.
