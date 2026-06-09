#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   📰  REVISTAS ANALYTICS — Nacional                         ║
║   Comparativo de Mídia Impressa e Digital Brasil            ║
║   Instagram · Facebook · YouTube · TikTok                   ║
╚══════════════════════════════════════════════════════════════╝

COMO CONFIGURAR AS REVISTAS PRINCIPAIS:
  Edite os campos "ids" de "Revista Total"
  com os @handles reais do Instagram, Facebook e TikTok.
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
#  VEÍCULOS — 4 PLATAFORMAS
#  Protagonista: Revista Total
#  Concorrentes: revistas nacionais brasileiras
# ═══════════════════════════════════════════════════════════════

VEICULOS = [
    # ── PROTAGONISTAS ─────────────────────────────────────────
    {
        "nome": "📋 Revista Total",
        "destaque": True,
        "grupo": "principal",
        "ids": {
            "instagram": "revistatotalbrasil",
            "facebook":  "revistatotalbrasil",
            "youtube":   "",
            "tiktok":    [],
        },
        "base": {
            "instagram": 61_000,
            "facebook":  50_000,
            "youtube":   5_000,
            "tiktok":    3_000,
        },
    },
    # ── NACIONAIS — ENTRETENIMENTO/CELEBRIDADES ────────────────
    {
        "nome": "⭐ Caras",
        "destaque": False,
        "grupo": "entretenimento",
        "ids": {
            "instagram": "carasbrasil",
            "facebook":  "carasbrasil",
            "youtube":   "@CARASBrasil",
            "tiktok":    ["carasbrasil"],
        },
        "base": {
            "instagram": 8_000_000,
            "facebook":  3_000_000,
            "youtube":   200_000,
            "tiktok":    500_000,
        },
    },
    {
        "nome": "💬 Contigo",
        "destaque": False,
        "grupo": "entretenimento",
        "ids": {
            "instagram": "tocontigo",
            "facebook":  "contigo",
            "youtube":   "@Contigo",
            "tiktok":    ["contigo"],
        },
        "base": {
            "instagram": 2_000_000,
            "facebook":  1_000_000,
            "youtube":   100_000,
            "tiktok":    200_000,
        },
    },
    # ── NACIONAIS — POLÍTICA/ANÁLISE ───────────────────────────
    {
        "nome": "🗞️  Veja",
        "destaque": False,
        "grupo": "politica",
        "ids": {
            "instagram": "veja",
            "facebook":  "veja",
            "youtube":   "@veja",
            "tiktok":    ["veja"],
        },
        "base": {
            "instagram": 1_000_000,
            "facebook":  8_000_000,
            "youtube":   300_000,
            "tiktok":    100_000,
        },
    },
    {
        "nome": "⚖️  IstoÉ",
        "destaque": False,
        "grupo": "politica",
        "ids": {
            "instagram": "revistaistoe",
            "facebook":  "revistaistoe",
            "youtube":   "@IstoE",
            "tiktok":    ["revistaistoe"],
        },
        "base": {
            "instagram": 1_000_000,
            "facebook":  2_000_000,
            "youtube":   100_000,
            "tiktok":    50_000,
        },
    },
    {
        "nome": "📖 Piauí",
        "destaque": False,
        "grupo": "politica",
        "ids": {
            "instagram": "revistapiaui",
            "facebook":  "revistapiaui",
            "youtube":   "",
            "tiktok":    [],
        },
        "base": {
            "instagram": 913_000,
            "facebook":  500_000,
            "youtube":   20_000,
            "tiktok":    0,
        },
    },
    {
        "nome": "🌱 Carta Capital",
        "destaque": False,
        "grupo": "politica",
        "ids": {
            "instagram": "cartacapital",
            "facebook":  "cartacapital",
            "youtube":   "@CartaCapital",
            "tiktok":    ["cartacapital"],
        },
        "base": {
            "instagram": 500_000,
            "facebook":  1_000_000,
            "youtube":   50_000,
            "tiktok":    30_000,
        },
    },
    # ── NACIONAIS — NEGÓCIOS ────────────────────────────────────
    {
        "nome": "💼 Exame",
        "destaque": False,
        "grupo": "negocios",
        "ids": {
            "instagram": "exame",
            "facebook":  "exame",
            "youtube":   "@exame",
            "tiktok":    ["exame"],
        },
        "base": {
            "instagram": 1_000_000,
            "facebook":  2_000_000,
            "youtube":   150_000,
            "tiktok":    100_000,
        },
    },
]

HISTORICO_FILE = Path(__file__).parent / "historico_revistas.json"

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
            if n and int(n) > 100: return int(n), True
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
                    if n > 100: return n, True
    except Exception: pass
    return None, False

# ── FACEBOOK ──────────────────────────────────────────────────
def coletar_facebook(page):
    if not page: return None, False
    for url in [
        f"https://www.facebook.com/{page}",
        f"https://m.facebook.com/{page}",
    ]:
        try:
            r = SESSION.get(url, headers={"Accept": "text/html"}, timeout=12)
            if r.status_code == 200:
                for pat in [
                    r'"followerCount"\s*:\s*(\d+)',
                    r'"page_likers"\s*:\s*\{[^}]*"count"\s*:\s*(\d+)',
                    r'([\d,.]+)\s+(?:seguidores|followers)',
                    r'"social_context".*?"([\d,]+)\s+(?:seguidores|followers)',
                ]:
                    m = re.search(pat, r.text, re.I)
                    if m:
                        raw = m.group(1).replace(",", "").replace(".", "")
                        if raw.isdigit() and int(raw) > 100:
                            return int(raw), True
        except Exception: pass
        time.sleep(0.3)
    return None, False

# ── YOUTUBE ──────────────────────────────────────────────────
def coletar_youtube(channel_id):
    if not channel_id: return None, False
    try:
        r = SESSION.get(
            f"https://mixerno.space/api/youtube-channel-counter/user/{channel_id}",
            timeout=12)
        if r.status_code == 200:
            counts = r.json().get("counts", [])
            subs = next((c["count"] for c in counts if c.get("value") == "subscribers"), None)
            if subs and int(subs) > 100:
                return int(subs), True
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
    return None, False, f"@{handles[0]}" if handles else ""

# ═══════════════════════════════════════════════════════════════
#  COLETA COMPLETA
# ═══════════════════════════════════════════════════════════════

def coletar_veiculo(v):
    ids  = v["ids"]
    base = v["base"]

    ig_v, ig_l = coletar_instagram(ids["instagram"])
    fb_v, fb_l = coletar_facebook(ids["facebook"])
    yt_v, yt_l = coletar_youtube(ids["youtube"])
    tt_v, tt_l, tt_h = coletar_tiktok(ids["tiktok"])

    return {
        "nome":     v["nome"],
        "destaque": v["destaque"],
        "grupo":    v.get("grupo", ""),
        "instagram": {"val": ig_v or base["instagram"], "live": ig_l},
        "facebook":  {"val": fb_v or base["facebook"],  "live": fb_l},
        "youtube":   {"val": yt_v or base["youtube"],   "live": yt_l},
        "tiktok":    {"val": tt_v or base["tiktok"],    "live": tt_l, "handle": tt_h},
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
        print(f"📰 REVISTAS ANALYTICS — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*90}")
        print(f"{'Veículo':<28} {'Instagram':>11} {'Facebook':>10} {'YouTube':>9} {'TikTok':>8}")
        print("-"*70)
        for r in resultados:
            print(f"{r['nome']:<28} "
                  f"{tag(r['instagram']['live'])}{fmt(r['instagram']['val']):>10} "
                  f"{tag(r['facebook']['live'])}{fmt(r['facebook']['val']):>9} "
                  f"{tag(r['youtube']['live'])}{fmt(r['youtube']['val']):>8} "
                  f"{tag(r['tiktok']['live'])}{fmt(r['tiktok']['val']):>7}")
        print(f"\n🟢 ao vivo  ⬜ base (Jun/2026)")
        return

    console.rule("[bold yellow]📰  REVISTAS ANALYTICS PARÁ — 4 PLATAFORMAS[/bold yellow]")
    console.print(
        f"[dim]{datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} "
        "| Instagram · Facebook · YouTube · TikTok[/dim]\n"
    )

    t = Table(
        box=box.DOUBLE_EDGE,
        header_style="bold white on dark_blue",
        border_style="bright_blue",
        expand=True, show_lines=True, padding=(0, 1),
    )
    t.add_column("Veículo",                    min_width=22, style="bold")
    t.add_column("📸 Instagram\nSeguidores",   justify="right", min_width=13)
    t.add_column("👤 Facebook\nSeguidores",    justify="right", min_width=13)
    t.add_column("▶️  YouTube\nInscritos",     justify="right", min_width=11)
    t.add_column("🎵 TikTok\nSeguidores",      justify="right", min_width=10)
    t.add_column("📡 Status",                  justify="center", min_width=18)

    for r in resultados:
        lv   = lambda k: "bold green" if r[k]["live"] else "white"
        c_ig = f"[{lv('instagram')}]{fmt(r['instagram']['val'])}[/]"
        c_fb = f"[{lv('facebook')}]{fmt(r['facebook']['val'])}[/]"
        c_yt = f"[{lv('youtube')}]{fmt(r['youtube']['val']) if r['youtube']['val'] else '—'}[/]"
        c_tt = f"[{lv('tiktok')}]{fmt(r['tiktok']['val'])}[/]"

        status = (
            f"{tag(r['instagram']['live'])}IG "
            f"{tag(r['facebook']['live'])}FB "
            f"{tag(r['youtube']['live'])}YT "
            f"{tag(r['tiktok']['live'])}TT"
        )

        pfx = "⭐ " if r["destaque"] else "   "
        t.add_row(
            f"{pfx}{r['nome']}",
            c_ig, c_fb, c_yt, c_tt, status,
            style="on grey11" if r["destaque"] else "",
        )

    console.print(t)

    # ── Tabela exatos ─────────────────────────────────────────
    console.print("\n[bold]📊 NÚMEROS EXATOS[/bold]")
    e = Table(box=box.SIMPLE_HEAD, header_style="bold dim", expand=True)
    e.add_column("Veículo")
    e.add_column("Instagram",  justify="right")
    e.add_column("Facebook",   justify="right")
    e.add_column("YouTube",    justify="right")
    e.add_column("TikTok",     justify="right")
    e.add_column("Total Social", justify="right")

    for r in resultados:
        total = sum(
            r[p]["val"] or 0
            for p in ("instagram","facebook","youtube","tiktok")
        )
        e.add_row(
            r["nome"],
            f"[magenta]{fmt(r['instagram']['val'], True)}[/]",
            f"[blue]{fmt(r['facebook']['val'], True)}[/]",
            f"[red]{fmt(r['youtube']['val'], True) if r['youtube']['val'] else '—'}[/]",
            f"[bright_blue]{fmt(r['tiktok']['val'], True)}[/]",
            f"[bold yellow]{fmt(total)}[/]",
        )

    console.print(e)
    console.print("\n[dim]🟢 ao vivo  ⬜ base verificado (Jun/2026)[/dim]")

    # ── Análise estratégica ───────────────────────────────────
    console.print("\n[bold yellow]⚡ ANÁLISE ESTRATÉGICA — Revistas vs Campo[/bold yellow]")
    principais = [r for r in resultados if r["destaque"]]
    for principal in principais:
        console.print(f"\n[bold]{principal['nome']}[/bold]")
        a = Table(box=box.SIMPLE, expand=True)
        a.add_column("Plataforma")
        a.add_column("Revista", justify="right")
        a.add_column("Líder do Mercado", justify="right")
        a.add_column("Veículo Líder")
        a.add_column("Gap")
        a.add_column("Posição")

        plats = [
            ("📸 Instagram", "instagram"),
            ("👤 Facebook",  "facebook"),
            ("▶️  YouTube",  "youtube"),
            ("🎵 TikTok",    "tiktok"),
        ]

        for label, plat in plats:
            p_val = principal[plat]["val"] or 0
            vals  = [(r["nome"], r[plat]["val"] or 0)
                     for r in resultados if r[plat]["val"]]
            if not vals: continue
            vals.sort(key=lambda x: x[1], reverse=True)
            lider_nome, lider_val = vals[0]
            posicao = next(
                (i + 1 for i, (n, v) in enumerate(vals)
                 if n == principal["nome"]), "—"
            )
            gap = lider_val - p_val

            gap_txt = (f"[red]-{fmt(gap)}[/red]" if gap > 0
                       else "[green]LIDERA[/green]")
            pos_txt = (f"[green]{posicao}ª[/green]" if posicao == 1
                       else f"[yellow]{posicao}ª de {len(vals)}[/yellow]")

            a.add_row(
                label,
                f"[bold]{fmt(p_val)}[/bold]",
                fmt(lider_val),
                re.sub(r'^[^\w]+', '', lider_nome).strip(),
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
                for p in ("instagram", "facebook", "youtube", "tiktok")
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
        for plat in ("Instagram", "Facebook", "YouTube", "TikTok"):
            t.add_column(f"Rev.Polícia\n{plat}", justify="right")
        for entry in hist[-20:]:
            ts = entry["timestamp"][:16].replace("T", " ")
            rpe = entry["dados"].get("📋 Revista Total", {})
            t.add_row(
                ts,
                fmt(rpe.get("instagram"), True),
                fmt(rpe.get("facebook"),  True),
                fmt(rpe.get("youtube"),   True) if rpe.get("youtube") else "—",
                fmt(rpe.get("tiktok"),    True),
            )
        console.print(t)

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Revistas Analytics Pará — 4 Plataformas")
    parser.add_argument("--historico",  action="store_true")
    parser.add_argument("--grupo",      help="principal | portal | digital")
    parser.add_argument("--veiculo",    help="Nome parcial do veículo")
    parser.add_argument("--json-only",  action="store_true", dest="json_only")
    args = parser.parse_args()

    if args.historico:
        mostrar_historico(); return

    veiculos = VEICULOS
    if args.grupo:
        veiculos = [v for v in VEICULOS if v.get("grupo", "") == args.grupo]
    if args.veiculo:
        veiculos = [v for v in VEICULOS
                    if args.veiculo.lower() in v["nome"].lower()]

    if RICH and not args.json_only:
        console.print(Panel.fit(
            "[bold yellow]📰  REVISTAS ANALYTICS PARÁ — v1.0[/bold yellow]\n"
            "[dim]Instagram · Facebook · YouTube · TikTok[/dim]",
            border_style="yellow",
        ))

    resultados = []
    for v in veiculos:
        if not args.json_only:
            if RICH:
                console.print(f"[dim]→ {v['nome']}...[/dim]")
            else:
                print(f"→ {v['nome']}...")
        resultados.append(coletar_veiculo(v))
        time.sleep(0.5)

    if not args.json_only:
        exibir(resultados)
    salvar(resultados)

    if not args.json_only and RICH:
        console.print(
            f"\n[dim]💾 Histórico: {HISTORICO_FILE}[/dim]\n"
            f"[dim]🕐 {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}[/dim]"
        )
    elif args.json_only:
        print(f"✅ {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} — {len(resultados)} veículos salvos")

if __name__ == "__main__":
    main()
