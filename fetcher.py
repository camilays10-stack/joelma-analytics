"""
Busca dados reais de cada artista em paralelo.
Plataformas suportadas: Deezer (grátis), Spotify (API), YouTube (API).
"""
import requests
import concurrent.futures
import threading
from datetime import datetime

_TIMEOUT = 12

# ── Spotify ────────────────────────────────────────────────────────────────────
def get_spotify_token(client_id: str, client_secret: str) -> str | None:
    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception:
        return None

def _fetch_spotify(name: str, token: str) -> dict:
    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={"q": name, "type": "artist", "limit": 3, "market": "BR"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        items = r.json().get("artists", {}).get("items", [])
        if not items:
            return {}
        # Pega o mais popular (mais relevante)
        a = sorted(items, key=lambda x: x.get("popularity", 0), reverse=True)[0]
        return {
            "seguidores":  a.get("followers", {}).get("total", 0),
            "popularidade": a.get("popularity", 0),
            "artist_id":   a["id"],
            "nome":        a.get("name", ""),
            "url":         f"https://open.spotify.com/artist/{a['id']}",
            "imagem":      (a.get("images") or [{}])[0].get("url", ""),
        }
    except Exception as e:
        return {"erro": str(e)}

# ── Deezer (sem autenticação) ──────────────────────────────────────────────────
def _fetch_deezer(name: str) -> dict:
    try:
        r = requests.get(
            "https://api.deezer.com/search/artist",
            params={"q": name, "limit": 1},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        items = r.json().get("data", [])
        if not items:
            return {}
        aid = items[0]["id"]
        r2 = requests.get(f"https://api.deezer.com/artist/{aid}", timeout=_TIMEOUT)
        r2.raise_for_status()
        d = r2.json()
        return {
            "fans":       d.get("nb_fan", 0),
            "albuns":     d.get("nb_album", 0),
            "url":        d.get("link", ""),
            "imagem":     d.get("picture_xl", ""),
            "artist_id":  aid,
        }
    except Exception as e:
        return {"erro": str(e)}

# ── YouTube Data API v3 ────────────────────────────────────────────────────────
def _fetch_youtube(name: str, api_key: str) -> dict:
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part":       "snippet",
                "q":          f"{name} oficial",
                "type":       "channel",
                "maxResults": 1,
                "regionCode": "BR",
                "key":        api_key,
            },
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            return {}
        channel_id = items[0]["id"]["channelId"]

        r2 = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "statistics", "id": channel_id, "key": api_key},
            timeout=_TIMEOUT,
        )
        r2.raise_for_status()
        ch = r2.json().get("items", [])
        if not ch:
            return {}
        s = ch[0].get("statistics", {})
        return {
            "inscritos":   int(s.get("subscriberCount", 0)),
            "views_total": int(s.get("viewCount", 0)),
            "videos":      int(s.get("videoCount", 0)),
            "channel_id":  channel_id,
            "url":         f"https://youtube.com/channel/{channel_id}",
        }
    except Exception as e:
        return {"erro": str(e)}

# ── Busca de um artista em todas as plataformas ────────────────────────────────
def fetch_artist(name: str, config: dict) -> dict:
    result = {
        "name":      name,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "data":      {},
    }

    dz = _fetch_deezer(name)
    if dz and "erro" not in dz:
        result["data"]["deezer"] = dz

    if config.get("spotify_token"):
        sp = _fetch_spotify(name, config["spotify_token"])
        if sp and "erro" not in sp:
            result["data"]["spotify"] = sp

    if config.get("youtube_api_key"):
        yt = _fetch_youtube(name, config["youtube_api_key"])
        if yt and "erro" not in yt:
            result["data"]["youtube"] = yt

    return result

# ── Busca paralela de todos os artistas ───────────────────────────────────────
def fetch_all_parallel(artist_names: list, config: dict, on_done=None) -> dict:
    """
    Roda fetch_artist em paralelo para todos os artistas.
    on_done(progress_0_to_1, artist_name) é chamado cada vez que um termina.
    """
    results = {}
    total   = len(artist_names)
    _done   = [0]
    _lock   = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(total, 8)) as ex:
        futures = {ex.submit(fetch_artist, n, config): n for n in artist_names}
        for f in concurrent.futures.as_completed(futures):
            n = futures[f]
            try:
                results[n] = f.result()
            except Exception as e:
                results[n] = {
                    "name": n,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "data": {},
                    "erro": str(e),
                }
            with _lock:
                _done[0] += 1
            if on_done:
                on_done(_done[0] / total, n)

    return results
