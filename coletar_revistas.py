"""
Script de coleta diária — revistas nacionais.
Roda via GitHub Actions todo dia às 03:00 BRT.
Salva snapshot em historico_revistas.json.
"""
import json, re, time, sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("requests não instalado"); sys.exit(1)

HISTORICO_FILE = Path(__file__).parent / "historico_revistas.json"

VEICULOS = [
    {
        "nome": "Revista Total",
        "ig": "revistatotalbrasil",
        "fb": "revistatotalbrasil",
        "yt": "",
        "tt": "revistatotalbrasil",
        "base": {"instagram": 63_500, "facebook": 4_763, "youtube": 0, "tiktok": 1_030},
    },
    {
        "nome": "Caras",
        "ig": "carasbrasil",
        "fb": "carasbrasil",
        "yt": "https://www.youtube.com/channel/UCAcm_kK9LeKsqntNX_5J9Rg",
        "tt": "carasbrasil",
        "base": {"instagram": 8_000_000, "facebook": 4_869_636, "youtube": 72_200, "tiktok": 1_600_000},
    },
    {
        "nome": "Contigo",
        "ig": "tocontigo",
        "fb": "Contigo",
        "yt": "https://www.youtube.com/@TVContigo",
        "tt": "tocontigo",
        "base": {"instagram": 2_000_000, "facebook": 3_400_000, "youtube": 398_000, "tiktok": 633_600},
    },
    {
        "nome": "Veja",
        "ig": "vejamais",
        "fb": "Veja",
        "yt": "https://www.youtube.com/user/vejapontocom",
        "tt": "",
        "base": {"instagram": 2_000_000, "facebook": 6_705_913, "youtube": 669_000, "tiktok": 0},
    },
    {
        "nome": "IstoÉ",
        "ig": "revistaistoe",
        "fb": "revistaISTOE",
        "yt": "https://www.youtube.com/channel/UC6Z3-B_ybUirOnOoAP9Rz4w",
        "tt": "revistaistoe",
        "base": {"instagram": 1_000_000, "facebook": 2_284_044, "youtube": 288_000, "tiktok": 73_300},
    },
    {
        "nome": "Piauí",
        "ig": "revistapiaui",
        "fb": "revistapiaui",
        "yt": "",
        "tt": "revistapiaui",
        "base": {"instagram": 913_000, "facebook": 455_428, "youtube": 0, "tiktok": 37_300},
    },
    {
        "nome": "Carta Capital",
        "ig": "cartacapital",
        "fb": "CartaCapital",
        "yt": "https://www.youtube.com/cartacapital",
        "tt": "cartacapital",
        "base": {"instagram": 1_000_000, "facebook": 1_691_650, "youtube": 694_000, "tiktok": 9_072},
    },
    {
        "nome": "Exame",
        "ig": "exame",
        "fb": "Exame",
        "yt": "https://www.youtube.com/user/portalexame",
        "tt": "exame",
        "base": {"instagram": 4_000_000, "facebook": 3_964_083, "youtube": 671_000, "tiktok": 302_800},
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def sessao():
    s = requests.Session()
    r = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.headers.update(HEADERS)
    return s


def fetch_instagram(s, username):
    """Tenta buscar seguidores via API interna do Instagram."""
    try:
        r = s.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers={"X-IG-App-ID": "936619743392459", "X-Requested-With": "XMLHttpRequest",
                     "Referer": "https://www.instagram.com/"},
            timeout=12,
        )
        if r.status_code == 200:
            n = r.json().get("data", {}).get("user", {}).get("edge_followed_by", {}).get("count")
            if n and int(n) > 500:
                return int(n), True
    except Exception:
        pass
    return None, False


def fetch_youtube(s, url):
    """Busca inscritos scrapeando a página do canal."""
    if not url:
        return None, False
    try:
        r = s.get(url, timeout=15)
        if r.status_code != 200:
            return None, False
        text = r.text
        # Padrão principal: subscriberCountText
        m = re.search(r'"subscriberCountText".*?"simpleText"\s*:\s*"([^"]+)"', text, re.DOTALL)
        if m:
            raw = m.group(1).strip()
            val = parse_yt_count(raw)
            if val:
                return val, True
        # Padrão alternativo: X mil inscritos
        m2 = re.search(r'(\d[\d,.]+)\s*mil\s*inscritos', text, re.I)
        if m2:
            val = parse_yt_count(m2.group(1) + " mil")
            if val:
                return val, True
    except Exception:
        pass
    return None, False


def parse_yt_count(raw):
    """Converte '398 mil', '1,2 M', '72,2 mil' → int."""
    raw = raw.strip().lower()
    raw = raw.replace(",", ".").replace("\xa0", " ")
    m = re.match(r"([\d.]+)\s*(mil|m|k)?", raw)
    if not m:
        return None
    num = float(m.group(1))
    sufx = (m.group(2) or "").strip()
    if sufx in ("mil", "k"):
        return int(num * 1_000)
    if sufx == "m":
        return int(num * 1_000_000)
    return int(num)


def fetch_tiktok(s, username):
    """TikTok bloqueia scraping — retorna None."""
    return None, False


def coletar():
    s = sessao()
    resultado = {}
    total_live = 0

    for v in VEICULOS:
        nome = v["nome"]
        base = v["base"]
        print(f"\n{'='*40}\n{nome}")

        ig_val, ig_live = fetch_instagram(s, v["ig"])
        yt_val, yt_live = fetch_youtube(s, v["yt"])
        tt_val, tt_live = fetch_tiktok(s, v["tt"])

        # Fallback para base quando ao vivo não disponível
        instagram = ig_val if ig_live else base["instagram"]
        youtube   = yt_val if yt_live else base["youtube"]
        facebook  = base["facebook"]   # Facebook requer autenticação
        tiktok    = tt_val if tt_live else base["tiktok"]  # TikTok bloqueia scraping

        resultado[nome] = {
            "instagram": instagram, "instagram_live": ig_live,
            "facebook":  facebook,  "facebook_live":  False,
            "youtube":   youtube,   "youtube_live":   yt_live,
            "tiktok":    tiktok,    "tiktok_live":    tt_live,
        }

        if ig_live:  total_live += 1
        if yt_live:  total_live += 1

        print(f"  IG:  {instagram:>12,}  {'🟢 ao vivo' if ig_live else '⬜ base'}")
        print(f"  FB:  {facebook:>12,}  ⬜ base")
        print(f"  YT:  {youtube:>12,}  {'🟢 ao vivo' if yt_live else '⬜ base'}")
        print(f"  TT:  {tiktok:>12,}  {'🟢 ao vivo' if tt_live else '⬜ base'}")

        time.sleep(1.5)

    return resultado, total_live


def salvar_snapshot(dados):
    hist = []
    if HISTORICO_FILE.exists():
        try:
            hist = json.loads(HISTORICO_FILE.read_text(encoding="utf-8"))
        except Exception:
            hist = []

    snapshot = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dados": {
            nome: {p: v[p] for p in ("instagram", "facebook", "youtube", "tiktok")}
            for nome, v in dados.items()
        },
    }
    hist.append(snapshot)
    # Mantém últimos 365 snapshots (~1 por dia)
    HISTORICO_FILE.write_text(
        json.dumps(hist[-365:], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n✅ Snapshot salvo — total: {len(hist)} registros")
    return snapshot


if __name__ == "__main__":
    print(f"🚀 Coleta iniciada: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    dados, total_live = coletar()
    snap = salvar_snapshot(dados)

    # Resumo para o log do GitHub Actions
    print("\n" + "="*50)
    print("RESUMO DO SNAPSHOT")
    print("="*50)
    for nome, vals in snap["dados"].items():
        total = sum(vals.values())
        print(f"{nome:20s} | total: {total:>12,}")
    print(f"\nMétricas ao vivo coletadas: {total_live}")
    print("✅ Concluído.")
