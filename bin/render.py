#!/usr/bin/env python3
"""Render hf7y.com's index.html or the hf7y/hf7y profile README from portfolio.json.

usage: render.py site|readme > out
"""
import html, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "hf7y-render"})
    if url.startswith("https://api.github.com/") and os.environ.get("GH_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GH_TOKEN"])
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def repo(name):
    r = json.loads(get(f"https://api.github.com/repos/hf7y/{name}"))
    return r["html_url"], r["description"] or ""


def compositions(url):
    # zach.audio marks each work up as <section typeof=Composition id=..><h2 property=title>..</h2>
    page = get(url)
    return [(url + "#" + i, html.unescape(t))
            for i, t in re.findall(r'typeof=Composition id="([^"]+)">\s*<h2 property=title>(.*?)</h2>', page)]


def main(fmt):
    p = json.loads((ROOT / "portfolio.json").read_text())
    repos = [(n, *repo(n)) for n in p["repos"]]
    works = compositions(p["music"])
    if not works:
        sys.exit(f"no <section typeof=Composition> found at {p['music']}")
    if fmt == "readme":
        out = ["## Code", ""] + [f"- [{n}]({u}) — {d}" for n, u, d in repos]
        out += ["", "## Music", ""] + [f"- [{t}]({u})" for u, t in works]
        out += ["", "## Sites", ""] + [f"- <{s}>" for s in p["sites"]]
        print("\n".join(out))
        return
    e = html.escape
    li = lambda href, text, note="": f'    <li><a href="{e(href)}">{e(text)}</a>{" — " + e(note) if note else ""}</li>'
    out = ['<!doctype html>', '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{e(p["title"])}</title>', '<main>', f'  <h1>{e(p["title"])}</h1>',
           '  <h2>Music</h2>', '  <ul>', *[li(u, t) for u, t in works], '  </ul>',
           '  <h2>Code</h2>', '  <ul>', *[li(u, n, d) for n, u, d in repos], '  </ul>',
           '  <h2>Sites</h2>', '  <ul>', *[li(s, s.split("//")[1].rstrip("/")) for s in p["sites"]], '  </ul>',
           '</main>']
    print("\n".join(out))


if __name__ == "__main__":
    if sys.argv[1:] not in (["site"], ["readme"]):
        sys.exit(__doc__.strip())
    main(sys.argv[1])
