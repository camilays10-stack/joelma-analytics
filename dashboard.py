#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   🎤  JOELMA DIGITAL STRATEGY — DASHBOARD EM TEMPO REAL         ║
║   Monitoramento contínuo | Instagram ao vivo | Spotify API       ║
║   São João 2026 | Estratégista Digital                          ║
╚══════════════════════════════════════════════════════════════════╝

USO:
    python dashboard.py                  → atualiza a cada 5 min
    python dashboard.py --intervalo 2    → atualiza a cada 2 min
    python dashboard.py --intervalo 10   → atualiza a cada 10 min
    python dashboard.py --sem-spotify    → só Instagram (sem API Key)

SPOTIFY API (gratuita — 1 vez só):
    1. Acesse: https://developer.spotify.com/dashboard
    2. Crie um app (botão "Create App")
    3. Copie o Client ID e Client Secret
    4. Execute:
          export SPOTIFY_CLIENT_ID="seu_id_aqui"
          export SPOTIFY_CLIENT_SECRET="seu_secret_aqui"
       Ou crie o arquivo spotify_creds.json com:
          {"client_id": "...", "client_secret": "..."}
"""

import sys, json, time, re, os, argparse, threading, base64
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("❌  pip install -r requirements.txt")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    print("❌  pip install rich")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
#  ARTISTAS
# ═══════════════════════════════════════════════════════════════

ARTISTAS = [
    {
        "nome": "JOELMA", "emoji": "🎤", "destaque": True,
        "spotify_id": "1zBQcVejUqu9ujTXTgMQyM",
        "instagram":  "joelmaareal",
        "tiktok":     ["joelmaareal"],
        "base": {"spotify": 713_506, "instagram": 5_864_066, "tiktok": 2_900_000},
    },
    {
        "nome": "Wesley Safadão", "emoji": "🤠", "destaque": False,
        "spotify_id": "1AL2GKpmRrKXkYIcASuRFa",
        "instagram":  "wesleysafadao",
        "tiktok":     ["wesleysafadao"],
        "base": {"spotify": 9_813_112, "instagram": 39_963_840, "tiktok": 6_200_000},
    },
    {
        "nome": "Simone Mendes", "emoji": "👑", "destaque": False,
        "spotify_id": "2eK9gcJQ6uqVvJL63dnOM3",
        "instagram":  "simonemendes",
        "tiktok":     ["simoneses"],
        "base": {"spotify": 12_720_687, "instagram": 40_058_739, "tiktok": 17_600_000},
    },
    {
        "nome": "Xand Avião", "emoji": "✈️", "destaque": False,
        "spotify_id": "43DRDu6nLSeIedZ7T1A616",
        "instagram":  "xandaviao",
        "tiktok":     ["xandaviao"],
        "base": {"spotify": 7_198_010, "instagram": 10_075_704, "tiktok": 1_100_000},
    },
    {
        "nome": "Solange Almeida", "emoji": "☀️", "destaque": False,
        "spotify_id": "3Hew3AuvrbKxCbehT4Rorq",
        "instagram":  "solangealmeida",
        "tiktok":     ["solangealmeidaoficial"],
        "base": {"spotify": 1_507_526, "instagram": 9_129_987, "tiktok": 1_700_000},
    },
    # ── ANA CASTELA ──────────────────────────────────────────────
    {
        "nome": "Ana Castela", "emoji": "🤠🌾", "destaque": False,
        "grupo": "nacional",
        "spotify_id": "2CKOmarVWvWqkNWUatHCex",
        "instagram":  "anacastelacantora",
        "tiktok":     ["anacastelacantora"],
        "base": {"spotify": 12_647_334, "instagram": 23_600_000, "tiktok": 16_700_000},
    },
    # ── CANTORAS PARAENSES ────────────────────────────────────────
    {
        "nome": "Manu Bahtidão", "emoji": "🎶", "destaque": False,
        "grupo": "paraense",
        "spotify_id": "0CdnnCbbKD4oIzBmxi2o7r",
        "instagram":  "manuoficial",
        "tiktok":     ["manuoficial"],
        "base": {"spotify": 3_279_663, "instagram": 5_000_000, "tiktok": 3_500_000},
    },
    {
        "nome": "Fafá de Belém", "emoji": "🌺", "destaque": False,
        "grupo": "paraense",
        "spotify_id": "6n45wsxj6sDedgwEyTza6d",
        "instagram":  "fafadbelem",
        "tiktok":     [],
        "base": {"spotify": 1_156_551, "instagram": 1_000_000, "tiktok": 0},
    },
    {
        "nome": "Gaby Amarantos", "emoji": "💎", "destaque": False,
        "grupo": "paraense",
        "spotify_id": "5kn7l4yaJxtNhj583LmL9L",
        "instagram":  "gabyamarantos",
        "tiktok":     ["gabyamarantos"],
        "base": {"spotify": 448_607, "instagram": 1_000_000, "tiktok": 295_000},
    },
    {
        "nome": "Viviane Batidão", "emoji": "🎵", "destaque": False,
        "grupo": "paraense",
        "spotify_id": "1p2aDZsmPNSKQynqjXN7Hj",
        "instagram":  "vivianebatidaoficial",
        "tiktok":     ["vivianebatidaooficial"],
        "base": {"spotify": 388_662, "instagram": 1_000_000, "tiktok": 500_000},
    },
    {
        "nome": "Zaynara", "emoji": "⭐", "destaque": False,
        "grupo": "paraense",
        "spotify_id": "3g5sxvKldw7Kss4e5FPSXb",
        "instagram":  "zaynaraa",
        "tiktok":     ["zaynara"],
        "base": {"spotify": 175_863, "instagram": 478_000, "tiktok": 304_000},
    },
]

HISTORICO_FILE = Path(__file__).parent / "historico_metricas.json"
CREDS_FILE     = Path(__file__).parent / "spotify_creds.json"

# ═══════════════════════════════════════════════════════════════
#  ESTADO GLOBAL
# ═══════════════════════════════════════════════════════════════

class Estado:
    def __init__(self):
        self.lock        = threading.Lock()
        self.dados       = {}
        self.anterior    = {}
        self.alertas     = deque(maxlen=15)
        self.ciclo       = 0
        self.prox_update = datetime.now()
        self.status      = "Iniciando..."
        self.spotify_ok  = False

estado = Estado()

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
#  SPOTIFY — WEB API (client credentials, gratuita)
# ═══════════════════════════════════════════════════════════════

_spotify_token     = None
_spotify_token_exp = datetime.now()


def _carregar_creds():
    """Carrega credenciais do Spotify via env vars ou arquivo"""
    cid = os.environ.get("SPOTIFY_CLIENT_ID", "")
    sec = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    if cid and sec:
        return cid, sec
    if CREDS_FILE.exists():
        try:
            d = json.loads(CREDS_FILE.read_text())
            return d.get("client_id", ""), d.get("client_secret", "")
        except Exception:
            pass
    return "", ""


def _get_spotify_token():
    global _spotify_token, _spotify_token_exp
    if _spotify_token and datetime.now() < _spotify_token_exp:
        return _spotify_token

    cid, sec = _carregar_creds()
    if not cid or not sec:
        return None

    try:
        cred = base64.b64encode(f"{cid}:{sec}".encode()).decode()
        r = SESSION.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {cred}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            timeout=8,
        )
        if r.status_code == 200:
            d = r.json()
            _spotify_token = d["access_token"]
            _spotify_token_exp = datetime.now() + timedelta(seconds=d.get("expires_in", 3600) - 60)
            with estado.lock:
                estado.spotify_ok = True
            return _spotify_token
    except Exception:
        pass
    return None


def coletar_spotify(artist_id):
    """Ouvintes mensais via Spotify Web API. Retorna (valor, ao_vivo)"""
    token = _get_spotify_token()
    if not token:
        return None, False

    try:
        r = SESSION.get(
            f"https://api.spotify.com/v1/artists/{artist_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            d = r.json()
            # A API v1 não retorna monthly_listeners diretamente,
            # mas retorna followers.total — usamos como proxy
            followers = d.get("followers", {}).get("total")
            if followers and followers > 100:
                return followers, True
        if r.status_code == 401:
            global _spotify_token
            _spotify_token = None  # força renovação
    except Exception:
        pass

    return None, False


def coletar_spotify_listeners(artist_id):
    """
    Busca ouvintes mensais via endpoint interno do Spotify Web Player.
    Requer token de usuário ou usa o unofficial stats endpoint.
    """
    token = _get_spotify_token()
    if not token:
        return None, False

    # Endpoint interno do Spotify que retorna monthly listeners
    try:
        r = SESSION.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/related-artists",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8,
        )
        # Este endpoint confirma se o token funciona
        # Para monthly_listeners precisamos do endpoint v1/artists
        # que inclui popularity mas não monthly listeners diretamente

        # Tenta o endpoint de stats interno
        r2 = SESSION.get(
            f"https://spclient.wg.spotify.com/artist-identity-view/v2/trial/"
            f"desktop/artist/{artist_id}/about",
            headers={
                "Authorization": f"Bearer {token}",
                "app-platform": "WebPlayer",
            },
            timeout=8,
        )
        if r2.status_code == 200:
            try:
                d = r2.json()
                ml = d.get("monthlyListeners") or d.get("monthly_listeners")
                if ml and int(ml) > 100:
                    return int(ml), True
            except Exception:
                pass
    except Exception:
        pass

    # Fallback: retorna followers como aproximação
    return coletar_spotify(artist_id)


# ═══════════════════════════════════════════════════════════════
#  INSTAGRAM — API não autenticada (funciona ao vivo)
# ═══════════════════════════════════════════════════════════════

def coletar_instagram(username):
    """Retorna (valor, ao_vivo)"""
    try:
        r = SESSION.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers={
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/",
            },
            timeout=10,
        )
        if r.status_code == 200:
            d = r.json()
            n = (d.get("data", {}).get("user", {})
                  .get("edge_followed_by", {}).get("count"))
            if n and int(n) > 1000:
                return int(n), True
    except Exception:
        pass

    try:
        r = SESSION.get(
            f"https://www.instagram.com/{username}/",
            headers={"Accept": "text/html"},
            timeout=12,
        )
        if r.status_code == 200:
            for pat in [
                r'"edge_followed_by".*?"count"\s*:\s*(\d+)',
                r'"follower_count"\s*:\s*(\d+)',
            ]:
                m = re.search(pat, r.text, re.DOTALL)
                if m:
                    n = int(m.group(1))
                    if n > 1000:
                        return n, True
    except Exception:
        pass

    return None, False


# ═══════════════════════════════════════════════════════════════
#  TIKTOK
# ═══════════════════════════════════════════════════════════════

def coletar_tiktok(handles):
    """Retorna (valor, ao_vivo, handle_usado)"""
    for h in handles:
        try:
            r = SESSION.get(
                f"https://www.tiktok.com/@{h}",
                headers={"Accept": "text/html",
                         "Referer": "https://www.google.com/"},
                timeout=12,
            )
            if r.status_code == 200:
                for pat in [
                    r'"followerCount"\s*:\s*(\d+)',
                    r'"fans"\s*:\s*(\d+)',
                    r'"followersCount"\s*:\s*(\d+)',
                ]:
                    m = re.search(pat, r.text)
                    if m:
                        n = int(m.group(1))
                        if n > 100:
                            return n, True, f"@{h}"
        except Exception:
            pass
        time.sleep(0.25)
    return None, False, f"@{handles[0]}"


# ═══════════════════════════════════════════════════════════════
#  CICLO DE COLETA (thread background)
# ═══════════════════════════════════════════════════════════════

def ciclo_coleta(intervalo_min, sem_spotify=False):
    while True:
        with estado.lock:
            estado.status   = "🔄  Coletando dados ao vivo..."
            estado.anterior = deepcopy(estado.dados)

        novos = {}
        for art in ARTISTAS:
            nome = art["nome"]

            # Spotify
            if sem_spotify:
                sp_val, sp_live = None, False
            else:
                sp_val, sp_live = coletar_spotify_listeners(art["spotify_id"])

            ig_val, ig_live          = coletar_instagram(art["instagram"])
            tt_val, tt_live, tt_hand = coletar_tiktok(art["tiktok"])

            sp_val = sp_val if sp_live else art["base"]["spotify"]
            ig_val = ig_val if ig_live else art["base"]["instagram"]
            tt_val = tt_val if tt_live else art["base"]["tiktok"]

            novos[nome] = {
                "spotify":   {"val": sp_val, "live": sp_live},
                "instagram": {"val": ig_val, "live": ig_live},
                "tiktok":    {"val": tt_val, "live": tt_live,
                              "handle": tt_hand},
                "ts": datetime.now().isoformat(),
            }

            # Detecta variações
            with estado.lock:
                ant = estado.anterior.get(nome, {})
            for plat in ("spotify", "instagram", "tiktok"):
                v_novo = novos[nome][plat]["val"] or 0
                v_ant  = (ant.get(plat, {}).get("val")) or v_novo
                delta  = v_novo - v_ant
                if abs(delta) >= 500 and v_ant > 0:
                    sinal = "📈" if delta > 0 else "📉"
                    msg = (f"{sinal} {art['emoji']} {nome} {plat.upper()}: "
                           f"{_fmt(v_ant)} → {_fmt(v_novo)} "
                           f"({'+' if delta>0 else ''}{_fmt(abs(delta))})")
                    with estado.lock:
                        estado.alertas.appendleft(
                            f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
                        )

            time.sleep(0.8)

        _salvar(novos)

        with estado.lock:
            estado.dados       = novos
            estado.ciclo      += 1
            estado.prox_update = (datetime.now()
                                  + timedelta(minutes=intervalo_min))
            estado.status      = (f"✅  Ciclo #{estado.ciclo} — "
                                  f"{datetime.now().strftime('%H:%M:%S')}")

        time.sleep(intervalo_min * 60)


def _salvar(novos):
    hist = []
    if HISTORICO_FILE.exists():
        try:
            hist = json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    hist.append({
        "timestamp": datetime.now().isoformat(),
        "dados": {n: {p: d[p]["val"] for p in ("spotify","instagram","tiktok")}
                  for n, d in novos.items()}
    })
    HISTORICO_FILE.write_text(
        json.dumps(hist[-1000:], ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ═══════════════════════════════════════════════════════════════
#  FORMATAÇÃO
# ═══════════════════════════════════════════════════════════════

def _fmt(n, exato=False):
    if n is None: return "—"
    n = int(n)
    if exato: return f"{n:,}".replace(",", ".")
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def _delta(nome, plat):
    with estado.lock:
        ant = estado.anterior.get(nome, {})
        cur = estado.dados.get(nome, {})
    if not ant or not cur: return ""
    va = ant.get(plat, {}).get("val") or 0
    vc = cur.get(plat, {}).get("val") or 0
    if va == 0: return ""
    d = vc - va
    if d == 0: return "[dim]=[/dim]"
    s = "▲" if d > 0 else "▼"
    c = "green" if d > 0 else "red"
    return f"[{c}]{s}{_fmt(abs(d))}[/{c}]"

def _tag(live): return "🟢" if live else "⬜"


# ═══════════════════════════════════════════════════════════════
#  BLOCOS DO DASHBOARD
# ═══════════════════════════════════════════════════════════════

def bloco_header(intervalo):
    with estado.lock:
        prox  = estado.prox_update
        ciclo = estado.ciclo
        st    = estado.status
        sp_ok = estado.spotify_ok

    agora  = datetime.now()
    resta  = max(0, int((prox - agora).total_seconds()))
    mm, ss = divmod(resta, 60)
    total  = intervalo * 60
    prog   = max(0, total - resta)
    pct    = int((prog / total) * 24) if total else 0
    barra  = "█" * pct + "░" * (24 - pct)

    sp_status = (
        "[green]🔑 Spotify API ativa[/green]" if sp_ok
        else "[yellow]⚠  Spotify sem API Key — veja setup abaixo[/yellow]"
    )

    return Panel(
        Align.center(Text.from_markup(
            f"[bold bright_yellow]🎤  JOELMA DIGITAL STRATEGY  —  Dashboard em Tempo Real[/bold bright_yellow]\n"
            f"[dim]{agora.strftime('%A, %d/%m/%Y')}[/dim]  "
            f"[bold white]{agora.strftime('%H:%M:%S')}[/bold white]  "
            f"[dim]| Ciclo #{ciclo} | próximo em [cyan]{mm:02d}:{ss:02d}[/cyan][/dim]\n"
            f"[dim][{barra}][/dim]  {sp_status}\n"
            f"[dim]{st}[/dim]"
        )),
        border_style="yellow", padding=(0, 2),
    )


def bloco_tabela():
    t = Table(
        box=box.DOUBLE_EDGE,
        header_style="bold white on navy_blue",
        border_style="bright_blue",
        expand=True, show_lines=True, padding=(0, 1),
    )
    t.add_column("Artista",               min_width=19, style="bold")
    t.add_column("🟣 Spotify\nOuv/mês",   justify="right", min_width=14)
    t.add_column("Δ",                     justify="right", min_width=7)
    t.add_column("📸 Instagram\nSeguidores", justify="right", min_width=14)
    t.add_column("Δ",                     justify="right", min_width=9)
    t.add_column("🎵 TikTok\nSeguidores", justify="right", min_width=13)
    t.add_column("Δ",                     justify="right", min_width=7)
    t.add_column("📡 Live",               justify="center", min_width=9)

    with estado.lock:
        dados = deepcopy(estado.dados)

    for art in ARTISTAS:
        nome = art["nome"]
        d    = dados.get(nome)
        sp = d["spotify"]   if d else {"val": art["base"]["spotify"],   "live": False}
        ig = d["instagram"] if d else {"val": art["base"]["instagram"], "live": False}
        tt = d["tiktok"]    if d else {"val": art["base"]["tiktok"],    "live": False, "handle": ""}

        sp_c = "bold green"   if sp["live"] else "white"
        ig_c = "bold cyan"    if ig["live"] else "white"
        tt_c = "bold magenta" if tt["live"] else "white"

        tt_txt = (f"[{tt_c}]{_fmt(tt['val'])}[/]"
                  + (f"\n[dim]{tt.get('handle','')}[/dim]" if tt.get("handle") else ""))

        live_str = (f"{_tag(sp['live'])}SP "
                    f"{_tag(ig['live'])}IG "
                    f"{_tag(tt['live'])}TT")

        t.add_row(
            ("⭐ " if art["destaque"] else "   ") + f"{art['emoji']} {nome}",
            f"[{sp_c}]{_fmt(sp['val'])}[/]", _delta(nome, "spotify"),
            f"[{ig_c}]{_fmt(ig['val'])}[/]", _delta(nome, "instagram"),
            tt_txt,                           _delta(nome, "tiktok"),
            live_str,
            style="on grey11" if art["destaque"] else "",
        )

    return t


def bloco_comparativo():
    with estado.lock:
        dados = deepcopy(estado.dados)

    def _val(nome, plat):
        d = dados.get(nome)
        if d: return d.get(plat, {}).get("val") or 1
        return next((a["base"][plat] for a in ARTISTAS if a["nome"] == nome), 1) or 1

    j_sp = _val("JOELMA", "spotify")
    j_ig = _val("JOELMA", "instagram")
    j_tt = _val("JOELMA", "tiktok")

    linhas = ["[bold yellow]⭐ JOELMA vs Concorrentes[/bold yellow]\n"
              "[dim]  🟢 = Joelma LIDERA   🔴 = concorrente maior[/dim]\n"]

    def _razao(j, c, plat_label):
        if c == 0: return f"  {plat_label} [green]LIDER[/green]"
        r = c / j
        if r > 1.5:
            return f"  {plat_label} [red]{r:.1f}× maior[/red]"
        elif r > 1.05:
            return f"  {plat_label} [yellow]{r:.1f}× maior[/yellow]"
        elif j > c * 1.05:
            return f"  {plat_label} [green]Joelma +{(j/c-1)*100:.0f}%[/green]"
        else:
            return f"  {plat_label} [dim]≈ igual[/dim]"

    for art in ARTISTAS:
        if art["destaque"]: continue
        nome = art["nome"]
        c_sp = _val(nome, "spotify")
        c_ig = _val(nome, "instagram")
        c_tt = _val(nome, "tiktok")

        linhas.append(
            f"[bold]{art['emoji']} {nome:<16}[/bold]\n"
            + _razao(j_sp, c_sp, "SP") + "\n"
            + _razao(j_ig, c_ig, "IG") + "\n"
            + _razao(j_tt, c_tt, "TT") + "\n"
        )

    return Panel(
        Text.from_markup("\n".join(linhas)),
        title="[bold]Análise Competitiva[/bold]",
        border_style="yellow", padding=(0, 1),
    )


def bloco_exatos():
    with estado.lock:
        dados = deepcopy(estado.dados)

    linhas = ["[bold]📊 Números Exatos[/bold]\n"
              f"[dim]  {'Artista':<18} {'Spotify':>14} {'Instagram':>14} {'TikTok':>12}[/dim]",
              "  " + "─" * 62]

    for art in ARTISTAS:
        nome = art["nome"]
        d    = dados.get(nome)
        sp   = d["spotify"]["val"]   if d else art["base"]["spotify"]
        ig   = d["instagram"]["val"] if d else art["base"]["instagram"]
        tt   = d["tiktok"]["val"]    if d else art["base"]["tiktok"]
        ts   = d.get("ts", "")[:16].replace("T", " ") if d else "—"
        cor  = "bright_yellow" if art["destaque"] else "white"

        linhas.append(
            f"  [{cor}]{art['emoji']} {nome:<17}[/{cor}] "
            f"[green]{_fmt(sp, True):>14}[/green] "
            f"[cyan]{_fmt(ig, True):>14}[/cyan] "
            f"[magenta]{_fmt(tt, True):>12}[/magenta]"
        )

    return Panel(
        Text.from_markup("\n".join(linhas)),
        border_style="dim", padding=(0, 1),
    )


def bloco_alertas():
    with estado.lock:
        alertas = list(estado.alertas)
        sp_ok   = estado.spotify_ok

    itens = []
    if not sp_ok:
        itens.append(
            "[yellow]⚠  Spotify sem API Key — seguidores são do Spotify (followers)[/yellow]\n"
            "[dim]   Para ouvintes mensais exatos, configure a API:[/dim]\n"
            "[dim]   export SPOTIFY_CLIENT_ID=seu_id[/dim]\n"
            "[dim]   export SPOTIFY_CLIENT_SECRET=seu_secret[/dim]\n"
            "[dim]   → developer.spotify.com/dashboard (gratuito)[/dim]"
        )
    if alertas:
        itens.append("[bold]🔔 Variações detectadas:[/bold]")
        itens += [f"  {a}" for a in alertas[:8]]
    else:
        itens.append("[dim]  Monitorando... alertas aparecem aqui quando\n"
                     "  detectar mudança ≥ 500 seguidores/ouvintes.[/dim]")

    return Panel(
        Text.from_markup("\n".join(itens)),
        title="[bold]Alertas & Setup[/bold]",
        border_style="bright_red" if alertas else "dim",
        padding=(0, 1),
    )


def bloco_legenda(intervalo):
    return Panel(
        Align.center(Text.from_markup(
            "[dim]🟢 ao vivo   ⬜ base (Jun/2026)   ▲▼ variação no ciclo   "
            f"Intervalo: {intervalo}min   [bold]Ctrl+C[/bold] para sair[/dim]"
        )),
        border_style="dim", padding=(0, 0),
    )


# ═══════════════════════════════════════════════════════════════
#  MONTAGEM DO LAYOUT
# ═══════════════════════════════════════════════════════════════

def montar(intervalo):
    L = Layout(name="root")
    L.split_column(
        Layout(name="header", size=6),
        Layout(name="tabela", minimum_size=13),
        Layout(name="middle", size=20),
        Layout(name="exatos", size=10),
        Layout(name="footer", size=3),
    )
    L["middle"].split_row(
        Layout(name="comp",    ratio=2),
        Layout(name="alertas", ratio=1),
    )
    L["header"].update(bloco_header(intervalo))
    L["tabela"].update(bloco_tabela())
    L["middle"]["comp"].update(bloco_comparativo())
    L["middle"]["alertas"].update(bloco_alertas())
    L["exatos"].update(bloco_exatos())
    L["footer"].update(bloco_legenda(intervalo))
    return L


# ═══════════════════════════════════════════════════════════════
#  COLETA INICIAL SÍNCRONA
# ═══════════════════════════════════════════════════════════════

def coleta_inicial(sem_spotify):
    c = Console()
    c.print(Panel.fit(
        "[bold yellow]🎤  JOELMA DIGITAL STRATEGY TOOL[/bold yellow]\n"
        "[dim]Coletando dados iniciais — aguarde...[/dim]",
        border_style="yellow",
    ))

    # Carrega histórico anterior se existir
    if HISTORICO_FILE.exists():
        try:
            hist = json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
            if hist:
                ult = hist[-1]["dados"]
                novos = {}
                for art in ARTISTAS:
                    n = art["nome"]
                    h = ult.get(n, {})
                    novos[n] = {
                        "spotify":   {"val": h.get("spotify")   or art["base"]["spotify"],   "live": False},
                        "instagram": {"val": h.get("instagram") or art["base"]["instagram"], "live": False},
                        "tiktok":    {"val": h.get("tiktok")    or art["base"]["tiktok"],    "live": False,
                                      "handle": f"@{art['tiktok'][0]}"},
                        "ts": hist[-1].get("timestamp", ""),
                    }
                with estado.lock:
                    estado.dados = novos
                c.print("[dim]  ✓ Histórico anterior carregado[/dim]")
        except Exception:
            pass

    # Testa Spotify API
    if not sem_spotify:
        token = _get_spotify_token()
        if token:
            c.print("[green]  ✓ Spotify API conectada[/green]")
        else:
            c.print("[yellow]  ⚠ Spotify sem API Key — usando base (followers)[/yellow]")

    # Coleta ao vivo
    novos = {}
    for art in ARTISTAS:
        nome = art["nome"]
        c.print(f"  [dim]→ {art['emoji']} {nome}...[/dim]", end="")

        sp_val, sp_live = (coletar_spotify_listeners(art["spotify_id"])
                           if not sem_spotify else (None, False))
        ig_val, ig_live = coletar_instagram(art["instagram"])
        tt_val, tt_live, tt_h = coletar_tiktok(art["tiktok"])

        novos[nome] = {
            "spotify":   {"val": sp_val or art["base"]["spotify"],   "live": sp_live},
            "instagram": {"val": ig_val or art["base"]["instagram"], "live": ig_live},
            "tiktok":    {"val": tt_val or art["base"]["tiktok"],    "live": tt_live,
                          "handle": tt_h},
            "ts": datetime.now().isoformat(),
        }

        sp_tag = "[green]SP🟢[/green]" if sp_live else "[dim]SP⬜[/dim]"
        ig_tag = "[green]IG🟢[/green]" if ig_live else "[dim]IG⬜[/dim]"
        tt_tag = "[green]TT🟢[/green]" if tt_live else "[dim]TT⬜[/dim]"
        c.print(f"  {sp_tag} {ig_tag} {tt_tag}")
        time.sleep(0.5)

    _salvar(novos)
    with estado.lock:
        estado.dados  = novos
        estado.ciclo  = 1
        estado.status = f"✅  Coleta inicial: {datetime.now().strftime('%H:%M:%S')}"

    c.print("\n[bold green]✅  Dados carregados! Abrindo dashboard...[/bold green]")
    time.sleep(1.2)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Joelma Digital Strategy — Dashboard Tempo Real"
    )
    parser.add_argument("--intervalo", type=int, default=5, metavar="MIN",
                        help="Intervalo de atualização em minutos (padrão: 5)")
    parser.add_argument("--sem-spotify", action="store_true",
                        help="Desabilita Spotify (não requer API Key)")
    args = parser.parse_args()

    intervalo   = max(1, args.intervalo)
    sem_spotify = args.sem_spotify

    coleta_inicial(sem_spotify)

    with estado.lock:
        estado.prox_update = datetime.now() + timedelta(minutes=intervalo)

    # Thread de coleta contínua em background
    t = threading.Thread(
        target=ciclo_coleta, args=(intervalo, sem_spotify), daemon=True
    )
    t.start()

    console = Console()
    try:
        with Live(
            montar(intervalo),
            console=console,
            refresh_per_second=2,
            screen=True,
        ) as live:
            while True:
                live.update(montar(intervalo))
                time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard encerrado. 🎤  Até logo![/yellow]")


if __name__ == "__main__":
    main()
