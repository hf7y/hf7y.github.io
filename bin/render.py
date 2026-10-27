#!/usr/bin/env python3
"""Render hf7y.com's index.html or the hf7y/hf7y profile README from portfolio.json.

usage: render.py site|readme > out
"""
import html, json, os, re, sys, urllib.parse, urllib.request
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
    # zach.audio's RDFa is its published contract: <section typeof=Composition id=..> holding
    # property=title|date|instrumentation and an <a typeof=Score href=..>.
    works = []
    for i, body in re.findall(r'<section typeof=Composition id="([^"]+)">(.*?)</section>', get(url), re.S):
        prop = lambda k: html.unescape(m.group(1).strip()) if (m := re.search(rf"property={k}>(.*?)</", body, re.S)) else ""
        score = re.search(r'typeof=Score href="([^"]+)"', body)
        works.append({"url": url + "#" + i, "title": prop("title"), "date": prop("date"),
                      "for": prop("instrumentation"), "score": score and urllib.parse.urljoin(url, score.group(1))})
    return works


def main(fmt):
    p = json.loads((ROOT / "portfolio.json").read_text())
    repos = [(n, *repo(n)) for n in p["repos"]]
    works = compositions(p["music"])
    if not works:
        sys.exit(f"no <section typeof=Composition> found at {p['music']}")
    if fmt == "readme":
        out = ["## Music", ""] + [f"- [{w['title']}]({w['url']}) ({w['date']})" + (f" — for {w['for']}" if w["for"] else "") for w in works]
        out += ["", "## Code", ""] + [f"- [{n}]({u}) — {d}" for n, u, d in repos]
        out += ["", "## Sites", ""] + [f"- <{s}>" for s in p["sites"]]
        print("\n".join(out))
        return
    # The zach.audio idiom: its stylesheets by URL, its header, a date | work table.
    e = html.escape
    li = lambda href, text, note="": f'      <li><a href="{e(href)}">{e(text)}</a>{" — " + e(note) if note else ""}</li>'
    row = lambda w: ("  <tr>\n"
                     f'    <td>{e(w["date"])}</td>\n'
                     f'    <td><a href="{e(w["url"])}">{e(w["title"])}</a>' + (f' <i>for</i> {e(w["for"])}' if w["for"] else "") + "</td>\n"
                     "    <td>" + (f'[<a href="{e(w["score"])}">Score</a>]' if w["score"] else "") + "</td>\n"
                     "  </tr>")
    out = ['<!doctype html>', '<html xmlns:mo="http://purl.org/ontology/mo/">', '<head>',
           '  <meta charset="utf-8">',
           '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
           f'  <title>{e(p["title"])}</title>',
           '  <link rel=stylesheet href="https://zach.audio/style.css">', '</head>',
           '<body typeof="mo:MusicArtist">', '  <header>',
           '    <link rel=stylesheet href="https://zach.audio/header.css">',
           f'    <h1 property="name"><a href="/">{e(p["title"])}</a></h1>',
           '    <nav><ul><li><a href="#music">music</a></li> <li><a href="#code">code</a></li> <li><a href="#sites">sites</a></li></ul></nav>',
           '  </header>',
           '  <h2 id=music>Music</h2>', '<table>', *map(row, works), '</table>',
           '  <h2 id=code>Code</h2>', '  <ul>', *[li(u, n, d) for n, u, d in repos], '  </ul>',
           '  <h2 id=sites>Sites</h2>', '  <ul>', *[li(s, s.split("//")[1].rstrip("/")) for s in p["sites"]], '  </ul>',
           '</body>', '</html>']
    print("\n".join(out))

if __name__ == "__main__":
    if sys.argv[1:] not in (["site"], ["readme"]):
        sys.exit(__doc__.strip())
    main(sys.argv[1])
