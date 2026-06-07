# ⚔️ Albion Master — Streamer Build Roulette & Challenge Generator

A lightweight, zero-cost Streamlit web app that generates random Albion Online
loadouts + high-stakes challenges for streamers and gamers. Built to be
window-captured in OBS as a stream overlay.

> **Project Constraint:** Fully self-contained in this `Albion/` folder.
> Does NOT touch the Gold Bot (`Riko_Genesis/`) or any trading data. P2 priority.

## Features
- **SPIN Engine** — weighted randomizer for Main Hand, Off-Hand, Head, Chest,
  Shoes, and Cape. Enforces the rule: a 2-Handed main weapon removes the off-hand.
- **Suspense Spin** — a 2-3s "Praying to the RNG Gods..." animation before the
  reveal, built for live-stream hype.
- **Inventory Cross-Layout** — slots arranged like the in-game paper-doll
  (Head on top, Main/Chest/Off/Cape in the middle, Shoes at the bottom).
- **Single-Slot Reroll** — a small Reroll button under every slot to change just
  one item (great for Twitch channel-point redemptions).
- **Real Item Art** — live images from the official Albion Render API.
- **Content Hook** — random gameplay challenge (with its own reroll).
- **Viral Export** — one-click "Copy Build to Clipboard" with a Ko-fi promo
  footer, plus a separate plain-text export for AI (Gemini / ChatGPT).
- **Obsidian-Dark UI** — high contrast, large text, OBS-friendly.
- **Monetization** — Ko-fi tip button + Google AdSense placeholder.

## Verify item accuracy
After adding/editing items, confirm every name matches its art:
```bash
python verify_items.py
```

## Run locally
```bash
cd Albion
pip install -r requirements.txt
streamlit run app_roulette.py
```
Open http://localhost:8501

## Configure (before deploy)
Edit the top of `app_roulette.py`:
- `KOFI_URL` — your Ko-fi / Buy Me a Coffee page.
- `ADSENSE_CLIENT` — your `ca-pub-XXXX` id once AdSense is approved.

## Deploy (Free Tier, $0)
**Streamlit Community Cloud**
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io → New app.
3. Main file path: `Albion/app_roulette.py`.

## Adding more items
All datasets are hardcoded Python lists near the top of `app_roulette.py`
(`MAIN_HANDS`, `OFF_HANDS`, `ARMOR_*`, `CAPES`, `CHALLENGES`).
Each entry has a `weight` controlling its roll chance. No database needed.
