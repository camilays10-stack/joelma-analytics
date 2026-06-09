import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json, re
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _REQUESTS_OK = True
except Exception:
    _REQUESTS_OK = False

# ── Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Revista Total · Analytics",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Dados ─────────────────────────────────────────────────────
VEICULOS_BASE = [
    {
        "nome": "Revista Total", "emoji": "📋",
        "destaque": True, "grupo": "principal",
        "cor": "#3B82F6",
        "ids": {"instagram":"revistatotalbrasil","facebook":"revistatotalbrasil","youtube":"","tiktok":[]},
        "base": {"instagram":63_500,"facebook":50_000,"youtube":5_000,"tiktok":3_000},
    },
    {
        "nome": "Caras", "emoji": "⭐",
        "destaque": False, "grupo": "entretenimento",
        "cor": "#EC4899",
        "ids": {"instagram":"carasbrasil","facebook":"carasbrasil","youtube":"@CARASBrasil","tiktok":["carasbrasil"]},
        "base": {"instagram":8_000_000,"facebook":3_000_000,"youtube":200_000,"tiktok":1_600_000},
    },
    {
        "nome": "Contigo", "emoji": "💬",
        "destaque": False, "grupo": "entretenimento",
        "cor": "#F472B6",
        "ids": {"instagram":"tocontigo","facebook":"contigo","youtube":"@TVContigo","tiktok":["tocontigo"]},
        "base": {"instagram":2_000_000,"facebook":1_000_000,"youtube":100_000,"tiktok":633_600},
    },
    {
        "nome": "Veja", "emoji": "🗞️",
        "destaque": False, "grupo": "politica",
        "cor": "#F59E0B",
        "ids": {"instagram":"vejamais","facebook":"vejamais","youtube":"@vejamais","tiktok":["vejamais"]},
        "base": {"instagram":2_000_000,"facebook":8_000_000,"youtube":300_000,"tiktok":100_000},
    },
    {
        "nome": "IstoÉ", "emoji": "⚖️",
        "destaque": False, "grupo": "politica",
        "cor": "#A78BFA",
        "ids": {"instagram":"revistaistoe","facebook":"revistaistoe","youtube":"@IstoE","tiktok":["revistaistoe"]},
        "base": {"instagram":1_000_000,"facebook":2_000_000,"youtube":100_000,"tiktok":73_300},
    },
    {
        "nome": "Piauí", "emoji": "📖",
        "destaque": False, "grupo": "politica",
        "cor": "#34D399",
        "ids": {"instagram":"revistapiaui","facebook":"revistapiaui","youtube":"","tiktok":["revistapiaui"]},
        "base": {"instagram":913_000,"facebook":500_000,"youtube":20_000,"tiktok":37_300},
    },
    {
        "nome": "Carta Capital", "emoji": "🌱",
        "destaque": False, "grupo": "politica",
        "cor": "#6EE7B7",
        "ids": {"instagram":"cartacapital","facebook":"cartacapital","youtube":"@CartaCapital","tiktok":["cartacapital"]},
        "base": {"instagram":1_000_000,"facebook":1_691_650,"youtube":50_000,"tiktok":9_072},
    },
    {
        "nome": "Exame", "emoji": "💼",
        "destaque": False, "grupo": "negocios",
        "cor": "#FCD34D",
        "ids": {"instagram":"exame","facebook":"exame","youtube":"@exame","tiktok":["exame"]},
        "base": {"instagram":4_000_000,"facebook":2_000_000,"youtube":150_000,"tiktok":302_800},
    },
]

HISTORICO_FILE = Path(__file__).parent / "historico_revistas.json"

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #04070F !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMain"], section.main { background: transparent !important; }
[data-testid="block-container"] { padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080D1A !important;
    border-right: 1px solid #0F1A2E !important;
}
[data-testid="stSidebar"] * { color: #8B9DBB !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #CBD5E1 !important; }

/* Headings */
h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif !important; color: #F8FAFC !important; }
p, li { color: #94A3B8; font-size: .9rem; }

/* Tabs */
[data-baseweb="tab-list"] {
    background: #080D1A !important;
    border-radius: 16px !important;
    padding: 6px !important;
    border: 1px solid #0F1A2E !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
    color: #475569 !important;
    border-radius: 12px !important;
    padding: 9px 18px !important;
    transition: all .25s ease !important;
}
[aria-selected="true"] {
    background: linear-gradient(135deg, #1E3A5F 0%, #172d4a 100%) !important;
    color: #60A5FA !important;
    box-shadow: 0 2px 12px rgba(59,130,246,.25) !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1E3A5F, #152d4a) !important;
    color: #93C5FD !important;
    border: 1px solid rgba(59,130,246,.3) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    padding: 10px 20px !important;
    transition: all .2s !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #264d80, #1a3a60) !important;
    box-shadow: 0 0 20px rgba(59,130,246,.3) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #0F1A2E !important;
}

/* Selectbox / inputs */
[data-testid="stSelectbox"] > div > div {
    background: #080D1A !important;
    border-color: #0F1A2E !important;
    color: #CBD5E1 !important;
    border-radius: 10px !important;
}

/* ════ COMPONENTES VISUAIS ════ */

/* Metric pills */
.pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #080D1A; border: 1px solid #0F1A2E;
    border-radius: 20px; padding: 5px 12px;
    font-size: .75rem; font-weight: 600; color: #64748B;
    transition: border-color .2s;
}
.pill-val { font-weight: 700; color: #CBD5E1; font-size: .8rem; }

/* Platform badges */
.pb-ig  { background: linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); border-radius: 8px; padding: 3px 8px; font-size:.7rem; font-weight:700; color:#fff; }
.pb-fb  { background: #1877F2; border-radius: 8px; padding: 3px 8px; font-size:.7rem; font-weight:700; color:#fff; }
.pb-yt  { background: #FF0000; border-radius: 8px; padding: 3px 8px; font-size:.7rem; font-weight:700; color:#fff; }
.pb-tt  { background: #010101; border-radius: 8px; padding: 3px 8px; font-size:.7rem; font-weight:700; color:#69C9D0; border:1px solid #1a2535; }

/* Live badge */
.live-dot { display:inline-block; width:7px; height:7px; background:#22C55E; border-radius:50%; margin-right:4px; box-shadow:0 0 6px #22C55E; }

/* ── HERO CARD (protagonista) ── */
.hero-wrap {
    background: linear-gradient(135deg, #0A1628 0%, #060D1C 100%);
    border-radius: 24px;
    padding: 32px 36px;
    border: 1px solid #1a3050;
    box-shadow: 0 0 60px rgba(59,130,246,.08), 0 20px 60px rgba(0,0,0,.4);
    position: relative; overflow: hidden;
    margin-bottom: 20px;
}
.hero-wrap::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #3B82F6 0%, #60A5FA 30%, #818CF8 60%, #C084FC 100%);
}
.hero-wrap::after {
    content: '';
    position: absolute; right: -80px; top: -80px;
    width: 300px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: .68rem; font-weight: 800; letter-spacing: 3px;
    text-transform: uppercase; color: #3B82F6; margin-bottom: 10px;
}
.hero-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem; font-weight: 700; color: #F8FAFC;
    margin-bottom: 4px; letter-spacing: -.5px;
}
.hero-total-label { font-size: .75rem; color: #475569; margin-bottom: 6px; }
.hero-total-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4rem; font-weight: 700; color: #FFFFFF;
    letter-spacing: -3px; line-height: 1;
    background: linear-gradient(135deg, #FFFFFF 0%, #93C5FD 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-plats {
    display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px;
}
.plat-tile {
    flex: 1; min-width: 100px;
    background: rgba(15,26,46,.8);
    border: 1px solid #1a3050;
    border-radius: 14px; padding: 14px 16px;
    transition: border-color .2s;
}
.plat-tile:hover { border-color: #3B82F6; }
.plat-tile-icon { font-size: 1.3rem; margin-bottom: 6px; }
.plat-tile-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem; font-weight: 700; color: #F1F5F9;
    letter-spacing: -.5px;
}
.plat-tile-name { font-size: .7rem; color: #475569; margin-top: 2px; }
.plat-tile-live { display:inline-block; width:5px; height:5px; background:#22C55E; border-radius:50%; margin-left:4px; vertical-align:middle; }
.plat-tile-base { display:inline-block; width:5px; height:5px; background:#F59E0B; border-radius:50%; margin-left:4px; vertical-align:middle; }

/* ── RANKING TABLE CARD ── */
.rank-card {
    background: #080D1A;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid #0F1A2E;
    margin-bottom: 20px;
}
.rank-row {
    display: flex; align-items: center;
    padding: 12px 16px; border-radius: 12px;
    margin-bottom: 6px;
    transition: background .15s;
}
.rank-row:hover { background: #0A1220; }
.rank-row.highlight { background: rgba(59,130,246,.06); border: 1px solid rgba(59,130,246,.15); }
.rank-pos { font-size: .9rem; font-weight: 800; width: 32px; text-align: center; }
.rank-pos.gold { color: #F59E0B; }
.rank-pos.silver { color: #94A3B8; }
.rank-pos.bronze { color: #CD7F32; }
.rank-pos.other { color: #334155; }
.rank-name { flex: 1; padding: 0 12px; }
.rank-name-main { font-size: .9rem; font-weight: 600; color: #E2E8F0; }
.rank-name-group { font-size: .7rem; color: #475569; margin-top: 1px; }
.rank-bar-wrap { flex: 2; padding: 0 16px; }
.rank-bar-bg { background: #0F1A2E; border-radius: 4px; height: 6px; overflow: hidden; }
.rank-bar-fill { height: 6px; border-radius: 4px; }
.rank-val { font-size: .9rem; font-weight: 700; color: #CBD5E1; min-width: 60px; text-align: right; }

/* ── SECTION TITLE ── */
.stitle {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px;
}
.stitle-line { flex: 1; height: 1px; background: #0F1A2E; }
.stitle-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: .8rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #334155;
    white-space: nowrap;
}

/* ── INSIGHT CARDS ── */
.ic {
    display: flex; gap: 14px; align-items: flex-start;
    border-radius: 14px; padding: 16px 18px;
    margin-bottom: 10px;
}
.ic-alert { background: #0E0808; border: 1px solid #3F1818; }
.ic-warn  { background: #0A0900; border: 1px solid #3D2E00; }
.ic-ok    { background: #040E07; border: 1px solid #0D3520; }
.ic-dot-alert { width:8px; height:8px; border-radius:50%; background:#EF4444; margin-top:5px; flex-shrink:0; box-shadow:0 0 8px #EF4444; }
.ic-dot-warn  { width:8px; height:8px; border-radius:50%; background:#F59E0B; margin-top:5px; flex-shrink:0; box-shadow:0 0 8px #F59E0B; }
.ic-dot-ok    { width:8px; height:8px; border-radius:50%; background:#22C55E; margin-top:5px; flex-shrink:0; box-shadow:0 0 8px #22C55E; }
.ic-body { font-size: .87rem; color: #94A3B8; line-height: 1.6; }
.ic-body strong { color: #E2E8F0; }

/* ── STAT CARD (abas individuais) ── */
.stat-card {
    background: #080D1A;
    border-radius: 18px; padding: 22px 24px;
    border: 1px solid #0F1A2E;
    position: relative; overflow: hidden;
}
.stat-card-accent {
    position: absolute; top: 0; left: 0; bottom: 0; width: 3px;
    border-radius: 3px 0 0 3px;
}
.stat-card-label { font-size: .7rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #334155; margin-bottom: 8px; }
.stat-card-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem; font-weight: 700; color: #F1F5F9;
    letter-spacing: -1.5px; line-height: 1;
}
.stat-card-sub { font-size: .75rem; color: #334155; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Utils ─────────────────────────────────────────────────────
def _sessao():
    if not _REQUESTS_OK: return None
    s = requests.Session()
    r = Retry(total=2, backoff_factor=.3, status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    })
    return s

@st.cache_data(ttl=300, show_spinner=False)
def fetch_instagram(username):
    if not username or not _REQUESTS_OK: return None, False
    s = _sessao()
    try:
        r = s.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                  headers={"X-IG-App-ID":"936619743392459","X-Requested-With":"XMLHttpRequest",
                           "Referer":"https://www.instagram.com/"}, timeout=10)
        if r.status_code == 200:
            n = r.json().get("data",{}).get("user",{}).get("edge_followed_by",{}).get("count")
            if n and int(n) > 100: return int(n), True
    except: pass
    try:
        r = s.get(f"https://www.instagram.com/{username}/", headers={"Accept":"text/html"}, timeout=12)
        if r.status_code == 200:
            for pat in [r'"edge_followed_by".*?"count"\s*:\s*(\d+)', r'"follower_count"\s*:\s*(\d+)']:
                m = re.search(pat, r.text, re.DOTALL)
                if m and int(m.group(1)) > 100: return int(m.group(1)), True
    except: pass
    return None, False

@st.cache_data(ttl=300, show_spinner=False)
def fetch_youtube(channel_id):
    if not channel_id or not _REQUESTS_OK: return None, False
    try:
        r = _sessao().get(f"https://mixerno.space/api/youtube-channel-counter/user/{channel_id}", timeout=12)
        if r.status_code == 200:
            subs = next((c["count"] for c in r.json().get("counts",[]) if c.get("value")=="subscribers"), None)
            if subs and int(subs) > 100: return int(subs), True
    except: pass
    return None, False

@st.cache_data(ttl=300, show_spinner=False)
def fetch_tiktok(handle):
    if not handle or not _REQUESTS_OK: return None, False
    try:
        r = _sessao().get(f"https://www.tiktok.com/@{handle}",
                          headers={"Accept":"text/html","Referer":"https://www.google.com/"}, timeout=12)
        if r.status_code == 200:
            for pat in [r'"followerCount"\s*:\s*(\d+)', r'"fans"\s*:\s*(\d+)']:
                m = re.search(pat, r.text)
                if m and int(m.group(1)) > 100: return int(m.group(1)), True
    except: pass
    return None, False

def carregar_dados():
    out = []
    for v in VEICULOS_BASE:
        ids, base = v["ids"], v["base"]
        ig_v, ig_l = fetch_instagram(ids["instagram"])
        yt_v, yt_l = fetch_youtube(ids["youtube"])
        tt_v, tt_l = (None, False)
        if ids["tiktok"]: tt_v, tt_l = fetch_tiktok(ids["tiktok"][0])
        out.append({
            "nome": v["nome"], "emoji": v["emoji"],
            "destaque": v["destaque"], "grupo": v["grupo"], "cor": v["cor"],
            "instagram": {"val": ig_v or base["instagram"], "live": ig_l},
            "facebook":  {"val": base["facebook"],          "live": False},
            "youtube":   {"val": yt_v or base["youtube"],   "live": yt_l},
            "tiktok":    {"val": tt_v or base["tiktok"],    "live": tt_l},
        })
    return out

def N(n):
    if not n and n != 0: return "—"
    n = int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)

def N2(n):
    if not n and n != 0: return "—"
    return f"{int(n):,}".replace(",",".")

def carregar_historico():
    if not HISTORICO_FILE.exists(): return []
    try: return json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
    except: return []

def salvar_snapshot(dados):
    hist = carregar_historico()
    hist.append({"timestamp": datetime.now().isoformat(),
                 "dados": {d["nome"]: {p: d[p]["val"] for p in ("instagram","facebook","youtube","tiktok")} for d in dados}})
    HISTORICO_FILE.write_text(json.dumps(hist[-1000:], ensure_ascii=False, indent=2), encoding="utf-8")

GRUPO_LABEL = {"principal":"Principal","entretenimento":"Entretenimento","politica":"Política/Análise","negocios":"Negócios"}

# ════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Controles")
    atualizar = st.button("🔄  Atualizar ao Vivo", use_container_width=True)
    st.markdown("---")
    st.markdown("**Filtrar por grupo**")
    grupos_op = ["Todos", "Entretenimento", "Política/Análise", "Negócios"]
    grupo_sel = st.selectbox("", grupos_op, label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    **Revistas monitoradas:** 8
    **Plataformas:** IG · FB · YT · TT
    **Escopo:** Brasil — Nacional
    """)
    st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ── Carregar dados ────────────────────────────────────────────
with st.spinner(""):
    dados = carregar_dados()

if atualizar:
    fetch_instagram.clear(); fetch_youtube.clear(); fetch_tiktok.clear()
    dados = carregar_dados()
    salvar_snapshot(dados)
    st.success("✅ Dados atualizados!")

grupo_map = {"Entretenimento":"entretenimento","Política/Análise":"politica","Negócios":"negocios"}
dados_vis = dados if grupo_sel == "Todos" else [d for d in dados if d["grupo"] == grupo_map.get(grupo_sel,"")]

# ════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;">
  <div>
    <div style="font-size:.65rem;font-weight:800;letter-spacing:4px;text-transform:uppercase;
        color:#1E40AF;margin-bottom:6px;">Revista Total · Analytics Dashboard</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:700;
        color:#F8FAFC;letter-spacing:-1.5px;line-height:1;">
      Comparativo Nacional
      <span style="font-size:1rem;font-weight:400;color:#334155;
          background:#080D1A;padding:5px 16px;border-radius:20px;
          border:1px solid #0F1A2E;margin-left:12px;vertical-align:middle;letter-spacing:0;">
        8 revistas · 4 plataformas
      </span>
    </div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:.75rem;color:#334155;">Última atualização</div>
    <div style="font-size:1rem;font-weight:700;color:#475569;">""" + datetime.now().strftime('%d/%m/%Y') + """</div>
    <div style="margin-top:6px;">
      <span style="background:#04110A;color:#22C55E;font-size:.7rem;font-weight:700;
          padding:4px 12px;border-radius:20px;border:1px solid #0D3520;">
        <span style="display:inline-block;width:6px;height:6px;background:#22C55E;
            border-radius:50%;margin-right:4px;vertical-align:middle;"></span>
        Jun/2026
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  ABAS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠  Visão Geral", "📸  Instagram", "👤  Facebook",
    "▶️  YouTube", "🎵  TikTok", "⚡  Análise", "📅  Histórico",
])

# ════════════════════════════════════════════════════════════════
#  ABA 1 — VISÃO GERAL
# ════════════════════════════════════════════════════════════════
with tab1:
    # ── Hero card ────────────────────────────────────────────
    principal = next((d for d in dados if d["destaque"]), None)
    if principal:
        total_p = sum(principal[p]["val"] or 0 for p in ("instagram","facebook","youtube","tiktok"))
        ig = principal["instagram"]
        fb = principal["facebook"]
        yt = principal["youtube"]
        tt = principal["tiktok"]

        def tile(icon, name, val, live):
            dot = '<span class="plat-tile-live"></span>' if live else '<span class="plat-tile-base"></span>'
            return f"""<div class="plat-tile">
                <div class="plat-tile-icon">{icon}</div>
                <div class="plat-tile-val">{N(val["val"])}{dot}</div>
                <div class="plat-tile-name">{name}</div>
            </div>"""

        st.markdown(f"""
        <div class="hero-wrap">
          <div class="hero-eyebrow">⭐ Revista Monitorada · Principal</div>
          <div style="display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:16px;">
            <div>
              <div class="hero-name">{principal["emoji"]} {principal["nome"]}</div>
              <div class="hero-total-label">Audiência total — 4 plataformas</div>
              <div class="hero-total-num">{N(total_p)}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:.7rem;color:#1E3A5F;font-weight:700;margin-bottom:4px;">@revistatotalbrasil</div>
              <div style="font-size:.75rem;color:#334155;">Instagram · Facebook · YouTube · TikTok</div>
            </div>
          </div>
          <div class="hero-plats">
            {tile("📸","Instagram",ig,ig["live"])}
            {tile("👤","Facebook",fb,fb["live"])}
            {tile("▶️","YouTube",yt,yt["live"])}
            {tile("🎵","TikTok",tt,tt["live"])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Divider ──────────────────────────────────────────────
    st.markdown("""<div class="stitle">
      <div class="stitle-line"></div>
      <div class="stitle-text">Ranking Geral — Audiência Total</div>
      <div class="stitle-line"></div>
    </div>""", unsafe_allow_html=True)

    # ── Ranking visual ────────────────────────────────────────
    rows = []
    for d in dados_vis:
        total = sum(d[p]["val"] or 0 for p in ("instagram","facebook","youtube","tiktok"))
        rows.append({"nome":d["nome"],"emoji":d["emoji"],"grupo":d["grupo"],
                     "cor":d["cor"],"destaque":d["destaque"],"total":total,
                     "ig":d["instagram"]["val"] or 0, "fb":d["facebook"]["val"] or 0,
                     "yt":d["youtube"]["val"] or 0,   "tt":d["tiktok"]["val"] or 0})
    rows.sort(key=lambda x: x["total"], reverse=True)
    max_total = rows[0]["total"] if rows else 1

    pos_icons = {1:"🥇",2:"🥈",3:"🥉"}
    pos_classes = {1:"gold",2:"silver",3:"bronze"}

    html_rows = ""
    for i, r in enumerate(rows, 1):
        pct = r["total"] / max_total * 100
        hl  = "highlight" if r["destaque"] else ""
        pos_icon  = pos_icons.get(i, str(i))
        pos_class = pos_classes.get(i, "other")
        html_rows += f"""
        <div class="rank-row {hl}">
          <div class="rank-pos {pos_class}">{pos_icon}</div>
          <div class="rank-name">
            <div class="rank-name-main">{r["emoji"]} {r["nome"]}</div>
            <div class="rank-name-group">{GRUPO_LABEL.get(r["grupo"],r["grupo"])}</div>
          </div>
          <div class="rank-bar-wrap">
            <div class="rank-bar-bg">
              <div class="rank-bar-fill" style="width:{pct:.1f}%;background:{r["cor"]};
                  box-shadow:0 0 8px {r["cor"]}66;"></div>
            </div>
          </div>
          <div class="rank-val">{N(r["total"])}</div>
        </div>"""

    st.markdown(f'<div class="rank-card">{html_rows}</div>', unsafe_allow_html=True)

    # ── Gráfico de barras ─────────────────────────────────────
    st.markdown("""<div class="stitle">
      <div class="stitle-line"></div>
      <div class="stitle-text">Distribuição por Plataforma</div>
      <div class="stitle-line"></div>
    </div>""", unsafe_allow_html=True)

    df_plat = pd.DataFrame([
        {"Plataforma":"Instagram","Total":sum(d["instagram"]["val"] or 0 for d in dados_vis),"cor":"#E91E63"},
        {"Plataforma":"Facebook", "Total":sum(d["facebook"]["val"]  or 0 for d in dados_vis),"cor":"#1877F2"},
        {"Plataforma":"YouTube",  "Total":sum(d["youtube"]["val"]   or 0 for d in dados_vis),"cor":"#FF0000"},
        {"Plataforma":"TikTok",   "Total":sum(d["tiktok"]["val"]    or 0 for d in dados_vis),"cor":"#69C9D0"},
    ])

    col_chart, col_donut = st.columns([3, 2])
    with col_chart:
        fig_bar = go.Figure()
        for _, row in df_plat.iterrows():
            fig_bar.add_trace(go.Bar(
                x=[row["Plataforma"]], y=[row["Total"]],
                marker=dict(color=row["cor"], line=dict(width=0),
                            pattern=dict(bgcolor=row["cor"])),
                name=row["Plataforma"],
                text=[N(row["Total"])], textposition="outside",
                textfont=dict(color="#E2E8F0", size=14, family="Space Grotesk"),
            ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#080D1A",
            font=dict(color="#475569", family="Inter"),
            height=300, showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=12,color="#64748B")),
            yaxis=dict(showgrid=True, gridcolor="#0F1A2E", showticklabels=False,
                       zeroline=False, range=[0, df_plat["Total"].max()*1.25]),
            margin=dict(l=0,r=0,t=20,b=0), bargap=.4,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_donut:
        fig_donut = go.Figure(go.Pie(
            labels=df_plat["Plataforma"].tolist(),
            values=df_plat["Total"].tolist(),
            hole=0.65,
            marker=dict(colors=df_plat["cor"].tolist(),
                        line=dict(color="#04070F", width=4)),
            textinfo="label+percent",
            textfont=dict(color="#94A3B8", size=11, family="Inter"),
            pull=[0.05,0,0,0],
        ))
        fig_donut.add_annotation(
            text=f"<b style='font-size:18px'>{N(df_plat['Total'].sum())}</b><br>total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#CBD5E1", size=13, family="Space Grotesk"),
            align="center",
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=300,
            margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(color="#475569",size=10), orientation="h",
                        y=-0.05, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)


def _plat_tab(plat_key, icon, nome_plat, cor):
    df = pd.DataFrame([{
        "emoji": d["emoji"], "nome": d["nome"],
        "grupo": GRUPO_LABEL.get(d["grupo"], d["grupo"]),
        "val": d[plat_key]["val"] or 0,
        "live": d[plat_key]["live"],
        "cor":  d["cor"],
        "destaque": d["destaque"],
    } for d in dados_vis]).sort_values("val", ascending=False).reset_index(drop=True)
    df.index += 1

    lider = df.iloc[0]
    total_val = df["val"].sum()

    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-card-accent" style="background:{cor};"></div>
          <div class="stat-card-label">🏆 Líder {nome_plat}</div>
          <div class="stat-card-val">{N(lider["val"])}</div>
          <div class="stat-card-sub">{lider["emoji"]} {lider["nome"]}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        rt = next((d for d in dados_vis if d["destaque"]), None)
        rt_val = rt[plat_key]["val"] or 0 if rt else 0
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-card-accent" style="background:#3B82F6;"></div>
          <div class="stat-card-label">📋 Revista Total</div>
          <div class="stat-card-val">{N(rt_val)}</div>
          <div class="stat-card-sub">{'🟢 ao vivo' if rt and rt[plat_key]['live'] else '⬜ base'}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-card-accent" style="background:#8B5CF6;"></div>
          <div class="stat-card-label">📊 Total Mercado</div>
          <div class="stat-card-val">{N(total_val)}</div>
          <div class="stat-card-sub">{len(df)} revistas monitoradas</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="stitle">
      <div class="stitle-line"></div>
      <div class="stitle-text">Ranking {nome_plat}</div>
      <div class="stitle-line"></div>
    </div>""", unsafe_allow_html=True)

    # Ranking visual
    max_v = df["val"].max() or 1
    html_r = ""
    for i, row in df.iterrows():
        pct = row["val"] / max_v * 100
        hl  = "highlight" if row["destaque"] else ""
        pi  = pos_icons.get(i, str(i))
        pc  = pos_classes.get(i, "other")
        live_txt = '<span class="live-dot"></span>' if row["live"] else ""
        html_r += f"""
        <div class="rank-row {hl}">
          <div class="rank-pos {pc}">{pi}</div>
          <div class="rank-name">
            <div class="rank-name-main">{row["emoji"]} {row["nome"]} {live_txt}</div>
            <div class="rank-name-group">{row["grupo"]}</div>
          </div>
          <div class="rank-bar-wrap">
            <div class="rank-bar-bg">
              <div class="rank-bar-fill" style="width:{pct:.1f}%;background:{row['cor']};box-shadow:0 0 8px {row['cor']}55;"></div>
            </div>
          </div>
          <div class="rank-val">{N(row["val"])}</div>
        </div>"""
    st.markdown(f'<div class="rank-card">{html_r}</div>', unsafe_allow_html=True)

    # Gráfico horizontal
    df_c = df.sort_values("val", ascending=True)
    fig = go.Figure(go.Bar(
        x=df_c["val"], y=df_c["emoji"] + " " + df_c["nome"],
        orientation="h",
        marker=dict(color=df_c["cor"].tolist(), line=dict(width=0), opacity=.9),
        text=[N(v) for v in df_c["val"]],
        textposition="outside",
        textfont=dict(color="#CBD5E1", size=12, family="Space Grotesk"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#080D1A",
        font=dict(color="#475569", family="Inter"), height=380,
        xaxis=dict(showgrid=True, gridcolor="#0F1A2E", showticklabels=False,
                   zeroline=False, range=[0, df_c["val"].max()*1.22]),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94A3B8")),
        margin=dict(l=8,r=90,t=8,b=8), bargap=.38,
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════
#  ABAS 2–5 — PLATAFORMAS
# ════════════════════════════════════════════════════════════════
with tab2: _plat_tab("instagram","📸","Instagram","#E91E63")
with tab3:
    st.info("ℹ️ Dados do Facebook são base Jun/2026 — coleta ao vivo requer autenticação.")
    _plat_tab("facebook","👤","Facebook","#1877F2")
with tab4: _plat_tab("youtube","▶️","YouTube","#FF0000")
with tab5: _plat_tab("tiktok","🎵","TikTok","#69C9D0")

# ════════════════════════════════════════════════════════════════
#  ABA 6 — ANÁLISE
# ════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("""<div class="stitle">
      <div class="stitle-line"></div>
      <div class="stitle-text">Análise Competitiva — Revista Total vs Mercado</div>
      <div class="stitle-line"></div>
    </div>""", unsafe_allow_html=True)

    principal = next((d for d in dados if d["destaque"]), None)
    concorrentes = [d for d in dados if not d["destaque"]]
    plats = [("📸 Instagram","instagram"),("👤 Facebook","facebook"),
             ("▶️ YouTube","youtube"),("🎵 TikTok","tiktok")]

    if principal:
        ana_rows = []
        for label, plat in plats:
            p_val = principal[plat]["val"] or 0
            todos = sorted([(d["nome"],d[plat]["val"] or 0) for d in dados if d[plat]["val"]],
                           key=lambda x:x[1], reverse=True)
            if not todos: continue
            lider_nome, lider_val = todos[0]
            posicao = next((i+1 for i,(n,v) in enumerate(todos) if n==principal["nome"]), len(todos))
            gap = lider_val - p_val
            pct_lider = p_val/lider_val*100 if lider_val>0 else 0
            ana_rows.append({
                "Plataforma": label,
                "Revista Total": N(p_val),
                "Líder": N(lider_val),
                "Veículo Líder": lider_nome,
                "Gap": f"-{N(gap)}" if gap>0 else "🏆 Lidera",
                "% do Líder": f"{pct_lider:.1f}%",
                f"Posição": f"{posicao}º/{len(todos)}",
            })

        st.dataframe(pd.DataFrame(ana_rows), use_container_width=True, hide_index=True)

        # Radar
        st.markdown("""<div class="stitle">
          <div class="stitle-line"></div>
          <div class="stitle-text">Radar — Revista Total vs Top 4 Concorrentes</div>
          <div class="stitle-line"></div>
        </div>""", unsafe_allow_html=True)

        plat_keys = ["instagram","facebook","youtube","tiktok"]
        plat_labels = ["Instagram","Facebook","YouTube","TikTok"]
        top4 = sorted(concorrentes, key=lambda d: sum(d[p]["val"] or 0 for p in plat_keys), reverse=True)[:4]

        fig_r = go.Figure()
        for d in [principal] + top4:
            vals = [d[p]["val"] or 0 for p in plat_keys]
            mx = max(vals) or 1
            norm = [v/mx*100 for v in vals]
            fig_r.add_trace(go.Scatterpolar(
                r=norm+[norm[0]], theta=plat_labels+[plat_labels[0]],
                fill="toself" if d["destaque"] else None,
                name=d["nome"],
                line=dict(color=d["cor"], width=2 if d["destaque"] else 1.5),
                opacity=1 if d["destaque"] else .6,
            ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="#080D1A",
                radialaxis=dict(visible=True, range=[0,100], color="#1E293B",
                                tickfont=dict(color="#334155",size=9)),
                angularaxis=dict(color="#334155", tickfont=dict(color="#64748B",size=11)),
            ),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#475569",family="Inter"),
            height=440, showlegend=True,
            legend=dict(font=dict(color="#64748B",size=11), bgcolor="rgba(0,0,0,0)",
                        bordercolor="#0F1A2E"),
            margin=dict(l=40,r=40,t=40,b=40),
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Insights
        st.markdown("""<div class="stitle">
          <div class="stitle-line"></div>
          <div class="stitle-text">Insights Estratégicos</div>
          <div class="stitle-line"></div>
        </div>""", unsafe_allow_html=True)

        total_p = sum(principal[p]["val"] or 0 for p in plat_keys)
        total_lider = max((sum(d[p]["val"] or 0 for p in plat_keys) for d in concorrentes), default=1)
        pct = total_p/total_lider*100

        if pct < 10:
            cls, dot_cls, msg = "ic-alert", "ic-dot-alert", f"Audiência total é <strong>{pct:.1f}%</strong> do líder. Grande espaço de crescimento digital — prioridade: Instagram e Facebook."
        elif pct < 30:
            cls, dot_cls, msg = "ic-warn", "ic-dot-warn", f"Audiência total é <strong>{pct:.1f}%</strong> do líder. Crescimento em andamento — investir em vídeo (YouTube/TikTok) para acelerar."
        else:
            cls, dot_cls, msg = "ic-ok", "ic-dot-ok", f"Audiência total é <strong>{pct:.1f}%</strong> do líder. Posição competitiva sólida no segmento nacional."

        st.markdown(f"""
        <div class="ic {cls}">
          <div class="{dot_cls}"></div>
          <div class="ic-body"><strong>Revista Total</strong> — {msg}</div>
        </div>""", unsafe_allow_html=True)

        for label, plat in plats:
            vals_c = [d[plat]["val"] or 0 for d in concorrentes]
            media = sum(vals_c)/len(vals_c) if vals_c else 0
            p_val = principal[plat]["val"] or 0
            if p_val < media * 0.5:
                st.markdown(f"""
                <div class="ic ic-alert">
                  <div class="ic-dot-alert"></div>
                  <div class="ic-body">
                    <strong>{label}</strong> — Abaixo da média do mercado (<strong>{N(int(media))}</strong>).
                    Atual: <strong>{N(p_val)}</strong>. Oportunidade de crescimento acelerado.
                  </div>
                </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  ABA 7 — HISTÓRICO
# ════════════════════════════════════════════════════════════════
with tab7:
    st.markdown("""<div class="stitle">
      <div class="stitle-line"></div>
      <div class="stitle-text">Histórico de Métricas</div>
      <div class="stitle-line"></div>
    </div>""", unsafe_allow_html=True)

    hist = carregar_historico()
    if not hist:
        st.markdown("""
        <div class="ic ic-warn">
          <div class="ic-dot-warn"></div>
          <div class="ic-body">Nenhum histórico registrado ainda. Clique em
          <strong>"Atualizar ao Vivo"</strong> na barra lateral para criar o primeiro snapshot.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ic ic-ok">
          <div class="ic-dot-ok"></div>
          <div class="ic-body"><strong>{len(hist)} snapshots</strong> registrados no histórico.</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            veiculo_sel = st.selectbox("Revista", [v["nome"] for v in VEICULOS_BASE])
        with c2:
            plat_sel = st.selectbox("Plataforma", ["instagram","facebook","youtube","tiktok"],
                                    format_func=lambda x: {"instagram":"📸 Instagram","facebook":"👤 Facebook",
                                                            "youtube":"▶️ YouTube","tiktok":"🎵 TikTok"}[x])

        rows_h = [{"Data": e["timestamp"][:16].replace("T"," "),
                   "Valor": e["dados"].get(veiculo_sel,{}).get(plat_sel)}
                  for e in hist if e["dados"].get(veiculo_sel,{}).get(plat_sel) is not None]

        if rows_h:
            df_h = pd.DataFrame(rows_h)
            df_h["Data"] = pd.to_datetime(df_h["Data"])
            df_h = df_h.sort_values("Data")

            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(
                x=df_h["Data"], y=df_h["Valor"],
                mode="lines+markers",
                line=dict(color="#3B82F6", width=2.5),
                marker=dict(size=7, color="#3B82F6",
                            line=dict(color="#04070F", width=2)),
                fill="tozeroy",
                fillcolor="rgba(59,130,246,.06)",
                name=veiculo_sel,
            ))
            fig_h.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#080D1A",
                font=dict(color="#475569",family="Inter"), height=320,
                xaxis=dict(showgrid=True, gridcolor="#0F1A2E",
                           tickfont=dict(color="#475569")),
                yaxis=dict(showgrid=True, gridcolor="#0F1A2E",
                           tickfont=dict(color="#475569")),
                margin=dict(l=10,r=10,t=20,b=10),
                hovermode="x unified",
            )
            st.plotly_chart(fig_h, use_container_width=True)

            if len(rows_h) >= 2:
                prim = rows_h[0]["Valor"]
                ulti = rows_h[-1]["Valor"]
                delta = ulti - prim
                pct_v = delta/prim*100 if prim > 0 else 0
                c1, c2, c3 = st.columns(3)
                c1.metric("Primeiro registro", N2(prim))
                c2.metric("Último registro",   N2(ulti))
                c3.metric("Variação total",     N2(delta), delta=f"{pct_v:+.1f}%")
        else:
            st.info("Sem dados históricos para esta combinação.")

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding-top:20px;border-top:1px solid #080D1A;
    display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
  <div style="font-size:.75rem;color:#1E293B;font-weight:600;">
    📰 Revista Total · Analytics — Brasil
  </div>
  <div style="font-size:.72rem;color:#1E293B;">
    Instagram (ao vivo) · Facebook (base) · YouTube (ao vivo via mixerno.space) · TikTok (ao vivo)
  </div>
</div>
""", unsafe_allow_html=True)
