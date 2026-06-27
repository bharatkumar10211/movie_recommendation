import streamlit as st
import pandas as pd
import pickle
import json
import time
from difflib import get_close_matches

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Language maps
language_map = {
    "english":"en","japanese":"ja","french":"fr","chinese":"zh","spanish":"es",
    "german":"de","hindi":"hi","russian":"ru","korean":"ko","telugu":"te",
    "chinese (alternative code)":"cn","italian":"it","dutch":"nl","tamil":"ta",
    "swedish":"sv","thai":"th","danish":"da","unknown":"xx","hungarian":"hu",
    "czech":"cs","portuguese":"pt","icelandic":"is","turkish":"tr",
    "norwegian bokmål":"nb","afrikaans":"af","polish":"pl","hebrew":"he",
    "arabic":"ar","vietnamese":"vi","kyrgyz":"ky","indonesian":"id",
    "romanian":"ro","persian":"fa","norwegian":"no","slovenian":"sl",
    "pashto":"ps","greek":"el"
}
code_to_lang = {v: k.title() for k, v in language_map.items()}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body {
    background: #F8FAFC;
    font-family: 'Inter', sans-serif;
    color: #1F2937;
}

/* -- App background ------------------------------- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
[data-testid="stMainBlockContainer"] {
    background: #F8FAFC !important;
}

/* -- Kill Streamlit chrome ------------------------ */
[data-testid="stHeader"], header,
[data-testid="stToolbar"], .stDeployButton,
button[kind="header"] {
    display: none !important;
    height: 0 !important;
}

/* -- Zero out default container padding completely -- */
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* -- Restore sensible vertical rhythm ------------- */
[data-testid="stVerticalBlock"] {
    gap: 12px !important;
}

/* -- Hide sidebar --------------------------------- */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
    width: 0 !important;
}

/* ==================================================
   PAGE SHELL — Centered, Responsive layout
================================================== */
.pg {
    width: 100% !important;
    max-width: 1320px !important; /* Desktop max content width: 1280px–1400px centered */
    margin: 0 auto !important;
    padding: 0px 32px 32px !important; /* Desktop default padding: 32px */
    transition: padding 0.2s ease;
}

/* ==================================================
   TOP NAV BAR & TYPOGRAPHY
================================================== */
.brand-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 10px;
    line-height: 1.2;
    padding-left: 7px;
}

.brand-sub {
    font-size: 0.86rem;
    color: #4B5563;
    margin-top: 9px;
    font-weight: 500;
    letter-spacing: 0.02em;
    padding-left: 50px;
}

/* Nav tab radio — clean underline tabs */
div.st-key-topnav {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}
div.st-key-topnav [role="radiogroup"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
    align-items: center !important;
}
div.st-key-topnav [role="radiogroup"] label {
    border: none !important;
    background: transparent !important;
    padding: 6px 14px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    border-bottom: 2.5px solid transparent !important;
    transition: color 0.18s ease, border-color 0.18s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 0 !important;
}
div.st-key-topnav [role="radiogroup"] label:hover {
    color: #4F46E5 !important;
}
div.st-key-topnav [role="radiogroup"] label:has(input:checked) {
    color: #4F46E5 !important;
    font-weight: 600 !important;
    border-bottom: 2.5px solid #4F46E5 !important;
}

/* Hide horizontal radio indicators globally */
[data-testid="stRadioButtonIndicator"],
[role="radiogroup"] label > div:first-child,
[role="radiogroup"] label > div:first-of-type,
[role="radiogroup"] label svg,
[role="radiogroup"] label circle,
[role="radiogroup"] input[type="radio"],
[role="radiogroup"] label [class*="Indicator"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
    flex: 0 0 0 !important;
}

/* ==================================================
   STICKY HEADER — keeps nav at top while scrolling
================================================== */
/* Allow sticky to propagate through Streamlit's wrapper divs */
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
.main .block-container {
    overflow: visible !important;
}

/* Target the first horizontal block (our header columns) */
[data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type {
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
    background: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    border-bottom: 1.5px solid #E2E8F0 !important;
    padding-top: 8px !important;
    padding-bottom: 4px !important;
    margin-left: -32px !important;
    margin-right: -32px !important;
    padding-left: 32px !important;
    padding-right: 32px !important;
    transition: all 0.2s ease;
}

/* Kill any gap ABOVE the first element so the header truly starts at y=0 */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
/* Also zero out the gap Streamlit adds before the first stVerticalBlock child */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* ==================================================
   PILL TOGGLE (Recommendation Type)
================================================== */
div.st-key-toggle_cb,
div.st-key-toggle_pb {
    display: flex !important;
    justify-content: center !important;
}
div.st-key-toggle_cb button,
div.st-key-toggle_pb button {
    height: 42px !important;
    width: 380px !important; /* Desktop default toggle width: 380px */
    max-width: 100% !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 16px !important;
}

/* Active pill — purple/indigo gradient */
div.st-key-toggle_cb button[class*="primary"],
div.st-key-toggle_cb button[data-testid*="primary"],
div.st-key-toggle_pb button[class*="primary"],
div.st-key-toggle_pb button[data-testid*="primary"],
div.st-key-toggle_cb button[kind="primary"],
div.st-key-toggle_pb button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    border: 1px solid transparent !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.22) !important;
}
div.st-key-toggle_cb button[class*="primary"]:hover,
div.st-key-toggle_pb button[class*="primary"]:hover,
div.st-key-toggle_cb button[kind="primary"]:hover,
div.st-key-toggle_pb button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
    box-shadow: 0 3px 12px rgba(79,70,229,0.3) !important;
    transform: translateY(-1px) !important;
}

/* Inactive pill — clean white with visible border */
div.st-key-toggle_cb button[class*="secondary"],
div.st-key-toggle_cb button[data-testid*="secondary"],
div.st-key-toggle_pb button[class*="secondary"],
div.st-key-toggle_pb button[data-testid*="secondary"],
div.st-key-toggle_cb button[kind="secondary"],
div.st-key-toggle_pb button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #374151 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
}
div.st-key-toggle_cb button[class*="secondary"]:hover,
div.st-key-toggle_pb button[class*="secondary"]:hover,
div.st-key-toggle_cb button[kind="secondary"]:hover,
div.st-key-toggle_pb button[kind="secondary"]:hover {
    border-color: #A5B4FC !important;
    background: #F5F3FF !important;
    color: #4F46E5 !important;
    box-shadow: 0 2px 4px rgba(79,70,229,0.06) !important;
}

/* ==================================================
   DESCRIPTION BANNER — compact info strip
================================================== */
.desc-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
}

.desc-strip {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: fit-content;
    max-width: 850px;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 10px 20px;
    color: #1E40AF;
    font-size: 0.80rem;
    font-weight: 500;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.desc-strip .di {
    color: #2563EB;
    font-size: 0.9rem;
    flex-shrink: 0;
}

/* ==================================================
   CARDS (bordered containers)
================================================== */
div[data-testid="stVerticalBlockBorder"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 14px !important; /* Unified border-radius: 14px */
    padding: 0 !important; /* Zero padding on container */
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    margin-bottom: 14px !important;
    margin-top: 14px !important;
    overflow: hidden !important;
}

/* Card inner content padding */
div[data-testid="stVerticalBlockBorder"] > div[data-testid="stVerticalBlock"] > div:not(:first-child) {
    padding: 18px 20px 20px 20px !important;
}

/* Card section heading */
.card-title {
    margin: -14px -18px 18px -18px;
    padding: 14px 20px;

    font-size: 0.95rem;
    font-weight: 700;
    color: #4F46E5;

    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;

    display: flex;
    align-items: center;
    gap: 8px;
    border-top-left-radius: 14px !important;
    border-top-right-radius: 14px !important;
}

.section-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    overflow: hidden;
    margin: 18px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
}

.section-header {
    padding: 14px 18px;
    font-size: 16px;
    font-weight: 700;
    color: #4F46E5;
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
}

.section-body {
    padding: 18px;
}

/* ==================================================
   FORM INPUTS
================================================== */
div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 3px !important;
}
div[data-testid="stSlider"] [data-testid="stWidgetLabel"] p {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
/* Dropdown box */
div[data-baseweb="select"] {
    border-radius: 8px !important;
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    min-height: 38px !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
div[data-baseweb="select"]:hover {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08) !important;
}

/* ==================================================
   RECOMMEND BUTTON
================================================== */
div.st-key-btn_cb button,
div.st-key-btn_pb button {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1.5px solid transparent !important;
    height: 38px !important;
    width: 100% !important;
    font-size: 0.82rem !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.22) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
div.st-key-btn_cb button:hover,
div.st-key-btn_pb button:hover {
    background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.32) !important;
    transform: translateY(-1px) !important;
}

/* ==================================================
   RESULTS TABLE
================================================== */
.results-header {
    margin: 0 !important;
    padding: 14px 20px !important;

    display: flex;
    align-items: center;
    gap: 8px;

    font-size: 0.95rem;
    font-weight: 700;
    color: #4F46E5;

    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    border-top-left-radius: 14px !important;
    border-top-right-radius: 14px !important;
}

.tbl-outer {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    overflow: hidden;
    background: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.tbl-body { overflow-x: auto !important; overflow-y: auto; max-height: 250px; }
.tbl-body::-webkit-scrollbar { width: 5px; height: 5px; }
.tbl-body::-webkit-scrollbar-track { background: #F9FAFB; }
.tbl-body::-webkit-scrollbar-thumb { background: #C7D2FE; border-radius: 6px; }

table.mrt {
    width: 100%;
    border-collapse: collapse;
    table-layout: auto; /* Allow auto sizing */
    font-family: 'Inter', sans-serif;
    text-align: left;
}

.mrt-content {
    min-width: 800px;
}

.mrt-popular {
    min-width: 950px;
}

/* Scoped Column Width Constraints to prevent collapsing/overlaps */
.col-num {
    width: 60px !important;
    min-width: 60px !important;
    text-align: center !important;
}
.col-ttl {
    width: 200px !important;
    min-width: 180px !important;
    white-space: normal !important;
}
.col-genre {
    width: 180px !important;
    min-width: 140px !important;
    white-space: normal !important;
}
.col-lang {
    width: 100px !important;
    min-width: 90px !important;
    text-align: center !important;
}
.col-ovw {
    width: auto !important;
    min-width: 320px !important;
    white-space: normal !important;
}
.col-avg {
    width: 110px !important;
    min-width: 100px !important;
    text-align: center !important;
}
.col-count {
    width: 120px !important;
    min-width: 110px !important;
    text-align: center !important;
}
.col-pop {
    width: 110px !important;
    min-width: 100px !important;
    text-align: center !important;
}
table.mrt thead { position: sticky; top: 0; z-index: 5; }
table.mrt thead tr {
    background: #F9FAFB;
    border-bottom: 1.5px solid #E2E8F0;
}
table.mrt th {
    padding: 8px 12px;
    font-size: 0.68rem;
    font-weight: 600;
    color: #9CA3AF;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
table.mrt td {
    padding: 9px 12px;
    font-size: 0.78rem;
    color: #374151;
    border-bottom: 1px solid #F1F5F9;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    background: #FFFFFF;
}
table.mrt tbody tr:nth-child(even) td { background: #FCFCFD; }
table.mrt tbody tr:hover td {
    background: #F5F3FF !important;
    transition: background 0.12s ease;
}
table.mrt tr:last-child td { border-bottom: none; }
table.mrt td.num {
    color: #1F2937;
    font-size: 0.81rem;
    text-align: center;
    font-weight: 700;
}
table.mrt td.ttl { font-weight: 600; color: #111827; white-space: normal; }
table.mrt td.avg { font-weight: 700; color: #4F46E5; }
table.mrt td.ovw {
    white-space: normal;
    line-height: 1.5;
    font-size: 0.76rem;
    color: #6B7280;
    max-width: 0;
}

/* ==================================================
   INFO CARDS (About / Dataset)
================================================== */
.ig { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 6px; }
.ic {
    background: #FAFAFA;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.ic h3 {
    margin: 0 0 8px;
    font-size: 0.88rem;
    font-weight: 700;
    color: #1F2937;
    display: flex;
    align-items: center;
    gap: 6px;
}
.ic p { margin: 0; font-size: 0.76rem; color: #6B7280; line-height: 1.6; }
.is {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F1F5F9;
    padding: 8px 0;
    font-size: 0.78rem;
}
.is:last-child { border-bottom: none; }
.is span:first-child { color: #9CA3AF; font-weight: 500; }
.is span:last-child  { color: #111827; font-weight: 600; }

/* ==================================================
   RESPONSIVE MEDIA QUERIES (Breakpoints)
================================================== */

/* Laptop / Desktop Transition (1200px - 1399px) */
@media (max-width: 1399px) {
    .pg {
        padding: 0px 24px 24px !important; /* Laptop padding: 24px */
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type {
        margin-left: -24px !important;
        margin-right: -24px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
    }
    div.st-key-toggle_cb button,
    div.st-key-toggle_pb button {
        width: 320px !important; /* Laptop toggle buttons: 320px */
    }
}

/* Tablet (768px - 1199px) */
@media (max-width: 1199px) {
    .pg {
        padding: 0px 20px 20px !important; /* Tablet padding: 20px */
    }
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type {
        margin-left: -20px !important;
        margin-right: -20px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    div.st-key-toggle_cb button,
    div.st-key-toggle_pb button {
        width: 280px !important; /* Tablet toggle buttons: 280px */
    }
    /* Let the controls wrap if tight */
    div[data-testid="stVerticalBlockBorder"] [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 16px 12px !important;
    }
}

/* Mobile Devices (<768px) */
@media (max-width: 767px) {
    .pg {
        padding: 0px 16px 16px !important; /* Mobile padding: 16px */
    }
    /* Sticky Header Layout for Mobile */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:first-of-type {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 10px !important;
        padding-top: 10px !important;
        padding-bottom: 8px !important;
        margin-left: -16px !important;
        margin-right: -16px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }
    .brand-title {
        font-size: 1.35rem;
        padding-left: 0;
    }
    .brand-sub {
        font-size: 0.78rem;
        margin-top: 4px;
        padding-left: 0;
    }
    
    /* Horizontal Scrollable Navigation on Mobile */
    div.st-key-topnav {
        justify-content: flex-start !important;
        width: 100% !important;
        overflow-x: auto !important;
        padding-bottom: 6px !important;
        -webkit-overflow-scrolling: touch;
    }
    div.st-key-topnav::-webkit-scrollbar {
        height: 3px;
    }
    div.st-key-topnav::-webkit-scrollbar-thumb {
        background: #D1D5DB;
        border-radius: 3px;
    }
    div.st-key-topnav [role="radiogroup"] {
        width: max-content !important;
        gap: 8px !important;
    }
    div.st-key-topnav [role="radiogroup"] label {
        padding: 4px 10px !important;
        font-size: 0.78rem !important;
    }

    /* Stack Toggle Buttons vertically & make full-width */
    div.st-key-toggle_cb button,
    div.st-key-toggle_pb button {
        width: 100% !important; /* Mobile width: 100% */
        height: 38px !important;
    }
    /* Let the toggle buttons horizontal block layout flow vertically */
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]:nth-of-type(2) {
        flex-direction: column !important;
        gap: 10px !important;
    }

    /* Stack All Form Control inputs Vertically */
    div[data-testid="stVerticalBlockBorder"] [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 12px !important;
    }
    div[data-testid="stVerticalBlockBorder"] [data-testid="column"] {
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
    }
    
    /* Flex grid for columns stacking */
    .ig {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }
}

/* Extra Small Mobile Devices (<576px) */
@media (max-width: 575px) {
    .brand-title {
        font-size: 1.2rem;
    }
    .brand-sub {
        font-size: 0.72rem;
    }
}
</style>
""", unsafe_allow_html=True)




# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    mdf = pickle.load(open("movies.pkl", "rb"))
    sim = pickle.load(open("similarity.pkl", "rb"))
    csv = pd.read_csv("tmdb_5000_movies.csv")
    csv['genres']            = csv['genres'].fillna('[]')
    csv['original_language'] = csv['original_language'].fillna('en')
    csv['overview']          = csv['overview'].fillna('')
    csv.set_index('id', inplace=True)
    return mdf, sim, csv

try:
    movies_df, sim_matrix, movies_csv = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}"); st.stop()


# ── Recommendation functions ──────────────────────────────────────────────────
def rec_content(query, n=7):
    titles = movies_df['title'].tolist()
    m = get_close_matches(query, titles, n=1, cutoff=0.5)
    if not m: return []
    matched = m[0]
    idx = movies_df[movies_df['title'] == matched].index[0]
    pairs = sorted(enumerate(sim_matrix[idx]), key=lambda x: x[1], reverse=True)
    out = []
    for i, _ in pairs:
        t   = movies_df.iloc[i]['title']
        if t.lower() == matched.lower(): continue
        rid = movies_df.iloc[i]['id']
        if rid in movies_csv.index:
            row = movies_csv.loc[rid]
            try:   genres = ", ".join(g['name'] for g in json.loads(row['genres']))
            except: genres = "Drama"
            overview = str(row.get('overview', '') or '').strip()
            out.append({'title': t, 'genres': genres,
                        'lang': code_to_lang.get(row['original_language'], row['original_language'].upper()),
                        'va': row['vote_average'], 'vc': int(row['vote_count']),
                        'pop': row['popularity'], 'overview': overview})
        else:
            out.append({'title': t, 'genres': 'Drama', 'lang': 'English',
                        'va': 7.0, 'vc': 100, 'pop': 10.0, 'overview': ''})
        if len(out) == n: break
    return out

def rec_popular(genre, language, n=7):
    code = language_map.get(language.lower(), "en")
    def gm(gs):
        try: return any(g['name'].lower() == genre.lower() for g in json.loads(gs))
        except: return False
    df = movies_csv[(movies_csv['original_language'] == code) &
                    movies_csv['genres'].apply(gm)].copy()
    if df.empty: return []
    C = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.9) if len(df) >= 10 else df['vote_count'].min()
    df['score'] = df.apply(
        lambda r: (r['vote_count']/(r['vote_count']+m))*r['vote_average'] +
                  (m/(r['vote_count']+m))*C if (r['vote_count']+m) > 0 else r['vote_average'],
        axis=1)
    out = []
    for _, row in df.sort_values('score', ascending=False).head(n).iterrows():
        try:   genres = ", ".join(g['name'] for g in json.loads(row['genres']))
        except: genres = genre
        out.append({'title': row['title'], 'genres': genres,
                    'lang': code_to_lang.get(row['original_language'], row['original_language'].upper()),
                    'va': row['vote_average'], 'vc': int(row['vote_count']),
                    'pop': row['popularity']})
    return out

def build_table(recs, mode="content"):
    """Build HTML recommendation table.
    mode='content'  -> S.No, Movie Title, Genre, Language, Overview
    mode='popular'  -> S.No, Movie Title, Genre, Language, Vote Avg, Vote Count, Popularity
    """
    if mode == "content":
        tbody = "".join(
            f'<tr>'
            f'<td class="num col-num">{i+1}</td>'
            f'<td class="ttl col-ttl">{r["title"]}</td>'
            f'<td class="col-genre">{r["genres"]}</td>'
            f'<td class="col-lang">{r["lang"]}</td>'
            f'<td class="ovw col-ovw">{r.get("overview","")}</td>'
            f'</tr>'
            for i, r in enumerate(recs)
        )
        head = """<tr>
    <th class="col-num">S.No</th>
    <th class="col-ttl">Movie Title</th>
    <th class="col-genre">Genre</th>
    <th class="col-lang">Language</th>
    <th class="col-ovw">Overview</th>
  </tr>"""
        tbl_class = "mrt mrt-content"
    else:
        tbody = "".join(
            f'<tr>'
            f'<td class="num col-num">{i+1}</td>'
            f'<td class="ttl col-ttl">{r["title"]}</td>'
            f'<td class="col-genre">{r["genres"]}</td>'
            f'<td class="col-lang">{r["lang"]}</td>'
            f'<td class="avg col-avg">{r["va"]:.1f}</td>'
            f'<td class="col-count">{r["vc"]:,}</td>'
            f'<td class="col-pop">{r["pop"]:.2f}</td>'
            f'</tr>'
            for i, r in enumerate(recs)
        )
        head = """<tr>
    <th class="col-num">S.No</th>
    <th class="col-ttl">Movie Title</th>
    <th class="col-genre">Genre</th>
    <th class="col-lang">Language</th>
    <th class="col-avg">Vote Avg ⭐</th>
    <th class="col-count">Vote Count 👥</th>
    <th class="col-pop">Popularity</th>
  </tr>"""
        tbl_class = "mrt mrt-popular"

    return f"""
<div class="tbl-outer">
  <div class="tbl-body">
    <table class="{tbl_class}">
      <thead>{head}</thead>
      <tbody>{tbody}</tbody>
    </table>
  </div>
</div>"""

# ── Dropdown data ─────────────────────────────────────────────────────────────
GENRES = ['Action','Adventure','Animation','Comedy','Crime','Documentary',
          'Drama','Family','Fantasy','Foreign','History','Horror','Music',
          'Mystery','Romance','Science Fiction','TV Movie','Thriller','War','Western']
DB_LANGS = ['en','fr','es','de','zh','ja','hi','ru','ko','te','it','nl','ta',
            'sv','th','da','pt','tr','pl','ar','vi','id','ro','fa','no','el']
LANGS = sorted(code_to_lang.get(c, c.upper()) for c in DB_LANGS)

# ── Session state ─────────────────────────────────────────────────────────────
if 'recs' not in st.session_state:
    st.session_state.recs = rec_content("The Avengers", 7)
if 'rec_type' not in st.session_state:
    st.session_state.rec_type = "Content-Based"

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE SHELL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="pg">', unsafe_allow_html=True)

# ── Top Nav Bar ───────────────────────────────────────────────────────────────
col_brand, col_nav = st.columns([7, 2])

with col_brand:
    st.markdown("""
    <div style="padding: 0 0 10px;">
        <div class="brand-title">
            🎬 Movie Recommendation System
        </div>
        <div class="brand-sub">
            Discover movies using Content-Based and Popularity-Based recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    st.markdown(
        "<div style='display:flex;justify-content:flex-end;padding-top:0px;'>",
        unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["🏠 Home", "ℹ️ About", "🗂 Dataset Info"],
        key="topnav",
        label_visibility="collapsed",
        horizontal=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:0;border-top:1.5px solid #E5E7EB;'></div>",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONTENT
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":

    # Top breathing room below nav divider
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── Pill toggle (recommendation type) ────────────────────────────────────
    left_space, col_t1, gap, col_t2, right_space = st.columns([1, 2, 0.8, 2, 1])
    with col_t1:
        if st.button(
            "🎯  Content-Based Recommendation",
            key="toggle_cb",
            use_container_width=True,
            type="primary" if st.session_state.rec_type == "Content-Based" else "secondary"
        ):
            st.session_state.rec_type = "Content-Based"
            st.rerun()
    with col_t2:
        if st.button(
            "📈  Popularity-Based Recommendation",
            key="toggle_pb",
            use_container_width=True,
            type="primary" if st.session_state.rec_type == "Popularity-Based" else "secondary"
        ):
            st.session_state.rec_type = "Popularity-Based"
            st.rerun()

    # Small gap below toggles
    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── Description strip ────────────────────────────────────────────────────
    if st.session_state.rec_type == "Content-Based":
        desc = "Get similar movies based on content, genre, overview, cast and crew of your selected movie."
    else:
        desc = "Discover top-ranked movies by weighted popularity score — filtered by your preferred genre and language."

    st.markdown(f"""
    <div class="desc-wrapper">
        <div class="desc-strip">
            <span class="di">ℹ️</span>
            <span class="msg">{desc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Form card ────────────────────────────────────────────────────────────
    rec_type = st.session_state.rec_type

    with st.container(border=True):
        if rec_type == "Content-Based":
            st.markdown(
                '<div class="card-title">🎯 Content-Based Recommendation</div>',
                unsafe_allow_html=True)
            c1, c2, c3 = st.columns([5.5, 3.5, 2.0])
            with c1:
                default_idx = (movies_df['title'].tolist().index("The Avengers")
                               if "The Avengers" in movies_df['title'].tolist() else 0)
                sel_movie = st.selectbox(
                    "Select Movie", movies_df['title'].tolist(),
                    index=default_idx, placeholder="Search a movie…", key="cb_movie")
            with c2:
                n_cb = st.slider("Number of Recommendations", 1, 20, 7, key="cb_n")
            with c3:
                if st.button("🔍  Recommend", key="btn_cb"):
                    with st.spinner("Finding similar movies…"):
                        time.sleep(0.2)
                        st.session_state.recs = rec_content(sel_movie, n_cb)
                        st.rerun()
        else:
            st.markdown(
                '<div class="card-title">📈 Popularity-Based Recommendation</div>',
                unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2.6, 2.6, 3.2, 1.8])
            with c1:
                sel_genre = st.selectbox("Genre", GENRES,
                                          index=GENRES.index("Drama"), key="pb_genre")
            with c2:
                sel_lang = st.selectbox("Language", LANGS,
                                         index=LANGS.index("English"), key="pb_lang")
            with c3:
                n_pb = st.slider("Number of Recommendations", 1, 20, 7, key="pb_n")
            with c4:
                if st.button("🔍  Recommend", key="btn_pb"):
                    with st.spinner("Ranking popular movies…"):
                        time.sleep(0.2)
                        st.session_state.recs = rec_popular(sel_genre, sel_lang, n_pb)
                        st.rerun()

    # Gap between form card and results card
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)

    # ── Results card ──────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown('<div class="results-header">⭐ Top Recommendations</div>',
                    unsafe_allow_html=True)
        recs = st.session_state.recs
        if recs:
            mode = "content" if rec_type == "Content-Based" else "popular"
            st.markdown(build_table(recs, mode), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex;justify-content:center;align-items:center;
                        height:120px;border:2px dashed #E5E7EB;border-radius:12px;">
              <div style="text-align:center;color:#D1D5DB;">
                <div style="font-size:1.8rem;margin-bottom:8px;">🎬</div>
                <div style="font-size:0.8rem;font-weight:500;color:#9CA3AF;">
                  No recommendations found. Try adjusting your filters.</div>
              </div>
            </div>""", unsafe_allow_html=True)

elif page == "ℹ️ About":
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div class="card-title">About the Recommendation Engine</div>',
            unsafe_allow_html=True)
        st.markdown("""<div class="ig">
          <div class="ic">
            <h3>🎯 Content-Based System</h3>
            <p>Analyzes genres, keywords, cast, crew and overviews. Maps them into a
            5,000-dimensional vector space via <b>CountVectorizer</b> and finds closest
            matches using <b>Cosine Similarity</b>.</p>
          </div>
          <div class="ic">
            <h3>📈 Popularity-Based System</h3>
            <p>Uses the <b>IMDB Weighted Rating</b> formula:<br><br>
            <code style="background:#EEF2FF;padding:3px 8px;border-radius:6px;
                         color:#4F46E5;font-size:0.75rem;">
              Score = (v/(v+m))×R + (m/(v+m))×C</code><br><br>
            Filters by genre and language before ranking.</p>
          </div>
        </div>""", unsafe_allow_html=True)

elif page == "🗂 Dataset Info":
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div class="card-title">TMDB 5000 Movies Dataset</div>',
            unsafe_allow_html=True)
        st.markdown("""<div class="ig">
          <div class="ic">
            <h3>📊 Dataset Overview</h3>
            <div class="is"><span>Source</span><span>TMDB (The Movie Database)</span></div>
            <div class="is"><span>Total Records</span><span>4,803 Movies</span></div>
            <div class="is"><span>Languages</span><span>37 Unique Languages</span></div>
            <div class="is"><span>Similarity Matrix</span><span>4,803 × 4,803</span></div>
          </div>
          <div class="ic">
            <h3>⚙️ ML Pipeline</h3>
            <div class="is"><span>NLP Method</span><span>Bag of Words</span></div>
            <div class="is"><span>Vocabulary Size</span><span>5,000 features</span></div>
            <div class="is"><span>Similarity Metric</span><span>Cosine Similarity</span></div>
            <div class="is"><span>Avg Query Time</span><span>&lt; 50 ms</span></div>
          </div>
        </div>""", unsafe_allow_html=True)
