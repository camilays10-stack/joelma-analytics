import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime

# ── Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Joelma Analytics — Comparativo de Artistas",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta ────────────────────────────────────────────────
COR_JOELMA = "#E74C3C"
COR_SEC    = ["#2471A3","#E67E22","#27AE60","#8E44AD","#F39C12",
              "#1ABC9C","#E91E63","#F1C40F","#7D3C98","#148F77",
              "#BA4A00","#1F618D"]
AZUL_DARK  = "#1A5276"

GRUPOS = {
    "Joelma":           "🎤 Joelma",
    "Wesley Safadão":   "🔴 Concorrente Direto",
    "Simone Mendes":    "🔴 Concorrente Direto",
    "Xand Avião":       "🔴 Concorrente Direto",
    "Solange Almeida":  "🔴 Concorrente Direto",
    "Ana Castela":      "📌 Referência Digital",
    "Gusttavo Lima":    "📌 Referência Digital",
    "João Gomes":       "📌 Referência Digital",
    "Manu Bahtidão":    "🌳 Artista Paraense",
    "Fafá de Belém":    "🌳 Artista Paraense",
    "Gaby Amarantos":   "🌳 Artista Paraense",
    "Viviane Batidão":  "🌳 Artista Paraense",
    "Zaynara":          "🌳 Artista Paraense",
}

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F1117;}
[data-testid="stSidebar"]{background:#161B22;}
h1,h2,h3{color:#FFFFFF;}
.metric-card{
    background:#1C2128;border-radius:12px;padding:20px;
    border-left:4px solid #E74C3C;margin-bottom:12px;
}
.metric-value{font-size:2rem;font-weight:800;color:#E74C3C;}
.metric-label{font-size:.85rem;color:#8B949E;margin-top:4px;}
.insight-card{
    background:#1C2128;border-radius:10px;padding:16px;
    border-left:4px solid #E67E22;margin-bottom:10px;
}
.insight-card-green{
    background:#1C2128;border-radius:10px;padding:16px;
    border-left:4px solid #27AE60;margin-bottom:10px;
}
.insight-card-yellow{
    background:#1C2128;border-radius:10px;padding:16px;
    border-left:4px solid #F39C12;margin-bottom:10px;
}
.badge-verified{
    display:inline-block;padding:2px 8px;border-radius:12px;
    font-size:.7rem;font-weight:700;background:#27AE60;color:white;margin-left:6px;
}
.badge-est{
    display:inline-block;padding:2px 8px;border-radius:12px;
    font-size:.7rem;font-weight:700;background:#F39C12;color:black;margin-left:6px;
}
</style>
""", unsafe_allow_html=True)

# ── Base de dados — números verificados Jun/2026 ──────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "artists_data.json")

DEFAULT_ARTISTS = {
    # ── JOELMA (dados 100% verificados — Jun/2026) ─────────────────────────
    "Joelma": {
        "genero": "Forró / Calypso",
        "estado": "PA",
        "grupo": "🎤 Joelma",
        "cor": COR_JOELMA,
        "instagram": {"seguidores": 5_800_000, "seguindo": 300, "posts": 1200,
                      "media_curtidas": 38000, "media_comentarios": 900,
                      "media_views_reels": 280000},
        "tiktok": {"seguidores": 2_900_000, "curtidas_total": 0,
                   "media_views": 320000, "media_curtidas": 15000},
        "youtube": {"inscritos": 4_200_000, "views_total": 1_500_000_000,
                    "media_views_video": 2_000_000, "videos": 380},
        "spotify":       {"seguidores": 274_793, "ouvintes_mensais": 713_506, "popularidade": 62},
        "deezer":        {"fans": 180_000, "albuns": 14},
        "apple_music":   {"ouvintes_mensais": 420_000},
        "youtube_music": {"streams_mensais": 1_200_000},
        "amazon_music":  {"streams_mensais": 280_000},
        "soundcloud":    {"plays": 12_000_000, "seguidores": 80_000},
        "shows_2026": 22,
        "cache_shows_2026": "Turnê Arraiá 30 Anos — 22 cidades",
        "top_hit": "Voando Pro Pará — 30M streams",
        "dados_verificados": True,
    },

    # ── CONCORRENTES DIRETOS (dados verificados — Jun/2026) ────────────────
    "Wesley Safadão": {
        "genero": "Forró / Eletrônico",
        "estado": "CE",
        "grupo": "🔴 Concorrente Direto",
        "cor": COR_SEC[0],
        "instagram": {"seguidores": 39_900_000, "seguindo": 400, "posts": 3200,
                      "media_curtidas": 200000, "media_comentarios": 5000,
                      "media_views_reels": 2_000_000},
        "tiktok": {"seguidores": 6_200_000, "curtidas_total": 51_500_000,
                   "media_views": 1_200_000, "media_curtidas": 55000},
        "youtube": {"inscritos": 14_000_000, "views_total": 8_000_000_000,
                    "media_views_video": 9_000_000, "videos": 720},
        "spotify":       {"seguidores": 3_800_000, "ouvintes_mensais": 9_813_112, "popularidade": 84},
        "deezer":        {"fans": 1_500_000, "albuns": 22},
        "apple_music":   {"ouvintes_mensais": 5_200_000},
        "youtube_music": {"streams_mensais": 18_000_000},
        "amazon_music":  {"streams_mensais": 3_800_000},
        "soundcloud":    {"plays": 95_000_000, "seguidores": 650_000},
        "shows_2026": 120,
        "cache_shows_2026": "WS in Fortaleza + Partiu São João (TV Globo)",
        "top_hit": "Ele É Ele, Eu Sou Eu — 228M streams",
        "dados_verificados": True,
    },
    "Simone Mendes": {
        "genero": "Sertanejo",
        "estado": "GO",
        "grupo": "🔴 Concorrente Direto",
        "cor": COR_SEC[2],
        "instagram": {"seguidores": 40_000_000, "seguindo": 350, "posts": 1600,
                      "media_curtidas": 200000, "media_comentarios": 5000,
                      "media_views_reels": 3_000_000},
        "tiktok": {"seguidores": 17_600_000, "curtidas_total": 107_900_000,
                   "media_views": 2_800_000, "media_curtidas": 100000},
        "youtube": {"inscritos": 9_000_000, "views_total": 4_500_000_000,
                    "media_views_video": 7_000_000, "videos": 480},
        "spotify":       {"seguidores": 4_200_000, "ouvintes_mensais": 12_720_687, "popularidade": 87},
        "deezer":        {"fans": 2_200_000, "albuns": 10},
        "apple_music":   {"ouvintes_mensais": 6_500_000},
        "youtube_music": {"streams_mensais": 24_000_000},
        "amazon_music":  {"streams_mensais": 5_000_000},
        "soundcloud":    {"plays": 120_000_000, "seguidores": 780_000},
        "shows_2026": 150,
        "cache_shows_2026": "Campina Grande + Maceió + Natal + Jequié",
        "top_hit": "Erro Gostoso (Ao Vivo) — 468M+ streams",
        "dados_verificados": True,
    },
    "Xand Avião": {
        "genero": "Forró",
        "estado": "CE",
        "grupo": "🔴 Concorrente Direto",
        "cor": COR_SEC[4],
        "instagram": {"seguidores": 10_200_000, "seguindo": 380, "posts": 2100,
                      "media_curtidas": 60000, "media_comentarios": 1800,
                      "media_views_reels": 700000},
        "tiktok": {"seguidores": 1_100_000, "curtidas_total": 18_000_000,
                   "media_views": 400000, "media_curtidas": 16000},
        "youtube": {"inscritos": 4_200_000, "views_total": 1_800_000_000,
                    "media_views_video": 2_400_000, "videos": 410},
        "spotify":       {"seguidores": 1_400_000, "ouvintes_mensais": 7_198_010, "popularidade": 74},
        "deezer":        {"fans": 750_000, "albuns": 16},
        "apple_music":   {"ouvintes_mensais": 3_800_000},
        "youtube_music": {"streams_mensais": 9_500_000},
        "amazon_music":  {"streams_mensais": 2_200_000},
        "soundcloud":    {"plays": 55_000_000, "seguidores": 300_000},
        "shows_2026": 90,
        "cache_shows_2026": "Meu São João — Campina Grande + Monteiro + Bananeiras",
        "top_hit": "Faixa ao vivo — 271M+ streams",
        "dados_verificados": True,
    },
    "Solange Almeida": {
        "genero": "Forró",
        "estado": "CE",
        "grupo": "🔴 Concorrente Direto",
        "cor": COR_SEC[1],
        "instagram": {"seguidores": 9_000_000, "seguindo": 450, "posts": 1800,
                      "media_curtidas": 55000, "media_comentarios": 1500,
                      "media_views_reels": 600000},
        "tiktok": {"seguidores": 1_700_000, "curtidas_total": 14_000_000,
                   "media_views": 350000, "media_curtidas": 14000},
        "youtube": {"inscritos": 2_200_000, "views_total": 900_000_000,
                    "media_views_video": 1_500_000, "videos": 320},
        "spotify":       {"seguidores": 680_000, "ouvintes_mensais": 1_507_526, "popularidade": 68},
        "deezer":        {"fans": 420_000, "albuns": 12},
        "apple_music":   {"ouvintes_mensais": 800_000},
        "youtube_music": {"streams_mensais": 2_200_000},
        "amazon_music":  {"streams_mensais": 480_000},
        "soundcloud":    {"plays": 25_000_000, "seguidores": 180_000},
        "shows_2026": 60,
        "cache_shows_2026": "Sol João 2ª ed. — Campina Grande + Recife",
        "top_hit": "Gravação ao vivo — Sol João",
        "dados_verificados": True,
    },

    # ── REFERÊNCIAS DIGITAIS ───────────────────────────────────────────────
    "Ana Castela": {
        "genero": "Sertanejo / Country BR",
        "estado": "GO",
        "grupo": "📌 Referência Digital",
        "cor": COR_SEC[3],
        "instagram": {"seguidores": 23_600_000, "seguindo": 200, "posts": 800,
                      "media_curtidas": 180000, "media_comentarios": 4500,
                      "media_views_reels": 3_500_000},
        "tiktok": {"seguidores": 16_700_000, "curtidas_total": 210_000_000,
                   "media_views": 4_000_000, "media_curtidas": 150000},
        "youtube": {"inscritos": 11_000_000, "views_total": 3_200_000_000,
                    "media_views_video": 12_000_000, "videos": 280},
        "spotify":       {"seguidores": 5_800_000, "ouvintes_mensais": 12_647_334, "popularidade": 90},
        "deezer":        {"fans": 2_800_000, "albuns": 6},
        "apple_music":   {"ouvintes_mensais": 6_200_000},
        "youtube_music": {"streams_mensais": 22_000_000},
        "amazon_music":  {"streams_mensais": 4_800_000},
        "soundcloud":    {"plays": 85_000_000, "seguidores": 520_000},
        "shows_2026": 160,
        "cache_shows_2026": "Boiadeira Tour 2026",
        "top_hit": "Ilusão de Ótica — 246M+ streams",
        "dados_verificados": True,
    },
    "Gusttavo Lima": {
        "genero": "Sertanejo Universitário",
        "estado": "GO",
        "grupo": "📌 Referência Digital",
        "cor": COR_SEC[5],
        "instagram": {"seguidores": 38_000_000, "seguindo": 280, "posts": 2800,
                      "media_curtidas": 250000, "media_comentarios": 6000,
                      "media_views_reels": 3_500_000},
        "tiktok": {"seguidores": 14_000_000, "curtidas_total": 180_000_000,
                   "media_views": 4_200_000, "media_curtidas": 150000},
        "youtube": {"inscritos": 22_000_000, "views_total": 12_000_000_000,
                    "media_views_video": 15_000_000, "videos": 950},
        "spotify":       {"seguidores": 9_800_000, "ouvintes_mensais": 28_000_000, "popularidade": 92},
        "deezer":        {"fans": 4_500_000, "albuns": 28},
        "apple_music":   {"ouvintes_mensais": 14_000_000},
        "youtube_music": {"streams_mensais": 38_000_000},
        "amazon_music":  {"streams_mensais": 8_500_000},
        "soundcloud":    {"plays": 200_000_000, "seguidores": 1_200_000},
        "shows_2026": 200,
        "cache_shows_2026": "Embaixador Tour 2026",
        "top_hit": "Bloqueio — 500M+ streams",
        "dados_verificados": False,
    },
    "João Gomes": {
        "genero": "Forró",
        "estado": "PE",
        "grupo": "📌 Referência Digital",
        "cor": COR_SEC[6],
        "instagram": {"seguidores": 14_500_000, "seguindo": 220, "posts": 890,
                      "media_curtidas": 95000, "media_comentarios": 2800,
                      "media_views_reels": 1_800_000},
        "tiktok": {"seguidores": 12_000_000, "curtidas_total": 145_000_000,
                   "media_views": 2_200_000, "media_curtidas": 85000},
        "youtube": {"inscritos": 6_800_000, "views_total": 2_800_000_000,
                    "media_views_video": 5_500_000, "videos": 320},
        "spotify":       {"seguidores": 4_200_000, "ouvintes_mensais": 15_000_000, "popularidade": 88},
        "deezer":        {"fans": 1_800_000, "albuns": 8},
        "apple_music":   {"ouvintes_mensais": 8_000_000},
        "youtube_music": {"streams_mensais": 20_000_000},
        "amazon_music":  {"streams_mensais": 4_500_000},
        "soundcloud":    {"plays": 180_000_000, "seguidores": 750_000},
        "shows_2026": 180,
        "cache_shows_2026": "Minha Namorada é Gente Boa Tour",
        "top_hit": "Me Chama de Amor — 300M+ streams",
        "dados_verificados": False,
    },

    # ── ARTISTAS PARAENSES (dados verificados — Jun/2026) ─────────────────
    "Manu Bahtidão": {
        "genero": "Tecnomelody / Sertanejo",
        "estado": "PA",
        "grupo": "🌳 Artista Paraense",
        "cor": COR_SEC[7],
        "instagram": {"seguidores": 5_000_000, "seguindo": 380, "posts": 950,
                      "media_curtidas": 42000, "media_comentarios": 1100,
                      "media_views_reels": 450000},
        "tiktok": {"seguidores": 3_500_000, "curtidas_total": 45_000_000,
                   "media_views": 380000, "media_curtidas": 16000},
        "youtube": {"inscritos": 2_500_000, "views_total": 700_000_000,
                    "media_views_video": 1_800_000, "videos": 280},
        "spotify":       {"seguidores": 1_029_243, "ouvintes_mensais": 3_279_663, "popularidade": 72},
        "deezer":        {"fans": 380_000, "albuns": 8},
        "apple_music":   {"ouvintes_mensais": 1_600_000},
        "youtube_music": {"streams_mensais": 3_800_000},
        "amazon_music":  {"streams_mensais": 700_000},
        "soundcloud":    {"plays": 18_000_000, "seguidores": 120_000},
        "shows_2026": 50,
        "cache_shows_2026": "DVD Destino + shows nordeste/norte",
        "top_hit": "Daqui Pra Sempre feat. Simone — 1,5B streams",
        "dados_verificados": True,
    },
    "Fafá de Belém": {
        "genero": "MPB / Carimbó",
        "estado": "PA",
        "grupo": "🌳 Artista Paraense",
        "cor": COR_SEC[8],
        "instagram": {"seguidores": 1_000_000, "seguindo": 200, "posts": 600,
                      "media_curtidas": 8000, "media_comentarios": 350,
                      "media_views_reels": 50000},
        "tiktok": {"seguidores": 25_000, "curtidas_total": 500_000,
                   "media_views": 20000, "media_curtidas": 800},
        "youtube": {"inscritos": 400_000, "views_total": 120_000_000,
                    "media_views_video": 500_000, "videos": 320},
        "spotify":       {"seguidores": 180_000, "ouvintes_mensais": 1_156_551, "popularidade": 52},
        "deezer":        {"fans": 120_000, "albuns": 20},
        "apple_music":   {"ouvintes_mensais": 600_000},
        "youtube_music": {"streams_mensais": 800_000},
        "amazon_music":  {"streams_mensais": 180_000},
        "soundcloud":    {"plays": 5_000_000, "seguidores": 35_000},
        "shows_2026": 20,
        "cache_shows_2026": "Shows culturais + São João",
        "top_hit": "Emorio — 94,7M streams",
        "dados_verificados": True,
    },
    "Gaby Amarantos": {
        "genero": "Pop / Tecnobrega",
        "estado": "PA",
        "grupo": "🌳 Artista Paraense",
        "cor": COR_SEC[9],
        "instagram": {"seguidores": 1_000_000, "seguindo": 250, "posts": 700,
                      "media_curtidas": 9000, "media_comentarios": 400,
                      "media_views_reels": 80000},
        "tiktok": {"seguidores": 295_000, "curtidas_total": 4_000_000,
                   "media_views": 60000, "media_curtidas": 2500},
        "youtube": {"inscritos": 1_000_000, "views_total": 320_000_000,
                    "media_views_video": 800_000, "videos": 250},
        "spotify":       {"seguidores": 95_000, "ouvintes_mensais": 448_607, "popularidade": 48},
        "deezer":        {"fans": 85_000, "albuns": 10},
        "apple_music":   {"ouvintes_mensais": 250_000},
        "youtube_music": {"streams_mensais": 500_000},
        "amazon_music":  {"streams_mensais": 120_000},
        "soundcloud":    {"plays": 4_500_000, "seguidores": 28_000},
        "shows_2026": 30,
        "cache_shows_2026": "Álbum Rock Doido + shows internacionais",
        "top_hit": "Foguinho — 11,5M streams",
        "dados_verificados": True,
    },
    "Viviane Batidão": {
        "genero": "Tecnomelody",
        "estado": "PA",
        "grupo": "🌳 Artista Paraense",
        "cor": COR_SEC[10],
        "instagram": {"seguidores": 1_000_000, "seguindo": 300, "posts": 550,
                      "media_curtidas": 7500, "media_comentarios": 280,
                      "media_views_reels": 70000},
        "tiktok": {"seguidores": 450_000, "curtidas_total": 6_000_000,
                   "media_views": 80000, "media_curtidas": 3000},
        "youtube": {"inscritos": 800_000, "views_total": 220_000_000,
                    "media_views_video": 600_000, "videos": 200},
        "spotify":       {"seguidores": 75_000, "ouvintes_mensais": 388_662, "popularidade": 45},
        "deezer":        {"fans": 65_000, "albuns": 7},
        "apple_music":   {"ouvintes_mensais": 200_000},
        "youtube_music": {"streams_mensais": 380_000},
        "amazon_music":  {"streams_mensais": 90_000},
        "soundcloud":    {"plays": 3_500_000, "seguidores": 22_000},
        "shows_2026": 35,
        "cache_shows_2026": "É Sal + Batidão Raíz 2026",
        "top_hit": "Só Pra Tu — 13M streams",
        "dados_verificados": True,
    },
    "Zaynara": {
        "genero": "Beat Melody",
        "estado": "PA",
        "grupo": "🌳 Artista Paraense",
        "cor": COR_SEC[11],
        "instagram": {"seguidores": 478_000, "seguindo": 180, "posts": 320,
                      "media_curtidas": 5500, "media_comentarios": 220,
                      "media_views_reels": 120000},
        "tiktok": {"seguidores": 304_000, "curtidas_total": 5_500_000,
                   "media_views": 95000, "media_curtidas": 4000},
        "youtube": {"inscritos": 500_000, "views_total": 150_000_000,
                    "media_views_video": 700_000, "videos": 120},
        "spotify":       {"seguidores": 42_000, "ouvintes_mensais": 175_863, "popularidade": 40},
        "deezer":        {"fans": 30_000, "albuns": 3},
        "apple_music":   {"ouvintes_mensais": 90_000},
        "youtube_music": {"streams_mensais": 180_000},
        "amazon_music":  {"streams_mensais": 45_000},
        "soundcloud":    {"plays": 2_000_000, "seguidores": 12_000},
        "shows_2026": 28,
        "cache_shows_2026": "Rock in Rio + The Town + shows Norte",
        "top_hit": "Aquele Alguém feat. Joelma",
        "dados_verificados": True,
    },
}

# ── Carregar / salvar dados ───────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return DEFAULT_ARTISTS

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Calcular métricas derivadas ───────────────────────────
def calc_metrics(artist):
    ig = artist["instagram"]
    tk = artist["tiktok"]
    yt = artist["youtube"]
    sp = artist["spotify"]

    er_ig = ((ig["media_curtidas"] + ig["media_comentarios"]) / ig["seguidores"] * 100) if ig["seguidores"] else 0
    er_tk = (tk["media_curtidas"] / tk["seguidores"] * 100) if tk["seguidores"] else 0
    total_seg = ig["seguidores"] + tk["seguidores"] + yt["inscritos"] + sp["seguidores"]
    score_digital = (
        ig["seguidores"] * 1.0 +
        tk["seguidores"] * 1.2 +
        yt["inscritos"] * 0.8 +
        sp["ouvintes_mensais"] * 0.5
    ) / 1_000_000

    return {
        "er_instagram": round(er_ig, 2),
        "er_tiktok": round(er_tk, 2),
        "total_seguidores": total_seg,
        "score_digital": round(score_digital, 1),
        "views_por_inscrito_yt": round(yt["views_total"] / yt["inscritos"], 0) if yt["inscritos"] else 0,
    }

# ── Formatação ────────────────────────────────────────────
def fmt(n):
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    if n >= 1_000:         return f"{n/1_000:.0f}K"
    return str(int(n))

# ═════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════
data = load_data()

with st.sidebar:
    st.markdown(f"## 🎤 Joelma Analytics")
    st.caption("Comparativo de Artistas · Jun/2026")
    st.markdown("---")

    # ── Filtro por grupo
    st.markdown("### Filtrar por grupo")
    grupos_disponiveis = sorted(set(v.get("grupo", "Outros") for v in data.values()))
    grupos_sel = st.multiselect(
        "Grupos:",
        options=grupos_disponiveis,
        default=grupos_disponiveis,
    )

    artistas_do_grupo = [k for k, v in data.items() if v.get("grupo", "") in grupos_sel]

    st.markdown("---")
    st.markdown("### Selecionar artistas")
    todos = artistas_do_grupo
    selecionados = st.multiselect(
        "Artistas:",
        options=todos,
        default=[a for a in ["Joelma","Wesley Safadão","Simone Mendes","Xand Avião","Solange Almeida"] if a in todos],
        help="Joelma é sempre incluída automaticamente"
    )
    if "Joelma" not in selecionados and "Joelma" in data:
        selecionados = ["Joelma"] + selecionados

    st.markdown("---")
    st.markdown("### Plataformas")
    mostrar_ig = st.checkbox("Instagram", value=True)
    mostrar_tk = st.checkbox("TikTok", value=True)
    mostrar_yt = st.checkbox("YouTube", value=True)
    mostrar_sp = st.checkbox("Spotify", value=True)

    st.markdown("---")
    with st.expander("➕ Adicionar / Editar artista"):
        nome_novo = st.text_input("Nome do artista")
        genero_novo = st.text_input("Gênero musical")
        estado_novo = st.text_input("Estado (UF)")
        grupo_novo  = st.selectbox("Grupo", grupos_disponiveis + ["🔴 Concorrente Direto","🌳 Artista Paraense","📌 Referência Digital"])

        st.markdown("**Instagram**")
        ig_seg  = st.number_input("Seguidores IG", min_value=0, value=0, step=10000)
        ig_curt = st.number_input("Média curtidas/post", min_value=0, value=0)
        ig_com  = st.number_input("Média comentários/post", min_value=0, value=0)
        ig_views= st.number_input("Média views Reels", min_value=0, value=0)

        st.markdown("**TikTok**")
        tk_seg   = st.number_input("Seguidores TK", min_value=0, value=0, step=10000)
        tk_views = st.number_input("Média views TK", min_value=0, value=0)
        tk_curt  = st.number_input("Média curtidas TK", min_value=0, value=0)

        st.markdown("**YouTube**")
        yt_ins   = st.number_input("Inscritos YT", min_value=0, value=0, step=10000)
        yt_views = st.number_input("Views total YT", min_value=0, value=0, step=1000000)
        yt_media = st.number_input("Média views/vídeo", min_value=0, value=0)
        yt_vids  = st.number_input("Nº de vídeos", min_value=0, value=0)

        st.markdown("**Spotify**")
        sp_seg = st.number_input("Seguidores SP", min_value=0, value=0, step=10000)
        sp_ouv = st.number_input("Ouvintes mensais SP", min_value=0, value=0, step=10000)
        sp_pop = st.number_input("Popularidade (0-100)", min_value=0, max_value=100, value=0)

        st.markdown("**Deezer**")
        dz_fans = st.number_input("Fans Deezer", min_value=0, value=0, step=10000)

        st.markdown("**Apple Music**")
        am_ouv = st.number_input("Ouvintes mensais Apple Music", min_value=0, value=0, step=10000)

        st.markdown("**YouTube Music**")
        ytm_str = st.number_input("Streams mensais YT Music", min_value=0, value=0, step=10000)

        st.markdown("**Amazon Music**")
        amz_str = st.number_input("Streams mensais Amazon", min_value=0, value=0, step=10000)

        st.markdown("**SoundCloud**")
        sc_plays = st.number_input("Plays SoundCloud", min_value=0, value=0, step=100000)
        sc_seg   = st.number_input("Seguidores SoundCloud", min_value=0, value=0, step=10000)

        if st.button("Salvar artista", type="primary"):
            if nome_novo:
                data[nome_novo] = {
                    "genero": genero_novo,
                    "estado": estado_novo,
                    "grupo":  grupo_novo,
                    "cor": COR_SEC[len(data) % len(COR_SEC)],
                    "instagram":    {"seguidores": ig_seg, "seguindo": 0, "posts": 0,
                                     "media_curtidas": ig_curt, "media_comentarios": ig_com,
                                     "media_views_reels": ig_views},
                    "tiktok":       {"seguidores": tk_seg, "curtidas_total": 0,
                                     "media_views": tk_views, "media_curtidas": tk_curt},
                    "youtube":      {"inscritos": yt_ins, "views_total": yt_views,
                                     "media_views_video": yt_media, "videos": yt_vids},
                    "spotify":      {"seguidores": sp_seg, "ouvintes_mensais": sp_ouv,
                                     "popularidade": sp_pop},
                    "deezer":       {"fans": dz_fans, "albuns": 0},
                    "apple_music":  {"ouvintes_mensais": am_ouv},
                    "youtube_music":{"streams_mensais": ytm_str},
                    "amazon_music": {"streams_mensais": amz_str},
                    "soundcloud":   {"plays": sc_plays, "seguidores": sc_seg},
                    "shows_2026": 0,
                    "cache_shows_2026": "",
                    "top_hit": "",
                    "dados_verificados": False,
                }
                save_data(data)
                st.success(f"✅ {nome_novo} salvo!")
                st.rerun()

    st.markdown("---")
    if st.button("⬇️ Exportar CSV", use_container_width=True):
        rows_exp = []
        for nome, art in data.items():
            m_ = calc_metrics(art)
            rows_exp.append({
                "Artista": nome,
                "Grupo": art.get("grupo","—"),
                "Gênero": art.get("genero","—"),
                "Estado": art.get("estado","—"),
                "IG Seguidores": art["instagram"]["seguidores"],
                "IG Média Curtidas": art["instagram"]["media_curtidas"],
                "IG Média Comentários": art["instagram"]["media_comentarios"],
                "IG Média Views Reels": art["instagram"]["media_views_reels"],
                "IG ER (%)": m_["er_instagram"],
                "TK Seguidores": art["tiktok"]["seguidores"],
                "TK Média Views": art["tiktok"]["media_views"],
                "TK ER (%)": m_["er_tiktok"],
                "YT Inscritos": art["youtube"]["inscritos"],
                "YT Views Total": art["youtube"]["views_total"],
                "YT Média Views/Vídeo": art["youtube"]["media_views_video"],
                "SP Ouvintes Mensais": art["spotify"]["ouvintes_mensais"],
                "SP Seguidores": art["spotify"]["seguidores"],
                "SP Popularidade": art["spotify"]["popularidade"],
                "Deezer Fans": art.get("deezer",{}).get("fans",0),
                "Apple Music Mensais": art.get("apple_music",{}).get("ouvintes_mensais",0),
                "YT Music Streams": art.get("youtube_music",{}).get("streams_mensais",0),
                "Amazon Streams": art.get("amazon_music",{}).get("streams_mensais",0),
                "SoundCloud Plays": art.get("soundcloud",{}).get("plays",0),
                "Shows 2026": art.get("shows_2026",0),
                "Score Digital": m_["score_digital"],
                "Verificado": "Sim" if art.get("dados_verificados") else "Estimado",
            })
        csv_str = pd.DataFrame(rows_exp).to_csv(index=False, sep=";").encode("utf-8")
        st.download_button(
            "📥 Baixar joelma_analytics.csv",
            data=csv_str,
            file_name="joelma_analytics.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    st.caption(f"Dados verificados · Jun/2026\nJoelma Analytics v2.0")

# ═════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════
st.markdown(f"""
<h1 style='color:{COR_JOELMA};margin-bottom:0'>🎤 Joelma Analytics</h1>
<p style='color:#8B949E;margin-top:4px;font-size:1rem'>
Comparativo de Engajamento · Forró, Sertanejo e Cena Paraense · {datetime.now().strftime("%B %Y")}
</p>
""", unsafe_allow_html=True)

artistas_sel = {k: data[k] for k in selecionados if k in data}
cores = {k: v["cor"] for k, v in artistas_sel.items()}

# ═════════════════════════════════════════════════════════
# MÉTRICAS JOELMA
# ═════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🌟 Joelma — Painel Principal")
j = data.get("Joelma", {})
m = calc_metrics(j)

c1, c2, c3, c4, c5, c6 = st.columns(6)
cards = [
    (c1, fmt(j["instagram"]["seguidores"]), "Seguidores Instagram", "📸"),
    (c2, fmt(j["tiktok"]["seguidores"]),    "Seguidores TikTok",    "🎵"),
    (c3, fmt(j["youtube"]["inscritos"]),    "Inscritos YouTube",    "▶️"),
    (c4, fmt(j["spotify"]["ouvintes_mensais"]), "Ouvintes Mensais Spotify", "🎧"),
    (c5, f"{m['er_instagram']}%",           "Taxa Engaj. Instagram", "💬"),
    (c6, str(j.get("shows_2026", 0)),       "Shows 2026",           "🎪"),
]
for col, val, lbl, ico in cards:
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.5rem">{ico}</div>
        <div class="metric-value">{val}</div>
        <div class="metric-label">{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Comparativo Geral",
    "📸 Instagram",
    "🎵 TikTok",
    "▶️ YouTube",
    "🎧 Streaming",
    "🧠 Análise Estratégica",
    "🏆 Rankings",
    "👤 Perfil do Artista",
])

# ─────────────────────────────────────────────────────────
# TAB 1 — COMPARATIVO GERAL
# ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("#### Total de Seguidores por Plataforma")

    rows = []
    for nome, art in artistas_sel.items():
        m_ = calc_metrics(art)
        rows.append({
            "Artista": nome,
            "Grupo": art.get("grupo", "—"),
            "Instagram": art["instagram"]["seguidores"],
            "TikTok": art["tiktok"]["seguidores"],
            "YouTube (inscritos)": art["youtube"]["inscritos"],
            "Spotify (ouvintes mensais)": art["spotify"]["ouvintes_mensais"],
            "Score Digital": m_["score_digital"],
            "ER Instagram (%)": m_["er_instagram"],
            "ER TikTok (%)": m_["er_tiktok"],
            "Gênero": art["genero"],
            "Verificado": "✅" if art.get("dados_verificados") else "~",
        })
    df = pd.DataFrame(rows)

    plats = []
    if mostrar_ig: plats.append("Instagram")
    if mostrar_tk: plats.append("TikTok")
    if mostrar_yt: plats.append("YouTube (inscritos)")
    if mostrar_sp: plats.append("Spotify (ouvintes mensais)")

    if plats:
        df_melt = df[["Artista"] + plats].melt(id_vars="Artista", var_name="Plataforma", value_name="Seguidores")
        fig_bar = px.bar(df_melt, x="Artista", y="Seguidores", color="Plataforma",
                         barmode="group",
                         color_discrete_map={
                             "Instagram": "#C13584",
                             "TikTok": "#69C9D0",
                             "YouTube (inscritos)": "#FF0000",
                             "Spotify (ouvintes mensais)": "#1DB954",
                         },
                         template="plotly_dark")
        fig_bar.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                              font_color="white", height=420, legend_title="")
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🎯 Score Digital Geral")
        fig_score = px.bar(df.sort_values("Score Digital", ascending=True),
                           x="Score Digital", y="Artista", orientation="h",
                           color="Score Digital", color_continuous_scale="Reds",
                           template="plotly_dark",
                           text="Score Digital")
        fig_score.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                                font_color="white", height=420,
                                coloraxis_showscale=False, showlegend=False)
        fig_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig_score, use_container_width=True)
        st.caption("Score = IG×1.0 + TK×1.2 + YT×0.8 + SP×0.5 (em milhões)")

    with col_b:
        st.markdown("#### 💬 Taxa de Engajamento")
        fig_er = go.Figure()
        fig_er.add_trace(go.Bar(
            name="ER Instagram (%)",
            x=df["Artista"], y=df["ER Instagram (%)"],
            marker_color="#C13584",
            text=df["ER Instagram (%)"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
        ))
        fig_er.add_trace(go.Bar(
            name="ER TikTok (%)",
            x=df["Artista"], y=df["ER TikTok (%)"],
            marker_color="#69C9D0",
            text=df["ER TikTok (%)"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
        ))
        fig_er.update_layout(barmode="group", template="plotly_dark",
                             paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                             font_color="white", height=420, legend_title="")
        st.plotly_chart(fig_er, use_container_width=True)
        st.caption("ER = (curtidas + comentários) ÷ seguidores × 100")

    st.markdown("#### 📋 Tabela Comparativa Completa")
    df_show = df[["Artista","Grupo","Gênero","Verificado","Instagram","TikTok",
                  "YouTube (inscritos)","Spotify (ouvintes mensais)","Score Digital",
                  "ER Instagram (%)","ER TikTok (%)"]].copy()
    for col_ in ["Instagram","TikTok","YouTube (inscritos)","Spotify (ouvintes mensais)"]:
        df_show[col_] = df_show[col_].apply(fmt)
    st.dataframe(df_show.set_index("Artista"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 2 — INSTAGRAM
# ─────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📸 Instagram — Análise Detalhada")
    ig_rows = []
    for nome, art in artistas_sel.items():
        ig = art["instagram"]
        er = (ig["media_curtidas"] + ig["media_comentarios"]) / ig["seguidores"] * 100 if ig["seguidores"] else 0
        ig_rows.append({
            "Artista": nome,
            "Seguidores": ig["seguidores"],
            "Média Curtidas": ig["media_curtidas"],
            "Média Comentários": ig["media_comentarios"],
            "Média Views Reels": ig["media_views_reels"],
            "ER (%)": round(er, 2),
            "cor": art["cor"],
        })
    df_ig = pd.DataFrame(ig_rows)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df_ig.sort_values("Seguidores", ascending=True),
                     x="Seguidores", y="Artista", orientation="h",
                     color="Artista", color_discrete_map=cores, template="plotly_dark",
                     text=df_ig.sort_values("Seguidores")["Seguidores"].apply(fmt))
        fig.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=400, showlegend=False,
                          title="Seguidores Instagram")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.bar(df_ig.sort_values("ER (%)", ascending=True),
                      x="ER (%)", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_ig.sort_values("ER (%)")["ER (%)"].apply(lambda x: f"{x:.2f}%"))
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=400, showlegend=False,
                           title="Taxa de Engajamento (%)")
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 👁️ Média de Views em Reels")
    fig3 = px.bar(df_ig.sort_values("Média Views Reels", ascending=False),
                  x="Artista", y="Média Views Reels",
                  color="Artista", color_discrete_map=cores, template="plotly_dark",
                  text=df_ig.sort_values("Média Views Reels", ascending=False)["Média Views Reels"].apply(fmt))
    fig3.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                       font_color="white", height=320, showlegend=False)
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    df_ig_show = df_ig.drop(columns=["cor"])
    for col_ in ["Seguidores","Média Curtidas","Média Comentários","Média Views Reels"]:
        df_ig_show[col_] = df_ig_show[col_].apply(fmt)
    st.dataframe(df_ig_show.set_index("Artista"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 3 — TIKTOK
# ─────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🎵 TikTok — Análise Detalhada")
    tk_rows = []
    for nome, art in artistas_sel.items():
        tk = art["tiktok"]
        er = tk["media_curtidas"] / tk["seguidores"] * 100 if tk["seguidores"] else 0
        tk_rows.append({
            "Artista": nome,
            "Seguidores": tk["seguidores"],
            "Curtidas Total": tk["curtidas_total"],
            "Média Views": tk["media_views"],
            "Média Curtidas": tk["media_curtidas"],
            "ER TikTok (%)": round(er, 2),
        })
    df_tk = pd.DataFrame(tk_rows)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(df_tk, x="Seguidores", y="Média Views",
                         size="Curtidas Total", color="Artista",
                         color_discrete_map=cores, template="plotly_dark",
                         hover_name="Artista", size_max=60,
                         title="Seguidores vs Média de Views (tamanho = curtidas totais)")
        fig.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.bar(df_tk.sort_values("ER TikTok (%)", ascending=True),
                      x="ER TikTok (%)", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_tk.sort_values("ER TikTok (%)")["ER TikTok (%)"].apply(lambda x: f"{x:.2f}%"),
                      title="Taxa de Engajamento TikTok (%)")
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=380, showlegend=False)
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📊 Seguidores TikTok — Ranking")
    fig_tk_rank = px.bar(df_tk.sort_values("Seguidores", ascending=False),
                         x="Artista", y="Seguidores",
                         color="Artista", color_discrete_map=cores, template="plotly_dark",
                         text=df_tk.sort_values("Seguidores", ascending=False)["Seguidores"].apply(fmt))
    fig_tk_rank.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                               font_color="white", height=320, showlegend=False)
    fig_tk_rank.update_traces(textposition="outside")
    st.plotly_chart(fig_tk_rank, use_container_width=True)

    df_tk_show = df_tk.copy()
    for col_ in ["Seguidores","Curtidas Total","Média Views","Média Curtidas"]:
        df_tk_show[col_] = df_tk_show[col_].apply(fmt)
    st.dataframe(df_tk_show.set_index("Artista"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 4 — YOUTUBE
# ─────────────────────────────────────────────────────────
with tab4:
    st.markdown("### ▶️ YouTube — Análise Detalhada")
    yt_rows = []
    for nome, art in artistas_sel.items():
        yt = art["youtube"]
        vpp = yt["views_total"] / yt["inscritos"] if yt["inscritos"] else 0
        yt_rows.append({
            "Artista": nome,
            "Inscritos": yt["inscritos"],
            "Views Total": yt["views_total"],
            "Média Views/Vídeo": yt["media_views_video"],
            "Vídeos": yt["videos"],
            "Views por Inscrito": round(vpp, 0),
        })
    df_yt = pd.DataFrame(yt_rows)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.treemap(df_yt, path=["Artista"], values="Views Total",
                         color="Inscritos", color_continuous_scale="Reds",
                         template="plotly_dark", title="Views Total YouTube")
        fig.update_layout(paper_bgcolor="#0F1117", font_color="white", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.scatter(df_yt, x="Inscritos", y="Média Views/Vídeo",
                          size="Views Total", color="Artista",
                          color_discrete_map=cores, template="plotly_dark",
                          hover_name="Artista", size_max=60,
                          title="Inscritos vs Média Views por Vídeo")
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=380)
        st.plotly_chart(fig2, use_container_width=True)

    df_yt_show = df_yt.copy()
    for col_ in ["Inscritos","Views Total","Média Views/Vídeo","Views por Inscrito"]:
        df_yt_show[col_] = df_yt_show[col_].apply(lambda x: fmt(int(x)))
    st.dataframe(df_yt_show.set_index("Artista"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 5 — STREAMING
# ─────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 🎧 Plataformas de Streaming — Comparativo Completo")

    COR_PLAT = {
        "Spotify":       "#1DB954",
        "Deezer":        "#EF5466",
        "Apple Music":   "#FC3C44",
        "YouTube Music": "#FF0000",
        "Amazon Music":  "#00A8E0",
        "SoundCloud":    "#FF5500",
    }

    str_rows = []
    for nome, art in artistas_sel.items():
        sp  = art.get("spotify",       {"seguidores":0,"ouvintes_mensais":0,"popularidade":0})
        dz  = art.get("deezer",        {"fans":0,"albuns":0})
        am  = art.get("apple_music",   {"ouvintes_mensais":0})
        ytm = art.get("youtube_music", {"streams_mensais":0})
        amz = art.get("amazon_music",  {"streams_mensais":0})
        sc  = art.get("soundcloud",    {"plays":0,"seguidores":0})
        str_rows.append({
            "Artista":              nome,
            "Spotify — Ouvintes":   sp["ouvintes_mensais"],
            "Spotify — Seguidores": sp["seguidores"],
            "Spotify — Popul.":     sp["popularidade"],
            "Deezer — Fans":        dz["fans"],
            "Apple Music":          am["ouvintes_mensais"],
            "YouTube Music":        ytm["streams_mensais"],
            "Amazon Music":         amz["streams_mensais"],
            "SoundCloud — Plays":   sc["plays"],
            "SoundCloud — Seguid.": sc["seguidores"],
        })
    df_str = pd.DataFrame(str_rows)

    st.markdown("#### 📊 Ouvintes / Streams Mensais — Todas as Plataformas")
    plat_cols = {
        "Spotify":       "Spotify — Ouvintes",
        "Apple Music":   "Apple Music",
        "YouTube Music": "YouTube Music",
        "Amazon Music":  "Amazon Music",
    }
    df_ouv = df_str[["Artista"] + list(plat_cols.values())].melt(
        id_vars="Artista", var_name="Plataforma", value_name="Streams")
    df_ouv["Plataforma"] = df_ouv["Plataforma"].map({v: k for k, v in plat_cols.items()})

    fig_all = px.bar(df_ouv, x="Artista", y="Streams", color="Plataforma",
                     barmode="group", template="plotly_dark",
                     color_discrete_map=COR_PLAT,
                     text=df_ouv["Streams"].apply(fmt))
    fig_all.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=420, legend_title="",
                          bargap=0.15, bargroupgap=0.05)
    fig_all.update_traces(textposition="outside", textfont_size=8)
    st.plotly_chart(fig_all, use_container_width=True)

    st.markdown("#### 🔍 Detalhamento por Plataforma")

    st.markdown("##### 🟢 Spotify")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.bar(df_str.sort_values("Spotify — Ouvintes", ascending=True),
                     x="Spotify — Ouvintes", y="Artista", orientation="h",
                     color="Artista", color_discrete_map=cores, template="plotly_dark",
                     text=df_str.sort_values("Spotify — Ouvintes")["Spotify — Ouvintes"].apply(fmt),
                     title="Ouvintes Mensais")
        fig.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=320, showlegend=False)
        fig.update_traces(textposition="outside", marker_color="#1DB954")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(df_str.sort_values("Spotify — Seguidores", ascending=True),
                      x="Spotify — Seguidores", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_str.sort_values("Spotify — Seguidores")["Spotify — Seguidores"].apply(fmt),
                      title="Seguidores")
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=320, showlegend=False)
        fig2.update_traces(textposition="outside", marker_color="#1DB954")
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        fig3 = px.bar(df_str.sort_values("Spotify — Popul.", ascending=True),
                      x="Spotify — Popul.", y="Artista", orientation="h",
                      color="Spotify — Popul.", color_continuous_scale=["#145A32","#1DB954"],
                      template="plotly_dark",
                      text=df_str.sort_values("Spotify — Popul.")["Spotify — Popul."],
                      title="Índice de Popularidade (0–100)")
        fig3.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=320, coloraxis_showscale=False)
        fig3.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("##### 🔴 Deezer  &  🍎 Apple Music")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df_str.sort_values("Deezer — Fans", ascending=True),
                     x="Deezer — Fans", y="Artista", orientation="h",
                     color="Artista", color_discrete_map=cores, template="plotly_dark",
                     text=df_str.sort_values("Deezer — Fans")["Deezer — Fans"].apply(fmt),
                     title="Deezer — Fans")
        fig.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=340, showlegend=False)
        fig.update_traces(textposition="outside", marker_color="#EF5466")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(df_str.sort_values("Apple Music", ascending=True),
                      x="Apple Music", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_str.sort_values("Apple Music")["Apple Music"].apply(fmt),
                      title="Apple Music — Ouvintes Mensais")
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=340, showlegend=False)
        fig2.update_traces(textposition="outside", marker_color="#FC3C44")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### 🎵 YouTube Music  ·  📦 Amazon Music  ·  ☁️ SoundCloud")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.bar(df_str.sort_values("YouTube Music", ascending=True),
                     x="YouTube Music", y="Artista", orientation="h",
                     color="Artista", color_discrete_map=cores, template="plotly_dark",
                     text=df_str.sort_values("YouTube Music")["YouTube Music"].apply(fmt),
                     title="YouTube Music — Streams Mensais")
        fig.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                          font_color="white", height=360, showlegend=False)
        fig.update_traces(textposition="outside", marker_color="#FF0000")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(df_str.sort_values("Amazon Music", ascending=True),
                      x="Amazon Music", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_str.sort_values("Amazon Music")["Amazon Music"].apply(fmt),
                      title="Amazon Music — Streams Mensais")
        fig2.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=360, showlegend=False)
        fig2.update_traces(textposition="outside", marker_color="#00A8E0")
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        fig3 = px.bar(df_str.sort_values("SoundCloud — Plays", ascending=True),
                      x="SoundCloud — Plays", y="Artista", orientation="h",
                      color="Artista", color_discrete_map=cores, template="plotly_dark",
                      text=df_str.sort_values("SoundCloud — Plays")["SoundCloud — Plays"].apply(fmt),
                      title="SoundCloud — Total de Plays")
        fig3.update_layout(paper_bgcolor="#0F1117", plot_bgcolor="#161B22",
                           font_color="white", height=360, showlegend=False)
        fig3.update_traces(textposition="outside", marker_color="#FF5500")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### 🕸️ Radar — Presença Relativa em Streaming")
    st.caption("Cada eixo representa a fatia do artista no total de cada plataforma (normalizado 0–100)")
    radar_plats = ["Spotify — Ouvintes","Apple Music","YouTube Music","Amazon Music","SoundCloud — Plays"]
    fig_rad = go.Figure()
    for nome in df_str["Artista"]:
        row = df_str[df_str["Artista"] == nome].iloc[0]
        vals = []
        for col_ in radar_plats:
            total = df_str[col_].sum()
            vals.append(round(row[col_] / total * 100, 1) if total else 0)
        vals.append(vals[0])
        cats = ["Spotify","Apple Music","YT Music","Amazon","SoundCloud","Spotify"]
        fig_rad.add_trace(go.Scatterpolar(
            r=vals, theta=cats, fill="toself",
            name=nome, line_color=cores.get(nome, "#888"),
            opacity=0.75,
        ))
    fig_rad.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,60],
                                   gridcolor="#333", tickfont_color="#888")),
        paper_bgcolor="#0F1117", font_color="white",
        height=460, legend_title="", showlegend=True,
        template="plotly_dark",
    )
    st.plotly_chart(fig_rad, use_container_width=True)

    st.markdown("#### 📋 Tabela Completa — Todas as Plataformas de Streaming")
    df_str_show = df_str.copy()
    for col_ in ["Spotify — Ouvintes","Spotify — Seguidores","Deezer — Fans",
                 "Apple Music","YouTube Music","Amazon Music",
                 "SoundCloud — Plays","SoundCloud — Seguid."]:
        df_str_show[col_] = df_str_show[col_].apply(fmt)
    st.dataframe(df_str_show.set_index("Artista"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 6 — ANÁLISE ESTRATÉGICA
# ─────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 🧠 Análise Estratégica — Joelma vs Mercado")
    st.caption("Baseada em dados verificados · Jun/2026 · Documentos 06 e 07")

    # ── Bloco 1: Concorrentes diretos
    st.markdown("---")
    st.markdown("#### 🔴 Concorrentes Diretos — Distâncias Reais")

    # Tabela de distâncias
    joelma = data.get("Joelma", {})
    j_ig = joelma.get("instagram",{}).get("seguidores", 0)
    j_tk = joelma.get("tiktok",{}).get("seguidores", 0)
    j_sp = joelma.get("spotify",{}).get("ouvintes_mensais", 0)

    concorrentes = ["Wesley Safadão","Simone Mendes","Xand Avião","Solange Almeida"]
    dist_rows = []
    for c in concorrentes:
        if c not in data: continue
        art = data[c]
        c_ig = art["instagram"]["seguidores"]
        c_tk = art["tiktok"]["seguidores"]
        c_sp = art["spotify"]["ouvintes_mensais"]
        fator_ig = round(c_ig / j_ig, 1) if j_ig else 0
        fator_tk = round(c_tk / j_tk, 1) if j_tk else 0
        fator_sp = round(c_sp / j_sp, 1) if j_sp else 0
        ig_str = f"{fmt(c_ig)} ({'+' if fator_ig > 1 else ''}{fator_ig}x)" if fator_ig != 1 else fmt(c_ig)
        tk_str = f"{fmt(c_tk)} ({'+' if fator_tk > 1 else ''}{fator_tk}x)" if fator_tk != 1 else fmt(c_tk)
        sp_str = f"{fmt(c_sp)} ({'+' if fator_sp > 1 else ''}{fator_sp}x)" if fator_sp != 1 else fmt(c_sp)
        dist_rows.append({
            "Artista": c,
            "Instagram": ig_str,
            "TikTok": tk_str,
            "Spotify Mensal": sp_str,
            "Risco": "🔴 ALTO" if fator_sp > 5 else ("🟡 MÉDIO" if fator_sp > 1.5 else "🟢 BAIXO"),
        })

    df_dist = pd.DataFrame(dist_rows)
    st.dataframe(df_dist.set_index("Artista"), use_container_width=True)
    st.caption(f"Base Joelma: Instagram {fmt(j_ig)} · TikTok {fmt(j_tk)} · Spotify {fmt(j_sp)} ouvintes/mês")

    # ── Bloco 2: Paraenses
    st.markdown("---")
    st.markdown("#### 🌳 Artistas Paraenses — Joelma no Cenário do Norte")

    paraenses = ["Manu Bahtidão","Fafá de Belém","Gaby Amarantos","Viviane Batidão","Zaynara"]
    par_rows = []
    for p in paraenses:
        if p not in data: continue
        art = data[p]
        p_ig = art["instagram"]["seguidores"]
        p_tk = art["tiktok"]["seguidores"]
        p_sp = art["spotify"]["ouvintes_mensais"]
        ig_w = "✅ Joelma lidera" if j_ig > p_ig else f"⚠️ {p} +{round(p_ig/j_ig,1)}x"
        tk_w = "✅ Joelma lidera" if j_tk > p_tk else f"⚠️ {p} +{round(p_tk/j_tk,1)}x"
        sp_w = "✅ Joelma lidera" if j_sp > p_sp else f"⚠️ {p} +{round(p_sp/j_sp,1)}x"
        par_rows.append({
            "Artista": p,
            "Gênero": art["genero"],
            "Instagram": f"{fmt(p_ig)} — {ig_w}",
            "TikTok": f"{fmt(p_tk)} — {tk_w}",
            "Spotify": f"{fmt(p_sp)} — {sp_w}",
            "Top Hit": art.get("top_hit","—"),
        })

    df_par = pd.DataFrame(par_rows)
    st.dataframe(df_par.set_index("Artista"), use_container_width=True)

    # ── Bloco 3: Ana Castela como referência
    st.markdown("---")
    st.markdown("#### 📌 Ana Castela — O Modelo Digital Que Joelma Deve Mirar")
    if "Ana Castela" in data:
        ac = data["Ana Castela"]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("TikTok", fmt(ac["tiktok"]["seguidores"]),
                      delta=f"Joelma tem {fmt(j_tk)} ({round(j_tk/ac['tiktok']['seguidores']*100)}% de AC)")
        with c2:
            st.metric("Spotify Mensal", fmt(ac["spotify"]["ouvintes_mensais"]),
                      delta=f"Joelma tem {fmt(j_sp)} ({round(j_sp/ac['spotify']['ouvintes_mensais']*100)}% de AC)")
        with c3:
            st.metric("Instagram", fmt(ac["instagram"]["seguidores"]),
                      delta=f"Joelma tem {fmt(j_ig)} ({round(j_ig/ac['instagram']['seguidores']*100)}% de AC)")
        st.info("Ana Castela não compite com Joelma em gênero, mas mostra o potencial de uma artista feminina popular que investe pesado no digital. Ela tem 16,7M no TikTok e 12,6M no Spotify Mensal.")

    # ── Bloco 4: 5 Insights
    st.markdown("---")
    st.markdown("#### 💡 5 Insights Estratégicos Prioritários")

    insights = [
        ("🔴", "URGENTE", "Simone Mendes é o maior risco real",
         "Não é Wesley — é Simone. Ela domina TikTok (+6x vs Joelma), Spotify mensal (+17,8x) e ocupa "
         "exatamente o mesmo posicionamento simbólico: mulher, ex-banda, reinventada, fé, Nordeste."),
        ("🔴", "URGENTE", "Gap de Spotify é o maior problema operacional",
         "Joelma tem 713K ouvintes mensais. Simone tem 12,7M. Até Solange Almeida (1,5M) tem o dobro. "
         "O catálogo da Calypso nunca foi lançado no streaming — isso precisa ser resolvido."),
        ("🟢", "FORÇA", "Joelma já vence dois concorrentes no TikTok",
         "vs Xand Avião: Joelma +142%. vs Solange Almeida: Joelma +70%. "
         "TikTok é a plataforma de descoberta do São João 2026 — Joelma já é competitiva aqui."),
        ("🟢", "ATIVO EXCLUSIVO", "O 'Alôôôô' é intransferível",
         "Nenhum concorrente tem bordão viral nacional comparável. O 'Alôôôô' de Joelma é trend "
         "recorrente no TikTok e ninguém pode copiar. É o maior diferencial digital subutilizado."),
        ("🟡", "OPORTUNIDADE", "30 anos de carreira + Manu Bahtidão + Zaynara",
         "Nenhum concorrente tem 30 anos de história para celebrar em 2026. Collab com Manu Bahtidão "
         "= fusão das duas maiores forças do Pará. Zaynara = narrativa de 'passagem de bastão'."),
    ]

    for cor_badge, tipo, titulo, descricao in insights:
        css_class = "insight-card" if cor_badge == "🔴" else ("insight-card-green" if cor_badge == "🟢" else "insight-card-yellow")
        st.markdown(f"""
        <div class="{css_class}">
            <strong>{cor_badge} {tipo} — {titulo}</strong><br>
            <span style="color:#8B949E;font-size:.9rem">{descricao}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Bloco 5: Collabs recomendadas
    st.markdown("---")
    st.markdown("#### 🤝 Collabs Recomendadas — Por Potencial de Impacto")

    collabs = [
        {"Collab": "Joelma + Manu Bahtidão", "Plataforma Principal": "Spotify + TikTok",
         "Impacto": "🔴 Máximo", "Por quê": "As 2 maiores artistas do Pará — streaming explosion garantido"},
        {"Collab": "Joelma + Zaynara", "Plataforma Principal": "TikTok + YouTube",
         "Impacto": "🔴 Alto", "Por quê": "Narrativa 'passagem de bastão' — já tem collab anterior"},
        {"Collab": "Joelma + Gaby Amarantos", "Plataforma Principal": "YouTube + mercado internacional",
         "Impacto": "🟡 Médio", "Por quê": "Grammy Latino de Gaby abre o mercado latino para Joelma"},
        {"Collab": "Joelma + Fafá de Belém", "Plataforma Principal": "São João ao vivo + TV",
         "Impacto": "🟡 Médio", "Por quê": "Evento histórico cultural — cobertura espontânea massiva"},
        {"Collab": "Joelma + Ana Castela", "Plataforma Principal": "TikTok",
         "Impacto": "🟢 Estratégico", "Por quê": "Ponte sertanejo/calypso — acesso ao público de 16,7M seguidores"},
    ]
    st.dataframe(pd.DataFrame(collabs).set_index("Collab"), use_container_width=True)

    # ── Bloco 6: Prioridades de ação
    st.markdown("---")
    st.markdown("#### 🎯 Recomendações Prioritárias")

    acoes = [
        {"Prioridade": "🔴 URGENTE", "Ação": "Relançar catálogo Calypso no Spotify",
         "Meta": "Subir de 713K para 2M+ ouvintes mensais"},
        {"Prioridade": "🔴 URGENTE", "Ação": "Campanha TikTok diária 'Alôôôô [cidade]'",
         "Meta": "Subir de 2,9M para 5M+ seguidores"},
        {"Prioridade": "🔴 URGENTE", "Ação": "Buscar espaço SBT/Band/RecordTV São João",
         "Meta": "Contrariar monopólio Globo de Wesley Safadão"},
        {"Prioridade": "🟡 IMPORTANTE", "Ação": "Collab com Manu Bahtidão",
         "Meta": "Hit nas 2 maiores plataformas de streaming do Norte"},
        {"Prioridade": "🟡 IMPORTANTE", "Ação": "Playlist editorial '30 Anos: Do Calypso ao Forró'",
         "Meta": "Disputar espaço editorial com Xand Avião no Spotify forró"},
        {"Prioridade": "🟢 ESTRATÉGICO", "Ação": "Mini-documentário YouTube '30 Anos'",
         "Meta": "Narrativa intransferível que nenhum concorrente pode copiar"},
        {"Prioridade": "🟢 ESTRATÉGICO", "Ação": "Mentoria pública de Zaynara no palco do São João",
         "Meta": "Marketing cultural de longo prazo + geração Z"},
    ]
    st.dataframe(pd.DataFrame(acoes).set_index("Prioridade"), use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 7 — RANKINGS
# ─────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 🏆 Rankings — Top Artistas por Métrica")
    st.caption("Baseado nos artistas selecionados no filtro lateral")

    MEDAL = {0: "🥇", 1: "🥈", 2: "🥉"}

    def ranking_block(title, getter, formatter=fmt):
        st.markdown(f"#### {title}")
        items = [(nome, getter(art)) for nome, art in artistas_sel.items()]
        items.sort(key=lambda x: x[1], reverse=True)
        cols_r = st.columns(min(len(items), 5))
        for i, (nome, val) in enumerate(items[:5]):
            medal = MEDAL.get(i, f"#{i+1}")
            cor_art = cores.get(nome, "#888")
            cols_r[i].markdown(f"""
            <div style="background:#1C2128;border-radius:10px;padding:14px;
                        border-top:4px solid {cor_art};text-align:center">
                <div style="font-size:1.6rem">{medal}</div>
                <div style="font-weight:700;color:{cor_art};font-size:.95rem;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nome}</div>
                <div style="font-size:1.25rem;font-weight:800;color:white;margin-top:4px">
                    {formatter(val)}</div>
            </div>
            """, unsafe_allow_html=True)

    col_rk1, col_rk2 = st.columns(2)
    with col_rk1:
        ranking_block("📸 Instagram — Seguidores",
                      lambda a: a["instagram"]["seguidores"])
    with col_rk2:
        ranking_block("💬 Instagram — Engajamento (%)",
                      lambda a: round((a["instagram"]["media_curtidas"] + a["instagram"]["media_comentarios"])
                                      / a["instagram"]["seguidores"] * 100, 2) if a["instagram"]["seguidores"] else 0,
                      formatter=lambda x: f"{x:.2f}%")

    st.markdown("---")
    col_rk3, col_rk4 = st.columns(2)
    with col_rk3:
        ranking_block("🎵 TikTok — Seguidores",
                      lambda a: a["tiktok"]["seguidores"])
    with col_rk4:
        ranking_block("👁️ TikTok — Média de Views",
                      lambda a: a["tiktok"]["media_views"])

    st.markdown("---")
    col_rk5, col_rk6 = st.columns(2)
    with col_rk5:
        ranking_block("▶️ YouTube — Inscritos",
                      lambda a: a["youtube"]["inscritos"])
    with col_rk6:
        ranking_block("▶️ YouTube — Views Totais",
                      lambda a: a["youtube"]["views_total"])

    st.markdown("---")
    col_rk7, col_rk8 = st.columns(2)
    with col_rk7:
        ranking_block("🎧 Spotify — Ouvintes Mensais",
                      lambda a: a["spotify"]["ouvintes_mensais"])
    with col_rk8:
        ranking_block("🌐 Score Digital Geral",
                      lambda a: calc_metrics(a)["score_digital"],
                      formatter=lambda x: f"{x:.1f}")

    st.markdown("---")
    col_rk9, col_rk10 = st.columns(2)
    with col_rk9:
        ranking_block("🎪 Shows em 2026",
                      lambda a: a.get("shows_2026", 0))
    with col_rk10:
        ranking_block("☁️ SoundCloud — Total de Plays",
                      lambda a: a.get("soundcloud", {}).get("plays", 0))

    # Tabela de posições consolidada
    st.markdown("---")
    st.markdown("#### 📋 Tabela de Posições — Resumo Consolidado")
    pos_rows = []
    metricas_rank = {
        "IG Seg.":    lambda a: a["instagram"]["seguidores"],
        "IG ER":      lambda a: (a["instagram"]["media_curtidas"]+a["instagram"]["media_comentarios"])
                                / a["instagram"]["seguidores"] * 100 if a["instagram"]["seguidores"] else 0,
        "TK Seg.":    lambda a: a["tiktok"]["seguidores"],
        "TK Views":   lambda a: a["tiktok"]["media_views"],
        "YT Inscr.":  lambda a: a["youtube"]["inscritos"],
        "SP Ouv.":    lambda a: a["spotify"]["ouvintes_mensais"],
        "Score":      lambda a: calc_metrics(a)["score_digital"],
        "Shows":      lambda a: a.get("shows_2026",0),
    }
    rankings_por_metrica = {}
    for met, fn in metricas_rank.items():
        ordered = sorted(artistas_sel.keys(), key=lambda n: fn(artistas_sel[n]), reverse=True)
        for pos, nome in enumerate(ordered, start=1):
            rankings_por_metrica.setdefault(nome, {})[met] = pos

    for nome in artistas_sel:
        row = {"Artista": nome}
        row.update(rankings_por_metrica.get(nome, {}))
        vals = [v for v in rankings_por_metrica.get(nome, {}).values()]
        row["Posição Média"] = round(sum(vals)/len(vals), 1) if vals else 0
        pos_rows.append(row)

    df_pos = pd.DataFrame(pos_rows).sort_values("Posição Média")
    df_pos = df_pos.set_index("Artista")
    st.dataframe(df_pos.style.background_gradient(
        subset=list(metricas_rank.keys()) + ["Posição Média"],
        cmap="RdYlGn_r",
    ), use_container_width=True)
    st.caption("Menor número = melhor posição. Posição Média considera todas as 8 métricas.")

# ─────────────────────────────────────────────────────────
# TAB 8 — PERFIL DO ARTISTA
# ─────────────────────────────────────────────────────────
with tab8:
    st.markdown("### 👤 Perfil Individual do Artista")

    artista_perfil = st.selectbox(
        "Escolha o artista para ver o perfil completo:",
        options=list(artistas_sel.keys()),
        index=0,
    )

    if artista_perfil and artista_perfil in artistas_sel:
        ap = artistas_sel[artista_perfil]
        mp = calc_metrics(ap)
        cor_p = ap["cor"]
        verified_badge = '<span class="badge-verified">✓ Verificado</span>' if ap.get("dados_verificados") else '<span class="badge-est">~ Estimado</span>'

        st.markdown(f"""
        <div style="background:#1C2128;border-radius:16px;padding:24px;
                    border-left:6px solid {cor_p};margin-bottom:20px">
            <h2 style="color:{cor_p};margin:0">{artista_perfil} {verified_badge}</h2>
            <p style="color:#8B949E;margin:6px 0 0 0">
                {ap.get('genero','—')} &nbsp;·&nbsp; {ap.get('estado','—')} &nbsp;·&nbsp;
                {ap.get('grupo','—')}
            </p>
            <p style="color:#E67E22;margin:8px 0 0 0">
                🎵 Top hit: {ap.get('top_hit','—')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # KPIs principais
        st.markdown("#### 📊 KPIs Principais")
        pk1, pk2, pk3, pk4, pk5, pk6 = st.columns(6)
        kpi_data = [
            (pk1, "📸 Instagram", fmt(ap["instagram"]["seguidores"]), "seguidores"),
            (pk2, "🎵 TikTok",    fmt(ap["tiktok"]["seguidores"]),    "seguidores"),
            (pk3, "▶️ YouTube",   fmt(ap["youtube"]["inscritos"]),     "inscritos"),
            (pk4, "🎧 Spotify",   fmt(ap["spotify"]["ouvintes_mensais"]), "ouv/mês"),
            (pk5, "💬 ER Insta",  f"{mp['er_instagram']:.2f}%",       "engajamento"),
            (pk6, "🎪 Shows",     str(ap.get("shows_2026",0)),         "em 2026"),
        ]
        for col, plat, val, sub in kpi_data:
            col.markdown(f"""
            <div style="background:#161B22;border-radius:10px;padding:14px;
                        border-top:3px solid {cor_p};text-align:center">
                <div style="font-size:.75rem;color:#8B949E">{plat}</div>
                <div style="font-size:1.4rem;font-weight:800;color:{cor_p}">{val}</div>
                <div style="font-size:.7rem;color:#555">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Gráfico radar do artista
        col_rad, col_tab = st.columns([1, 1])
        with col_rad:
            st.markdown("#### 🕸️ Perfil em Radar")
            # Normaliza em relação ao máximo entre todos os artistas selecionados
            def norm_max(getter):
                vals_all = [getter(a) for a in artistas_sel.values()]
                mx = max(vals_all) if vals_all else 1
                return round(getter(ap) / mx * 100, 1) if mx else 0

            radar_vals = [
                norm_max(lambda a: a["instagram"]["seguidores"]),
                norm_max(lambda a: a["tiktok"]["seguidores"]),
                norm_max(lambda a: a["youtube"]["inscritos"]),
                norm_max(lambda a: a["spotify"]["ouvintes_mensais"]),
                norm_max(lambda a: a.get("soundcloud",{}).get("plays",0)),
                norm_max(lambda a: a.get("shows_2026",0)),
            ]
            cats_rad = ["Instagram","TikTok","YouTube","Spotify","SoundCloud","Shows"]
            radar_vals_c = radar_vals + [radar_vals[0]]
            cats_rad_c   = cats_rad   + [cats_rad[0]]

            fig_pr = go.Figure()
            fig_pr.add_trace(go.Scatterpolar(
                r=radar_vals_c, theta=cats_rad_c,
                fill="toself", name=artista_perfil,
                line_color=cor_p, fillcolor=cor_p, opacity=0.35,
            ))
            fig_pr.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                           gridcolor="#333", tickfont_color="#666")),
                paper_bgcolor="#0F1117", font_color="white",
                height=350, showlegend=False,
                margin=dict(l=40,r=40,t=40,b=40),
            )
            st.plotly_chart(fig_pr, use_container_width=True)
            st.caption("Valores normalizados em relação ao maior entre os artistas selecionados (100 = líder)")

        with col_tab:
            st.markdown("#### 📋 Dados Completos")

            plataformas_detail = {
                "📸 Instagram": {
                    "Seguidores":     ap["instagram"]["seguidores"],
                    "Posts":          ap["instagram"].get("posts", 0),
                    "Média Curtidas": ap["instagram"]["media_curtidas"],
                    "Média Coment.":  ap["instagram"]["media_comentarios"],
                    "Média Views Reels": ap["instagram"]["media_views_reels"],
                    "Taxa Engaj.":    f"{mp['er_instagram']:.2f}%",
                },
                "🎵 TikTok": {
                    "Seguidores":    ap["tiktok"]["seguidores"],
                    "Curtidas Total": ap["tiktok"].get("curtidas_total",0),
                    "Média Views":   ap["tiktok"]["media_views"],
                    "Média Curtidas": ap["tiktok"]["media_curtidas"],
                    "Taxa Engaj.":   f"{mp['er_tiktok']:.2f}%",
                },
                "▶️ YouTube": {
                    "Inscritos":     ap["youtube"]["inscritos"],
                    "Views Total":   ap["youtube"]["views_total"],
                    "Vídeos":        ap["youtube"].get("videos",0),
                    "Média Views/Vídeo": ap["youtube"]["media_views_video"],
                    "Views/Inscrito": fmt(int(mp["views_por_inscrito_yt"])),
                },
                "🎧 Spotify": {
                    "Seguidores":      ap["spotify"]["seguidores"],
                    "Ouvintes Mensais": ap["spotify"]["ouvintes_mensais"],
                    "Popularidade":    ap["spotify"]["popularidade"],
                },
                "🔴 Deezer": {
                    "Fans":   ap.get("deezer",{}).get("fans",0),
                    "Álbuns": ap.get("deezer",{}).get("albuns",0),
                },
                "🍎 Apple Music": {
                    "Ouvintes Mensais": ap.get("apple_music",{}).get("ouvintes_mensais",0),
                },
                "🎶 YouTube Music": {
                    "Streams Mensais": ap.get("youtube_music",{}).get("streams_mensais",0),
                },
                "📦 Amazon Music": {
                    "Streams Mensais": ap.get("amazon_music",{}).get("streams_mensais",0),
                },
                "☁️ SoundCloud": {
                    "Total de Plays":  ap.get("soundcloud",{}).get("plays",0),
                    "Seguidores":      ap.get("soundcloud",{}).get("seguidores",0),
                },
            }

            for plat_nome, plat_data in plataformas_detail.items():
                with st.expander(plat_nome, expanded=(plat_nome in ["📸 Instagram","🎵 TikTok","▶️ YouTube"])):
                    rows_plat = []
                    for k, v in plat_data.items():
                        display_v = v if isinstance(v, str) else fmt(v)
                        rows_plat.append({"Métrica": k, "Valor": display_v})
                    st.dataframe(pd.DataFrame(rows_plat).set_index("Métrica"),
                                 use_container_width=True, hide_index=False)

        # Posição relativa nos rankings
        st.markdown("---")
        st.markdown("#### 🏅 Posição nos Rankings (entre os artistas selecionados)")

        rank_metricas = {
            "Instagram — Seguidores":     lambda a: a["instagram"]["seguidores"],
            "Instagram — Engajamento (%)": lambda a: (a["instagram"]["media_curtidas"]+a["instagram"]["media_comentarios"])
                                                     / a["instagram"]["seguidores"]*100 if a["instagram"]["seguidores"] else 0,
            "TikTok — Seguidores":        lambda a: a["tiktok"]["seguidores"],
            "TikTok — Média Views":       lambda a: a["tiktok"]["media_views"],
            "YouTube — Inscritos":        lambda a: a["youtube"]["inscritos"],
            "YouTube — Views Totais":     lambda a: a["youtube"]["views_total"],
            "Spotify — Ouvintes Mensais": lambda a: a["spotify"]["ouvintes_mensais"],
            "Score Digital":              lambda a: calc_metrics(a)["score_digital"],
            "Shows 2026":                 lambda a: a.get("shows_2026",0),
        }
        rank_pos_rows = []
        for met_name, fn in rank_metricas.items():
            ordered = sorted(artistas_sel.keys(), key=lambda n: fn(artistas_sel[n]), reverse=True)
            pos = ordered.index(artista_perfil) + 1 if artista_perfil in ordered else len(ordered)
            total = len(ordered)
            medal_r = MEDAL.get(pos-1, f"#{pos}")
            valor_atual = fn(ap) if not isinstance(fn(ap), float) or fn(ap) >= 1 else fn(ap)
            if met_name == "Instagram — Engajamento (%)" or met_name == "Score Digital":
                val_str = f"{valor_atual:.2f}"
            else:
                val_str = fmt(int(valor_atual))
            rank_pos_rows.append({
                "Métrica": met_name,
                "Posição": f"{medal_r} {pos}º de {total}",
                "Valor": val_str,
            })
        st.dataframe(pd.DataFrame(rank_pos_rows).set_index("Métrica"),
                     use_container_width=True)

        # Agenda 2026
        agenda_txt = ap.get("cache_shows_2026","")
        if agenda_txt:
            st.markdown("---")
            st.markdown("#### 🗓️ Agenda / Turnê 2026")
            st.info(f"**{artista_perfil}** — {agenda_txt}")

# ─────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<p style='color:#555;font-size:.8rem;text-align:center'>
Joelma Analytics v2.0 · Dados verificados Jun/2026 · ✅ = 100% verificado · ~ = estimado ·
Desenvolvido por Camila Yasmin
</p>
""", unsafe_allow_html=True)
