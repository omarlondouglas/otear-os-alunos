import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
TIMEOUT_SECONDS = 8
MAX_HTML_CHARS = 250_000

BUILDER_SIGNATURES_URL = {
    ".wixsite.com": "Wix",
    "sites.google.com": "Google Sites",
    ".negocio.site": "Google Meu Negocio",
    "canva.site": "Canva",
    ".my.canva.site": "Canva",
    ".wordpress.com": "WordPress.com gratuito",
    ".webnode.page": "Webnode",
    ".webnode.com.br": "Webnode",
    ".site123.me": "SITE123",
    ".lojaintegrada.com.br": "Loja Integrada",
    ".goomer.app": "Goomer",
}

BUILDER_SIGNATURES_HTML = {
    "static.wixstatic.com": "Wix",
    "static.parastorage.com": "Wix",
    'generator" content="wix': "Wix",
    'generator" content="site123': "SITE123",
    'generator" content="webnode': "Webnode",
    "canva-site": "Canva",
    "websitebuilder": "construtor de site",
}

MIXED_CONTENT_RE = re.compile(r"""(?:\ssrc=["']http://|href=["']http://)""", re.IGNORECASE)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_DESC_RE = re.compile(
    r"""<meta[^>]+name=["']description["'][^>]+content=["'](.{20,})["']""",
    re.IGNORECASE | re.DOTALL,
)
COPYRIGHT_YEAR_RE = re.compile(r"(?:copyright|©)\D{0,20}(20\d{2})", re.IGNORECASE)


TRACKING_SIGNATURES = {
    "meta": {
        "platform": "Meta",
        "markers": ("connect.facebook.net", "fbevents.js", "fbq(", "facebook pixel", "facebook.com/tr"),
    },
    "google_ads": {
        "platform": "Google Ads",
        "markers": (
            "googleadservices.com",
            "googlesyndication.com",
            "doubleclick.net",
            "gtag/js?id=aw-",
            "gtag('config', 'aw-",
            'gtag("config", "aw-',
            "conversion_async.js",
        ),
    },
    "google_tag_manager": {
        "platform": "Google Tag Manager",
        "markers": ("googletagmanager.com/gtm.js", "gtm-"),
    },
    "google_analytics": {
        "platform": "Google Analytics",
        "markers": (
            "google-analytics.com",
            "googletagmanager.com/gtag/js?id=g-",
            "gtag('config', 'g-",
            'gtag("config", "g-',
        ),
    },
    "tiktok": {
        "platform": "TikTok",
        "markers": ("analytics.tiktok.com", "ttq.load"),
    },
    "linkedin": {
        "platform": "LinkedIn",
        "markers": ("snap.licdn.com", "_linkedin_partner_id"),
    },
}


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.lower().startswith(("http://", "https://")):
        return url
    return f"https://{url}"


def _request(url: str, verify_ssl: bool = True) -> tuple[str, str, float, int]:
    context = None if verify_ssl else ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS, context=context) as response:
        elapsed = time.perf_counter() - started
        raw = response.read(MAX_HTML_CHARS)
        charset = response.headers.get_content_charset() or "utf-8"
        html = raw.decode(charset, errors="replace")
        return response.geturl(), html, elapsed, getattr(response, "status", 200)


def _is_dns_failure(error: Exception) -> bool:
    text = str(error).lower()
    return any(marker in text for marker in ("getaddrinfo", "name or service not known", "nodename nor servname"))


def _detect_builder(final_url: str, html: str) -> str | None:
    final_lower = (final_url or "").lower()
    for signature, name in BUILDER_SIGNATURES_URL.items():
        if signature in final_lower:
            return name

    html_lower = (html or "").lower()
    for signature, name in BUILDER_SIGNATURES_HTML.items():
        if signature in html_lower:
            return name
    return None


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value or "")).strip()


def _checklist(html: str) -> dict:
    html_lower = (html or "").lower()
    title_match = TITLE_RE.search(html or "")
    title = _plain_text(title_match.group(1)) if title_match else ""
    meta_description = META_DESC_RE.search(html or "")

    checks = [
        ("botao de WhatsApp", "wa.me" in html_lower or "api.whatsapp.com" in html_lower or "whatsapp" in html_lower),
        ("telefone clicavel", 'href="tel:' in html_lower or "href='tel:" in html_lower),
        ("email de contato", "mailto:" in html_lower),
        ("link para redes sociais", "instagram.com" in html_lower or "facebook.com" in html_lower),
        ("endereco ou mapa", "google.com/maps" in html_lower or "maps.google" in html_lower),
        ("titulo descritivo", len(title) > 8 and title.lower() not in {"home", "index", "inicio", "untitled"}),
        ("descricao para Google", bool(meta_description)),
        ("favicon", "rel=\"icon" in html_lower or "rel='icon" in html_lower or "shortcut icon" in html_lower),
    ]
    return {
        "present": [name for name, ok in checks if ok],
        "missing": [name for name, ok in checks if not ok],
    }


def _domain_from_url(url: str | None) -> str:
    parsed = urllib.parse.urlparse(_normalize_url(url or ""))
    host = parsed.netloc.lower().removeprefix("www.")
    return host.split(":")[0]


def _meta_ads_library_url(name: str | None) -> str:
    query = urllib.parse.quote((name or "").strip())
    return (
        "https://www.facebook.com/ads/library/"
        f"?active_status=active&ad_type=all&country=BR&media_type=all"
        f"&search_type=keyword_unordered&q={query}"
    )


def _google_ads_transparency_url(domain: str | None, name: str | None) -> str:
    query = urllib.parse.quote((domain or name or "").strip())
    return f"https://adstransparency.google.com/?region=BR&query={query}"


def detect_ads_signals(html: str, final_url: str | None, business_name: str | None = None) -> dict:
    html_lower = (html or "").lower()
    platforms: list[str] = []
    signals: list[str] = []

    for config in TRACKING_SIGNATURES.values():
        matched = [marker for marker in config["markers"] if marker in html_lower]
        if matched:
            platforms.append(config["platform"])
            signals.append(f"{config['platform']}: {', '.join(matched[:3])}")

    paid_platforms = [p for p in platforms if p in {"Meta", "Google Ads", "TikTok", "LinkedIn"}]
    has_tracking_pixels = bool(platforms)
    has_paid_ads_signals = bool(paid_platforms)
    domain = _domain_from_url(final_url)

    if has_paid_ads_signals:
        status = "tracking_detected"
    elif has_tracking_pixels:
        status = "analytics_only"
    else:
        status = "unknown"

    return {
        "status": status,
        "has_tracking_pixels": has_tracking_pixels,
        "has_paid_ads_signals": has_paid_ads_signals,
        "platforms": platforms,
        "signals": signals,
        "meta_ads_library_url": _meta_ads_library_url(business_name),
        "google_ads_transparency_url": _google_ads_transparency_url(domain, business_name),
        "domain": domain,
        "note": "Pixels e tags indicam estrutura de trafego, mas nao provam anuncio ativo. Use os links para conferir criativos ativos nas bibliotecas publicas.",
    }


def audit_website(url: str | None, business_name: str | None = None) -> dict:
    """Best-effort website quality audit. Never raises for normal network/site failures."""
    if not url:
        return {
            "status": "missing",
            "score": 0,
            "final_url": None,
            "problems": ["sem site"],
            "checklist": {"present": [], "missing": []},
            "ads": detect_ads_signals("", None, business_name),
        }

    normalized = _normalize_url(url)
    problems: list[str] = []
    final_url = normalized
    html = ""
    elapsed = 0.0
    status_code = 0

    try:
        final_url, html, elapsed, status_code = _request(normalized)
    except ssl.SSLError:
        problems.append("certificado SSL invalido ou vencido")
        try:
            final_url, html, elapsed, status_code = _request(normalized, verify_ssl=False)
        except Exception:
            pass
    except urllib.error.HTTPError as error:
        status_code = error.code
        problems.append(f"site responde com erro HTTP {error.code}")
        try:
            raw = error.read(MAX_HTML_CHARS)
            html = raw.decode("utf-8", errors="replace")
            final_url = error.geturl()
        except Exception:
            html = ""
    except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
        if _is_dns_failure(error):
            return {
                "status": "bad",
                "score": 100,
                "final_url": normalized,
                "problems": ["dominio nao encontrado ou expirado"],
                "checklist": {"present": [], "missing": []},
                "ads": detect_ads_signals("", normalized, business_name),
                "response_time_seconds": None,
                "http_status": None,
            }
        if normalized.startswith("https://"):
            try:
                final_url, html, elapsed, status_code = _request("http://" + normalized.removeprefix("https://"))
                problems.append("sem HTTPS")
            except Exception:
                return {
                    "status": "bad",
                    "score": 90,
                    "final_url": normalized,
                    "problems": ["site fora do ar ou nao responde"],
                    "checklist": {"present": [], "missing": []},
                    "ads": detect_ads_signals("", normalized, business_name),
                    "response_time_seconds": None,
                    "http_status": None,
                }

    final_lower = (final_url or "").lower()
    html_lower = (html or "").lower()

    if status_code >= 400 and not any("HTTP" in p for p in problems):
        problems.append(f"site responde com erro HTTP {status_code}")
    if elapsed > 5:
        problems.append(f"site lento para responder ({elapsed:.1f}s)")
    if final_lower.startswith("http://"):
        problems.append("sem HTTPS")
    elif MIXED_CONTENT_RE.search(html or ""):
        problems.append("conteudo misto inseguro")
    if "viewport" not in html_lower:
        problems.append("nao adaptado para celular")
    if len((html or "").strip()) < 800:
        problems.append("pagina quase vazia")

    builder = _detect_builder(final_url, html)
    if builder:
        problems.append(f"feito em construtor pronto ({builder})")

    years = [int(y) for y in COPYRIGHT_YEAR_RE.findall(html or "")]
    if years and max(years) <= date.today().year - 2:
        problems.append(f"sem sinal de atualizacao desde {max(years)}")

    checklist = _checklist(html)
    ads = detect_ads_signals(html, final_url, business_name)
    missing_count = len(checklist["missing"])
    if missing_count >= 4:
        problems.append("site sem itens basicos de conversao")

    weighted = 0
    weights = {
        "site fora do ar": 45,
        "dominio nao encontrado": 50,
        "certificado SSL": 18,
        "sem HTTPS": 14,
        "nao adaptado": 18,
        "lento": 12,
        "construtor pronto": 12,
        "pagina quase vazia": 20,
        "sem itens basicos": 16,
    }
    for problem in problems:
        lower = problem.lower()
        weighted += next((points for marker, points in weights.items() if marker in lower), 8)
    weighted += min(missing_count * 3, 18)
    score = min(weighted, 100)

    return {
        "status": "bad" if problems else "ok",
        "score": score,
        "final_url": final_url,
        "problems": problems,
        "checklist": checklist,
        "ads": ads,
        "response_time_seconds": round(elapsed, 2) if elapsed else None,
        "http_status": status_code or None,
    }
