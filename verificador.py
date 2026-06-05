#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   🎤  JOELMA DIGITAL STRATEGY TOOL — v3.0                   ║
║   5 Plataformas em Tempo Real                               ║
║   Spotify · Deezer · YouTube · Instagram · TikTok           ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys, json, re, time, argparse
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("❌  pip install -r requirements.txt"); sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH = True
    console = Console()
except ImportError:
    RICH = False

# ═══════════════════════════════════════════════════════════════
#  ARTISTAS — 5 PLATAFORMAS
# ═══════════════════════════════════════════════════════════════

ARTISTAS = [
    {
        "nome": "🎤 JOELMA", "destaque": True, "grupo": "joelma",
        "ids": {
            "spotify":   "1zBQcVejUqu9ujTXTgMQyM",
            "deezer":    "266598",
            "youtube":   "UClPOJqFbYMKGyM2Nqst0NxA",
            "instagram": "joelmaareal",
            "tiktok":    ["joelmaareal"],
        },
        "base": {
            "spotify": 713_506, "deezer": 196_375,
            "youtube": 1_790_000, "instagram": 5_864_066, "tiktok": 2_900_000,
        },
    },
    {
        "nome": "🤠 Wesley Safadão", "destaque": False, "grupo": "nacional",
        "ids": {
            "spotify":   "1AL2GKpmRrKXkYIcASuRFa",
            "deezer":    "4611283",
            "youtube":   "UCciJLMuECsXuOyhA4FO48Sg",
            "instagram": "wesleysafadao",
            "tiktok":    ["wesleysafadao"],
        },
        "base": {
            "spotify": 9_813_112, "deezer": 4_972_139,
            "youtube": 12_000_000, "instagram": 39_963_840, "tiktok": 6_200_000,
        },
    },
    {
        "nome": "👑 Simone Mendes", "destaque": False, "grupo": "nacional",
        "ids": {
            "spotify":   "2eK9gcJQ6uqVvJL63dnOM3",
            "deezer":    "73171372",
            "youtube":   "UCH7vP1JyEwTy-D-ikZUoCww",
            "instagram": "simonemendes",
            "tiktok":    ["simoneses"],
        },
        "base": {
            "spotify": 12_720_687, "deezer": 1_034_457,
            "youtube": 4_730_000, "instagram": 40_058_739, "tiktok": 17_600_000,
        },
    },
    {
        "nome": "✈️  Xand Avião", "destaque": False, "grupo": "nacional",
        "ids": {
            "spotify":   "43DRDu6nLSeIedZ7T1A616",
            "deezer":    "5832280",
            "youtube":   "",
            "instagram": "xandaviao",
            "tiktok":    ["xandaviao"],
        },
        "base": {
            "spotify": 7_198_010, "deezer": 2_320_967,
            "youtube": 0, "instagram": 10_075_704, "tiktok": 1_100_000,
        },
    },
    {
        "nome": "☀️  Solange Almeida", "destaque": False, "grupo": "nacional",
        "ids": {
            "spotify":   "3Hew3AuvrbKxCbehT4Rorq",
            "deezer":    "9910102",
            "youtube":   "",
            "instagram": "solangealmeida",
            "tiktok":    ["solangealmeidaoficial"],
        },
        "base": {
            "spotify": 1_507_526, "deezer": 537_544,
            "youtube": 0, "instagram": 9_129_987, "tiktok": 1_700_000,
        },
    },
    {
        "nome": "🌾 Ana Castela", "destaque": False, "grupo": "nacional",
        "ids": {
            "spotify":   "2CKOmarVWvWqkNWUatHCex",
            "deezer":    "123053672",
            "youtube":   "UCRD1ypvmK7e_05Rtu9zHOfQ",
            "instagram": "anacastelacantora",
            "tiktok":    ["anacastelacantora"],
        },
        "base": {
            "spotify": 12_647_334, "deezer": 1_338_072,
            "youtube": 8_000_000, "instagram": 23_600_000, "tiktok": 16_700_000,
        },
    },
    # ── CANTORAS PARAENSES ────────────────────────────────────
    {
        "nome": "🎶 Manu Bahtidão", "destaque": False, "grupo": "paraense",
        "ids": {
            "spotify":   "0CdnnCbbKD4oIzBmxi2o7r",
            "deezer":    "119396922",
            "youtube":   "UCTa_X-4mmje4Tk0lig9t4Mw",
            "instagram": "manuoficial",
            "tiktok":    ["manuoficial"],
        },
        "base": {
            "spotify": 3_279_663, "deezer": 177_258,
            "youtube": 2_500_000, "instagram": 5_000_000, "tiktok": 3_500_000,
        },
    },
    {
        "nome": "🌺 Fafá de Belém", "destaque": False, "grupo": "paraense",
        "ids": {
            "spotify":   "6n45wsxj6sDedgwEyTza6d",
            "deezer":    "95771",
            "youtube":   "",
            "instagram": "fafadbelem",
            "tiktok":    [],
        },
        "base": {
            "spotify": 1_156_551, "deezer": 65_926,
            "youtube": 0, "instagram": 1_000_000, "tiktok": 0,
        },
    },
    {
        "nome": "💎 Gaby Amarantos", "destaque": False, "grupo": "paraense",
        "ids": {
            "spotify":   "5kn7l4yaJxtNhj583LmL9L",
            "deezer":    "1233002",
            "youtube":   "",
            "instagram": "gabyamarantos",
            "tiktok":    ["gabyamarantos"],
        },
        "base": {
            "spotify": 448_607, "deezer": 179_865,
            "youtube": 0, "instagram": 1_000_000, "tiktok": 295_000,
        },
    },
    {
        "nome": "🎵 Viviane Batidão", "destaque": False, "grupo": "paraense",
        "ids": {
            "spotify":   "1p2aDZsmPNSKQynqjXN7Hj",
            "deezer":    "7968118",
            "youtube":   "",
            "instagram": "vivianebatidaoficial",
            "tiktok":    ["vivianebatidaooficial"],
        },
        "base": {
            "spotify": 388_662, "deezer": 24_990,
            "youtube": 0, "instagram": 1_000_000, "tiktok": 500_000,
        },
    },
    {
        "nome": "⭐ Zaynara", "destaque": False, "grupo": "paraense",
        "ids": {
            "spotify":   "3g5sxvKldw7Kss4e5FPSXb",
            "deezer":    "123326172",
            "youtube":   "",
            "instagram": "zaynaraa",
            "tiktok":    ["zaynara"],
        },
        "base": {
            "spotify": 175_863, "deezer": 2_897,
            "youtube": 0, "instagram": 478_000, "tiktok": 304_000,
        },
    },
]

HISTORICO_FILE = Path(__file__).parent / "historico_metricas.json"

# ═══════════════════════════════════════════════════════════════
#  HTTP SESSION
# ═══════════════════════════════════════════════════════════════

def _sessao():
    s = requests.Session()
    r = Retry(total=2, backoff_factor=0.3,
              status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    })
    return s

SESSION = _sessao()

# ═══════════════════════════════════════════════════════════════
#  COLETORES
# ═══════════════════════════════════════════════════════════════

# ── SPOTIFY ──────────────────────────────────────────────────
def coletar_spotify(artist_id):
    if not artist_id: return None, False
    try:
        r = SESSION.get(
            f"https://open.spotify.com/artist/{artist_id}",
            headers={"Accept": "text/html"}, timeout=12)
        if r.status_code != 200: return None, False
        html = r.text
        m = re.search(r'([\d,]+)\s+monthly\s+listeners', html, re.I)
        if m:
            n = int(m.group(1).replace(",", ""))
            if n > 1000: return n, True
        m = re.search(r'([\d.]+)\s+ouvintes\s+mensais', html, re.I)
        if m:
            n = int(m.group(1).replace(".", ""))
            if n > 1000: return n, True
        for k in ["monthlyListeners", "monthly_listeners"]:
            m = re.search(rf'"{k}"\s*:\s*(\d+)', html)
            if m:
                n = int(m.group(1))
                if n > 1000: return n, True
    except Exception: pass
    return None, False

# ── DEEZER (API pública, sem auth) ────────────────────────────
def coletar_deezer(deezer_id):
    if not deezer_id: return None, False
    try:
        r = SESSION.get(
            f"https://api.deezer.com/artist/{deezer_id}",
            timeout=10)
        if r.status_code == 200:
            d = r.json()
            n = d.get("nb_fan")
            if n and int(n) >= 0:
                return int(n), True
    except Exception: pass
    return None, False

# ── YOUTUBE ───────────────────────────────────────────────────
def coletar_youtube(channel_id):
    if not channel_id: return None, False
    # Método 1: Scraping da página do canal
    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        r = SESSION.get(url, headers={"Accept": "text/html"}, timeout=12)
        if r.status_code == 200:
            html = r.text
            for pat in [
                r'"subscriberCountText".*?"simpleText"\s*:\s*"([\d,.KM ]+)"',
                r'"(\d+)\s+inscritos"',
                r'"(\d+)\s+subscribers"',
                r'subscriberCount["\s:]+(\d+)',
                r'"channelMetadataRenderer".*?"subscriberCount"\s*:\s*"(\d+)"',
            ]:
                m = re.search(pat, html, re.S | re.I)
                if m:
                    raw = m.group(1).replace(",", "").replace(".", "").strip()
                    if raw.isdigit() and int(raw) > 1000:
                        return int(raw), True
    except Exception: pass

    # Método 2: youtubers.me
    try:
        r = SESSION.get(
            f"https://us.youtubers.me/channel/{channel_id}/youtube-statistics",
            timeout=10)
        if r.status_code == 200:
            m = re.search(r'"subscribers"\s*:\s*"?([\d,]+)"?', r.text, re.I)
            if m:
                n = int(m.group(1).replace(",", ""))
                if n > 1000: return n, True
    except Exception: pass

    return None, False

# ── INSTAGRAM ─────────────────────────────────────────────────
def coletar_instagram(username):
    if not username: return None, False
    try:
        r = SESSION.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers={
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/",
            }, timeout=10)
        if r.status_code == 200:
            d = r.json()
            n = (d.get("data", {}).get("user", {})
                  .get("edge_followed_by", {}).get("count"))
            if n and int(n) > 1000: return int(n), True
    except Exception: pass
    try:
        r = SESSION.get(
            f"https://www.instagram.com/{username}/",
            headers={"Accept": "text/html"}, timeout=12)
        if r.status_code == 200:
            for pat in [
                r'"edge_followed_by".*?"count"\s*:\s*(\d+)',
                r'"follower_count"\s*:\s*(\d+)',
            ]:
                m = re.search(pat, r.text, re.DOTALL)
                if m:
                    n = int(m.group(1))
                    if n > 1000: return n, True
    except Exception: pass
    return None, False

# ── TIKTOK ────────────────────────────────────────────────────
def coletar_tiktok(handles):
    if not handles: return None, False, ""
    for h in handles:
        try:
            r = SESSION.get(
                f"https://www.tiktok.com/@{h}",
                headers={"Accept": "text/html", "Referer": "https://www.google.com/"},
                timeout=12)
            if r.status_code == 200:
                for pat in [r'"followerCount"\s*:\s*(\d+)',
                             r'"fans"\s*:\s*(\d+)',
                             r'"followersCount"\s*:\s*(\d+)']:
                    m = re.search(pat, r.text)
                    if m:
                        n = int(m.group(1))
                        if n > 100: return n, True, f"@{h}"
        except Exception: pass
        time.sleep(0.2)
    return None, False, f"@{handles[0]}"

# ═══════════════════════════════════════════════════════════════
#  COLETA COMPLETA
# ═══════════════════════════════════════════════════════════════

def coletar_artista(art):
    ids = art["ids"]
    base = art["base"]

    sp_v, sp_l = coletar_spotify(ids["spotify"])
    dz_v, dz_l = coletar_deezer(ids["deezer"])
    yt_v, yt_l = coletar_youtube(ids["youtube"])
    ig_v, ig_l = coletar_instagram(ids["instagram"])
    tt_v, tt_l, tt_h = coletar_tiktok(ids["tiktok"])

    return {
        "nome":     art["nome"],
        "destaque": art["destaque"],
        "grupo":    art.get("grupo", ""),
        "spotify":   {"val": sp_v or base["spotify"],  "live": sp_l},
        "deezer":    {"val": dz_v if dz_l else base["deezer"], "live": dz_l},
        "youtube":   {"val": yt_v or base["youtube"],  "live": yt_l},
        "instagram": {"val": ig_v or base["instagram"],"live": ig_l},
        "tiktok":    {"val": tt_v or base["tiktok"],   "live": tt_l, "handle": tt_h},
        "ts": datetime.now().isoformat(),
    }

# ═══════════════════════════════════════════════════════════════
#  FORMATAÇÃO
# ═══════════════════════════════════════════════════════════════

def fmt(n, exato=False):
    if not n and n != 0: return "—"
    n = int(n)
    if exato: return f"{n:,}".replace(",", ".")
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)

def tag(live): return "🟢" if live else "⬜"

# ═══════════════════════════════════════════════════════════════
#  DISPLAY
# ═══════════════════════════════════════════════════════════════

def exibir(resultados):
    if not RICH:
        print(f"\n{'='*90}")
        print(f"🎤 JOELMA DIGITAL STRATEGY — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*90}")
        print(f"{'Artista':<22} {'Spotify':>9} {'Deezer':>8} {'YouTube':>9} {'Instagram':>12} {'TikTok':>9}")
        print("-"*75)
        for r in resultados:
            print(f"{r['nome']:<22} "
                  f"{tag(r['spotify']['live'])}{fmt(r['spotify']['val']):>8} "
                  f"{tag(r['deezer']['live'])}{fmt(r['deezer']['val']):>7} "
                  f"{tag(r['youtube']['live'])}{fmt(r['youtube']['val']):>8} "
                  f"{tag(r['instagram']['live'])}{fmt(r['instagram']['val']):>11} "
                  f"{tag(r['tiktok']['live'])}{fmt(r['tiktok']['val']):>8}")
        print(f"\n🟢 ao vivo  ⬜ base (Jun/2026)")
        return

    console.rule("[bold yellow]🎤  JOELMA DIGITAL STRATEGY — 5 PLATAFORMAS[/bold yellow]")
    console.print(
        f"[dim]{datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} "
        "| Spotify · Deezer · YouTube · Instagram · TikTok[/dim]\n"
    )

    # ── Tabela principal ──────────────────────────────────────
    t = Table(
        box=box.DOUBLE_EDGE,
        header_style="bold white on navy_blue",
        border_style="bright_blue",
        expand=True, show_lines=True, padding=(0, 1),
    )
    t.add_column("Artista",            min_width=18, style="bold")
    t.add_column("🟣 Spotify\nOuv/mês",  justify="right", min_width=13)
    t.add_column("🎵 Deezer\nFãs",       justify="right", min_width=10)
    t.add_column("▶️  YouTube\nInscritos",justify="right", min_width=11)
    t.add_column("📸 Instagram\nSeguid.", justify="right", min_width=13)
    t.add_column("TikTok\nSeguid.",       justify="right", min_width=10)
    t.add_column("📡", justify="center", min_width=16)

    for r in resultados:
        lv = lambda k: "bold green" if r[k]["live"] else "white"
        c_sp = f"[{lv('spotify')}]{fmt(r['spotify']['val'])}[/]"
        c_dz = f"[{lv('deezer')}]{fmt(r['deezer']['val'])}[/]"
        c_yt = f"[{lv('youtube')}]{fmt(r['youtube']['val']) if r['youtube']['val'] else '—'}[/]"
        c_ig = f"[{lv('instagram')}]{fmt(r['instagram']['val'])}[/]"
        c_tt = f"[{lv('tiktok')}]{fmt(r['tiktok']['val'])}[/]"

        status = (
            f"{tag(r['spotify']['live'])}SP "
            f"{tag(r['deezer']['live'])}DZ "
            f"{tag(r['youtube']['live'])}YT "
            f"{tag(r['instagram']['live'])}IG "
            f"{tag(r['tiktok']['live'])}TT"
        )

        pfx = "⭐ " if r["destaque"] else "   "
        t.add_row(
            f"{pfx}{r['nome']}",
            c_sp, c_dz, c_yt, c_ig, c_tt, status,
            style="on grey11" if r["destaque"] else "",
        )

    console.print(t)

    # ── Tabela exatos ─────────────────────────────────────────
    console.print("\n[bold]📊 NÚMEROS EXATOS[/bold]")
    e = Table(box=box.SIMPLE_HEAD, header_style="bold dim", expand=True)
    e.add_column("Artista")
    e.add_column("Spotify Mensal", justify="right")
    e.add_column("Deezer Fãs",     justify="right")
    e.add_column("YouTube",        justify="right")
    e.add_column("Instagram",      justify="right")
    e.add_column("TikTok",         justify="right")

    for r in resultados:
        yt_fmt = fmt(r["youtube"]["val"], True) if r["youtube"]["val"] else "—"
        e.add_row(
            r["nome"],
            f"[green]{fmt(r['spotify']['val'], True)}[/]",
            f"[cyan]{fmt(r['deezer']['val'], True)}[/]",
            f"[red]{yt_fmt}[/]",
            f"[magenta]{fmt(r['instagram']['val'], True)}[/]",
            f"[bright_blue]{fmt(r['tiktok']['val'], True)}[/]",
        )

    console.print(e)
    console.print("\n[dim]🟢 ao vivo  ⬜ base verificado (Jun/2026)[/dim]")

    # ── Análise estratégica ───────────────────────────────────
    console.print("\n[bold yellow]⚡ ANÁLISE ESTRATÉGICA — Joelma vs Campo[/bold yellow]")
    joelma = next((r for r in resultados if "JOELMA" in r["nome"]), None)
    if joelma:
        a = Table(box=box.SIMPLE, expand=True)
        a.add_column("Plataforma")
        a.add_column("Joelma",    justify="right")
        a.add_column("Líder",     justify="right")
        a.add_column("Artista líder")
        a.add_column("Gap")
        a.add_column("Posição de Joelma")

        plats = [
            ("🟣 Spotify",   "spotify"),
            ("🎵 Deezer",    "deezer"),
            ("▶️  YouTube",  "youtube"),
            ("📸 Instagram", "instagram"),
            ("🎵 TikTok",    "tiktok"),
        ]

        for label, plat in plats:
            j_val = joelma[plat]["val"] or 0
            vals  = [(r["nome"], r[plat]["val"] or 0)
                     for r in resultados if r[plat]["val"]]
            if not vals: continue
            vals.sort(key=lambda x: x[1], reverse=True)
            lider_nome, lider_val = vals[0]
            posicao = next((i+1 for i, (n,v) in enumerate(vals) if "JOELMA" in n), "—")
            gap = lider_val - j_val

            gap_txt = f"[red]-{fmt(gap)}[/red]" if gap > 0 else "[green]LIDERA[/green]"
            pos_txt = (f"[green]{posicao}ª[/green]" if posicao == 1
                       else f"[yellow]{posicao}ª de {len(vals)}[/yellow]")

            a.add_row(
                label,
                f"[bold]{fmt(j_val)}[/bold]",
                fmt(lider_val),
                lider_nome.replace("🎤 ", "").replace("👑 ", "").replace("🤠 ", ""),
                gap_txt,
                pos_txt,
            )
        console.print(a)

# ═══════════════════════════════════════════════════════════════
#  HISTÓRICO
# ═══════════════════════════════════════════════════════════════

def salvar(resultados):
    hist = []
    if HISTORICO_FILE.exists():
        try: hist = json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
        except: pass
    hist.append({
        "timestamp": datetime.now().isoformat(),
        "dados": {
            r["nome"]: {
                p: r[p]["val"]
                for p in ("spotify","deezer","youtube","instagram","tiktok")
            }
            for r in resultados
        }
    })
    HISTORICO_FILE.write_text(
        json.dumps(hist[-1000:], ensure_ascii=False, indent=2), encoding="utf-8"
    )

def mostrar_historico():
    if not HISTORICO_FILE.exists():
        print("Nenhum histórico. Execute o verificador primeiro.")
        return
    hist = json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
    if RICH:
        console.rule("[bold]📅 HISTÓRICO[/bold]")
        t = Table(box=box.SIMPLE_HEAD, expand=True)
        t.add_column("Data/Hora")
        for plat in ("Spotify","Deezer","YouTube","Instagram","TikTok"):
            t.add_column(f"Joelma\n{plat}", justify="right")
        for entry in hist[-20:]:
            ts = entry["timestamp"][:16].replace("T"," ")
            j  = entry["dados"].get("🎤 JOELMA", {})
            t.add_row(
                ts,
                fmt(j.get("spotify"), True),
                fmt(j.get("deezer"), True),
                fmt(j.get("youtube"), True) if j.get("youtube") else "—",
                fmt(j.get("instagram"), True),
                fmt(j.get("tiktok"), True),
            )
        console.print(t)

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Joelma Digital — 5 Plataformas")
    parser.add_argument("--historico", action="store_true")
    parser.add_argument("--grupo",     help="joelma | nacional | paraense")
    parser.add_argument("--artista",   help='Nome parcial do artista')
    args = parser.parse_args()

    if args.historico:
        mostrar_historico(); return

    artistas = ARTISTAS
    if args.grupo:
        artistas = [a for a in ARTISTAS if a.get("grupo","") == args.grupo]
    if args.artista:
        artistas = [a for a in ARTISTAS
                    if args.artista.lower() in a["nome"].lower()]

    if RICH:
        console.print(Panel.fit(
            "[bold yellow]🎤  JOELMA DIGITAL STRATEGY — v3.0[/bold yellow]\n"
            "[dim]Spotify · Deezer · YouTube · Instagram · TikTok[/dim]",
            border_style="yellow",
        ))

    resultados = []
    for art in artistas:
        if RICH:
            console.print(f"[dim]→ {art['nome']}...[/dim]")
        else:
            print(f"→ {art['nome']}...")
        resultados.append(coletar_artista(art))
        time.sleep(0.6)

    exibir(resultados)
    salvar(resultados)

    if RICH:
        console.print(
            f"\n[dim]💾 Histórico: {HISTORICO_FILE}[/dim]\n"
            f"[dim]🕐 {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}[/dim]"
        )

if __name__ == "__main__":
    main()
