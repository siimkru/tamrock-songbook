# TAMROCK songbook

ChordPro sources and instrument-specific layouts for the TAMROCK songbook.
Commits to `main` generate PDFs for changed songs and upload them to Google
Drive through GitHub Actions.

## Repository layout

```text
songs/       ChordPro song sources
config/      Guitar, keyboard, and lyrics layouts
scripts/     Google Drive OAuth and upload utilities
build/       Locally generated PDFs (ignored by Git)
```

## Render a song

With Docker:

```bash
mkdir -p build
docker run --rm -v "$(pwd):/app" -w /app chordpro/chordpro \
  chordpro --config=config/guitar.json \
  --output=build/heiki-Kitarr.pdf songs/heiki.cho
```

On macOS with ChordPro installed:

```bash
mkdir -p build
/Applications/ChordPro.app/Contents/Resources/cli/chordpro \
  --config config/lyrics.json \
  --output build/vocals.pdf songs/*.cho
```

Render changes with all three files in `config/` before submitting them and
inspect the PDFs for clipping, page breaks, chord placement, and diagrams.

## Google Drive tooling

Install dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Upload a rendered PDF:

```bash
python scripts/upload_to_drive.py build/heiki-Kitarr.pdf <folder-id> Kitarr
```

The uploader reads `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET`, and
`GDRIVE_REFRESH_TOKEN` from the environment. For initial OAuth provisioning,
place the downloaded credentials in the ignored root file
`client_secret.json`, then run `python scripts/generate_token.py`.
