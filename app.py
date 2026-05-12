"""
Priya Sid Enterprise — Brand Deals Tracker
Streamlit app, Mercury Dark theme, live Google Sheets connection.

Reads from + writes to: FY26 Brand Deals — Live (Google Sheets)
Sheet ID: 1vVUjdW43b45GHqg91bSu9_zQlkUn0xaRKqBFzmf2go8

Auth: shared password (set in Streamlit Cloud secrets as APP_PASSWORD)
Data: gspread + service account JSON in secrets as 'gcp_service_account'
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime
import json

# ============== CONFIG ==============
st.set_page_config(
    page_title="Priya Sid Enterprise",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SHEET_ID = "1KywyIay918fxbY-GjTe2QGwwS5Vzek2ALxFN-QK2Ujk"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
H2_MONTHS = {"July", "August", "September", "October", "November", "December"}

# ============== STYLES (Mercury Dark) ==============
st.markdown("""
<style>
  /* App background */
  .stApp, .main, .block-container { background: #0A0A0A; color: #FAFAFA; }
  .block-container { max-width: 480px; padding-top: 0.5rem; padding-bottom: 5rem; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; color: #FAFAFA; }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none !important; }

  /* Brand bar */
  .brand { font-size: 10.5px; font-weight: 500; color: #A1A1AA;
           letter-spacing: 1.5px; text-transform: uppercase; margin: 0; }
  .app-name { font-family: 'Helvetica Neue', 'Helvetica', 'Inter', sans-serif;
              font-size: 20px; font-weight: 600; color: #FAFAFA;
              letter-spacing: -0.5px; margin: 0 0 10px; line-height: 1.0; }

  /* Period pill */
  .period-pill { display: inline-flex; align-items: center; gap: 6px;
                 padding: 4px 10px; border-radius: 6px;
                 font-size: 11px; font-weight: 500; }
  .pp-fy { background: #0F2547; border: 0.5px solid #1E40AF; color: #93C5FD; }
  .pp-quarter { background: #1E1B0B; border: 0.5px solid #84671A; color: #FBBF24; }
  .pp-calendar { background: #052E2A; border: 0.5px solid #047857; color: #6EE7B7; }

  /* Currency pill */
  .currency-pill { display: inline-flex; align-items: center; gap: 4px;
                   padding: 5px 10px; background: #18181B;
                   border: 0.5px solid #27272A; border-radius: 8px;
                   font-size: 11px; font-weight: 500; color: #FAFAFA; }

  /* Section labels */
  .section-label { font-size: 11px; font-weight: 500; color: #A1A1AA;
                   letter-spacing: 0.4px; text-transform: uppercase;
                   margin: 18px 0 10px; }

  /* KPI tiles */
  .kpi { background: #18181B; border: 0.5px solid #27272A; border-radius: 14px;
         padding: 14px 14px 16px; margin-bottom: 10px; }
  .kpi-label { font-size: 11px; color: #A1A1AA; font-weight: 500;
               margin-bottom: 6px; letter-spacing: 0.2px; }
  .kpi-value { font-size: 22px; font-weight: 500; color: #FAFAFA;
               letter-spacing: -0.6px; line-height: 1.1; }
  .kpi-sub { font-size: 10.5px; color: #A1A1AA; margin-top: 6px;
             font-weight: 400; line-height: 1.3; }
  .accent-green { color: #10B981; font-weight: 500; }

  /* Status cards */
  .status-card { background: #18181B; border: 0.5px solid #27272A;
                 border-radius: 14px; margin-bottom: 8px; padding: 14px 16px;
                 display: flex; align-items: center; justify-content: space-between; }
  .status-dot { width: 8px; height: 8px; border-radius: 50%;
                display: inline-block; margin-right: 12px; vertical-align: middle; }
  .status-name { font-size: 14px; font-weight: 500; color: #FAFAFA; }
  .status-count { font-size: 11px; color: #A1A1AA; margin-top: 2px; }
  .status-amount { font-size: 15px; font-weight: 500; color: #FAFAFA;
                   letter-spacing: -0.2px; }
  .summary-row { display: flex; justify-content: space-between; align-items: center;
                 background: #18181B; border: 0.5px solid #27272A;
                 border-radius: 14px; margin-top: 8px; padding: 14px 16px; }

  /* Deal pills */
  .pill { display: inline-block; padding: 2px 7px; border-radius: 6px;
          font-size: 10px; font-weight: 500; letter-spacing: 0.1px; }
  .pill-paid { background: #052E2A; color: #34D399; }
  .pill-invoiced-india { background: #3A2410; color: #FB923C; }
  .pill-invoiced-nonindia { background: #0F2547; color: #60A5FA; }
  .pill-not-invoiced { background: #3D2F08; color: #FACC15; }
  .pill-locked { background: #3A1313; color: #F87171; }
  .pill-pitched { background: #262626; color: #A1A1AA; }

  /* Deal cards */
  .deal-card { background: #18181B; border: 0.5px solid #27272A;
               border-radius: 12px; margin-bottom: 8px; padding: 12px 14px; }

  /* Streamlit input overrides for dark theme */
  div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input,
  .stTextArea textarea {
    background: #18181B !important; border: 0.5px solid #27272A !important;
    color: #FAFAFA !important;
  }
  .stButton button { background: #FAFAFA; color: #0A0A0A;
                     border: none; border-radius: 12px; padding: 10px 20px;
                     font-weight: 500; }

  /* Tab labels */
  .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
  .stTabs [data-baseweb="tab"] { background: #18181B; border-radius: 8px;
                                  color: #A1A1AA; padding: 8px 12px; font-size: 12px; }
  .stTabs [aria-selected="true"] { background: #FAFAFA !important; color: #0A0A0A !important; }
</style>
""", unsafe_allow_html=True)

# ============== AUTH ==============
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

# ============== GOOGLE SHEETS CONNECTION ==============
@st.cache_resource
def get_gspread_client():
    """Authenticate with Google using the service account JSON in secrets."""
    creds_info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def load_deals():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
    all_values = sh.get_all_values()
    # Find header row by looking for FY column
    header_idx = None
    for i, row in enumerate(all_values):
        if "FY" in row and "Status" in row and "Brand" in row:
            header_idx = i
            break
    if header_idx is None:
        return pd.DataFrame()
    headers = all_values[header_idx]
    rows = all_values[header_idx + 1:]
    # Deduplicate header names (gspread breaks on dupes)
    seen = {}
    clean_headers = []
    for h in headers:
        if h in seen:
            seen[h] += 1
            clean_headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            clean_headers.append(h)
    df = pd.DataFrame(rows, columns=clean_headers)
    df = df[df["FY"].astype(str).str.strip() != ""]
    return df

@st.cache_data(ttl=300)
def load_ad_revenue():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("Ad Revenue")
    all_values = sh.get_all_values()
    # Find header row by looking for "Month" + "YouTube" columns
    header_idx = None
    for i, row in enumerate(all_values):
        if any("Month" == c.strip() for c in row) and any("YouTube" in c for c in row):
            header_idx = i
            break
    if header_idx is None:
        return pd.DataFrame()
    headers = all_values[header_idx]
    # Data rows: from next row until we hit "TOTAL" or empty Month
    rows = []
    for r in all_values[header_idx + 1:]:
        if not r or not r[0] or "TOTAL" in str(r[0]).upper():
            break
        rows.append(r)
    df = pd.DataFrame(rows, columns=headers)
    return df

@st.cache_data(ttl=300)
def load_fx_rates():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID).worksheet("FX Rates")
    all_values = sh.get_all_values()
    rates = {}
    for row in all_values:
        if len(row) >= 3 and row[1] in ("AUD", "USD", "AED", "INR"):
            try:
                rates[row[1]] = float(row[2])
            except:
                pass
    return rates

# ============== HELPERS ==============
def parse_money(s):
    """Parse a money string like '$1,234.56' or '7,307' to float."""
    if not s or s == "" or s == "-":
        return 0.0
    s = str(s).replace("$", "").replace("A$", "").replace("₹", "").replace("د.إ", "")
    s = s.replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return 0.0

def parse_pct(s):
    """Parse '15.0%' or '0.15' to 0.15."""
    if not s or s == "" or s == "-":
        return 0.0
    s = str(s).strip()
    if s.endswith("%"):
        return float(s[:-1]) / 100
    try:
        v = float(s)
        return v / 100 if v > 1 else v
    except:
        return 0.0

def get_period_filter():
    """Return (start_year, start_month, end_year, end_month) for current period selection."""
    mode = st.session_state.get("period_mode", "FY")
    year = st.session_state.get("period_year", "FY26")
    quarter = st.session_state.get("period_quarter", "All")

    if mode == "FY":
        yr = int(year[2:])  # 'FY26' → 26 → year 2026
        # FY26 = Jul 2025 - Jun 2026
        if quarter == "All":
            return (2000 + yr - 1, 7, 2000 + yr, 6)
        elif quarter == "Q1":
            return (2000 + yr - 1, 7, 2000 + yr - 1, 9)
        elif quarter == "Q2":
            return (2000 + yr - 1, 10, 2000 + yr - 1, 12)
        elif quarter == "Q3":
            return (2000 + yr, 1, 2000 + yr, 3)
        elif quarter == "Q4":
            return (2000 + yr, 4, 2000 + yr, 6)
    elif mode == "Calendar":
        yr = int(year)
        if quarter == "All":
            return (yr, 1, yr, 12)
        elif quarter == "Q1":
            return (yr, 1, yr, 3)
        elif quarter == "Q2":
            return (yr, 4, yr, 6)
        elif quarter == "Q3":
            return (yr, 7, yr, 9)
        elif quarter == "Q4":
            return (yr, 10, yr, 12)
    return (2025, 7, 2026, 6)  # fallback FY26

def parse_month_date(s):
    """Parse '01/06/2026' or similar to date."""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(s, fmt).date()
        except:
            continue
    return None

def in_period(month_date, period):
    """Check if a month_date is within the period range."""
    if not month_date:
        return False
    sy, sm, ey, em = period
    start = date(sy, sm, 1)
    if em == 12:
        end = date(ey + 1, 1, 1)
    else:
        end = date(ey, em + 1, 1)
    return start <= month_date < end

def months_elapsed(period):
    """How many months in the period have elapsed up to today."""
    sy, sm, ey, em = period
    today = date.today()
    start = date(sy, sm, 1)
    end = date(ey, em, 28)  # use 28 to be safe

    if today < start:
        return 0

    # Cap end at today
    effective_end = min(today, end)
    return (effective_end.year - start.year) * 12 + (effective_end.month - start.month) + 1

def format_money(amt, currency="AUD"):
    """Format a number as currency string."""
    if currency == "AUD":
        return f"${amt:,.0f}"
    elif currency == "USD":
        return f"${amt:,.0f}"
    elif currency == "INR":
        # Indian grouping
        if amt >= 10000000:
            return f"₹{amt:,.0f}"  # crores
        elif amt >= 100000:
            return f"₹{amt:,.0f}"
        else:
            return f"₹{amt:,.0f}"
    elif currency == "AED":
        return f"د.إ {amt:,.0f}"
    return f"{amt:,.0f}"

def format_original_currency(gross_orig, currency):
    """Format a deal amount in its original currency for the Deals list."""
    if currency == "INR":
        if gross_orig >= 100000:
            return f"₹{gross_orig/100000:.1f}L"
        return f"₹{gross_orig:,.0f}"
    elif currency == "USD":
        return f"${gross_orig:,.0f}"
    elif currency == "AED":
        return f"د.إ {gross_orig:,.0f}"
    elif currency == "AUD":
        return f"A${gross_orig:,.0f}"
    return f"{gross_orig:,.0f}"

def pill_class(status):
    if not status: return "pill-pitched"
    if status == "Paid": return "pill-paid"
    if "Invoiced (India)" in status: return "pill-invoiced-india"
    if "Invoiced (Non" in status: return "pill-invoiced-nonindia"
    if "Not Invoiced" in status: return "pill-not-invoiced"
    if "Locked" in status: return "pill-locked"
    return "pill-pitched"

# ============== LOAD DATA ==============
try:
    deals_raw = load_deals()
    ad_rev_raw = load_ad_revenue()
    fx_rates = load_fx_rates()
except Exception as e:
    st.error(f"Couldn't load data from Google Sheets: {e}")
    st.stop()

# Parse + enrich deals
deals = []
for _, r in deals_raw.iterrows():
    d = r.to_dict()
    d["gross_orig"] = parse_money(d.get("Gross (orig)", 0))
    d["commission_pct"] = parse_pct(d.get("Commission %", 0))
    d["gross_aud"] = parse_money(d.get("Gross AUD", 0))
    d["net_aud"] = parse_money(d.get("Net AUD", 0))
    d["commission_aud"] = parse_money(d.get("Commission AUD", 0))
    d["month_date"] = parse_month_date(d.get("Month Date", ""))
    deals.append(d)

# Parse ad revenue monthly
ad_rev_monthly = []
for _, r in ad_rev_raw.iterrows():
    month = r.get("Month", "")
    if not month: continue
    yt_aud = parse_money(r.get("YouTube (AUD)", 0))
    fb_usd = parse_money(r.get("Facebook (USD)", 0))
    fb_aud = parse_money(r.get("Facebook (AUD)", 0))
    monthly_total = parse_money(r.get("Monthly Total (AUD)", 0))
    ad_rev_monthly.append({
        "month": month, "yt_aud": yt_aud, "fb_usd": fb_usd,
        "fb_aud": fb_aud, "total_aud": monthly_total,
    })

# ============== SESSION STATE DEFAULTS ==============
if "period_mode" not in st.session_state:
    st.session_state.period_mode = "FY"
if "period_year" not in st.session_state:
    st.session_state.period_year = "FY26"
if "period_quarter" not in st.session_state:
    st.session_state.period_quarter = "All"
if "display_currency" not in st.session_state:
    st.session_state.display_currency = "AUD"

# ============== HEADER ==============
def render_global_header():
    """Render the brand bar + currency + period filter ONCE at the top (not per-tab)."""
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<p class='brand'>Priya Sid Enterprise</p>", unsafe_allow_html=True)
    with c2:
        cur_options = ["AUD", "USD", "INR", "AED"]
        st.selectbox("Currency", cur_options,
                     index=cur_options.index(st.session_state.display_currency),
                     key="display_currency", label_visibility="collapsed")
    with st.expander(f"📅 {period_label()}", expanded=False):
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

def render_header(tab_name, show_period=True, show_currency=True):
    """Per-tab title only. Brand/currency/period are global (rendered above)."""
    st.markdown(f"<p class='app-name'>{tab_name}</p>", unsafe_allow_html=True)

def period_label():
    mode = st.session_state.period_mode
    year = st.session_state.period_year
    quarter = st.session_state.period_quarter
    if quarter == "All":
        return f"{year} · All"
    return f"{year} · {quarter}"

def period_pill_class():
    quarter = st.session_state.period_quarter
    if quarter != "All":
        return "pp-quarter"
    return "pp-calendar" if st.session_state.period_mode == "Calendar" else "pp-fy"

# ============== GLOBAL HEADER (once, before tabs) ==============
render_global_header()

# Quick debug info if no deals loaded
if len(deals) == 0:
    st.warning(f"⚠️ No brand deals loaded. Sheet returned {len(deals_raw)} rows. "
               f"Check that the 'Deals Log' tab in your Google Sheet has data and the FY column is filled.")

# ============== TABS ==============
tabs = st.tabs(["Overview", "Brand Deals", "Charts", "Ad Revenue", "Add"])

# ============== TAB 1: OVERVIEW ==============
with tabs[0]:
    render_header("Overview")
    period = get_period_filter()
    elapsed = max(months_elapsed(period), 1)
    period_deals = [d for d in deals if in_period(d["month_date"], period)]

    # Ad revenue for period
    ad_total_period = 0
    ad_months_with_data = 0
    for ar in ad_rev_monthly:
        try:
            month_name = ar["month"].split(" ")[0]
            year = int(ar["month"].split(" ")[1])
            m = MONTHS.index(month_name) + 1
            md = date(year, m, 1)
            if in_period(md, period) and ar["total_aud"] > 0:
                ad_total_period += ar["total_aud"]
                ad_months_with_data += 1
        except:
            continue

    # Aggregate
    total_gross_deals = sum(d["gross_aud"] for d in period_deals)
    total_net_deals = sum(d["net_aud"] for d in period_deals)
    total_gross = total_gross_deals + ad_total_period
    total_net = total_net_deals + ad_total_period

    # Commission and TDS
    total_comm = sum(d["commission_aud"] for d in period_deals)
    total_tds = 0
    for d in period_deals:
        if d.get("Currency") == "INR":
            net_fee = d["gross_orig"] - d["gross_orig"] * d["commission_pct"]
            total_tds += net_fee * 0.2122 * fx_rates.get("INR", 0.014614)

    # KPI tiles 2x3
    st.markdown("<p class='section-label'>Total</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='kpi'><div class='kpi-label'>Gross Revenue</div>"
                    f"<div class='kpi-value'>{format_money(total_gross)}</div>"
                    f"<div class='kpi-sub'>Includes <span class='accent-green'>+ {format_money(ad_total_period)}</span> in Ad Revenue</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='kpi'><div class='kpi-label'>Avg Gross / Month</div>"
                    f"<div class='kpi-value'>{format_money(total_gross/elapsed)}</div>"
                    f"<div class='kpi-sub'>Gross, {elapsed}mo Elapsed</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='kpi'><div class='kpi-label'>Commission</div>"
                    f"<div class='kpi-value'>{format_money(total_comm)}</div>"
                    f"<div class='kpi-sub'>Agency Commission 15%</div></div>",
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi'><div class='kpi-label'>Net Income</div>"
                    f"<div class='kpi-value'>{format_money(total_net)}</div>"
                    f"<div class='kpi-sub'>After Commission, TDS, etc.</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='kpi'><div class='kpi-label'>Avg Net / Month</div>"
                    f"<div class='kpi-value'>{format_money(total_net/elapsed)}</div>"
                    f"<div class='kpi-sub'>Net, {elapsed}mo Elapsed</div></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='kpi'><div class='kpi-label'>TDS</div>"
                    f"<div class='kpi-value'>{format_money(total_tds)}</div>"
                    f"<div class='kpi-sub'>Tax Deducted in India 21.22%</div></div>",
                    unsafe_allow_html=True)

    # Operational
    st.markdown("<p class='section-label'>Operational</p>", unsafe_allow_html=True)
    paid_d = [d for d in period_deals if d.get("Status") == "Paid"]
    paid_amt = sum(d["net_aud"] for d in paid_d) + ad_total_period
    awaiting_d = [d for d in period_deals if str(d.get("Status", "")).startswith("Invoiced")]
    awaiting_amt = sum(d["net_aud"] for d in awaiting_d)
    need_inv_d = [d for d in period_deals if "Not Invoiced" in str(d.get("Status", ""))]
    need_inv_amt = sum(d["net_aud"] for d in need_inv_d)
    locked_d = [d for d in period_deals if d.get("Status") == "Locked & Executing"]
    locked_amt = sum(d["net_aud"] for d in locked_d)

    for name, color, df_grp, amt, sub in [
        ("Paid", "#10B981", paid_d, paid_amt, f"{len(paid_d)} Deals + Ad Revenue"),
        ("Awaiting Payment", "#FB923C", awaiting_d, awaiting_amt, f"{len(awaiting_d)} Invoiced"),
        ("Need to Invoice", "#FACC15", need_inv_d, need_inv_amt, f"{len(need_inv_d)} Deals"),
        ("Locked & Executing", "#F87171", locked_d, locked_amt, f"{len(locked_d)} Deals"),
    ]:
        st.markdown(
            f"<div class='status-card'>"
            f"<div><span class='status-dot' style='background:{color}'></span>"
            f"<span class='status-name'>{name}</span>"
            f"<div class='status-count' style='margin-left:20px'>{sub}</div></div>"
            f"<div class='status-amount'>{format_money(amt)}</div></div>",
            unsafe_allow_html=True
        )

    coming_in = awaiting_amt + need_inv_amt + locked_amt
    st.markdown(
        f"<div class='summary-row'>"
        f"<div><div style='font-size:13px;font-weight:500'>Total Money Coming in (Net)</div>"
        f"<div class='status-count' style='margin-top:2px'>Awaiting + Need to Invoice + Locked</div></div>"
        f"<div class='status-amount'>{format_money(coming_in)}</div></div>",
        unsafe_allow_html=True
    )

# ============== TAB 2: BRAND DEALS ==============
with tabs[1]:
    render_header("Brand Deals")
    period = get_period_filter()
    period_deals = [d for d in deals if in_period(d["month_date"], period)]
    period_deals.sort(key=lambda d: d.get("month_date") or date.min, reverse=True)

    st.markdown("<p class='section-label'>Filter</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        statuses = sorted(set(d.get("Status", "") for d in period_deals if d.get("Status")))
        status_f = st.multiselect("Status", statuses)
    with c2:
        regions = sorted(set(d.get("Region", "") for d in period_deals if d.get("Region")))
        region_f = st.multiselect("Region", regions)
    search = st.text_input("Search brand", placeholder="e.g. Plum, Etihad…")

    filtered = period_deals
    if status_f: filtered = [d for d in filtered if d.get("Status") in status_f]
    if region_f: filtered = [d for d in filtered if d.get("Region") in region_f]
    if search: filtered = [d for d in filtered if search.lower() in str(d.get("Brand", "")).lower()]

    st.markdown(f"<p style='font-size:11px;color:#71717A;margin:8px 0'>{len(filtered)} deals</p>", unsafe_allow_html=True)

    for d in filtered:
        brand = d.get("Brand", "")
        month = d.get("Month", "")
        region = d.get("Region", "")
        agency = d.get("Agency", "")
        status = d.get("Status", "")
        inv = d.get("Invoice #", "")
        amt_str = format_original_currency(d["gross_orig"], d.get("Currency", "AUD"))
        pcl = pill_class(status)
        meta = f"{month} 2026 · {region}" + (f" · {agency}" if agency else "")
        pills = f"<span class='pill {pcl}'>{status}</span>"
        if inv:
            pills += f" <span class='pill {pcl}'>{inv}</span>"
        st.markdown(
            f"<div class='deal-card'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px'>"
            f"<div><div style='font-size:14px;font-weight:500'>{brand}</div>"
            f"<div style='font-size:11px;color:#A1A1AA;margin-top:2px'>{meta}</div></div>"
            f"<div style='text-align:right'><div style='font-size:14px;font-weight:500'>{amt_str}</div>"
            f"<div style='margin-top:4px'>{pills}</div></div></div></div>",
            unsafe_allow_html=True
        )

# ============== TAB 3: CHARTS ==============
with tabs[2]:
    render_header("Charts")
    period = get_period_filter()
    elapsed = max(months_elapsed(period), 1)
    period_deals = [d for d in deals if in_period(d["month_date"], period)]

    # Monthly aggregation (deals AUD)
    from collections import defaultdict
    monthly = defaultdict(float)
    monthly_india = defaultdict(float)
    monthly_row = defaultdict(float)

    FX_INR = fx_rates.get("INR", 0.014614)
    FX_USD = fx_rates.get("USD", 1.3807)
    FX_AED = fx_rates.get("AED", 0.376)

    def to_inr_lakhs(d):
        g = d["gross_orig"]; c = d.get("Currency", "AUD")
        if c == "INR": inr = g
        elif c == "AUD": inr = g / FX_INR
        elif c == "USD": inr = g * FX_USD / FX_INR
        elif c == "AED": inr = g * FX_AED / FX_INR
        else: inr = 0
        return inr / 100000

    for d in period_deals:
        if not d.get("month_date"): continue
        ym = d["month_date"].strftime("%Y-%m")
        monthly[ym] += d["gross_aud"]
        if d.get("Region") == "India":
            monthly_india[ym] += to_inr_lakhs(d)
        else:
            monthly_row[ym] += d["gross_aud"]

    # Monthly Gross
    st.markdown("<p class='section-label'>Monthly Gross — Brand Deals (All Regions)</p>", unsafe_allow_html=True)
    total_dg = sum(monthly.values())
    avg_dg = total_dg / elapsed
    df_m = pd.DataFrame(sorted(monthly.items()), columns=["Month", "AUD"])
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin:-8px 0 8px'>Avg {format_money(avg_dg)} / month</div>", unsafe_allow_html=True)
    if len(df_m) > 0:
        st.bar_chart(df_m.set_index("Month"), color="#10B981", height=180)

    # India Lakhs
    st.markdown("<p class='section-label'>Collective / India — Monthly Gross (₹ Lakhs)</p>", unsafe_allow_html=True)
    total_india_lakhs = sum(monthly_india.values())
    avg_india = total_india_lakhs / elapsed
    df_i = pd.DataFrame(sorted(monthly_india.items()), columns=["Month", "Lakhs"])
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin:-8px 0 8px'>Avg ₹{avg_india:.1f}L / month</div>", unsafe_allow_html=True)
    if len(df_i) > 0:
        st.bar_chart(df_i.set_index("Month"), color="#FB923C", height=180)

    # Rest of World
    st.markdown("<p class='section-label'>Rest of World — Monthly Gross (AUD)</p>", unsafe_allow_html=True)
    total_row = sum(monthly_row.values())
    avg_row = total_row / elapsed
    df_r = pd.DataFrame(sorted(monthly_row.items()), columns=["Month", "AUD"])
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin:-8px 0 8px'>Avg {format_money(avg_row)} / month</div>", unsafe_allow_html=True)
    if len(df_r) > 0:
        st.bar_chart(df_r.set_index("Month"), color="#3B82F6", height=180)

    # Ad Revenue
    st.markdown("<p class='section-label'>Ad Revenue — Monthly</p>", unsafe_allow_html=True)
    ad_in_period = []
    for ar in ad_rev_monthly:
        try:
            month_name, year_str = ar["month"].split(" ")
            m = MONTHS.index(month_name) + 1
            md = date(int(year_str), m, 1)
            if in_period(md, period):
                ad_in_period.append({"Month": md.strftime("%Y-%m"), "YouTube": ar["yt_aud"], "Facebook": ar["fb_aud"]})
        except:
            continue
    df_ad = pd.DataFrame(ad_in_period)
    months_with_data_ar = sum(1 for ar in ad_in_period if ar["YouTube"] > 0 or ar["Facebook"] > 0)
    ar_total_aud = sum(ar["YouTube"] + ar["Facebook"] for ar in ad_in_period)
    ar_avg = ar_total_aud / max(months_with_data_ar, 1)
    st.markdown(f"<div style='font-size:11px;color:#A1A1AA;text-align:right;margin:-8px 0 8px'>Avg {format_money(ar_avg)} / month (÷{months_with_data_ar})</div>", unsafe_allow_html=True)
    if len(df_ad) > 0:
        st.bar_chart(df_ad.set_index("Month"), height=180, color=["#EF4444", "#3B82F6"])

    # Top brands
    st.markdown("<p class='section-label'>Top Brands — Roll-up (AUD)</p>", unsafe_allow_html=True)
    brand_sums = defaultdict(float)
    for d in period_deals:
        rb = d.get("Roll-up Brand") or d.get("Brand") or "Unknown"
        brand_sums[rb] += d["gross_aud"]
    top10 = sorted(brand_sums.items(), key=lambda x: -x[1])[:10]
    df_top = pd.DataFrame(top10, columns=["Brand", "AUD"])
    if len(df_top) > 0:
        st.bar_chart(df_top.set_index("Brand"), color="#A1A1AA", height=240)

# ============== TAB 4: AD REVENUE ==============
with tabs[3]:
    render_header("Ad Revenue")
    period = get_period_filter()

    yt_total = 0; fb_total_usd = 0; fb_total_aud = 0; total_aud = 0
    months_entered = 0; months_in_period = 0
    rows_to_show = []
    for ar in ad_rev_monthly:
        try:
            month_name, year_str = ar["month"].split(" ")
            m = MONTHS.index(month_name) + 1
            md = date(int(year_str), m, 1)
            if not in_period(md, period):
                continue
            months_in_period += 1
            has_data = ar["yt_aud"] > 0 or ar["fb_usd"] > 0
            if has_data: months_entered += 1
            yt_total += ar["yt_aud"]
            fb_total_usd += ar["fb_usd"]
            fb_total_aud += ar["fb_aud"]
            total_aud += ar["total_aud"]
            rows_to_show.append((md, ar, has_data))
        except:
            continue

    avg_month = total_aud / max(months_entered, 1)

    st.markdown(
        f"<div class='kpi' style='padding:18px 18px'>"
        f"<div style='display:flex;gap:14px'>"
        f"<div style='flex:1'><div class='kpi-label'>TOTAL</div>"
        f"<div class='kpi-value' style='font-size:24px'>{format_money(total_aud)}</div></div>"
        f"<div style='flex:1'><div class='kpi-label'>AVG / MONTH</div>"
        f"<div class='kpi-value' style='font-size:24px'>{format_money(avg_month)}</div></div>"
        f"</div>"
        f"<div style='display:flex;gap:18px;margin-top:14px;font-size:11px;color:#A1A1AA;padding-top:14px;border-top:0.5px solid #27272A'>"
        f"<div><span class='status-dot' style='background:#EF4444;margin-right:6px'></span>YouTube · {format_money(yt_total)}</div>"
        f"<div><span class='status-dot' style='background:#3B82F6;margin-right:6px'></span>Facebook · {format_money(fb_total_aud)}</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("<p class='section-label'>Monthly Breakdown</p>", unsafe_allow_html=True)
    for md, ar, has_data in sorted(rows_to_show, reverse=True):
        if has_data:
            st.markdown(
                f"<div class='deal-card'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<div><div style='font-size:13px;font-weight:500'>{ar['month']}</div>"
                f"<div style='font-size:11px;color:#A1A1AA;margin-top:2px'>"
                f"<span style='color:#FCA5A5'>YT ${ar['yt_aud']:,.0f}</span>  "
                f"<span style='color:#93C5FD'>FB ${ar['fb_usd']:,.0f} USD</span></div></div>"
                f"<div style='font-size:14px;font-weight:500'>${ar['total_aud']:,.0f}</div></div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='deal-card' style='border-style:dashed;opacity:0.55'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<div><div style='font-size:13px;font-weight:500'>{ar['month']}</div>"
                f"<div style='font-size:11px;color:#525252;margin-top:2px'>Not yet entered</div></div>"
                f"<div style='font-size:11px;color:#71717A;font-style:italic'>Tap to add</div></div></div>",
                unsafe_allow_html=True
            )

    with st.expander("➕ Add this month's payout"):
        c1, c2 = st.columns(2)
        with c1:
            new_month = st.selectbox("Month", [ar["month"] for ar in ad_rev_monthly])
            new_yt = st.number_input("YouTube (AUD)", min_value=0.0, step=10.0)
        with c2:
            new_fb_usd = st.number_input("Facebook (USD)", min_value=0.0, step=10.0)
        if st.button("Save Ad Revenue", key="save_ad"):
            try:
                gc = get_gspread_client()
                ws = gc.open_by_key(SHEET_ID).worksheet("Ad Revenue")
                # Find the row by month name
                all_vals = ws.get_all_values()
                for idx, row in enumerate(all_vals):
                    if len(row) > 0 and row[0] == new_month:
                        row_num = idx + 1  # 1-indexed
                        ws.update_cell(row_num, 2, new_yt)
                        ws.update_cell(row_num, 3, new_fb_usd)
                        st.success(f"Saved {new_month}!")
                        st.cache_data.clear()
                        st.rerun()
                        break
                else:
                    st.error("Month not found in sheet")
            except Exception as e:
                st.error(f"Save failed: {e}")

# ============== TAB 5: ADD DEAL ==============
with tabs[4]:
    render_header("New Deal", show_period=False)
    st.markdown("<p style='font-size:11px;color:#71717A;margin-top:-8px'>Saves to Deals Log · auto-converts currency</p>", unsafe_allow_html=True)

    with st.form("add_deal", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_fy = st.selectbox("FY", ["FY26", "FY27"])
            new_status = st.selectbox("Status", ["Pitched", "Locked & Executing",
                                                  "Completed (India) - Not Invoiced",
                                                  "Completed (Not-India) - Not Invoiced",
                                                  "Invoiced (India)", "Invoiced (Non-India)", "Paid"])
            new_month = st.selectbox("Month", MONTHS)
            new_region = st.selectbox("Region", ["India", "Australia", "UAE", "US/Global"])
            new_currency = st.selectbox("Currency", ["AUD", "USD", "INR", "AED"])
        with c2:
            new_brand = st.text_input("Brand", placeholder="e.g. Plum")
            new_agency = st.text_input("Agency", placeholder="Optional")
            new_gross = st.number_input("Gross (orig)", min_value=0.0, step=1000.0)
            new_commission = st.number_input("Commission %", min_value=0.0, max_value=100.0, step=5.0, value=15.0) / 100
            new_invoice = st.text_input("Invoice #", placeholder="Optional")
        new_deliv = st.text_area("Deliverables", placeholder="e.g. 1 IG Reel + 2 Stories…")

        submitted = st.form_submit_button("Add Deal", use_container_width=True)
        if submitted:
            if not new_brand:
                st.error("Brand is required")
            else:
                try:
                    gc = get_gspread_client()
                    ws = gc.open_by_key(SHEET_ID).worksheet("Deals Log")
                    # Build new row matching column order
                    headers = ws.row_values(2)
                    new_row = [""] * len(headers)
                    field_map = {
                        "FY": new_fy, "Status": new_status, "Month": new_month,
                        "Region": new_region, "Agency": new_agency, "Brand": new_brand,
                        "Currency": new_currency, "Gross (orig)": new_gross,
                        "Commission %": new_commission, "Invoice #": new_invoice,
                        "Deliverables": new_deliv,
                    }
                    for h, v in field_map.items():
                        if h in headers:
                            new_row[headers.index(h)] = v
                    # Append to next empty row
                    ws.append_row(new_row, value_input_option="USER_ENTERED")
                    st.success(f"Added {new_brand}!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Failed to add: {e}")
