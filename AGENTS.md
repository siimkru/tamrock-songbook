# Repository Guidelines

## Project Structure & Module Organization

This repository contains the TamRock ChordPro songbook. Song sources live in `songs/` as `*.cho`; use lowercase, underscore-separated filenames such as `oma_laulu_ei_leia_ma_ules.cho`. Instrument-specific ChordPro configurations are in `config/` (`guitar.json`, `keyboard.json`, and `lyrics.json`). Google Drive utilities live in `scripts/`, and CI build/upload behavior is defined in `.github/workflows/main.yml`. Put generated PDFs in the ignored `build/` directory.

## Build, Test, and Development Commands

Create `build/`, then render a song with Docker:

```bash
mkdir -p build
docker run --rm -v "$(pwd):/app" -w /app chordpro/chordpro \
  chordpro --config=config/guitar.json \
  --output=build/heiki-Kitarr.pdf songs/heiki.cho
```

On macOS with ChordPro installed, render all songs with:

```bash
/Applications/ChordPro.app/Contents/Resources/cli/chordpro \
  --config config/lyrics.json --output build/vocals.pdf songs/*.cho
```

Install Drive dependencies with `python -m pip install -r requirements.txt`. Upload with `python scripts/upload_to_drive.py <pdf> <folder-id> <type>`. Run `python scripts/generate_token.py` only when provisioning credentials.

## Coding Style & Naming Conventions

Start song files with `{title: ...}` and add `{artist: ...}` when known. Place chords inline, for example `[Am]`, and label sections with directives such as `{comment: Intro}`. Preserve Estonian spelling and UTF-8 text. For Python, use four-space indentation, snake_case names, and PEP 8 conventions. Match the surrounding JSON-like formatting in configuration files.

## Testing Guidelines

There is no automated test suite or coverage target. Render song and configuration changes with all three configurations, then inspect PDFs for clipped text, incorrect page breaks, misplaced chords, and unwanted diagrams. For Python edits, run `python3 -m py_compile scripts/upload_to_drive.py scripts/generate_token.py`. Do not perform a real Drive upload unless explicitly testing credentials.

## Commit & Push Guidelines

History uses brief messages and has no formal convention. Prefer specific imperative subjects such as `Add chords for Kõnõtraat`. Do not create pull requests or dedicated PR branches. When explicitly asked to commit and push, use the currently checked-out branch.

## Security & Configuration

Never commit OAuth secrets, refresh tokens, folder IDs, `client_secret.json`, or generated PDFs. Supply Drive credentials through environment variables or GitHub Actions secrets.
