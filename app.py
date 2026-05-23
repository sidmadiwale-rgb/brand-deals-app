"""
Priya Sid Enterprise — Brand Deals Tracker
Streamlit app, Mercury Dark theme, live Google Sheets.
"""

import base64
import io
import json
import urllib.request
import urllib.error
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from collections import defaultdict
from PIL import Image

# Icon embedded as base64 (for browser tab favicon) + hosted at GitHub for iOS apple-touch-icon.
_ICON_BASE64 = "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"
_ICON_REMOTE_URL = "https://raw.githubusercontent.com/sidmadiwale-rgb/brand-deals-app/main/static/apple-touch-icon.png"

try:
    _PAGE_ICON = Image.open(io.BytesIO(base64.b64decode(_ICON_BASE64)))
except Exception:
    _PAGE_ICON = "\U0001F4CA"

st.set_page_config(page_title="Brand Deals", page_icon=_PAGE_ICON,
                    layout="centered", initial_sidebar_state="collapsed")

# iOS Safari ignores apple-touch-icon links injected into <body> via st.markdown, AND
# refuses data-URL apple-touch-icons. The reliable fix is to inject a real URL link
# into <head> via a tiny iframe component (whose script can reach the parent document).
_INJECT_HTML = """
<script>
(function() {
    try {
        var head = window.parent.document.head;
        if (!head) return;
        head.querySelectorAll('link[rel="apple-touch-icon"], link[rel="apple-touch-icon-precomposed"]').forEach(function(el){ el.remove(); });
        var apple = window.parent.document.createElement('link');
        apple.rel = 'apple-touch-icon';
        apple.sizes = '180x180';
        apple.href = '__REMOTE_URL__';
        head.appendChild(apple);
        var theme = head.querySelector('meta[name="theme-color"]');
        if (!theme) {
            theme = window.parent.document.createElement('meta');
            theme.name = 'theme-color';
            head.appendChild(theme);
        }
        theme.content = '#0A0A0A';
        var mobile = head.querySelector('meta[name="apple-mobile-web-app-capable"]');
        if (!mobile) {
            mobile = window.parent.document.createElement('meta');
            mobile.name = 'apple-mobile-web-app-capable';
            mobile.content = 'yes';
            head.appendChild(mobile);
        }
        var title = head.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (!title) {
            title = window.parent.document.createElement('meta');
            title.name = 'apple-mobile-web-app-title';
            title.content = 'Brand Deals';
            head.appendChild(title);
        }
    } catch(e) { console.error('icon inject failed:', e); }
})();
</script>
"""
components.html(_INJECT_HTML.replace("__REMOTE_URL__", _ICON_REMOTE_URL), height=0)

SHEET_ID = "1KywyIay918fxbY-GjTe2QGwwS5Vzek2ALxFN-QK2Ujk"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme")
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.47.0/tabler-icons.min.css">
<style>
.stApp,.main{background:#0A0A0A!important}
.block-container{max-width:480px!important;padding-top:1rem;padding-bottom:5rem}
html,body,[class^="css"]{color:#FAFAFA;font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif}
#MainMenu,footer,header,.stDeployButton{visibility:hidden!important;display:none!important}
div[data-testid="stToolbar"]{display:none!important}
.brand{font-size:10.5px;font-weight:500;color:#A1A1AA;letter-spacing:1.5px;text-transform:uppercase;margin:0}
.app-name{font-family:'Helvetica Neue','Helvetica','Inter',sans-serif;font-size:20px;font-weight:600;color:#FAFAFA;letter-spacing:-0.5px;margin:8px 0 10px;line-height:1.0}
.period-pill{display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:6px;font-size:11px;font-weight:500;margin:0}
.pp-fy{background:#0F2547;border:0.5px solid #1E40AF;color:#93C5FD}
.pp-quarter{background:#1E1B0B;border:0.5px solid #84671A;color:#FBBF24}
.pp-calendar{background:#052E2A;border:0.5px solid #047857;color:#6EE7B7}
.section-label{font-size:11px;font-weight:500;color:#A1A1AA;letter-spacing:0.4px;text-transform:uppercase;margin:18px 0 10px}
.kpi{background:#18181B;border:0.5px solid #27272A;border-radius:14px;padding:14px 14px 16px;margin-bottom:10px;min-height:96px}
.kpi-label{font-size:11px;color:#A1A1AA;font-weight:500;margin-bottom:6px;letter-spacing:0.2px}
.kpi-value{font-size:22px;font-weight:500;color:#FAFAFA;letter-spacing:-0.6px;line-height:1.1}
.kpi-sub{font-size:10.5px;color:#A1A1AA;margin-top:6px;font-weight:400;line-height:1.3}
.accent-green{color:#10B981;font-weight:500}
.status-card{background:#18181B;border:0.5px solid #27272A;border-radius:14px;margin-bottom:8px;padding:14px 16px;display:flex;align-items:center;justify-content:space-between}
.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:12px;vertical-align:middle}
.status-name{font-size:14px;font-weight:500;color:#FAFAFA}
.status-count{font-size:11px;color:#A1A1AA;margin-top:2px;margin-left:20px}
.status-amount{font-size:15px;font-weight:500;color:#FAFAFA;letter-spacing:-0.2px;white-space:nowrap}
.summary-row{display:flex;justify-content:space-between;align-items:center;background:#18181B;border:0.5px solid #27272A;border-radius:14px;margin-top:8px;padding:14px 16px}
.pill{display:inline-block;padding:2px 7px;border-radius:6px;font-size:10px;font-weight:500;letter-spacing:0.1px;margin-left:4px}
.pill-paid{background:#052E2A;color:#34D399}
.pill-invoiced-india{background:#3A2410;color:#FB923C}
.pill-invoiced-nonindia{background:#0F2547;color:#60A5FA}
.pill-not-invoiced{background:#3D2F08;color:#FACC15}
.pill-locked{background:#3A1313;color:#F87171}
.pill-pitched{background:#262626;color:#A1A1AA}
.deal-card{background:#18181B;border:0.5px solid #27272A;border-radius:12px;margin-bottom:4px;padding:12px 14px}
div[data-baseweb="select"]>div{background:#18181B!important;border:0.5px solid #27272A!important;color:#FAFAFA!important}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:#18181B!important;border:0.5px solid #27272A!important;color:#FAFAFA!important}
.stButton button{background:#18181B!important;color:#A1A1AA!important;border:0.5px solid #27272A!important;border-radius:10px!important;padding:8px 14px!important;font-weight:500!important;font-size:12px!important}
.stButton button:hover{background:#27272A!important;border-color:#3F3F46!important;color:#FAFAFA!important}
.stButton button[kind="primary"]{background:#FAFAFA!important;color:#0A0A0A!important;border:none!important;padding:10px 16px!important;font-size:13px!important}
.stButton button[kind="primary"]:hover{background:#E5E5E5!important;color:#0A0A0A!important}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:transparent;border-bottom:0.5px solid #27272A;padding-bottom:0}
.stTabs [data-baseweb="tab"]{background:transparent;border:none;color:#A1A1AA;padding:8px 12px;font-size:12px;font-weight:500}
.stTabs [aria-selected="true"]{background:transparent!important;color:#FAFAFA!important;border-bottom:2px solid #FAFAFA!important}
.total-card{background:#18181B;border:0.5px solid #27272A;border-radius:14px;margin-bottom:14px;padding:18px 18px}
.total-label{font-size:10.5px;color:#A1A1AA;font-weight:500;margin-bottom:6px;letter-spacing:0.2px}
.total-value{font-size:24px;font-weight:500;color:#FAFAFA;letter-spacing:-0.6px;line-height:1.1}
.total-split-row{display:flex;gap:18px;margin-top:14px;font-size:11px;color:#A1A1AA;padding-top:14px;border-top:0.5px solid #27272A}
.summary-title{font-size:13px;font-weight:500;color:#FAFAFA}
.deal-brand-name{font-size:14px;font-weight:500;color:#FAFAFA}
.deal-amt{font-size:14px;font-weight:500;color:#FAFAFA}
.month-name{font-size:13px;font-weight:500;color:#FAFAFA}
.month-total{font-size:14px;font-weight:500;color:#FAFAFA}
.month-tap{font-size:11px;color:#A1A1AA;font-style:italic}
/* Clickable card overlay: button after a card-overlay-trigger gets pulled up to overlap the card */
.card-overlay-trigger{position:relative;z-index:1;cursor:pointer}
div[data-testid="stElementContainer"]:has(.card-overlay-trigger)+div[data-testid="stElementContainer"] .stButton{margin-top:-78px;position:relative;z-index:5}
div[data-testid="stElementContainer"]:has(.card-overlay-trigger)+div[data-testid="stElementContainer"] .stButton button{width:100%!important;min-height:74px!important;background:transparent!important;border:none!important;color:transparent!important;cursor:pointer!important;padding:0!important;font-size:0!important}
div[data-testid="stElementContainer"]:has(.card-overlay-trigger)+div[data-testid="stElementContainer"] .stButton button:hover{background:rgba(255,255,255,0.03)!important;border:0.5px solid #3F3F46!important;border-radius:12px!important}
/* Period popover: style as colored pill */
div[data-testid="stPopover"] button{display:inline-flex!important;align-items:center!important;gap:6px!important;padding:5px 11px!important;border-radius:6px!important;font-size:11px!important;font-weight:500!important;border:0.5px solid #1E40AF!important;background:#0F2547!important;color:#93C5FD!important;min-height:auto!important;width:auto!important}
div[data-testid="stPopover"] button:hover{background:#15315E!important;border-color:#1E40AF!important;color:#93C5FD!important}
/* Period popover when quarter selected — amber */
.pp-popover-quarter div[data-testid="stPopover"] button{background:#1E1B0B!important;border-color:#84671A!important;color:#FBBF24!important}
.pp-popover-quarter div[data-testid="stPopover"] button:hover{background:#2A2410!important}
.pp-popover-calendar div[data-testid="stPopover"] button{background:#052E2A!important;border-color:#047857!important;color:#6EE7B7!important}
.pp-popover-calendar div[data-testid="stPopover"] button:hover{background:#063E36!important}
</style>
""", unsafe_allow_html=True)

def check_password():
    if st.session_state.get("authed"):
        return True
    st.markdown("<p class='brand' style='text-align:center;margin-top:80px'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='app-name' style='text-align:center;font-size:24px;margin:8px 0 32px'>🔒 Brand Deals Tracker</h1>", unsafe_allow_html=True)
    pw = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
    if pw == APP_PASSWORD:
        st.session_state.authed = True
        st.rerun()
    elif pw:
        st.error("Incorrect password")
    return False

if not check_password():
    st.stop()

@st.cache_resource
def get_gspread_client():
    creds_info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def load_deals():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
    all_values = sh.get_all_values()
    header_idx = None
    for i, row in enumerate(all_values):
        if "FY" in row and "Status" in row and "Campaign" in row:
            header_idx = i; break
    if header_idx is None:
        return pd.DataFrame(), []
    headers = all_values[header_idx]
    seen = {}; clean = []
    for h in headers:
        if h in seen:
            seen[h] += 1; clean.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0; clean.append(h)
    rows = all_values[header_idx + 1:]
    df = pd.DataFrame(rows, columns=clean)
    df["_sheet_row"] = list(range(header_idx + 2, header_idx + 2 + len(rows)))
    df = df[df["FY"].astype(str).str.strip() != ""]
    return df, headers

@st.cache_data(ttl=300)
def load_ad_revenue():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("Ad Revenue")
    all_values = sh.get_all_values()
    header_idx = None
    for i, row in enumerate(all_values):
        if any(c.strip() == "Month" for c in row) and any("YouTube" in c for c in row):
            header_idx = i; break
    if header_idx is None:
        return pd.DataFrame()
    headers = all_values[header_idx]
    rows = []
    for r in all_values[header_idx + 1:]:
        if not r or not r[0] or "TOTAL" in str(r[0]).upper():
            break
        rows.append(r)
    return pd.DataFrame(rows, columns=headers)

_FX_FALLBACK = {"AUD": 1.0, "USD": 1.3807, "AED": 0.376, "INR": 0.014614}

def _fetch_live_fx():
    """Fetch live FX rates from open.er-api.com (free, no API key). Base = AUD.
    Returns dict like {'AUD': 1.0, 'USD': 1.52, ...} mapping foreign currency -> AUD,
    or None on any failure (network, parse, missing keys)."""
    try:
        req = urllib.request.Request(
            "https://open.er-api.com/v6/latest/AUD",
            headers={"User-Agent": "brand-deals-app"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("result") != "success":
            return None
        api_rates = data.get("rates", {})
        # API gives "1 AUD = X foreign". We want "1 foreign = Y AUD" = 1/X.
        out = {"AUD": 1.0}
        for code in ("USD", "AED", "INR"):
            v = api_rates.get(code)
            if not v or float(v) == 0:
                return None
            out[code] = 1.0 / float(v)
        return out
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError, TypeError, OSError):
        return None

def _load_fx_from_sheet():
    """Fallback: read FX Rates tab from the Google Sheet."""
    try:
        gc = get_gspread_client()
        sh = gc.open_by_key(SHEET_ID).worksheet("FX Rates")
        all_values = sh.get_all_values()
        rates = dict(_FX_FALLBACK)
        for row in all_values:
            if len(row) >= 3 and row[1] in ("AUD", "USD", "AED", "INR"):
                try: rates[row[1]] = float(row[2])
                except: pass
        return rates
    except Exception:
        return dict(_FX_FALLBACK)

@st.cache_data(ttl=3600)
def load_fx_rates():
    """Live FX with graceful fallback. Cached for 1 hour.
    Priority: live API -> Google Sheet "FX Rates" tab -> hardcoded defaults."""
    live = _fetch_live_fx()
    if live is not None:
        return live
    return _load_fx_from_sheet()

def parse_money(s):
    if s is None or s == "" or s == "-": return 0.0
    s = str(s).strip()
    s = s.replace("A$", "").replace("د.إ", "").replace("₹", "")
    s = s.replace("$", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    if s in ("", "-"): return 0.0
    try: return float(s)
    except: return 0.0

def parse_pct(s):
    if not s or s == "" or s == "-": return 0.0
    s = str(s).strip()
    if s.endswith("%"):
        try: return float(s[:-1]) / 100
        except: return 0.0
    try:
        v = float(s)
        return v / 100 if v > 1 else v
    except: return 0.0

def parse_month_date(s):
    if not s: return None
    s = str(s).strip()
    for fmt in ["%m/%d/%y", "%m/%d/%Y", "%d/%m/%y", "%d/%m/%Y",
                "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
        try: return datetime.strptime(s, fmt).date()
        except: continue
    return None

def derive_month_date(month_name, fy):
    if not month_name or not fy: return None
    try:
        m = MONTHS.index(month_name) + 1
        fy_year = int(str(fy).replace("FY", ""))
        year = 2000 + fy_year - 1 if m >= 7 else 2000 + fy_year
        return date(year, m, 1)
    except: return None

@st.cache_data(ttl=300)
def load_campaigns():
    """Load Campaigns tab. Row 1 = headers. Returns (DataFrame, headers)."""
    gc = get_gspread_client()
    try:
        sh = gc.open_by_key(SHEET_ID).worksheet("Campaigns")
    except Exception:
        return pd.DataFrame(), []
    all_values = sh.get_all_values()
    if not all_values: return pd.DataFrame(), []
    headers = all_values[0]
    rows = all_values[1:]
    df = pd.DataFrame(rows, columns=headers)
    df["_sheet_row"] = list(range(2, 2 + len(rows)))
    df = df[df["Campaign ID"].astype(str).str.strip() != ""]
    return df, headers

@st.cache_data(ttl=300)
def load_post_tracking():
    """Load Post Tracking tab. Row 1 = headers. Returns (DataFrame, headers)."""
    gc = get_gspread_client()
    try:
        sh = gc.open_by_key(SHEET_ID).worksheet("Post Tracking")
    except Exception:
        return pd.DataFrame(), []
    all_values = sh.get_all_values()
    if not all_values: return pd.DataFrame(), []
    headers = all_values[0]
    rows = all_values[1:]
    df = pd.DataFrame(rows, columns=headers)
    df["_sheet_row"] = list(range(2, 2 + len(rows)))
    df = df[df["Post ID"].astype(str).str.strip() != ""]
    return df, headers

# CPV rating thresholds (in INR, locked). Other currencies derived from FX at startup.
# INR: <0.30 Incredible, <0.50 Great, <1.00 Good, else High
_CPV_INR = {"incredible": 0.30, "great": 0.50, "good": 1.00}

def cpv_thresholds_for(currency, fx_rates):
    """Return dict of thresholds {incredible, great, good} in the given currency.
    Derived from INR thresholds using FX rates. INR returns the locked values."""
    cur = (currency or "").upper()
    if cur == "INR" or cur == "":
        return dict(_CPV_INR)
    fx_inr = fx_rates.get("INR", 0.014614)  # 1 INR = X AUD
    fx_cur = fx_rates.get(cur, 1.0)         # 1 cur = X AUD
    if fx_cur == 0: return dict(_CPV_INR)
    # Convert INR threshold -> AUD -> currency: threshold_cur = threshold_inr * fx_inr / fx_cur
    factor = fx_inr / fx_cur
    return {k: v * factor for k, v in _CPV_INR.items()}

def rate_cpv(cpv_value, currency, fx_rates):
    """Return (emoji, label) for a CPV value in the given currency."""
    if cpv_value is None or cpv_value <= 0:
        return ("", "")
    t = cpv_thresholds_for(currency, fx_rates)
    if cpv_value < t["incredible"]: return ("🟢🟢", "Incredible")
    if cpv_value < t["great"]:      return ("🟢", "Great")
    if cpv_value < t["good"]:       return ("🟡", "Good")
    return ("🔴", "High")

def format_rate_chip(currency, rate_orig):
    """Format a rate in original currency for display (e.g. '₹5.00L', 'USD $15,000')."""
    if rate_orig is None or rate_orig == "" or rate_orig == 0:
        return ""
    try: r = float(rate_orig)
    except: return ""
    cur = (currency or "").upper()
    if cur == "INR":
        return f"₹{r/100000:.2f}L" if r >= 100000 else f"₹{int(r):,}"
    if cur == "USD": return f"USD ${int(r):,}"
    if cur == "AED": return f"AED {int(r):,}"
    if cur == "AUD": return f"AUD ${int(r):,}"
    return f"{cur} {int(r):,}"

def format_cpv(value, currency):
    """Format CPV in original currency. CPV values are typically small decimals."""
    if value is None or value <= 0: return "—"
    cur = (currency or "").upper()
    if cur == "INR":  return f"₹{value:.4f}".rstrip("0").rstrip(".") if value < 1 else f"₹{value:.2f}"
    if cur == "USD":  return f"${value:.6f}".rstrip("0").rstrip(".") if value < 0.01 else f"${value:.4f}"
    if cur == "AED":  return f"AED {value:.6f}".rstrip("0").rstrip(".") if value < 0.01 else f"AED {value:.4f}"
    if cur == "AUD":  return f"AUD ${value:.6f}".rstrip("0").rstrip(".") if value < 0.01 else f"AUD ${value:.4f}"
    return f"{value:.4f}"

def format_compact_int(n):
    """Format a number compactly: 1234 -> 1,234; 1_500_000 -> 1.5M; 22_000 -> 22.0K"""
    if n is None: return "—"
    try: n = float(n)
    except: return "—"
    if n == 0: return "0"
    abs_n = abs(n)
    if abs_n >= 1_000_000: return f"{n/1_000_000:.2f}M".rstrip("0").rstrip(".") + "M" if False else f"{n/1_000_000:.2f}M"
    if abs_n >= 1_000:     return f"{n/1_000:.1f}K"
    return f"{int(n):,}"

@st.cache_data(ttl=300)
def process_deals(deals_raw, fx_rates):
    """Parse the raw deals DataFrame into a list of dicts with normalized numeric fields.
    Cached because string-parsing every cell on every rerun is the biggest mobile bottleneck.
    Re-runs only when deals_raw or fx_rates actually change (or on cache.clear() after a save)."""
    deals = []
    for _, r in deals_raw.iterrows():
        d = r.to_dict()
        d["_sheet_row"] = int(d.get("_sheet_row", 0))
        d["gross_orig"] = parse_money(d.get("Gross (orig)", 0))
        d["commission_pct"] = parse_pct(d.get("Commission %", 0))
        gross_aud = parse_money(d.get("Gross AUD", 0))
        if gross_aud == 0 and d["gross_orig"] > 0:
            curr = d.get("Currency", "AUD")
            gross_aud = d["gross_orig"] * fx_rates.get(curr, 1.0)
        d["gross_aud"] = gross_aud
        net_aud = parse_money(d.get("Net AUD", 0))
        if net_aud == 0 and d["gross_orig"] > 0:
            gross = d["gross_orig"]
            comm = gross * d["commission_pct"]
            net_fee = gross - comm
            if d.get("Currency") == "INR":
                net_fee -= net_fee * 0.2122
            net_aud = net_fee * fx_rates.get(d.get("Currency", "AUD"), 1.0)
        d["net_aud"] = net_aud
        comm_aud = parse_money(d.get("Commission AUD", 0))
        if comm_aud == 0 and d["gross_orig"] > 0:
            comm_aud = d["gross_orig"] * d["commission_pct"] * fx_rates.get(d.get("Currency", "AUD"), 1.0)
        d["commission_aud"] = comm_aud
        md = parse_month_date(d.get("Month Date", ""))
        if not md:
            md = derive_month_date(d.get("Month", ""), d.get("FY", ""))
        d["month_date"] = md
        deals.append(d)
    return deals

@st.cache_data(ttl=300)
def process_ad_revenue(ad_rev_raw):
    """Parse the raw ad revenue DataFrame into a list of monthly payout dicts. Cached."""
    ad_rev_monthly = []
    for _, r in ad_rev_raw.iterrows():
        month = r.get("Month", "")
        if not month: continue
        ad_rev_monthly.append({"month": month,
            "yt_aud": parse_money(r.get("YouTube (AUD)", 0)),
            "fb_usd": parse_money(r.get("Facebook (USD)", 0)),
            "fb_aud": parse_money(r.get("Facebook (AUD)", 0)),
            "total_aud": parse_money(r.get("Monthly Total (AUD)", 0))})
    return ad_rev_monthly

def get_display_mult(currency, fx_rates):
    rate = fx_rates.get(currency, 1.0)
    return 1.0 / rate if rate else 1.0

def format_inr(amt):
    amt = int(round(amt))
    if amt < 0: return "-" + format_inr(-amt)
    s = str(amt)
    if len(s) <= 3: return f"₹{s}"
    last3 = s[-3:]; rest = s[:-3]; groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:]); rest = rest[:-2]
    if rest: groups.insert(0, rest)
    return f"₹{','.join(groups)},{last3}"

def format_money(amt, currency="AUD"):
    if amt is None: amt = 0
    if currency == "INR": return format_inr(amt)
    elif currency == "AED": return f"د.إ {amt:,.0f}"
    else: return f"${amt:,.0f}"

def format_original_currency(gross_orig, currency):
    if currency == "INR":
        if gross_orig >= 100000: return f"₹{gross_orig/100000:.1f}L"
        return f"₹{gross_orig:,.0f}"
    elif currency == "USD": return f"${gross_orig:,.0f}"
    elif currency == "AED": return f"د.إ {gross_orig:,.0f}"
    elif currency == "AUD": return f"A${gross_orig:,.0f}"
    return f"{gross_orig:,.0f}"

def get_period_range():
    mode = st.session_state.get("period_mode", "FY")
    year = st.session_state.get("period_year", "FY26")
    quarter = st.session_state.get("period_quarter", "All")
    if mode == "FY":
        yr = int(year[2:])
        if quarter == "All": return (date(2000+yr-1, 7, 1), date(2000+yr, 7, 1))
        if quarter == "Q1": return (date(2000+yr-1, 7, 1),  date(2000+yr-1, 10, 1))
        if quarter == "Q2": return (date(2000+yr-1, 10, 1), date(2000+yr, 1, 1))
        if quarter == "Q3": return (date(2000+yr, 1, 1),    date(2000+yr, 4, 1))
        if quarter == "Q4": return (date(2000+yr, 4, 1),    date(2000+yr, 7, 1))
    else:
        yr = int(year)
        if quarter == "All": return (date(yr, 1, 1),  date(yr+1, 1, 1))
        if quarter == "Q1": return (date(yr, 1, 1),  date(yr, 4, 1))
        if quarter == "Q2": return (date(yr, 4, 1),  date(yr, 7, 1))
        if quarter == "Q3": return (date(yr, 7, 1),  date(yr, 10, 1))
        if quarter == "Q4": return (date(yr, 10, 1), date(yr+1, 1, 1))
    return (date(2025, 7, 1), date(2026, 7, 1))

def in_period(md, period):
    if not md: return False
    return period[0] <= md < period[1]

def months_elapsed(period):
    today = date.today()
    start, end = period
    if today < start: return 0
    last_day = end - timedelta(days=1)
    eff_end = min(today, last_day)
    months = (eff_end.year - start.year) * 12 + (eff_end.month - start.month) + 1
    return max(months, 1)

def period_label():
    year = st.session_state.period_year
    q = st.session_state.period_quarter
    return f"{year} · All" if q == "All" else f"{year} · {q}"

def period_pill_class():
    if st.session_state.period_quarter != "All": return "pp-quarter"
    return "pp-calendar" if st.session_state.period_mode == "Calendar" else "pp-fy"

def period_months_in_range(period):
    start, end = period
    out = []
    y, m = start.year, start.month
    while date(y, m, 1) < end:
        out.append((y, m))
        m += 1
        if m > 12: m = 1; y += 1
    return out

def base_layout(height=200):
    return dict(plot_bgcolor="#18181B", paper_bgcolor="#18181B",
        font=dict(family="Inter, Helvetica, sans-serif", size=10, color="#A1A1AA"),
        margin=dict(l=12, r=12, t=10, b=10), height=height,
        xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=0),
        yaxis=dict(showgrid=True, gridcolor="#27272A", tickfont=dict(size=9), zeroline=False),
        showlegend=False, bargap=0.4)

def make_bar_chart(df, x_col, y_col, color, faded_indices=None, label_prefix=""):
    colors = [color] * len(df)
    if faded_indices:
        for i in faded_indices:
            if 0 <= i < len(colors): colors[i] = "#3F3F46"
    fig = go.Figure(data=[go.Bar(x=df[x_col], y=df[y_col],
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate=f"<b>%{{x}}</b><br>{label_prefix}%{{y:,.1f}}<extra></extra>")])
    fig.update_layout(**base_layout())
    return fig

def make_split_bar_chart(df, x_col, y1_col, y2_col, name1, name2):
    fig = go.Figure(data=[
        go.Bar(name=name1, x=df[x_col], y=df[y1_col], marker=dict(color="#EF4444", line=dict(width=0))),
        go.Bar(name=name2, x=df[x_col], y=df[y2_col], marker=dict(color="#3B82F6", line=dict(width=0)))])
    layout = base_layout(height=220)
    layout.update(dict(barmode="group", showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.15, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#A1A1AA")),
        bargroupgap=0.1))
    fig.update_layout(**layout)
    return fig

def make_hbar_chart(df, x_col, y_col, color="#FAFAFA"):
    df = df.sort_values(x_col, ascending=True)
    fig = go.Figure(data=[go.Bar(x=df[x_col], y=df[y_col], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>")])
    layout = base_layout(height=260)
    layout["xaxis"] = dict(showgrid=True, gridcolor="#27272A",
                            tickfont=dict(size=9, color="#A1A1AA"), zeroline=False)
    layout["yaxis"] = dict(showgrid=False, tickfont=dict(size=11, color="#FAFAFA"))
    fig.update_layout(**layout)
    return fig

try:
    deals_raw, deals_headers = load_deals()
    ad_rev_raw = load_ad_revenue()
    fx_rates = load_fx_rates()
    campaigns_raw, campaigns_headers = load_campaigns()
    posts_raw, posts_headers = load_post_tracking()
except Exception as e:
    st.error(f"Couldn't load Google Sheets: {type(e).__name__}: {e}")
    st.stop()

FX_INR = fx_rates.get("INR", 0.014614)
FX_USD = fx_rates.get("USD", 1.3807)
FX_AED = fx_rates.get("AED", 0.376)

# Heavy parsing now happens inside cached functions — only re-runs when source data changes.
deals = process_deals(deals_raw, fx_rates)
ad_rev_monthly = process_ad_revenue(ad_rev_raw)

for k, v in [("period_mode", "FY"), ("period_year", "FY26"),
             ("period_quarter", "All"), ("display_currency", "AUD")]:
    if k not in st.session_state:
        st.session_state[k] = v

def render_global_header():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    with c2:
        cur_options = ["AUD", "USD", "INR", "AED"]
        if st.session_state.display_currency not in cur_options:
            st.session_state.display_currency = "AUD"
        st.selectbox("Currency", cur_options,
                     index=cur_options.index(st.session_state.display_currency),
                     key="display_currency", label_visibility="collapsed")
    pill_class = period_pill_class()
    # Wrap popover in color-class container so its trigger button picks up the right pill color
    popover_wrap_class = ""
    if pill_class == "pp-quarter":
        popover_wrap_class = "pp-popover-quarter"
    elif pill_class == "pp-calendar":
        popover_wrap_class = "pp-popover-calendar"
    st.markdown(f"<div class='{popover_wrap_class}' style='margin:8px 0 2px'>", unsafe_allow_html=True)
    with st.popover(f"📅 {period_label()}", use_container_width=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("Mode", ["FY", "Calendar"], key="period_mode")
        with c2:
            years = ["FY25", "FY26", "FY27"] if st.session_state.period_mode == "FY" else ["2024", "2025", "2026"]
            if st.session_state.period_year not in years:
                st.session_state.period_year = years[1] if len(years) > 1 else years[0]
            st.selectbox("Year", years, key="period_year")
        with c3:
            st.selectbox("Quarter", ["All", "Q1", "Q2", "Q3", "Q4"], key="period_quarter")
        if st.button("🔄 Refresh from Google Sheet", key="refresh_btn", use_container_width=True):
            st.cache_data.clear(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

render_global_header()

period = get_period_range()
elapsed = months_elapsed(period)
display_cur = st.session_state.display_currency
mult = get_display_mult(display_cur, fx_rates)
period_deals = [d for d in deals if in_period(d["month_date"], period)]

ad_in_period = []
for ar in ad_rev_monthly:
    try:
        mn, yr = ar["month"].split(" ")
        md = date(int(yr), MONTHS.index(mn) + 1, 1)
        if in_period(md, period):
            ad_in_period.append({**ar, "md": md})
    except: continue
ad_total_aud = sum(ar["total_aud"] for ar in ad_in_period)
ad_months_with_data = sum(1 for ar in ad_in_period if ar["total_aud"] > 0)

total_gross_deals = sum(d["gross_aud"] for d in period_deals)
total_net_deals = sum(d["net_aud"] for d in period_deals)
total_gross = total_gross_deals + ad_total_aud
total_net = total_net_deals + ad_total_aud
total_commission = sum(d["commission_aud"] for d in period_deals)
total_tds = 0
for d in period_deals:
    if d.get("Currency") == "INR":
        net_fee = d["gross_orig"] * (1 - d["commission_pct"])
        total_tds += net_fee * 0.2122 * fx_rates.get("INR", 0.014614)

paid_d = [d for d in period_deals if d.get("Status") == "Paid"]
awaiting_d = [d for d in period_deals if str(d.get("Status", "")).startswith("Invoiced")]
need_inv_d = [d for d in period_deals if "Not Invoiced" in str(d.get("Status", ""))]
locked_d = [d for d in period_deals if d.get("Status") == "Locked & Executing"]
paid_amt = sum(d["net_aud"] for d in paid_d) + ad_total_aud
awaiting_amt = sum(d["net_aud"] for d in awaiting_d)
need_inv_amt = sum(d["net_aud"] for d in need_inv_d)
locked_amt = sum(d["net_aud"] for d in locked_d)
coming_in = awaiting_amt + need_inv_amt + locked_amt

@st.dialog("Edit Deal", width="large")
def edit_deal_dialog(deal):
    sheet_row = deal.get("_sheet_row")
    if not sheet_row:
        st.error("Sheet row not tracked."); return
    st.markdown(f"<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='app-name' style='margin-top:4px'>{deal.get('Campaign', '(no name)')}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:#A1A1AA;margin:0 0 12px'>"
                f"{deal.get('Month','')} · {deal.get('Region','')} · {deal.get('Agency','')}</p>",
                unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Status & Invoice</p>", unsafe_allow_html=True)
    status_options = ["Pitched", "Locked & Executing",
        "Completed (India) - Not Invoiced", "Completed (Not-India) - Not Invoiced",
        "Invoiced (India)", "Invoiced (Non-India)", "Paid", "Partially Delivered", "Overdue"]
    cur_status = deal.get("Status", "Pitched")
    if cur_status not in status_options: status_options.insert(0, cur_status)
    new_status = st.selectbox("Status", status_options,
                               index=status_options.index(cur_status), key=f"e_status_{sheet_row}")
    new_inv = st.text_input("Invoice #", value=deal.get("Invoice #", "") or "", key=f"e_inv_{sheet_row}")
    c1, c2 = st.columns(2)
    with c1:
        new_inv_date = st.text_input("Invoice Date", value=deal.get("Invoice Date", "") or "",
                                      placeholder="DD/MM/YYYY", key=f"e_idate_{sheet_row}")
    with c2:
        new_pay_date = st.text_input("Payment Date", value=deal.get("Payment Date", "") or "",
                                      placeholder="DD/MM/YYYY", key=f"e_pdate_{sheet_row}")
    st.markdown("<p class='section-label'>Deal Details</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fy_opts = ["FY25", "FY26", "FY27"]
        cur_fy = deal.get("FY", "FY26")
        if cur_fy not in fy_opts: fy_opts.insert(0, cur_fy)
        new_fy = st.selectbox("FY", fy_opts, index=fy_opts.index(cur_fy), key=f"e_fy_{sheet_row}")
        cur_month = deal.get("Month", "")
        m_idx = MONTHS.index(cur_month) if cur_month in MONTHS else 0
        new_month = st.selectbox("Month", MONTHS, index=m_idx, key=f"e_month_{sheet_row}")
    with c2:
        region_opts = ["India", "Australia", "UAE", "US/Global"]
        cur_region = deal.get("Region", "India")
        if cur_region not in region_opts: region_opts.insert(0, cur_region)
        new_region = st.selectbox("Region", region_opts,
                                    index=region_opts.index(cur_region), key=f"e_region_{sheet_row}")
        new_agency = st.text_input("Agency", value=deal.get("Agency", "") or "", key=f"e_agency_{sheet_row}")
    new_campaign = st.text_input("Campaign", value=deal.get("Campaign", "") or "",
                                    placeholder="Specific deal name (e.g. Plum #2, Etihad - Phuket)",
                                    key=f"e_campaign_{sheet_row}")
    new_brand = st.text_input("Brand", value=deal.get("Brand", "") or "",
                                placeholder="Rolled-up brand (e.g. Plum, Etihad)",
                                key=f"e_brand_{sheet_row}")
    new_parent = st.text_input("Parent/Group", value=deal.get("Parent/Group", "") or "",
                                placeholder="e.g. HUL, NMA, or same as Brand",
                                key=f"e_pg_{sheet_row}")
    st.markdown("<p class='section-label'>Financials</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        cur_opts = ["AUD", "USD", "INR", "AED"]
        cur_curr = deal.get("Currency", "AUD")
        new_curr = st.selectbox("Currency", cur_opts,
                                  index=cur_opts.index(cur_curr) if cur_curr in cur_opts else 0,
                                  key=f"e_curr_{sheet_row}")
        new_gross = st.number_input("Gross (orig)", min_value=0.0, step=1000.0,
                                       value=float(deal.get("gross_orig", 0)), key=f"e_gross_{sheet_row}")
    with c2:
        cur_pct = float(deal.get("commission_pct", 0)) * 100
        new_comm_pct = st.number_input("Commission %", min_value=0.0, max_value=100.0,
                                          step=5.0, value=cur_pct, key=f"e_comm_{sheet_row}") / 100
    st.markdown("<p class='section-label'>Deliverables</p>", unsafe_allow_html=True)
    new_deliv = st.text_area("Deliverables", value=deal.get("Deliverables", "") or "",
                              key=f"e_deliv_{sheet_row}", label_visibility="collapsed")
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("💾 Save Changes", key=f"save_{sheet_row}", use_container_width=True, type="primary"):
            try:
                gc = get_gspread_client()
                ws = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
                field_updates = {"FY": new_fy, "Status": new_status,
                    "Month": new_month, "Region": new_region, "Agency": new_agency,
                    "Campaign": new_campaign, "Brand": new_brand, "Parent/Group": new_parent,
                    "Currency": new_curr, "Gross (orig)": new_gross,
                    "Commission %": new_comm_pct, "Invoice #": new_inv, "Invoice Date": new_inv_date,
                    "Payment Date": new_pay_date, "Deliverables": new_deliv}
                updates = []
                for field, val in field_updates.items():
                    if field in deals_headers:
                        col_idx = deals_headers.index(field) + 1
                        updates.append({"range": gspread.utils.rowcol_to_a1(sheet_row, col_idx),
                                          "values": [[val]]})
                if updates:
                    ws.batch_update(updates, value_input_option="USER_ENTERED")
                st.success("Saved!"); st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")
    with c2:
        confirm_key = f"confirm_del_{sheet_row}"
        if st.session_state.get(confirm_key):
            if st.button("⚠ Confirm Delete", key=f"delc_{sheet_row}", use_container_width=True):
                try:
                    gc = get_gspread_client()
                    ws = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
                    ws.delete_rows(sheet_row)
                    st.session_state[confirm_key] = False
                    st.success("Deleted."); st.cache_data.clear(); st.rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")
        else:
            if st.button("🗑 Delete", key=f"del_{sheet_row}", use_container_width=True):
                st.session_state[confirm_key] = True; st.rerun()

@st.dialog("Edit Ad Revenue", width="large")
def edit_ad_revenue_dialog(month_label, yt_aud, fb_usd):
    st.markdown(f"<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='app-name' style='margin-top:4px'>{month_label}</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px;color:#A1A1AA;margin:0 0 12px'>Ad Revenue · YouTube + Facebook</p>",
                unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Payouts</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        new_yt = st.number_input("YouTube (AUD)", min_value=0.0, step=10.0,
                                  value=float(yt_aud or 0), key=f"are_yt_{month_label}")
    with c2:
        new_fb_usd = st.number_input("Facebook (USD)", min_value=0.0, step=10.0,
                                      value=float(fb_usd or 0), key=f"are_fb_{month_label}")
    if st.button("💾 Save Changes", key=f"are_save_{month_label}", use_container_width=True, type="primary"):
        try:
            gc = get_gspread_client()
            ws = gc.open_by_key(SHEET_ID).worksheet("Ad Revenue")
            all_vals = ws.get_all_values()
            for idx, row in enumerate(all_vals):
                if len(row) > 0 and row[0] == month_label:
                    ws.update_cell(idx + 1, 2, new_yt)
                    ws.update_cell(idx + 1, 3, new_fb_usd)
                    st.success(f"Saved {month_label}!"); st.cache_data.clear(); st.rerun()
                    break
            else:
                st.error(f"Month '{month_label}' not found in sheet")
        except Exception as e:
            st.error(f"Save failed: {e}")

# -------- Campaign / Post helpers --------

def _campaign_id_from(brand_value, month_value, fy_value="FY26"):
    """Generate a campaign_id slug from brand/month."""
    import re as _re
    src = (str(brand_value or "") + "-" + str(month_value or "")).lower()
    if fy_value == "FY25" and not month_value:
        src = (str(brand_value or "") + "-fy25").lower()
    return _re.sub(r"[^a-z0-9-]", "", src.replace(" ", "-").replace("--", "-")).strip("-")

def _derive_brand_from_campaign(campaign):
    """Apply the brand-stripping rules (same as restructure script)."""
    import re as _re
    c = (campaign or "").strip()
    if not c: return ""
    if _re.match(r"^Plum\s*(#\d+|Part\s+\d+)", c, _re.I): return "Plum"
    if _re.match(r"^MARS\s+Part", c, _re.I): return "MARS"
    if c.startswith("Abu Dhabi -"): return "Visit Abu Dhabi"
    if c.startswith("Visit Abu Dhabi"): return "Visit Abu Dhabi"
    if c.startswith("Etihad"): return "Etihad"
    if c.startswith("Knorr"): return "Knorr"
    if c.startswith("Vaseline"): return "Vaseline"
    if c.startswith("Kissaan"): return "Kissaan"
    if c.startswith("Nexxus"): return "Nexxus"
    if c.startswith("Nykaa"): return "Nykaa"
    if c.startswith("Godrej Properties"): return "Godrej Properties"
    if c.strip().startswith("Airbnb"): return "Airbnb"
    if "Visit UAE Deep Dive" in c: return "Visit UAE Deep Dive Dubai"
    if "Prasuma" in c or "Blinkit - Prasuma" in c: return "Prasuma"
    if c == "Simple Skin": return "Simple"
    return c

_HUL_BRANDS = {"dove", "tresemme", "nexxus", "knorr", "kissaan",
               "love beauty planet", "vaseline", "simple"}
_NMA_BRANDS = {"impact makers workshop", "visit uae deep dive dubai", "openmasters games"}

def _derive_parent_from_brand(brand):
    b = (brand or "").strip().lower()
    if b in _HUL_BRANDS: return "HUL"
    if b in _NMA_BRANDS: return "NMA"
    return brand

@st.dialog("New Brand Deal", width="large")
def add_deal_dialog():
    st.markdown("<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown("<p class='app-name' style='margin-top:4px'>New Brand Deal</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px;color:#A1A1AA;margin:0 0 12px'>Saves to Deals Log · auto-converts currency · auto-creates a Campaign</p>",
                unsafe_allow_html=True)
    with st.form("add_deal_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            new_fy = st.selectbox("FY", ["FY26", "FY27"], key="ad_fy")
            new_status = st.selectbox("Status", ["Pitched", "Locked & Executing",
                "Completed (India) - Not Invoiced", "Completed (Not-India) - Not Invoiced",
                "Invoiced (India)", "Invoiced (Non-India)", "Paid"], key="ad_status")
            new_month = st.selectbox("Month", MONTHS, key="ad_month")
            new_region = st.selectbox("Region", ["India", "Australia", "UAE", "US/Global"], key="ad_region")
            new_currency = st.selectbox("Currency", ["AUD", "USD", "INR", "AED"], key="ad_curr")
        with c2:
            new_campaign = st.text_input("Campaign", placeholder="e.g. Plum #4, Etihad - Greece", key="ad_camp")
            new_brand = st.text_input("Brand", placeholder="Rolled-up (e.g. Plum) — blank auto-fills", key="ad_brand")
            new_parent = st.text_input("Parent/Group", placeholder="e.g. HUL — blank auto-fills", key="ad_pg")
            new_agency = st.text_input("Agency", placeholder="Optional", key="ad_agency")
            new_gross = st.number_input("Gross (orig)", min_value=0.0, step=1000.0, key="ad_gross")
            new_comm = st.number_input("Commission %", min_value=0.0, max_value=100.0,
                                         step=5.0, value=15.0, key="ad_comm") / 100
            new_inv = st.text_input("Invoice #", placeholder="Optional", key="ad_inv")
        new_deliv = st.text_area("Deliverables", placeholder="e.g. 1 IG Reel + 2 Stories…", key="ad_deliv")
        submitted = st.form_submit_button("Add Deal", use_container_width=True, type="primary")
        if submitted:
            if not new_campaign:
                st.error("Campaign is required")
                return
            effective_brand = (new_brand or _derive_brand_from_campaign(new_campaign)).strip()
            effective_parent = (new_parent or _derive_parent_from_brand(effective_brand)).strip()
            try:
                gc = get_gspread_client()
                # 1. Append to Deals Log
                ws_d = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
                headers_d = None
                for r in ws_d.get_all_values():
                    if "FY" in r and "Status" in r and "Campaign" in r:
                        headers_d = r; break
                if not headers_d:
                    st.error("Couldn't find Deals Log header row"); return
                new_row = [""] * len(headers_d)
                fields = {"FY": new_fy, "Status": new_status, "Month": new_month,
                    "Region": new_region, "Agency": new_agency,
                    "Campaign": new_campaign, "Brand": effective_brand, "Parent/Group": effective_parent,
                    "Currency": new_currency, "Gross (orig)": new_gross,
                    "Commission %": new_comm, "Invoice #": new_inv,
                    "Deliverables": new_deliv}
                for h, v in fields.items():
                    if h in headers_d:
                        new_row[headers_d.index(h)] = v
                ws_d.append_row(new_row, value_input_option="USER_ENTERED")
                # 2. Auto-create Campaigns row
                try:
                    ws_c = gc.open_by_key(SHEET_ID).worksheet("Campaigns")
                    headers_c = ws_c.row_values(1)
                    cid = _campaign_id_from(new_campaign, new_month, new_fy)
                    rate_display = format_rate_chip(new_currency, new_gross)
                    camp_fields = {"Campaign ID": cid, "Campaign Name": new_campaign,
                        "Brand": effective_brand, "Deal Group": effective_parent,
                        "Month": new_month, "FY": new_fy, "Status": new_status,
                        "Region": new_region, "Type": "Brand Deal",
                        "Currency": new_currency, "Rate (orig)": new_gross,
                        "Rate Display": rate_display, "Invoice #": new_inv,
                        "Linked Live Rows": "", "Notes": ""}
                    camp_row = [""] * len(headers_c)
                    for h, v in camp_fields.items():
                        if h in headers_c: camp_row[headers_c.index(h)] = v
                    ws_c.append_row(camp_row, value_input_option="USER_ENTERED")
                except Exception as e_c:
                    st.warning(f"Deal added but couldn't auto-create campaign: {e_c}")
                st.success(f"Added {new_campaign}!"); st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

@st.dialog("New Campaign (Standalone)", width="large")
def new_campaign_dialog():
    st.markdown("<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown("<p class='app-name' style='margin-top:4px'>New Standalone Campaign</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px;color:#A1A1AA;margin:0 0 12px'>For barters / performance-only. Doesn't touch Brand Deals.</p>",
                unsafe_allow_html=True)
    with st.form("new_camp_form", clear_on_submit=False):
        new_name = st.text_input("Campaign Name", placeholder="e.g. Nexxus Train Series", key="nc_name")
        c1, c2 = st.columns(2)
        with c1:
            new_brand = st.text_input("Brand", placeholder="e.g. Nexxus", key="nc_brand")
            new_month = st.text_input("Month", placeholder="e.g. Jan-Feb 2026", key="nc_month")
            new_fy = st.selectbox("FY", ["FY26", "FY27", "FY25"], key="nc_fy")
        with c2:
            new_parent = st.text_input("Parent/Group", placeholder="Blank = auto-fill", key="nc_pg")
            new_region = st.selectbox("Region", ["India", "Australia", "UAE", "US/Global"], key="nc_region")
            new_status = st.text_input("Status", value="Barter — Live", key="nc_status")
        new_notes = st.text_area("Notes", placeholder="e.g. Performance-only, no financial entry", key="nc_notes")
        submitted = st.form_submit_button("Create Campaign", use_container_width=True, type="primary")
        if submitted:
            if not new_name:
                st.error("Campaign Name is required"); return
            effective_brand = (new_brand or new_name).strip()
            effective_parent = (new_parent or _derive_parent_from_brand(effective_brand)).strip()
            try:
                gc = get_gspread_client()
                ws_c = gc.open_by_key(SHEET_ID).worksheet("Campaigns")
                headers_c = ws_c.row_values(1)
                cid = _campaign_id_from(effective_brand, new_month, new_fy) + "-standalone"
                camp_fields = {"Campaign ID": cid, "Campaign Name": new_name,
                    "Brand": effective_brand, "Deal Group": effective_parent,
                    "Month": new_month, "FY": new_fy, "Status": new_status,
                    "Region": new_region, "Type": "Standalone (Barter)",
                    "Currency": "", "Rate (orig)": "", "Rate Display": "",
                    "Invoice #": "", "Linked Live Rows": "", "Notes": new_notes}
                camp_row = [""] * len(headers_c)
                for h, v in camp_fields.items():
                    if h in headers_c: camp_row[headers_c.index(h)] = v
                ws_c.append_row(camp_row, value_input_option="USER_ENTERED")
                st.success(f"Added {new_name}!"); st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

def _safe_int(v):
    try: return int(float(v)) if v not in (None, "", "None") else 0
    except: return 0

def _safe_float(v):
    try: return float(v) if v not in (None, "", "None") else 0.0
    except: return 0.0

@st.cache_data(ttl=300)
def _posts_by_campaign_id(posts_df):
    """Pre-index posts by Campaign ID. Returns dict[campaign_id] -> list[post dict]."""
    if posts_df.empty: return {}
    idx = {}
    records = posts_df.to_dict("records")
    for p in records:
        cid = str(p.get("Campaign ID", "")).strip()
        if not cid: continue
        idx.setdefault(cid, []).append(p)
    return idx

def posts_for_campaign(campaign_id, posts_df):
    """O(1) lookup via cached index."""
    idx = _posts_by_campaign_id(posts_df)
    return idx.get(str(campaign_id).strip(), [])

def campaign_aggregates(campaign_row, posts_for_camp):
    """Compute totals across all posts for a campaign. Single-pass over posts."""
    ig_views = ig_likes = ig_comments = ig_reposts = ig_shares = ig_saves = 0
    yt_views = tt_views = tt_likes = tt_comments = 0
    for p in posts_for_camp:
        ig_views    += _safe_int(p.get("IG Views"))
        ig_likes    += _safe_int(p.get("IG Likes"))
        ig_comments += _safe_int(p.get("IG Comments"))
        ig_reposts  += _safe_int(p.get("IG Reposts"))
        ig_shares   += _safe_int(p.get("IG Shares"))
        ig_saves    += _safe_int(p.get("IG Saves"))
        yt_views    += _safe_int(p.get("YT Views"))
        tt_views    += _safe_int(p.get("TT Views"))
        tt_likes    += _safe_int(p.get("TT Likes"))
        tt_comments += _safe_int(p.get("TT Comments"))
    combined_views = ig_views + yt_views + tt_views
    combined_engagement = ig_likes + ig_comments + ig_reposts + ig_shares + ig_saves + tt_likes + tt_comments
    rate_orig = _safe_float(campaign_row.get("Rate (orig)"))
    currency = (campaign_row.get("Currency") or "").upper()
    cpv = (rate_orig / combined_views) if (rate_orig > 0 and combined_views > 0) else 0
    cpm = (rate_orig * 1000 / combined_views) if (rate_orig > 0 and combined_views > 0) else 0
    cpe = (rate_orig / combined_engagement) if (rate_orig > 0 and combined_engagement > 0) else 0
    er = (combined_engagement * 100 / combined_views) if combined_views > 0 else 0
    return {
        "combined_views": combined_views, "combined_engagement": combined_engagement,
        "ig_views": ig_views, "yt_views": yt_views, "tt_views": tt_views,
        "rate_orig": rate_orig, "currency": currency,
        "cpv": cpv, "cpm": cpm, "cpe": cpe, "er_pct": er,
    }

@st.cache_data(ttl=300)
def process_campaigns_full(campaigns_raw, posts_raw):
    """Precompute campaign list with aggregates and posts_count for every campaign.
    Cached — only re-runs when raw data changes. Returns list of {camp, posts_count, agg}."""
    if campaigns_raw.empty: return []
    posts_idx = _posts_by_campaign_id(posts_raw)
    out = []
    records = campaigns_raw.to_dict("records")
    for cd in records:
        cid = str(cd.get("Campaign ID", "")).strip()
        posts_c = posts_idx.get(cid, [])
        agg = campaign_aggregates(cd, posts_c)
        out.append({"camp": cd, "posts_count": len(posts_c), "agg": agg})
    return out

def add_post_dialog(campaign_id, campaign_name):
    st.markdown(f"<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='app-name' style='margin-top:4px'>Add post to {campaign_name}</p>", unsafe_allow_html=True)
    with st.form(f"add_post_form_{campaign_id}", clear_on_submit=False):
        d_type = st.selectbox("Deliverable type",
            ["IG Reel", "IG Story", "IG Carousel", "YT Short", "YT Long-form", "TikTok"],
            key=f"ap_type_{campaign_id}")
        c1, c2 = st.columns(2)
        with c1:
            d_date = st.text_input("Date posted", placeholder="YYYY-MM-DD", key=f"ap_date_{campaign_id}")
        with c2:
            d_title = st.text_input("Title / Caption", placeholder="Optional", key=f"ap_title_{campaign_id}")
        st.markdown("<p class='section-label'>Instagram (optional)</p>", unsafe_allow_html=True)
        ig_url = st.text_input("IG URL", placeholder="instagram.com/p/…", key=f"ap_ig_url_{campaign_id}")
        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            ig_views = st.number_input("Views", min_value=0, step=100, key=f"ap_ig_v_{campaign_id}")
            ig_reposts = st.number_input("Reposts", min_value=0, step=10, key=f"ap_ig_r_{campaign_id}")
        with ic2:
            ig_likes = st.number_input("Likes", min_value=0, step=100, key=f"ap_ig_l_{campaign_id}")
            ig_shares = st.number_input("Shares", min_value=0, step=10, key=f"ap_ig_s_{campaign_id}")
        with ic3:
            ig_comments = st.number_input("Comments", min_value=0, step=1, key=f"ap_ig_c_{campaign_id}")
            ig_saves = st.number_input("Saves", min_value=0, step=10, key=f"ap_ig_sv_{campaign_id}")
        st.markdown("<p class='section-label'>YouTube (optional)</p>", unsafe_allow_html=True)
        yt_url = st.text_input("YT URL", placeholder="youtu.be/… or youtube.com/watch?v=…", key=f"ap_yt_url_{campaign_id}")
        yc1, yc2 = st.columns(2)
        with yc1:
            yt_views = st.number_input("YT Views", min_value=0, step=100, key=f"ap_yt_v_{campaign_id}")
        with yc2:
            yt_subs = st.number_input("YT Subs Gained", min_value=0, step=1, key=f"ap_yt_subs_{campaign_id}")
        st.markdown("<p class='section-label'>TikTok (optional)</p>", unsafe_allow_html=True)
        tt_url = st.text_input("TT URL", placeholder="tiktok.com/@…/video/…", key=f"ap_tt_url_{campaign_id}")
        tc1, tc2, tc3 = st.columns(3)
        with tc1: tt_views = st.number_input("TT Views", min_value=0, step=100, key=f"ap_tt_v_{campaign_id}")
        with tc2: tt_likes = st.number_input("TT Likes", min_value=0, step=10, key=f"ap_tt_l_{campaign_id}")
        with tc3: tt_comments = st.number_input("TT Comments", min_value=0, step=1, key=f"ap_tt_c_{campaign_id}")
        st.caption("IG Reel includes cross-posted FB stats. ER % = engagement ÷ views.")
        submitted = st.form_submit_button("Save Post", use_container_width=True, type="primary")
        if submitted:
            try:
                gc = get_gspread_client()
                ws = gc.open_by_key(SHEET_ID).worksheet("Post Tracking")
                headers = ws.row_values(1)
                all_rows = ws.get_all_values()
                existing_for_camp = sum(1 for r in all_rows[1:] if len(r) > 1 and r[1] == campaign_id)
                pid = f"{campaign_id}-p{existing_for_camp + 1}"
                combined_views = ig_views + yt_views + tt_views
                combined_engagement = ig_likes + ig_comments + ig_reposts + ig_shares + ig_saves + tt_likes + tt_comments
                fields = {"Post ID": pid, "Campaign ID": campaign_id, "Date": d_date,
                    "Deliverable Type": d_type, "Title/Caption": d_title,
                    "IG URL": ig_url, "IG Views": ig_views or "", "IG Likes": ig_likes or "",
                    "IG Comments": ig_comments or "", "IG Reposts": ig_reposts or "",
                    "IG Shares": ig_shares or "", "IG Saves": ig_saves or "",
                    "YT URL": yt_url, "YT Views": yt_views or "", "YT Subs Gained": yt_subs or "",
                    "TT URL": tt_url, "TT Views": tt_views or "", "TT Likes": tt_likes or "",
                    "TT Comments": tt_comments or "",
                    "Combined Views": combined_views or "", "Combined Engagement": combined_engagement or "",
                    "Source": "manual"}
                new_row = [""] * len(headers)
                for h, v in fields.items():
                    if h in headers: new_row[headers.index(h)] = v
                ws.append_row(new_row, value_input_option="USER_ENTERED")
                st.session_state[f"cd_addmode_{campaign_id}"] = False
                st.success("Post saved!"); st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

def edit_post_dialog(post_dict, campaign_id, campaign_name):
    post_sr = int(post_dict.get("_sheet_row", 0))
    st.markdown(f"<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='app-name' style='margin-top:4px'>Edit post · {campaign_name}</p>", unsafe_allow_html=True)
    deliverable_types = ["IG Reel", "IG Story", "IG Carousel", "YT Short", "YT Long-form", "TikTok"]
    cur_type = str(post_dict.get("Deliverable Type", "IG Reel"))
    if cur_type not in deliverable_types: deliverable_types.insert(0, cur_type)
    d_type = st.selectbox("Deliverable type", deliverable_types,
                            index=deliverable_types.index(cur_type), key=f"ep_type_{post_sr}")
    c1, c2 = st.columns(2)
    with c1:
        d_date = st.text_input("Date posted", value=str(post_dict.get("Date", ""))[:10], key=f"ep_date_{post_sr}")
    with c2:
        d_title = st.text_input("Title / Caption", value=str(post_dict.get("Title/Caption", "")), key=f"ep_title_{post_sr}")
    st.markdown("<p class='section-label'>Instagram</p>", unsafe_allow_html=True)
    ig_url = st.text_input("IG URL", value=str(post_dict.get("IG URL", "")), key=f"ep_ig_url_{post_sr}")
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        ig_views = st.number_input("Views", min_value=0, step=100, value=_safe_int(post_dict.get("IG Views")), key=f"ep_ig_v_{post_sr}")
        ig_reposts = st.number_input("Reposts", min_value=0, step=10, value=_safe_int(post_dict.get("IG Reposts")), key=f"ep_ig_r_{post_sr}")
    with ic2:
        ig_likes = st.number_input("Likes", min_value=0, step=100, value=_safe_int(post_dict.get("IG Likes")), key=f"ep_ig_l_{post_sr}")
        ig_shares = st.number_input("Shares", min_value=0, step=10, value=_safe_int(post_dict.get("IG Shares")), key=f"ep_ig_s_{post_sr}")
    with ic3:
        ig_comments = st.number_input("Comments", min_value=0, step=1, value=_safe_int(post_dict.get("IG Comments")), key=f"ep_ig_c_{post_sr}")
        ig_saves = st.number_input("Saves", min_value=0, step=10, value=_safe_int(post_dict.get("IG Saves")), key=f"ep_ig_sv_{post_sr}")
    st.markdown("<p class='section-label'>YouTube</p>", unsafe_allow_html=True)
    yt_url = st.text_input("YT URL", value=str(post_dict.get("YT URL", "")), key=f"ep_yt_url_{post_sr}")
    yc1, yc2 = st.columns(2)
    with yc1: yt_views = st.number_input("YT Views", min_value=0, step=100, value=_safe_int(post_dict.get("YT Views")), key=f"ep_yt_v_{post_sr}")
    with yc2: yt_subs = st.number_input("YT Subs Gained", min_value=0, step=1, value=_safe_int(post_dict.get("YT Subs Gained")), key=f"ep_yt_subs_{post_sr}")
    st.markdown("<p class='section-label'>TikTok</p>", unsafe_allow_html=True)
    tt_url = st.text_input("TT URL", value=str(post_dict.get("TT URL", "")), key=f"ep_tt_url_{post_sr}")
    tc1, tc2, tc3 = st.columns(3)
    with tc1: tt_views = st.number_input("TT Views", min_value=0, step=100, value=_safe_int(post_dict.get("TT Views")), key=f"ep_tt_v_{post_sr}")
    with tc2: tt_likes = st.number_input("TT Likes", min_value=0, step=10, value=_safe_int(post_dict.get("TT Likes")), key=f"ep_tt_l_{post_sr}")
    with tc3: tt_comments = st.number_input("TT Comments", min_value=0, step=1, value=_safe_int(post_dict.get("TT Comments")), key=f"ep_tt_c_{post_sr}")
    st.caption("IG Reel includes cross-posted FB stats. ER % = engagement ÷ views.")
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        if st.button("💾 Save changes", key=f"ep_save_{post_sr}", use_container_width=True, type="primary"):
            try:
                gc = get_gspread_client()
                ws = gc.open_by_key(SHEET_ID).worksheet("Post Tracking")
                headers = ws.row_values(1)
                combined_views = ig_views + yt_views + tt_views
                combined_engagement = ig_likes + ig_comments + ig_reposts + ig_shares + ig_saves + tt_likes + tt_comments
                fields = {"Date": d_date, "Deliverable Type": d_type, "Title/Caption": d_title,
                    "IG URL": ig_url, "IG Views": ig_views or "", "IG Likes": ig_likes or "",
                    "IG Comments": ig_comments or "", "IG Reposts": ig_reposts or "",
                    "IG Shares": ig_shares or "", "IG Saves": ig_saves or "",
                    "YT URL": yt_url, "YT Views": yt_views or "", "YT Subs Gained": yt_subs or "",
                    "TT URL": tt_url, "TT Views": tt_views or "", "TT Likes": tt_likes or "",
                    "TT Comments": tt_comments or "",
                    "Combined Views": combined_views or "", "Combined Engagement": combined_engagement or ""}
                updates = []
                for k, v in fields.items():
                    if k in headers:
                        col = headers.index(k) + 1
                        updates.append({"range": gspread.utils.rowcol_to_a1(post_sr, col), "values": [[v]]})
                if updates:
                    ws.batch_update(updates, value_input_option="USER_ENTERED")
                st.session_state[f"cd_editmode_{campaign_id}"] = None
                st.success("Saved!"); st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")
    with sc2:
        del_key = f"ep_del_conf_{post_sr}"
        if st.session_state.get(del_key):
            if st.button("⚠ Confirm delete", key=f"ep_delc_{post_sr}", use_container_width=True):
                try:
                    gc = get_gspread_client()
                    ws = gc.open_by_key(SHEET_ID).worksheet("Post Tracking")
                    ws.delete_rows(post_sr)
                    st.session_state[del_key] = False
                    st.session_state[f"cd_editmode_{campaign_id}"] = None
                    st.success("Deleted."); st.cache_data.clear(); st.rerun()
                except Exception as e: st.error(f"Delete failed: {e}")
        else:
            if st.button("🗑 Delete", key=f"ep_del_{post_sr}", use_container_width=True):
                st.session_state[del_key] = True; st.rerun()

@st.dialog("Campaign Detail", width="large")
def campaign_detail_dialog(camp_dict):
    cid = camp_dict.get("Campaign ID", "")
    name = camp_dict.get("Campaign Name", cid)
    currency = camp_dict.get("Currency", "")
    rate_orig = _safe_float(camp_dict.get("Rate (orig)"))
    rate_chip = format_rate_chip(currency, rate_orig)
    month = camp_dict.get("Month", "")
    fy = camp_dict.get("FY", "")
    region = camp_dict.get("Region", "")
    deal_group = camp_dict.get("Deal Group", "")
    is_barter = "Standalone" in str(camp_dict.get("Type", ""))

    st.markdown("<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='app-name' style='margin-top:4px'>{name}</p>", unsafe_allow_html=True)
    if rate_chip:
        st.markdown(f"<span style='display:inline-block;background:rgba(250,250,250,0.06);"
                    f"border:1px solid rgba(250,250,250,0.2);color:#FAFAFA;font-size:11px;"
                    f"padding:3px 10px;border-radius:999px;font-weight:500;margin-bottom:4px'>{rate_chip}</span>",
                    unsafe_allow_html=True)
    elif is_barter:
        st.markdown("<span style='display:inline-block;background:rgba(192,221,151,0.15);color:#C0DD97;"
                    "font-size:10px;padding:2px 8px;border-radius:6px;font-weight:500;margin-bottom:4px'>BARTER</span>",
                    unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:#A1A1AA;margin:4px 0 12px'>"
                f"{month} {fy} · {region} · {deal_group}</p>", unsafe_allow_html=True)

    posts = posts_for_campaign(cid, posts_raw)
    agg = campaign_aggregates(camp_dict, posts)

    if agg["cpv"] > 0:
        emoji, label = rate_cpv(agg["cpv"], currency, fx_rates)
        rating_colors = {"Incredible": "#97C459", "Great": "#C0DD97", "Good": "#EF9F27", "High": "#E24B4A"}
        bg = {"Incredible": "rgba(151,196,89,0.18)", "Great": "rgba(192,221,151,0.15)",
              "Good": "rgba(239,159,39,0.15)", "High": "rgba(226,75,74,0.15)"}.get(label, "rgba(161,161,170,0.15)")
        st.markdown(f"<span style='display:inline-block;background:{bg};color:{rating_colors.get(label,'#A1A1AA')};"
                    f"font-size:10px;padding:2px 6px;border-radius:5px;font-weight:500;margin-bottom:8px'>"
                    f"{emoji} {label}</span>", unsafe_allow_html=True)

    def tile(label, value, accent=False, good=False):
        color = "#E89E7E" if accent else ("#97C459" if good else "#FAFAFA")
        return (f"<div style='background:#18181B;border:1px solid #27272A;border-radius:8px;padding:9px 11px'>"
                f"<p style='font-size:9px;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.3px;margin:0 0 3px'>{label}</p>"
                f"<div style='font-size:14px;font-weight:500;line-height:1.1;color:{color}'>{value}</div></div>")

    cpv_str = format_cpv(agg["cpv"], currency) if agg["cpv"] > 0 else "—"
    cpm_str = format_cpv(agg["cpm"], currency) if agg["cpm"] > 0 else "—"
    cpe_str = format_cpv(agg["cpe"], currency) if agg["cpe"] > 0 else "—"
    er_str = f"{agg['er_pct']:.2f}%" if agg["er_pct"] > 0 else "—"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(tile("Total views", format_compact_int(agg["combined_views"]), accent=True), unsafe_allow_html=True)
    with c2:
        st.markdown(tile("Total engagement", format_compact_int(agg["combined_engagement"])), unsafe_allow_html=True)
    with c3:
        st.markdown(tile("ER %", er_str, good=True), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(tile(f"CPV {currency}", cpv_str), unsafe_allow_html=True)
    with c2: st.markdown(tile(f"CPM {currency}", cpm_str), unsafe_allow_html=True)
    with c3: st.markdown(tile(f"CPE {currency}", cpe_str), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

    # Session-state for inline form toggles within this dialog
    add_mode_key = f"cd_addmode_{cid}"
    edit_mode_key = f"cd_editmode_{cid}"  # holds the post sheet_row being edited

    if st.session_state.get(add_mode_key):
        st.markdown("<p class='section-label'>Add Post</p>", unsafe_allow_html=True)
        if st.button("← Back to posts", key=f"cd_addback_{cid}"):
            st.session_state[add_mode_key] = False
            st.rerun()
        add_post_dialog(cid, name)
    elif st.session_state.get(edit_mode_key):
        edit_sr = st.session_state[edit_mode_key]
        p_to_edit = next((x for x in posts if int(x.get("_sheet_row", 0)) == edit_sr), None)
        if p_to_edit:
            st.markdown("<p class='section-label'>Edit Post</p>", unsafe_allow_html=True)
            if st.button("← Back to posts", key=f"cd_editback_{cid}"):
                st.session_state[edit_mode_key] = None
                st.rerun()
            edit_post_dialog(p_to_edit, cid, name)
        else:
            st.session_state[edit_mode_key] = None
            st.rerun()
    else:
        hcol1, hcol2 = st.columns([3, 1])
        with hcol1:
            st.markdown(f"<p class='section-label' style='margin:0'>Posts ({len(posts)})</p>", unsafe_allow_html=True)
        with hcol2:
            if st.button("+ Add Post", key=f"cd_addpost_{cid}", use_container_width=True, type="primary"):
                st.session_state[add_mode_key] = True
                st.rerun()

        for i, p in enumerate(posts):
            d_date = str(p.get("Date", ""))[:10]
            d_caption = str(p.get("Title/Caption", ""))[:80]
            ig_v = _safe_int(p.get("IG Views"))
            yt_v = _safe_int(p.get("YT Views"))
            tt_v = _safe_int(p.get("TT Views"))
            post_total = ig_v + yt_v + tt_v
            ig_likes_n = _safe_int(p.get("IG Likes"))
            ig_comments_n = _safe_int(p.get("IG Comments"))
            platforms = []
            if p.get("IG URL") or ig_v: platforms.append("<i class='ti ti-brand-instagram' style='color:#1877F2;font-size:15px;vertical-align:-2px'></i>")
            if p.get("YT URL") or yt_v: platforms.append("<i class='ti ti-brand-youtube' style='color:#E24B4A;font-size:15px;vertical-align:-2px'></i>")
            if p.get("TT URL") or tt_v: platforms.append("<i class='ti ti-brand-tiktok' style='color:#FAFAFA;font-size:15px;vertical-align:-2px'></i>")
            platforms_str = " ".join(platforms) if platforms else "<span style='color:#A1A1AA;font-size:11px'>—</span>"
            st.markdown(f"<div class='deal-card card-overlay-trigger' style='background:#18181B;border:1px solid #27272A;border-radius:10px;padding:10px;margin-bottom:0'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                        f"<div style='display:flex;gap:6px;align-items:center'>{platforms_str}</div>"
                        f"<div style='font-size:10px;color:#A1A1AA'>{d_date}</div></div>"
                        f"<p style='font-size:11px;color:#FAFAFA;margin:6px 0 6px;opacity:0.85'>{d_caption}</p>"
                        f"<div style='display:flex;gap:14px;padding-top:6px;border-top:1px solid #27272A'>"
                        f"<div><div style='font-size:14px;font-weight:500;color:#E89E7E'>{format_compact_int(post_total)}</div>"
                        f"<div style='font-size:9px;color:#A1A1AA;text-transform:uppercase'>Views</div></div>"
                        f"<div><div style='font-size:14px;font-weight:500;color:#FAFAFA'>{format_compact_int(ig_likes_n)}</div>"
                        f"<div style='font-size:9px;color:#A1A1AA;text-transform:uppercase'>Likes</div></div>"
                        f"<div><div style='font-size:14px;font-weight:500;color:#FAFAFA'>{format_compact_int(ig_comments_n)}</div>"
                        f"<div style='font-size:9px;color:#A1A1AA;text-transform:uppercase'>Comments</div></div></div></div>",
                        unsafe_allow_html=True)
            post_sr = int(p.get("_sheet_row", 0))
            if st.button("⠀", key=f"cd_postedit_{post_sr}", use_container_width=True):
                st.session_state[edit_mode_key] = post_sr
                st.rerun()

    st.markdown("<div style='margin-top:18px;padding-top:12px;border-top:1px solid #27272A'></div>", unsafe_allow_html=True)
    camp_sr = int(camp_dict.get("_sheet_row", 0))
    camp_conf_key = f"cd_camp_del_{camp_sr}"
    if st.session_state.get(camp_conf_key):
        colA, colB = st.columns(2)
        with colA:
            if st.button("Confirm delete campaign", key=f"cd_campcdel_{camp_sr}", use_container_width=True):
                try:
                    gc = get_gspread_client()
                    ws = gc.open_by_key(SHEET_ID).worksheet("Campaigns")
                    ws.delete_rows(camp_sr)
                    st.session_state[camp_conf_key] = False
                    st.success("Campaign deleted (Brand Deals untouched)."); st.cache_data.clear(); st.rerun()
                except Exception as e: st.error(f"Delete failed: {e}")
        with colB:
            if st.button("Cancel", key=f"cd_campccancel_{camp_sr}", use_container_width=True):
                st.session_state[camp_conf_key] = False; st.rerun()
    else:
        if st.button("Delete this campaign", key=f"cd_campdel_{camp_sr}", use_container_width=True):
            st.session_state[camp_conf_key] = True; st.rerun()

tabs = st.tabs(["Overview", "Brand Deals", "Charts", "Ad Revenue", "Campaigns", "Analytics"])

with tabs[0]:
    st.markdown("<p class='app-name'>Overview</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Total</p>", unsafe_allow_html=True)
    def kpi(label, value, subtitle):
        return (f"<div class='kpi'><div class='kpi-label'>{label}</div>"
                f"<div class='kpi-value'>{value}</div>"
                f"<div class='kpi-sub'>{subtitle}</div></div>")
    ad_disp = ad_total_aud * mult
    gross_disp = total_gross * mult
    net_disp = total_net * mult
    avg_gross = gross_disp / elapsed if elapsed else 0
    avg_net = net_disp / elapsed if elapsed else 0
    comm_disp = total_commission * mult
    tds_disp = total_tds * mult
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(kpi("Gross Revenue", format_money(gross_disp, display_cur),
                        f"Includes <span class='accent-green'>+ {format_money(ad_disp, display_cur)}</span> in Ad Revenue"),
                    unsafe_allow_html=True)
        st.markdown(kpi("Avg Gross / Month", format_money(avg_gross, display_cur),
                        f"Gross, {elapsed}mo Elapsed"), unsafe_allow_html=True)
        st.markdown(kpi("Commission", format_money(comm_disp, display_cur),
                        "Agency Commission 15%"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Net Income", format_money(net_disp, display_cur),
                        "After Commission, TDS, etc."), unsafe_allow_html=True)
        st.markdown(kpi("Avg Net / Month", format_money(avg_net, display_cur),
                        f"Net, {elapsed}mo Elapsed"), unsafe_allow_html=True)
        st.markdown(kpi("TDS", format_money(tds_disp, display_cur),
                        "Tax Deducted in India 21.22%"), unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Operational</p>", unsafe_allow_html=True)
    op_data = [("Paid", "#10B981", f"{len(paid_d)} Deals + Ad Revenue", paid_amt),
        ("Awaiting Payment", "#FB923C", f"{len(awaiting_d)} Invoiced", awaiting_amt),
        ("Need to Invoice", "#FACC15", f"{len(need_inv_d)} Deals", need_inv_amt),
        ("Locked & Executing", "#F87171", f"{len(locked_d)} Deals", locked_amt)]
    for name, color, sub, amt in op_data:
        st.markdown(f"<div class='status-card'>"
            f"<div><span class='status-dot' style='background:{color}'></span>"
            f"<span class='status-name'>{name}</span>"
            f"<div class='status-count'>{sub}</div></div>"
            f"<div class='status-amount'>{format_money(amt * mult, display_cur)}</div></div>",
            unsafe_allow_html=True)
    st.markdown(f"<div class='summary-row'>"
        f"<div><div class='summary-title'>Total Money Coming in (Net)</div>"
        f"<div class='status-count' style='margin:2px 0 0'>Awaiting + Need to Invoice + Locked</div></div>"
        f"<div class='status-amount'>{format_money(coming_in * mult, display_cur)}</div></div>",
        unsafe_allow_html=True)

with tabs[1]:
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown("<p class='app-name'>Brand Deals</p>", unsafe_allow_html=True)
    with hcol2:
        if st.button("+ New Deal", key="bd_new_deal", use_container_width=True, type="primary"):
            add_deal_dialog()
    sorted_deals = sorted(period_deals, key=lambda d: d.get("month_date") or date.min, reverse=True)
    st.markdown("<p class='section-label'>Filter</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        statuses = sorted(set(d.get("Status", "") for d in sorted_deals if d.get("Status")))
        status_f = st.multiselect("Status", statuses, key="bd_status_filter")
    with c2:
        regions = sorted(set(d.get("Region", "") for d in sorted_deals if d.get("Region")))
        region_f = st.multiselect("Region", regions, key="bd_region_filter")
    search = st.text_input("Search", placeholder="Campaign, brand, or parent group…", key="bd_search")
    filtered = sorted_deals
    if status_f: filtered = [d for d in filtered if d.get("Status") in status_f]
    if region_f: filtered = [d for d in filtered if d.get("Region") in region_f]
    if search:
        s = search.lower()
        filtered = [d for d in filtered
                    if s in str(d.get("Campaign", "")).lower()
                    or s in str(d.get("Brand", "")).lower()
                    or s in str(d.get("Parent/Group", "")).lower()]
    st.markdown(f"<p style='font-size:11px;color:#71717A;margin:8px 0'>{len(filtered)} deals</p>",
                unsafe_allow_html=True)
    def pill_cls(status):
        if not status: return "pill-pitched"
        if status == "Paid": return "pill-paid"
        if "Invoiced (India)" in status: return "pill-invoiced-india"
        if "Invoiced (Non" in status: return "pill-invoiced-nonindia"
        if "Not Invoiced" in status: return "pill-not-invoiced"
        if "Locked" in status: return "pill-locked"
        return "pill-pitched"
    for d in filtered:
        brand = d.get("Campaign", ""); month = d.get("Month", "")
        region = d.get("Region", ""); agency = d.get("Agency", "")
        status = d.get("Status", ""); inv = d.get("Invoice #", "")
        md = d.get("month_date"); year_str = str(md.year) if md else ""
        amt_str = format_original_currency(d["gross_orig"], d.get("Currency", "AUD"))
        pcl = pill_cls(status)
        meta = f"{month} {year_str} · {region}" + (f" · {agency}" if agency else "")
        pills = f"<span class='pill {pcl}'>{status}</span>"
        if inv and inv.strip(): pills += f"<span class='pill {pcl}'>{inv}</span>"
        sheet_row = d.get("_sheet_row", 0)
        st.markdown(f"<div class='deal-card card-overlay-trigger'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px'>"
            f"<div><div class='deal-brand-name'>{brand}</div>"
            f"<div style='font-size:11px;color:#A1A1AA;margin-top:2px'>{meta}</div></div>"
            f"<div style='text-align:right;flex-shrink:0'>"
            f"<div class='deal-amt'>{amt_str}</div>"
            f"<div style='margin-top:4px;display:flex;gap:4px;justify-content:flex-end;flex-wrap:wrap'>{pills}</div></div>"
            f"</div></div>", unsafe_allow_html=True)
        if st.button("⠀", key=f"edit_btn_{sheet_row}", use_container_width=True):
            edit_deal_dialog(d)

with tabs[2]:
    st.markdown("<p class='app-name'>Charts</p>", unsafe_allow_html=True)
    months_list = period_months_in_range(period)
    today = date.today()
    monthly_gross = {(y, m): 0.0 for y, m in months_list}
    monthly_india = {(y, m): 0.0 for y, m in months_list}
    monthly_row = {(y, m): 0.0 for y, m in months_list}
    def to_inr_lakhs(d):
        g = d["gross_orig"]; c = d.get("Currency", "AUD")
        if c == "INR": return g / 100000
        if c == "AUD": return (g / FX_INR) / 100000
        if c == "USD": return (g * FX_USD / FX_INR) / 100000
        if c == "AED": return (g * FX_AED / FX_INR) / 100000
        return 0
    for d in period_deals:
        if not d["month_date"]: continue
        key = (d["month_date"].year, d["month_date"].month)
        if key not in monthly_gross: continue
        monthly_gross[key] += d["gross_aud"]
        if d.get("Region") == "India":
            monthly_india[key] += to_inr_lakhs(d)
        else:
            monthly_row[key] += d["gross_aud"]
    faded = []
    for i, (y, m) in enumerate(months_list):
        if date(y, m, 1) > date(today.year, today.month, 1):
            faded.append(i)
    def label_months(monthly_dict):
        labels = [f"{MONTHS[m-1][:3]} {str(y)[-2:]}" for y, m in months_list]
        values = [monthly_dict[(y, m)] for y, m in months_list]
        return pd.DataFrame({"Month": labels, "Value": values})

    st.markdown("<p class='section-label'>Monthly Gross — Brand Deals (All Regions)</p>", unsafe_allow_html=True)
    df_g = label_months(monthly_gross); df_g["Value"] = df_g["Value"] * mult
    total_g = sum(monthly_gross.values()) * mult
    avg_g = total_g / elapsed if elapsed else 0
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin-bottom:6px'>Avg {format_money(avg_g, display_cur)} / month</div>", unsafe_allow_html=True)
    st.plotly_chart(make_bar_chart(df_g, "Month", "Value", "#10B981", faded_indices=faded),
                     use_container_width=True, config={"displayModeBar": False})

    st.markdown("<p class='section-label'>Collective / India — Monthly Gross (₹ Lakhs)</p>", unsafe_allow_html=True)
    df_i = label_months(monthly_india)
    total_il = sum(monthly_india.values()); avg_il = total_il / elapsed if elapsed else 0
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin-bottom:6px'>Avg ₹{avg_il:.1f}L / month</div>", unsafe_allow_html=True)
    st.plotly_chart(make_bar_chart(df_i, "Month", "Value", "#FB923C", faded_indices=faded, label_prefix="₹"),
                     use_container_width=True, config={"displayModeBar": False})

    st.markdown("<p class='section-label'>Rest of World — Monthly Gross</p>", unsafe_allow_html=True)
    df_r = label_months(monthly_row); df_r["Value"] = df_r["Value"] * mult
    total_r = sum(monthly_row.values()) * mult
    avg_r = total_r / elapsed if elapsed else 0
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin-bottom:6px'>Avg {format_money(avg_r, display_cur)} / month</div>", unsafe_allow_html=True)
    st.plotly_chart(make_bar_chart(df_r, "Month", "Value", "#3B82F6", faded_indices=faded),
                     use_container_width=True, config={"displayModeBar": False})

    st.markdown("<p class='section-label'>Ad Revenue — Monthly</p>", unsafe_allow_html=True)
    ad_dict = {(ar["md"].year, ar["md"].month): ar for ar in ad_in_period}
    rows = []
    for y, m in months_list:
        ar = ad_dict.get((y, m), {})
        yt = ar.get("yt_aud", 0) * mult
        fb = ar.get("fb_aud", 0) * mult
        rows.append({"Month": f"{MONTHS[m-1][:3]} {str(y)[-2:]}", "YouTube": yt, "Facebook": fb})
    df_ad = pd.DataFrame(rows)
    ar_avg = (ad_total_aud * mult) / max(ad_months_with_data, 1)
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin-bottom:6px'>Avg {format_money(ar_avg, display_cur)} / month (÷{ad_months_with_data})</div>", unsafe_allow_html=True)
    st.plotly_chart(make_split_bar_chart(df_ad, "Month", "YouTube", "Facebook", "YouTube (AUD)", "Facebook (AUD eq)"),
                     use_container_width=True, config={"displayModeBar": False})

    st.markdown("<p class='section-label'>Top Brands — Roll-up</p>", unsafe_allow_html=True)
    brand_sums = defaultdict(float)
    for d in period_deals:
        rb = (d.get("Parent/Group") or d.get("Brand") or d.get("Campaign") or "Unknown").strip()
        brand_sums[rb] += d["gross_aud"] * mult
    top10 = sorted(brand_sums.items(), key=lambda x: -x[1])[:10]
    df_top = pd.DataFrame(top10, columns=["Brand", "AUD"])
    if len(df_top) > 0:
        st.plotly_chart(make_hbar_chart(df_top, "AUD", "Brand"),
                         use_container_width=True, config={"displayModeBar": False})

with tabs[3]:
    st.markdown("<p class='app-name'>Ad Revenue</p>", unsafe_allow_html=True)
    yt_total = sum(ar["yt_aud"] for ar in ad_in_period) * mult
    fb_total_aud = sum(ar["fb_aud"] for ar in ad_in_period) * mult
    total_aud_disp = sum(ar["total_aud"] for ar in ad_in_period) * mult
    avg_month = total_aud_disp / max(ad_months_with_data, 1)
    st.markdown(f"<div class='total-card'>"
        f"<div style='display:flex;gap:14px'>"
        f"<div style='flex:1'><div class='total-label'>TOTAL</div>"
        f"<div class='total-value'>{format_money(total_aud_disp, display_cur)}</div></div>"
        f"<div style='flex:1'><div class='total-label'>AVG / MONTH</div>"
        f"<div class='total-value'>{format_money(avg_month, display_cur)}</div></div>"
        f"</div><div class='total-split-row'>"
        f"<div><span class='status-dot' style='background:#EF4444;margin-right:6px'></span>"
        f"YouTube · {format_money(yt_total, display_cur)}</div>"
        f"<div><span class='status-dot' style='background:#3B82F6;margin-right:6px'></span>"
        f"Facebook · {format_money(fb_total_aud, display_cur)}</div>"
        f"</div></div>", unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Monthly Breakdown</p>", unsafe_allow_html=True)
    for ar in sorted(ad_in_period, key=lambda x: x["md"], reverse=True):
        has_data = ar["total_aud"] > 0
        safe_key = ar["month"].replace(" ", "_")
        if has_data:
            st.markdown(f"<div class='deal-card card-overlay-trigger'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<div><div class='month-name'>{ar['month']}</div>"
                f"<div style='font-size:11px;color:#A1A1AA;margin-top:2px'>"
                f"<span style='color:#FCA5A5'>YT ${ar['yt_aud']:,.0f}</span>  "
                f"<span style='color:#93C5FD'>FB ${ar['fb_usd']:,.0f} USD</span></div></div>"
                f"<div class='month-total'>{format_money(ar['total_aud'] * mult, display_cur)}</div></div></div>",
                unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='deal-card card-overlay-trigger' style='border-style:dashed;opacity:0.65'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<div><div class='month-name'>{ar['month']}</div>"
                f"<div style='font-size:11px;color:#525252;margin-top:2px'>Not yet entered</div></div>"
                f"<div class='month-tap'>Tap to add</div></div></div>",
                unsafe_allow_html=True)
        if st.button("⠀", key=f"ar_edit_{safe_key}", use_container_width=True):
            edit_ad_revenue_dialog(ar["month"], ar["yt_aud"], ar["fb_usd"])

with tabs[4]:
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown("<p class='app-name'>Campaigns</p>", unsafe_allow_html=True)
    with hcol2:
        if st.button("+ New", key="camp_new", use_container_width=True, type="primary"):
            new_campaign_dialog()
    if campaigns_raw.empty:
        st.info("No campaigns yet. Add one with '+ New' above, or add a Brand Deal to auto-create one.")
    else:
        camp_list = process_campaigns_full(campaigns_raw, posts_raw)
        st.markdown("<p class='section-label'>Filter</p>", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            fy_opts = sorted(set(str(c["camp"].get("FY", "")) for c in camp_list if c["camp"].get("FY")))
            fy_f = st.multiselect("FY", fy_opts, default=["FY26"] if "FY26" in fy_opts else [], key="camp_fy_filter")
        with fc2:
            regions_c = sorted(set(str(c["camp"].get("Region", "")) for c in camp_list if c["camp"].get("Region")))
            reg_f = st.multiselect("Region", regions_c, key="camp_region_filter")
        search_c = st.text_input("Search", placeholder="Campaign, brand, parent group…", key="camp_search")
        sort_opt = st.selectbox("Sort by",
            ["Best CPV", "Worst CPV", "Most views", "Most recent", "Posts count"], key="camp_sort")
        filtered_c = camp_list
        if fy_f: filtered_c = [c for c in filtered_c if str(c["camp"].get("FY", "")) in fy_f]
        if reg_f: filtered_c = [c for c in filtered_c if str(c["camp"].get("Region", "")) in reg_f]
        if search_c:
            s = search_c.lower()
            filtered_c = [c for c in filtered_c if
                          s in str(c["camp"].get("Campaign Name", "")).lower()
                          or s in str(c["camp"].get("Brand", "")).lower()
                          or s in str(c["camp"].get("Deal Group", "")).lower()]
        if sort_opt == "Best CPV":
            filtered_c.sort(key=lambda c: c["agg"]["cpv"] if c["agg"]["cpv"] > 0 else float("inf"))
        elif sort_opt == "Worst CPV":
            filtered_c.sort(key=lambda c: -c["agg"]["cpv"])
        elif sort_opt == "Most views":
            filtered_c.sort(key=lambda c: -c["agg"]["combined_views"])
        elif sort_opt == "Posts count":
            filtered_c.sort(key=lambda c: -c["posts_count"])
        else:
            filtered_c.sort(key=lambda c: str(c["camp"].get("Month", "")), reverse=True)
        st.markdown(f"<p style='font-size:11px;color:#71717A;margin:8px 0'>{len(filtered_c)} campaigns</p>",
                    unsafe_allow_html=True)
        for item in filtered_c:
            c = item["camp"]
            agg = item["agg"]
            cid = c.get("Campaign ID", "")
            name = c.get("Campaign Name", cid)
            month = c.get("Month", "")
            brand = c.get("Brand", "")
            currency = c.get("Currency", "")
            rate_orig = _safe_float(c.get("Rate (orig)"))
            rate_chip_str = format_rate_chip(currency, rate_orig)
            is_barter = "Standalone" in str(c.get("Type", ""))
            posts_count = item["posts_count"]
            cpv = agg["cpv"]
            emoji, label = rate_cpv(cpv, currency, fx_rates) if cpv > 0 else ("", "")
            rating_colors = {"Incredible": "#97C459", "Great": "#C0DD97",
                             "Good": "#EF9F27", "High": "#E24B4A"}
            rb_bg = {"Incredible": "rgba(151,196,89,0.18)", "Great": "rgba(192,221,151,0.15)",
                     "Good": "rgba(239,159,39,0.15)", "High": "rgba(226,75,74,0.15)"}.get(label, "rgba(161,161,170,0.15)")
            border_left = "border-left:3px solid #C0DD97;" if is_barter else ""
            barter_badge = ("<span style='background:rgba(192,221,151,0.15);color:#C0DD97;font-size:9px;"
                            "padding:2px 6px;border-radius:4px;margin-left:5px;font-weight:500'>BARTER</span>") if is_barter else ""
            rating_chip = ""
            if label:
                rating_chip = (f"<span style='background:{rb_bg};color:{rating_colors.get(label,'#A1A1AA')};"
                               f"font-size:10px;padding:2px 7px;border-radius:5px;font-weight:500'>{emoji} {label}</span>")
            rate_pill = (f"<span style='background:rgba(250,250,250,0.06);border:1px solid rgba(250,250,250,0.2);"
                         f"color:#FAFAFA;font-size:10px;padding:2px 8px;border-radius:999px;font-weight:500'>{rate_chip_str}</span>"
                         ) if rate_chip_str else ""
            cpv_label = f"<span style='font-size:10px;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.3px;margin-right:4px'>CPV</span>" if cpv > 0 else ""
            cpv_html = (f"<div style='display:flex;align-items:baseline;gap:4px'>{cpv_label}"
                        f"<span style='font-size:18px;font-weight:500;color:#E89E7E'>{format_cpv(cpv, currency)}</span></div>") if cpv > 0 else "<div style='font-size:13px;color:#6B6B73;font-style:italic'>No performance data yet</div>"
            views_html = f"<div style='font-size:12px;color:#FAFAFA'>{format_compact_int(agg['combined_views'])} views</div>" if agg['combined_views'] > 0 else ""
            st.markdown(f"<div class='deal-card card-overlay-trigger' style='{border_left}'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:start;gap:8px'>"
                        f"<div style='flex:1'>"
                        f"<div style='font-size:14px;font-weight:500;color:#FAFAFA'>{name}{barter_badge}</div>"
                        f"<div style='font-size:11px;color:#A1A1AA;margin-top:2px'>{month} · {brand} · {posts_count} post{'s' if posts_count != 1 else ''}</div>"
                        f"<div style='margin-top:6px'>{rate_pill}</div>"
                        f"</div>"
                        f"<div style='flex-shrink:0'>{rating_chip}</div></div>"
                        f"<div style='display:flex;justify-content:space-between;align-items:baseline;margin-top:8px'>"
                        f"{cpv_html}{views_html}</div></div>", unsafe_allow_html=True)
            if st.button("⠀", key=f"camp_btn_{cid}_{c.get('_sheet_row', 0)}", use_container_width=True):
                campaign_detail_dialog(c)

with tabs[5]:
    st.markdown("<p class='app-name'>Analytics</p>", unsafe_allow_html=True)
    if campaigns_raw.empty:
        st.info("No campaigns yet. Add some via Brand Deals + New Deal or Campaigns + New.")
    else:
        all_camps = process_campaigns_full(campaigns_raw, posts_raw)
        fy_opts = sorted(set(str(c["camp"].get("FY", "")) for c in all_camps if c["camp"].get("FY")))
        ac1, ac2 = st.columns(2)
        with ac1:
            an_fy = st.multiselect("FY", fy_opts, default=["FY26"] if "FY26" in fy_opts else [],
                                    key="an_fy_filter")
        with ac2:
            brands = sorted(set(str(c["camp"].get("Brand", "")) for c in all_camps if c["camp"].get("Brand")))
            an_brand = st.multiselect("Brand", brands, key="an_brand_filter")
        ac3, ac4 = st.columns(2)
        with ac3:
            parents = sorted(set(str(c["camp"].get("Deal Group", "")) for c in all_camps if c["camp"].get("Deal Group")))
            an_parent = st.multiselect("Parent/Group", parents, key="an_parent_filter")
        with ac4:
            regions_a = sorted(set(str(c["camp"].get("Region", "")) for c in all_camps if c["camp"].get("Region")))
            an_region = st.multiselect("Region", regions_a, key="an_region_filter")
        filt = all_camps
        if an_fy:     filt = [c for c in filt if str(c["camp"].get("FY", "")) in an_fy]
        if an_brand:  filt = [c for c in filt if str(c["camp"].get("Brand", "")) in an_brand]
        if an_parent: filt = [c for c in filt if str(c["camp"].get("Deal Group", "")) in an_parent]
        if an_region: filt = [c for c in filt if str(c["camp"].get("Region", "")) in an_region]
        currencies_in_view = sorted(set(c["camp"].get("Currency", "") for c in filt
                                         if c["camp"].get("Currency") and c["agg"]["cpv"] > 0))
        st.markdown(f"<p style='font-size:11px;color:#71717A;margin:8px 0'>{len(filt)} campaigns in view</p>",
                    unsafe_allow_html=True)
        def render_tile(label, value, accent=False, good=False):
            color = "#E89E7E" if accent else ("#97C459" if good else "#FAFAFA")
            return (f"<div style='background:#18181B;border:1px solid #27272A;border-radius:8px;padding:9px 11px'>"
                    f"<p style='font-size:9px;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.3px;margin:0 0 3px'>{label}</p>"
                    f"<div style='font-size:14px;font-weight:500;line-height:1.1;color:{color}'>{value}</div></div>")
        def render_aggregate_block(camps_in_currency, currency_label):
            if not camps_in_currency: return
            cpvs = [c["agg"]["cpv"] for c in camps_in_currency if c["agg"]["cpv"] > 0]
            cpes = [c["agg"]["cpe"] for c in camps_in_currency if c["agg"]["cpe"] > 0]
            ers = [c["agg"]["er_pct"] for c in camps_in_currency if c["agg"]["er_pct"] > 0]
            def avg(lst): return (sum(lst) / len(lst)) if lst else 0
            def med(lst):
                if not lst: return 0
                s = sorted(lst); n = len(s)
                return s[n//2] if n % 2 == 1 else (s[n//2 - 1] + s[n//2]) / 2
            avg_cpv = avg(cpvs); med_cpv = med(cpvs)
            avg_cpe = avg(cpes); med_cpe = med(cpes)
            avg_er = avg(ers); med_er = med(ers)
            st.markdown(f"<p class='section-label'>{currency_label} · {len(camps_in_currency)} campaigns</p>", unsafe_allow_html=True)
            tc1, tc2, tc3 = st.columns(3)
            with tc1: st.markdown(render_tile("Avg CPV", format_cpv(avg_cpv, currency_label), accent=True), unsafe_allow_html=True)
            with tc2: st.markdown(render_tile("Avg CPE", format_cpv(avg_cpe, currency_label), accent=True), unsafe_allow_html=True)
            with tc3: st.markdown(render_tile("Avg ER %", f"{avg_er:.2f}%" if avg_er else "—", good=True), unsafe_allow_html=True)
            tc1, tc2, tc3 = st.columns(3)
            with tc1: st.markdown(render_tile("Median CPV", format_cpv(med_cpv, currency_label)), unsafe_allow_html=True)
            with tc2: st.markdown(render_tile("Median CPE", format_cpv(med_cpe, currency_label)), unsafe_allow_html=True)
            with tc3: st.markdown(render_tile("Median ER %", f"{med_er:.2f}%" if med_er else "—"), unsafe_allow_html=True)
        if len(currencies_in_view) == 1:
            cur = currencies_in_view[0]
            in_cur = [c for c in filt if c["camp"].get("Currency", "") == cur]
            render_aggregate_block(in_cur, cur)
        elif len(currencies_in_view) > 1:
            for cur in currencies_in_view:
                in_cur = [c for c in filt if c["camp"].get("Currency", "") == cur]
                render_aggregate_block(in_cur, cur)
        else:
            n_in_filter = len(filt)
            if n_in_filter > 0:
                st.markdown(f"<div style='background:#18181B;border:1px solid #27272A;border-radius:10px;padding:14px;margin:8px 0'>"
                            f"<div style='color:#E89E7E;font-size:12px;font-weight:500;margin-bottom:4px'>{n_in_filter} campaigns in this filter — none have posts attached yet</div>"
                            f"<div style='color:#A1A1AA;font-size:11px;line-height:1.5'>"
                            f"Performance metrics need at least one post per campaign. Open the Campaigns tab, tap into a campaign, "
                            f"and use <b>+ Add Post</b> to start tracking. Once posts are added with view counts, this tab will populate.</div></div>",
                            unsafe_allow_html=True)
            else:
                st.info("No campaigns match this filter.")
        if currencies_in_view:
            cur_counts = {c: sum(1 for x in filt if x["camp"].get("Currency", "") == c) for c in currencies_in_view}
            chart_currency = max(cur_counts.keys(), key=lambda k: cur_counts[k])
            in_chart_cur = [c for c in filt if c["camp"].get("Currency", "") == chart_currency]
            with_perf = [c for c in in_chart_cur if c["agg"]["cpv"] > 0]
            if with_perf:
                st.markdown(f"<p class='section-label'>Trend over time · {chart_currency}</p>", unsafe_allow_html=True)
                trend_metric = st.radio("Metric", ["CPV", "CPE"], horizontal=True,
                                          key=f"trend_metric_{chart_currency}", label_visibility="collapsed")
                MONTH_ORDER = ["July","August","September","October","November","December",
                               "January","February","March","April","May","June"]
                month_buckets = {m: [] for m in MONTH_ORDER}
                for c in with_perf:
                    m = c["camp"].get("Month", "")
                    if m in month_buckets:
                        v = c["agg"]["cpv"] if trend_metric == "CPV" else c["agg"]["cpe"]
                        if v > 0: month_buckets[m].append(v)
                trend_df = pd.DataFrame([
                    {"Month": m[:3], "Value": (sum(vs)/len(vs)) if vs else 0}
                    for m, vs in month_buckets.items()
                ])
                if trend_df["Value"].sum() > 0:
                    fig = go.Figure(data=[go.Scatter(x=trend_df["Month"], y=trend_df["Value"],
                        mode="lines+markers", line=dict(color="#E89E7E", width=2),
                        marker=dict(size=7, color="#E89E7E"),
                        hovertemplate=f"<b>%{{x}}</b><br>{trend_metric}: %{{y:.4f}}<extra></extra>")])
                    layout = base_layout(height=200)
                    fig.update_layout(**layout)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(f"<p class='section-label'>Top + Bottom 5 by CPV · {chart_currency}</p>",
                            unsafe_allow_html=True)
                sorted_perf = sorted(with_perf, key=lambda c: c["agg"]["cpv"])
                top5 = sorted_perf[:5]
                bot5 = sorted_perf[-5:] if len(sorted_perf) > 5 else []
                st.markdown("<p style='font-size:10px;color:#97C459;text-transform:uppercase;letter-spacing:0.4px;margin:8px 0 4px'>Top 5 (best CPV)</p>",
                            unsafe_allow_html=True)
                top_df = pd.DataFrame([{"Name": c["camp"].get("Campaign Name", "")[:30], "CPV": c["agg"]["cpv"]} for c in top5])
                if not top_df.empty:
                    st.plotly_chart(make_hbar_chart(top_df, "CPV", "Name", color="#97C459"),
                                    use_container_width=True, config={"displayModeBar": False})
                if bot5:
                    st.markdown("<p style='font-size:10px;color:#E24B4A;text-transform:uppercase;letter-spacing:0.4px;margin:8px 0 4px'>Bottom 5 (worst CPV)</p>",
                                unsafe_allow_html=True)
                    bot_df = pd.DataFrame([{"Name": c["camp"].get("Campaign Name", "")[:30], "CPV": c["agg"]["cpv"]} for c in bot5])
                    st.plotly_chart(make_hbar_chart(bot_df, "CPV", "Name", color="#E24B4A"),
                                    use_container_width=True, config={"displayModeBar": False})
                st.markdown(f"<p class='section-label'>CPV by Brand · {chart_currency}</p>", unsafe_allow_html=True)
                brand_cpvs = defaultdict(list)
                for c in with_perf:
                    b = c["camp"].get("Brand", "Unknown")
                    brand_cpvs[b].append(c["agg"]["cpv"])
                brand_avg = sorted([(b, sum(v)/len(v)) for b, v in brand_cpvs.items()], key=lambda x: x[1])
                if brand_avg:
                    bb_df = pd.DataFrame([{"Brand": b, "CPV": cpv} for b, cpv in brand_avg])
                    st.plotly_chart(make_hbar_chart(bb_df, "CPV", "Brand", color="#E89E7E"),
                                    use_container_width=True, config={"displayModeBar": False})
