# Brand Deals App — Project Context

> **For future Claude:** Read this first before doing any work in this folder. It's the condensed handoff from prior conversations. Last updated 2026-05-23.

---

## 1. TL;DR

A Streamlit-based mobile-optimised brand deals + ad revenue tracker for **Priya Sid Enterprise (PSE)**. Live deployed on Streamlit Cloud, backed by a Google Sheet, installed as a PWA on Sid's iPhone home screen.

- **Live app:** https://priya-sid-brand-deals.streamlit.app (alias of `brand-deals-app-wsgyzelzotxtxm7qtzuefl.streamlit.app`)
- **GitHub repo (public):** `sidmadiwale-rgb/brand-deals-app`
- **Google Sheet:** https://docs.google.com/spreadsheets/d/1KywyIay918fxbY-GjTe2QGwwS5Vzek2ALxFN-QK2Ujk/edit  (ID: `1KywyIay918fxbY-GjTe2QGwwS5Vzek2ALxFN-QK2Ujk`)
- **Deploy mechanism:** GitHub push → Streamlit Cloud auto-redeploys
- **Login:** password gate, stored in Streamlit Cloud secrets

---

## 2. App architecture

Single-file Streamlit app (`app.py`, ~976 lines) with five tabs:

| Tab | Purpose |
|---|---|
| Overview | Summary tiles (gross, net, AUD totals, commission, TDS), period filter pill |
| Brand Deals | Card list of every deal, click a card to edit via dialog |
| Charts | Plotly bar charts grouped by month / brand |
| Ad Revenue | Per-month YouTube (AUD) + Facebook (USD) revenue, click month to edit |
| Add | Form to create a new deal, saves to Google Sheet |

**Design system (Mercury Dark theme):**
- Background `#0A0A0A` · Cards `#18181B` · Borders `#27272A`
- Text `#FAFAFA` · Muted `#A1A1AA` · Accent peach `#E89E7E`
- Defined in `.streamlit/config.toml` plus inline CSS in `app.py`

---

## 3. File map

```
2026-05-12-brand-deals-app/
├── app.py                          # Main Streamlit app (~976 lines)
├── CONTEXT.md                      # This file
├── requirements.txt                # streamlit, gspread, plotly, pillow, pandas
├── .streamlit/
│   └── config.toml                 # Theme + enableStaticServing = true
└── static/
    ├── apple-touch-icon.png        # 180x180 PSE B&W logo
    ├── icon-192.png                # PWA
    ├── icon-512.png                # PWA
    ├── favicon.png
    ├── manifest.json               # PWA manifest
    ├── PSE Logo .png               # Source logo (500x500)
    └── PSE Logo BG Removed.png     # Source logo (transparent)
```

**Important:** `app.py` lives at the **root** of the repo, NOT inside a wrapper folder. A past deploy disaster was caused by uploading the whole folder and ending up with `2026-05-12-brand-deals-app/app.py` in the repo — Streamlit Cloud couldn't find the main module. Always upload contents flat to repo root.

---

## 4. Data model (Google Sheet tabs)

| Tab | Columns (key ones) |
|---|---|
| `Deals Log` | FY, Status, Month, Region, Brand, Agency, Currency, Gross (orig), Commission %, Invoice #, Deliverables |
| `Ad Revenue` | Month, YouTube AUD, Facebook USD |
| `FX Rates` | Code, Currency, Rate  — **fallback only**, see §6 |

**Currency handling:** Every deal stores its `Gross (orig)` in the **original currency** (AUD/USD/AED/INR). FX conversion happens at display/calc time only — the stored value is never overwritten by FX changes.

---

## 5. Secrets / credentials

Configured in Streamlit Cloud → app settings → Secrets:

```toml
APP_PASSWORD = "<the login password>"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "...@....iam.gserviceaccount.com"
# ...etc
```

Service account email has Editor access to the Google Sheet.

---

## 6. Live FX rates (added 2026-05-23)

`load_fx_rates()` fetches live rates from `https://open.er-api.com/v6/latest/AUD` (free, no API key). Caches for **1 hour**.

**Fallback chain:**
1. Live API (`_fetch_live_fx()`)
2. Google Sheet "FX Rates" tab (`_load_fx_from_sheet()`)
3. Hardcoded defaults: `{"USD": 1.3807, "AED": 0.376, "INR": 0.014614}`

The sheet rates and hardcoded defaults are stale by design — they're only safety nets.

---

## 7. Performance optimisations in place

- `@st.cache_data(ttl=300)` on `process_deals(deals_raw, fx_rates)`
- `@st.cache_data(ttl=300)` on `process_ad_revenue(ad_rev_raw)`
- `@st.cache_data(ttl=3600)` on `load_fx_rates()`
- These re-run only when inputs change or cache is cleared after a save

If user reports lag again, options discussed were: (a) further reduce gspread calls, (b) migrate to Next.js (~half day of work for a real native-feeling app — see §10).

---

## 8. PWA / home screen icon

- Apple-touch-icon hosted at GitHub raw URL, injected via `streamlit.components.v1.html` JS that writes into the parent document `<head>`
- Manifest at `/app/static/manifest.json`
- Browser tab favicon: embedded base64 PIL image via `st.set_page_config(page_icon=...)`

**Known issue (unresolved):** iOS Safari refuses to use the custom favicon and still shows Streamlit's red default in tab + Add-to-Home-Screen preview. Same URL on desktop browsers correctly shows PSE logo. Determined to be a Streamlit Cloud `/favicon.ico` precedence bug on iOS Safari specifically. User chose to **accept the default for now** rather than migrate platforms.

---

## 9. Pitfalls & gotchas

1. **OneDrive sync truncation** — the project folder lives under OneDrive. Direct Edit/Write of large files often syncs partial content, leaving `app.py` ending mid-line with syntax errors. **Workaround:** edit in `/tmp/`, verify with `ast.parse`, then `cp` back to OneDrive atomically. There are backup copies at `/tmp/app_v2.py` and `/sessions/.../outputs/app.py`.
2. **Deploy wrapper folder** — never upload the whole `2026-05-12-brand-deals-app/` folder to the repo. Upload files individually at the repo root.
3. **`.streamlit/config.toml` skipped by GitHub web uploader** — dot-prefixed folders get skipped. Use GitHub web UI → "Add file → Create new file" → type `.streamlit/config.toml` (slash creates folder) → paste content.
4. **Editing on iOS** — user uses GitHub.dev (press `.` on the repo page) as a web VS Code editor when needed.

---

## 10. Future direction options discussed

- **Native (Swift/React Native):** rejected — too much maintenance overhead for solo iteration.
- **Next.js migration:** ~half day of Claude's work, ~30 min user time. Would fix the iOS favicon bug and make the app feel native (no Streamlit lag, real PWA). Bring up if user gets fed up with Streamlit performance or icon issue.

---

## 11. User preferences (Sid)

These are explicit, repeated requests across the project — honour them strictly:

- **Ask questions one at a time** when needing input. Don't bundle 3 questions into one message.
- **Outline the plan and wait for approval** before executing multi-step work.
- **Show what will change before overwriting/deleting** any existing file.
- **At end of task,** list all files created/modified with their full paths.
- **Naming convention** for new artifact files: `YYYY-MM-DD-descriptive-name`. (Stable reference files like this `CONTEXT.md` are exempt.)
- **Don't modify files outside the current working folder** unless explicitly asked.
- **Don't redo work that was just caused by Claude's mistake** — own it and fix it without making the user re-do steps.

---

## 12. Open threads (as of 2026-05-23)

- iOS Safari favicon bug — accepted, not fixed. Tab + Add-to-Home-Screen preview show Streamlit red logo on iPhone only.
- Biometric/Face ID login via Safari Passwords app — instructions given, completion status unconfirmed.
- Live FX rates just shipped (2026-05-23) — needs real-world verification on next app open.

---

## 13. Where the conversation history lives

Full prior transcripts (pre-this-doc):
`C:\Users\sidma\AppData\Roaming\Claude\local-agent-mode-sessions\c2e360c4-5087-46cb-aebc-7beea9d6f143\c52b5fe0-95ad-4bed-b88b-c197b6d3dddc\local_b9fe15a3-a373-4839-bbbe-cf519bfca89d\.claude\projects\`

Only relevant for forensic deep-dives — this CONTEXT.md should be sufficient for normal handoff.
