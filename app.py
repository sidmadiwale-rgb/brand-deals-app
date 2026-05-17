"""
Priya Sid Enterprise — Brand Deals Tracker
Streamlit app, Mercury Dark theme, live Google Sheets.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from collections import defaultdict

st.set_page_config(page_title="Brand Deals", page_icon="static/apple-touch-icon.png",
                    layout="centered", initial_sidebar_state="collapsed")

# PWA / Add-to-Home-Screen support: link manifest + apple-touch-icon, declare standalone mode.
# Streamlit serves files from /app/static/ when enableStaticServing=true (set in .streamlit/config.toml).
st.markdown("""
<link rel="manifest" href="app/static/manifest.json">
<link rel="apple-touch-icon" sizes="180x180" href="app/static/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="app/static/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="app/static/icon-512.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Brand Deals">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0A0A0A">
""", unsafe_allow_html=True)

SHEET_ID = "1KywyIay918fxbY-GjTe2QGwwS5Vzek2ALxFN-QK2Ujk"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme")
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

st.markdown("""
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
        if "FY" in row and "Status" in row and "Brand" in row:
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

@st.cache_data(ttl=300)
def load_fx_rates():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("FX Rates")
    all_values = sh.get_all_values()
    rates = {"AUD": 1.0, "USD": 1.3807, "AED": 0.376, "INR": 0.014614}
    for row in all_values:
        if len(row) >= 3 and row[1] in ("AUD", "USD", "AED", "INR"):
            try: rates[row[1]] = float(row[2])
            except: pass
    return rates

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
    st.markdown(f"<p class='app-name' style='margin-top:4px'>{deal.get('Brand', '(no name)')}</p>", unsafe_allow_html=True)
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
    new_brand = st.text_input("Brand", value=deal.get("Brand", "") or "", key=f"e_brand_{sheet_row}")
    new_deal_group = st.text_input("Deal Group", value=deal.get("Deal Group", "") or "",
                                    placeholder="Optional", key=f"e_dg_{sheet_row}")
    new_rollup = st.text_input("Roll-up Brand", value=deal.get("Roll-up Brand", "") or "",
                                placeholder="e.g. HUL", key=f"e_rb_{sheet_row}")
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
                field_updates = {"FY": new_fy, "Status": new_status, "Deal Group": new_deal_group,
                    "Month": new_month, "Region": new_region, "Agency": new_agency,
                    "Brand": new_brand, "Currency": new_curr, "Gross (orig)": new_gross,
                    "Commission %": new_comm_pct, "Invoice #": new_inv, "Invoice Date": new_inv_date,
                    "Payment Date": new_pay_date, "Deliverables": new_deliv, "Roll-up Brand": new_rollup}
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

tabs = st.tabs(["Overview", "Brand Deals", "Charts", "Ad Revenue", "Add"])

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
    st.markdown("<p class='app-name'>Brand Deals</p>", unsafe_allow_html=True)
    sorted_deals = sorted(period_deals, key=lambda d: d.get("month_date") or date.min, reverse=True)
    st.markdown("<p class='section-label'>Filter</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        statuses = sorted(set(d.get("Status", "") for d in sorted_deals if d.get("Status")))
        status_f = st.multiselect("Status", statuses, key="bd_status_filter")
    with c2:
        regions = sorted(set(d.get("Region", "") for d in sorted_deals if d.get("Region")))
        region_f = st.multiselect("Region", regions, key="bd_region_filter")
    search = st.text_input("Search brand", placeholder="e.g. Plum, Etihad…", key="bd_search")
    filtered = sorted_deals
    if status_f: filtered = [d for d in filtered if d.get("Status") in status_f]
    if region_f: filtered = [d for d in filtered if d.get("Region") in region_f]
    if search: filtered = [d for d in filtered if search.lower() in str(d.get("Brand", "")).lower()]
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
        brand = d.get("Brand", ""); month = d.get("Month", "")
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
        rb = (d.get("Roll-up Brand") or d.get("Brand") or "Unknown").strip()
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
    st.markdown("<p class='app-name'>New Deal</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px;color:#71717A;margin-top:-4px'>Saves to Deals Log · auto-converts currency</p>", unsafe_allow_html=True)
    with st.form("add_deal", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_fy = st.selectbox("FY", ["FY26", "FY27"])
            new_status = st.selectbox("Status", ["Pitched", "Locked & Executing",
                "Completed (India) - Not Invoiced", "Completed (Not-India) - Not Invoiced",
                "Invoiced (India)", "Invoiced (Non-India)", "Paid"])
            new_month = st.selectbox("Month", MONTHS)
            new_region = st.selectbox("Region", ["India", "Australia", "UAE", "US/Global"])
            new_currency = st.selectbox("Currency", ["AUD", "USD", "INR", "AED"])
        with c2:
            new_brand = st.text_input("Brand", placeholder="e.g. Plum")
            new_agency = st.text_input("Agency", placeholder="Optional")
            new_gross = st.number_input("Gross (orig)", min_value=0.0, step=1000.0)
            new_comm = st.number_input("Commission %", min_value=0.0, max_value=100.0,
                                         step=5.0, value=15.0) / 100
            new_inv = st.text_input("Invoice #", placeholder="Optional")
        new_deliv = st.text_area("Deliverables", placeholder="e.g. 1 IG Reel + 2 Stories…")
        submitted = st.form_submit_button("Add Deal", use_container_width=True, type="primary")
        if submitted:
            if not new_brand:
                st.error("Brand is required")
            else:
                try:
                    gc = get_gspread_client()
                    ws = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
                    headers = None
                    for r in ws.get_all_values():
                        if "FY" in r and "Status" in r and "Brand" in r:
                            headers = r; break
                    if not headers:
                        st.error("Couldn't find header row")
                    else:
                        new_row = [""] * len(headers)
                        fields = {"FY": new_fy, "Status": new_status, "Month": new_month,
                            "Region": new_region, "Agency": new_agency, "Brand": new_brand,
                            "Currency": new_currency, "Gross (orig)": new_gross,
                            "Commission %": new_comm, "Invoice #": new_inv,
                            "Deliverables": new_deliv}
                        for h, v in fields.items():
                            if h in headers:
                                new_row[headers.index(h)] = v
                        ws.append_row(new_row, value_input_option="USER_ENTERED")
                        st.success(f"Added {new_brand}!"); st.cache_data.clear()
                except Exception as e:
                    st.error(f"Failed to add: {e}")
to add: {e}")
