import hashlib
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Documentation-Research-MVP/0.1 (+local testing)"

@dataclass
class ScrapedPage:
    url: str
    title: str
    domain: str
    clean_text: str
    content_hash: str
    status_code: int
    content_type: str
    links: list[str]


def normalize_text(text: str) -> str:
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_main_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "svg", "form", "nav", "footer", "header"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(" ", strip=True)

    # Intenta elegir el contenido principal. Si no existe, usa body.
    main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|article|entry", re.I)) or soup.body or soup

    parts = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "th", "td"]):
        txt = el.get_text(" ", strip=True)
        if not txt:
            continue
        if len(txt) < 2:
            continue
        parts.append(txt)

    clean_text = normalize_text("\n".join(parts))
    return title, clean_text


def extract_links(html: str, base_url: str, same_domain_only: bool = True) -> list[str]:
    """Extrae enlaces normalizados desde una página.

    - Convierte enlaces relativos a absolutos.
    - Elimina fragmentos (#...).
    - Filtra mailto:, tel:, javascript:, PDFs e imágenes comunes.
    - Por defecto mantiene solo enlaces del mismo dominio.
    """
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    links: set[str] = set()

    ignored_ext = (".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".zip")

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base_url, href)
        absolute, _fragment = urldefrag(absolute)
        parsed = urlparse(absolute)

        if parsed.scheme not in {"http", "https"}:
            continue
        if same_domain_only and parsed.netloc != base_domain:
            continue
        if parsed.path.lower().endswith(ignored_ext):
            continue

        links.add(absolute)

    return sorted(links)


def scrape_url(url: str, timeout: int = 20) -> ScrapedPage:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    response = requests.get(url, headers=headers, timeout=timeout)
    content_type = response.headers.get("content-type", "")
    response.raise_for_status()

    title, clean_text = extract_main_text(response.text)
    links = extract_links(response.text, url)
    content_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    domain = urlparse(url).netloc

    return ScrapedPage(
        url=url,
        title=title,
        domain=domain,
        clean_text=clean_text,
        content_hash=content_hash,
        status_code=response.status_code,
        content_type=content_type,
        links=links,
    )
