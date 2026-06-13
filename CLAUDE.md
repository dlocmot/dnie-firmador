# dnie-firmador — Project Context for Claude

## What this project is

Linux desktop app to sign PDFs with the Peruvian DNIe (electronic ID card) — a open-source alternative to RENIEC's Refirma (Windows-only). The goal is to replicate Refirma's visual signature stamp and UX on Debian/Ubuntu.

## Key decisions already made

### Architecture: Approach A — PyQt6 + pyHanko interrupted signing + pyscard direct
- **No OpenSC** — the Peruvian DNIe v2 ATR (`3B:DC:18:FF:81:91:FE:1F:C3:80:73:C8:21:13:66:05:03:63:51:00:02:50`) is NOT recognized by OpenSC (Issue #1147). We talk to the card directly via pyscard APDUs.
- **pyHanko interrupted signing** — pyHanko prepares the PDF and returns a hash → pyscard signs the hash with the DNIe private key → pyHanko embeds the signature. No PKCS#11 module needed.
- **PyQt6** for GUI, **PyMuPDF (fitz)** for PDF rendering and interactive signature placement.

### Stack
| Layer | Library |
|---|---|
| Card communication | `pyscard` (direct APDU to DNIe) |
| PDF signing | `pyHanko[pkcs11]` (interrupted signing mode) |
| PDF rendering | `PyMuPDF` (fitz) |
| GUI | `PyQt6` |
| Signature rendering | `Pillow` + `cairosvg` |
| Certificate parsing | `cryptography` |

### Why not JSignPDF / AutoFirma
Tested on the user's machine — OpenSC says "token not recognized" for the Peruvian DNIe. JSignPDF depends on OpenSC, so it fails at the card layer before even signing.

### Why not a custom PKCS#11 wrapper (Approach B)
Would require writing a C `.so` — too much complexity for now. The interrupted signing approach avoids it entirely. Can be added later if needed for ecosystem compatibility.

## Hardware confirmed working
- **Reader:** bit4id miniLector-EVO (detected by pcscd as `bit4id miniLector-EVO 00 00`)
- **Card:** DNIe Perú v2, ATR: `3B:DC:18:FF:81:91:FE:1F:C3:80:73:C8:21:13:66:05:03:63:51:00:02:50`
- **OS:** Debian 13 (trixie)

## Signature appearance (Refirma-compatible)
Rectangular stamp with red border:
- **Left:** Escudo Nacional del Perú (SVG, public domain, Wikimedia) + "FIRMA DIGITAL" label
- **Right:** "Firmado digitalmente por: NOMBRE APELLIDO DNI hard", Motivo, Fecha con zona horaria
- Both the image and the text fields are configurable (custom image supported)
- The escudo SVG is at `src/dnie_firmador/assets/escudo.svg`

## Project structure
```
src/dnie_firmador/
├── card/
│   ├── reader.py       # Detects reader, validates DNIe ATR
│   ├── dnie.py         # APDU: read cert, verify PIN, sign hash
│   └── exceptions.py   # CardNotFoundError, PinError, etc.
├── signing/
│   ├── signer.py       # pyHanko orchestration (prepare → sign → embed)
│   └── appearance.py   # Renders Refirma-compatible visual stamp
├── ui/
│   ├── main_window.py  # Main window, wires all layers
│   ├── pdf_viewer.py   # Scrollable PDF with drag-to-place signature rect
│   ├── sig_config.py   # Appearance config panel
│   └── pin_dialog.py   # Secure PIN dialog
└── assets/
    └── escudo.svg      # Escudo Nacional del Perú (public domain)
```

## Current status (2026-06-12)
- [x] Project scaffolded and pushed to GitHub (https://github.com/dlocmot/dnie-firmador)
- [x] All source files created (card, signing, UI layers)
- [ ] Dependencies not yet installed — blocked on system packages
- [ ] Card layer not yet tested with real DNIe
- [ ] pyHanko interrupted signing API calls need validation against current pyHanko version (0.35.x) — the API may differ from the stub in `signer.py`
- [ ] UI not yet launched or tested

## Pending: install dependencies
The venv install failed because `libpcsclite-dev` and `swig` were missing:
```bash
sudo apt install -y libpcsclite-dev swig
cd /home/jfqp/Documents/GitHub/dnie-firmador
.venv/bin/pip install -e ".[dev]"
```

## Critical unknown: APDU commands
The APDU sequences in `card/dnie.py` are based on the `edeustua/peru-dnie` project pattern but have NOT been tested yet. This is the highest-risk component. If the APDUs don't match the card's actual protocol, the card layer will fail. Reference: https://github.com/edeustua/peru-dnie

## Critical unknown: pyHanko interrupted signing API
`signing/signer.py` uses `signers.sign_pdf_prepare` and `signers.sign_pdf_embed` — these names need to be verified against pyHanko 0.35.x docs. The actual API for interrupted/external signing may differ. Check: https://pyhanko.readthedocs.io

## Reference projects
- https://github.com/edeustua/peru-dnie — Peruvian DNIe pyscard communication
- https://github.com/MatthiasValvekens/pyHanko — PDF signing backend
- https://github.com/schorschii/Simple-Signer — Simple Linux PDF signer (Qt, no smart card)
- https://github.com/open-eid/DigiDoc4-Client — Production-grade eID desktop app (architectural reference)

## What NOT to do
- Do not use OpenSC's pkcs11 module — it doesn't recognize the Peruvian DNIe
- Do not publish or commit anything from `/home/jfqp/Documents/GitHub/refirma_Linux/` — private reference screenshots
- Do not add Windows-specific code or dependencies
