#!/usr/bin/env python3
"""Fetch a webpage and emit JSON with the page title and a filtered list of image URLs.

Usage:
    python3 scrape.py <url>

Output (stdout):
    {"title": "...", "url": "<final url>", "images": [{"url": "...", "alt": "...", "width": null, "height": null}, ...]}
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

try:
    # Optional: a browser-fingerprinted HTTP client. When installed (the Astria
    # web-chat sandbox bundles it) fetch() uses it to get past TLS-fingerprint
    # bot blocking. Marketplace installs without it fall back to urllib.
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None


CHROME_PATH_HINTS = (
    "/icons/", "/icon/", "/logo", "/logos/", "/sprite", "/favicon",
    "/static/svg/", "/assets/svg/", "/social/", "/badge", "/spinner",
    "/loader", "/placeholder", "/avatar", "/thumb-",
)
CHROME_NAME_HINTS = (
    "logo", "icon", "favicon", "sprite", "spinner", "loader",
    "placeholder", "badge", "social",
)
MIN_HINTED_SIDE = 200


def _parse_int(value):
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.og_title = None
        self.og_images = []
        self.base_href = None
        self.images = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "base" and a.get("href"):
            self.base_href = a["href"]
        elif tag == "meta":
            prop = (a.get("property") or a.get("name") or "").lower()
            content = a.get("content")
            if prop == "og:title" and content:
                self.og_title = content
            elif prop in ("og:image", "og:image:secure_url", "twitter:image") and content:
                self.og_images.append(content)
        elif tag == "img":
            url = a.get("src") or a.get("data-src") or a.get("data-original")
            if url:
                self.images.append({
                    "url": url,
                    "alt": a.get("alt") or "",
                    "width": _parse_int(a.get("width")),
                    "height": _parse_int(a.get("height")),
                })
            srcset = a.get("srcset") or a.get("data-srcset")
            if srcset:
                self.images.extend(_srcset_entries(srcset, a.get("alt") or ""))
        elif tag == "source":
            srcset = a.get("srcset") or a.get("data-srcset")
            if srcset:
                self.images.extend(_srcset_entries(srcset, ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and not self.title:
            stripped = data.strip()
            if stripped:
                self.title = stripped


def _srcset_entries(srcset, alt):
    entries = []
    for part in srcset.split(","):
        token = part.strip().split()
        if not token:
            continue
        entries.append({"url": token[0], "alt": alt, "width": None, "height": None})
    return entries


def _is_chrome(url, alt):
    lower_url = url.lower()
    if lower_url.startswith("data:") or lower_url.endswith(".svg"):
        return True
    if any(hint in lower_url for hint in CHROME_PATH_HINTS):
        return True
    lower_alt = (alt or "").lower()
    if lower_alt and any(hint in lower_alt for hint in CHROME_NAME_HINTS):
        return True
    return False


def _too_small(width, height):
    if width is not None and width < MIN_HINTED_SIDE:
        return True
    if height is not None and height < MIN_HINTED_SIDE:
        return True
    return False


def fetch(url):
    if cffi_requests is not None:
        response = cffi_requests.get(url, impersonate="chrome", timeout=20)
        response.raise_for_status()
        return response.url, response.text
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=20) as response:
        final_url = response.geturl()
        encoding = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(encoding, errors="replace")
    return final_url, html


def scrape(url):
    final_url, html = fetch(url)
    parser = _PageParser()
    parser.feed(html)
    base = urljoin(final_url, parser.base_href) if parser.base_href else final_url

    title = (parser.og_title or parser.title or urlparse(final_url).netloc).strip()

    seen = set()
    images = []
    candidates = parser.images + [{"url": u, "alt": "", "width": None, "height": None} for u in parser.og_images]
    for item in candidates:
        absolute = urljoin(base, item["url"]).split("#", 1)[0]
        if absolute in seen:
            continue
        if _is_chrome(absolute, item["alt"]):
            continue
        if _too_small(item["width"], item["height"]):
            continue
        seen.add(absolute)
        images.append({
            "url": absolute,
            "alt": item["alt"],
            "width": item["width"],
            "height": item["height"],
        })

    return {"title": title, "url": final_url, "images": images}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="The page URL to scrape")
    args = parser.parse_args()
    json.dump(scrape(args.url), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
