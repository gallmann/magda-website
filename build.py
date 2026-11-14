#!/usr/bin/env python3
"""
Static site generator for magda-schwerzmann.ch.
Reads data/content.json and generates static HTML for all 7 pages.
Zero third-party dependencies (uses Python standard library only).
"""

import json
import html
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "content.json"

NAV_ITEMS = [
    ("home", "HOME", "/"),
    ("konzerte", "KONZERTE", "/konzerte/"),
    ("verschiedenes", "VERSCHIEDENES", "/verschiedenes/"),
    ("lebenslauf", "LEBENSLAUF", "/lebenslauf/"),
    ("unterricht", "UNTERRICHT", "/unterricht/"),
    ("hoerbeispiele", "HÖRBEISPIELE", "/hoerbeispiele/"),
    ("links", "LINKS", "/links/"),
]


MONTHS_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def esc(text: str) -> str:
    return html.escape(str(text or ""))


def rel_asset(path_str: str, prefix: str) -> str:
    s = str(path_str or "")
    if s.startswith("/"):
        return f"{prefix}{s}"
    return s


def format_concert_date(c: dict) -> str:
    date_iso = (c.get("dateIso") or "").strip()
    time_str = (c.get("time") or "").strip()
    if date_iso and len(date_iso.split("-")) == 3:
        y, m, d = date_iso.split("-")
        base = f"{int(d)}. {MONTHS_DE[int(m) - 1]} {y}"
        if time_str:
            t_disp = time_str.replace(":", ".")
            if "uhr" not in t_disp.lower():
                t_disp = f"{t_disp} Uhr"
            return f"{base}, {t_disp}"
        return base
    return c.get("dateDisplay", "")


def render_shell(data: dict, active_key: str, page_title: str, body_html: str) -> str:
    site = data["site"]
    contact = site["contact"]
    prefix = "." if active_key == "home" else ".."

    nav_links = []
    for key, label, href in NAV_ITEMS:
        cls = ' class="active"' if key == active_key else ""
        rel_href = f"{prefix}/" if href == "/" else f"{prefix}{href}"
        nav_links.append(f'<li><a href="{rel_href}"{cls}>{esc(label)}</a></li>')
    nav_html = "\n          ".join(nav_links)

    full_title = (
        f"Musikerin | {site['title']} | {site['location']}"
        if active_key == "home"
        else f"{page_title} | {site['title']}"
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(site['title'])} – {esc(site['subtitle'])} in {esc(site['location'])}" />
  <link rel="icon" href="{prefix}/assets/images/logo.png" type="image/png" />
  <link rel="stylesheet" href="{prefix}/assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="{prefix}/" class="brand">
        <img src="{prefix}/assets/images/logo.png" alt="Logo" />
        <span>{esc(site['title'])}</span>
      </a>
      <button class="nav-toggle" aria-label="Menü öffnen">☰</button>
      <nav class="site-nav" aria-label="Hauptnavigation">
        <ul>
          {nav_html}
        </ul>
      </nav>
    </div>
  </header>

  <main>
{body_html}
  </main>

  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-contact">
        <p><strong>{esc(contact['name'])}</strong></p>
        <p>{esc(contact['street'])}, {esc(contact['city'])}</p>
        <p><a href="mailto:{esc(contact['email'])}">{esc(contact['emailDisplay'])}</a> · <a href="tel:{esc(contact['phone'].replace(' ', ''))}">{esc(contact['phone'])}</a></p>
      </div>
      <div class="footer-social">
        <a href="{esc(contact['facebookUrl'])}" target="_blank" rel="noopener noreferrer">
          Auf Facebook folgen
        </a>
        <a href="{prefix}/admin/" class="footer-admin-link" title="Website bearbeiten">Bearbeiten</a>
      </div>
    </div>
  </footer>

  <script src="{prefix}/assets/site.js"></script>
</body>
</html>
"""


def get_aktuell_concert(data: dict) -> dict:
    home = data["home"]
    if home.get("aktuellMode") == "auto":
        today = datetime.date.today().isoformat()
        upcoming = [
            c for c in data.get("concerts", [])
            if c.get("dateIso", "") >= today
        ]
        upcoming.sort(key=lambda c: c.get("dateIso", ""))
        if upcoming:
            nxt = upcoming[0]
            return {
                "label": "Aktuell:",
                "dateDisplay": format_concert_date(nxt),
                "location": nxt.get("location", ""),
                "program": nxt.get("title", ""),
                "note": nxt.get("details", ""),
            }
        # Fallback to most recent concert in list if none in future
        if data.get("concerts"):
            top = data["concerts"][0]
            return {
                "label": "Aktuell:",
                "dateDisplay": format_concert_date(top),
                "location": top.get("location", ""),
                "program": top.get("title", ""),
                "note": top.get("details", ""),
            }
    return home.get("aktuellConcert", {})


def build_home(data: dict) -> str:
    home = data["home"]
    akt = get_aktuell_concert(data)
    program_lines = akt.get("program", "")
    if akt.get("note"):
        program_lines = f"{program_lines}\n{akt['note']}".strip()

    body = f"""    <section class="page-banner home-hero" style="background-image: url('{esc(rel_asset(home['heroImage'], '.'))}');">
      <div class="page-banner-content">
        <h1>{esc(home['heroTitle'])}</h1>
        <a href="./konzerte/" class="btn-hero">{esc(home['heroButtonLabel'])}</a>
      </div>
    </section>

    <div class="container">
      <div class="home-grid">
        <div class="home-card home-card-aktuell">
          <span class="aktuell-badge">{esc(akt.get('label', 'Aktuell:'))}</span>
          <div class="aktuell-date">{esc(akt.get('dateDisplay', ''))}</div>
          <div class="aktuell-location">{esc(akt.get('location', ''))}</div>
          <div class="aktuell-program">{esc(program_lines)}</div>
          <a href="./konzerte/" class="aktuell-link">Alle Konzertdaten →</a>
        </div>

        <div class="home-card home-card-about">
          <h2>{esc(home['aboutTitle'])}</h2>
          <p>{esc(home['aboutText'])}</p>
        </div>
      </div>

      <div class="home-Listen-banner">
        <div class="home-nature-photo" style="background-image: url('{esc(rel_asset(home['secondaryImage'], '.'))}');"></div>
        <div class="home-listen-box" style="background-image: url('{esc(rel_asset(home['listenImage'], '.'))}');">
          <a href="./hoerbeispiele/">{esc(home['listenTitle'])}</a>
        </div>
      </div>
    </div>"""
    return render_shell(data, "home", "HOME", body)


def render_concert_item(c: dict, is_upcoming: bool = False) -> str:
    cls = "concert-item upcoming" if is_upcoming else "concert-item"
    link_html = ""
    if c.get("linkUrl"):
        lbl = c.get("linkLabel") or c["linkUrl"]
        link_html = f'\n            <a href="{esc(c["linkUrl"])}" target="_blank" rel="noopener noreferrer" class="concert-link">{esc(lbl)} →</a>'

    return f"""        <article class="{cls}">
          <div class="concert-meta">
            <div class="concert-date">{esc(format_concert_date(c))}</div>
            <div class="concert-location">{esc(c.get('location', ''))}</div>
          </div>
          <div class="concert-body">
            <h3>{esc(c.get('title', ''))}</h3>
            <div class="concert-details">{esc(c.get('details', ''))}</div>{link_html}
          </div>
        </article>"""


def build_konzerte(data: dict) -> str:
    concerts = sorted(
        data.get("concerts", []),
        key=lambda x: x.get("dateIso", ""),
        reverse=True,
    )
    items_html = "\n".join(render_concert_item(c, idx == 0) for idx, c in enumerate(concerts))

    body = f"""    <section class="page-banner banner-konzerte" style="background-image: url('../assets/images/banner-konzerte.jpg');">
      <div class="page-banner-content">
        <h1>KONZERTE</h1>
      </div>
    </section>

    <div class="container">
      <div class="concerts-list">
{items_html}
      </div>
    </div>"""
    return render_shell(data, "konzerte", "KONZERTE", body)


def build_verschiedenes(data: dict) -> str:
    v = data["verschiedenes"]
    cards_html = []
    for card in v.get("cards", []):
        color_cls = f"color-{card.get('color', 'sage')}"
        cards_html.append(f"""        <div class="feature-card {esc(color_cls)}">
          <h3>{esc(card.get('title', ''))}</h3>
          <div class="subtitle">{esc(card.get('subtitle', ''))}</div>
          <p>{esc(card.get('text', ''))}</p>
        </div>""")

    body = f"""    <section class="page-banner banner-verschiedenes" style="background-image: url('{esc(rel_asset(v['bannerImage'], '..'))}');">
      <div class="page-banner-content">
        <h1>{esc(v['title'])}</h1>
      </div>
    </section>

    <div class="container">
      <div class="feature-cards-grid">
{chr(10).join(cards_html)}
      </div>
    </div>"""
    return render_shell(data, "verschiedenes", "VERSCHIEDENES", body)


def build_lebenslauf(data: dict) -> str:
    leb = data["lebenslauf"]
    paras = "\n        ".join(f"<p>{esc(p)}</p>" for p in leb.get("paragraphs", []))

    body = f"""    <section class="page-banner banner-lebenslauf" style="background-image: url('{esc(rel_asset(leb['bannerImage'], '..'))}');">
      <div class="page-banner-content">
        <h1>{esc(leb['title'])}</h1>
      </div>
    </section>

    <div class="container">
      <article class="bio-card">
        <h2>{esc(leb['heading'])}</h2>
        {paras}
      </article>
    </div>"""
    return render_shell(data, "lebenslauf", "LEBENSLAUF", body)


def build_unterricht(data: dict) -> str:
    u = data["unterricht"]
    cards_html = []
    for inst in u.get("institutions", []):
        color_cls = f"color-{inst.get('color', 'rose')}"
        li_html = "\n            ".join(f"<li>{esc(item)}</li>" for item in inst.get("items", []))
        cards_html.append(f"""        <div class="feature-card {esc(color_cls)}">
          <h3>{esc(inst.get('shortName', inst.get('name', '')))}</h3>
          <div class="subtitle">{esc(inst.get('name', ''))}</div>
          <ul>
            {li_html}
          </ul>
        </div>""")

    body = f"""    <section class="page-banner banner-unterricht" style="background-image: url('{esc(rel_asset(u['bannerImage'], '..'))}');">
      <div class="page-banner-content">
        <h1>{esc(u['title'])}</h1>
      </div>
    </section>

    <div class="container">
      <h2 class="section-heading">{esc(u['heading'])}</h2>
      <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 2rem;">{esc(u['subheading'])}</p>
      <div class="feature-cards-grid">
{chr(10).join(cards_html)}
      </div>
    </div>"""
    return render_shell(data, "unterricht", "UNTERRICHT", body)


def build_hoerbeispiele(data: dict) -> str:
    h = data["hoerbeispiele"]
    albums_html = []
    play_svg = '<svg viewBox="0 0 18 20"><path d="M17.29,9.02 C18.25,9.56 18.25,10.44 17.29,10.98 L1.74,19.78 C0.78,20.33 0,19.87 0,18.76 L0,1.24 C0,0.13 0.78,-0.32 1.74,0.22 L17.29,9.02 Z"></path></svg>'

    for album in h.get("albums", []):
        tracks_html = []
        for t in album.get("tracks", []):
            dur = t.get("duration", "00:30")
            sub = f'<span class="track-subtitle">{esc(t["subtitle"])}</span>' if t.get("subtitle") else ""
            tracks_html.append(f"""            <div class="audio-track" data-duration="{esc(dur)}">
              <button type="button" class="play-btn" aria-label="Abspielen: {esc(t['title'])}">{play_svg}</button>
              <div class="track-info">
                <div class="track-title-row">
                  <div><span class="track-title">{esc(t['title'])}</span>{sub}</div>
                  <span class="track-time">00:00 / {esc(dur)}</span>
                </div>
                <input type="range" class="track-progress" min="0" max="30" step="0.1" value="0" aria-label="Fortschritt" />
              </div>
              <audio preload="metadata" src="{esc(rel_asset(t['audioUrl'], '..'))}"></audio>
            </div>""")

        albums_html.append(f"""      <section class="album-section">
        <div class="album-header">
          <h2>{esc(album['title'])}</h2>
          <p>{esc(album['description'])}</p>
        </div>
        <div class="album-grid">
          <img src="{esc(rel_asset(album['coverImage'], '..'))}" alt="{esc(album['title'])}" class="album-cover" />
          <div class="tracks-list">
{chr(10).join(tracks_html)}
          </div>
        </div>
      </section>""")

    body = f"""    <section class="page-banner banner-hoerbeispiele" style="background-image: url('{esc(rel_asset(h['bannerImage'], '..'))}');">
      <div class="page-banner-content">
        <h1>{esc(h['title'])}</h1>
      </div>
    </section>

    <div class="container">
{chr(10).join(albums_html)}
    </div>"""
    return render_shell(data, "hoerbeispiele", "HÖRBEISPIELE", body)


def build_links(data: dict) -> str:
    l = data["links"]
    cards_html = []
    for item in l.get("items", []):
        cards_html.append(f"""        <a href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer" class="link-card">
          <div>
            <h3>{esc(item['title'])}</h3>
            <p>{esc(item.get('description', ''))}</p>
          </div>
          <span>Website öffnen →</span>
        </a>""")

    body = f"""    <section class="page-banner banner-links" style="background-image: url('{esc(rel_asset(l['bannerImage'], '..'))}');">
      <div class="page-banner-content">
        <h1>{esc(l['title'])}</h1>
      </div>
    </section>

    <div class="container">
      <h2 class="section-heading">{esc(l.get('note', 'Links'))}</h2>
      <div class="links-grid">
{chr(10).join(cards_html)}
      </div>
    </div>"""
    return render_shell(data, "links", "LINKS", body)


def build_sitemap() -> str:
    base_url = "https://www.magda-schwerzmann.ch"
    today = datetime.date.today().isoformat()
    urls = []
    for _key, _label, href in NAV_ITEMS:
        loc = f"{base_url}/" if href == "/" else f"{base_url}{href.rstrip('/')}"
        urls.append(f"""  <url>
    <loc>{esc(loc)}</loc>
    <lastmod>{today}</lastmod>
  </url>""")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build_all() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    outputs = {
        ROOT / "index.html": build_home(data),
        ROOT / "konzerte" / "index.html": build_konzerte(data),
        ROOT / "verschiedenes" / "index.html": build_verschiedenes(data),
        ROOT / "lebenslauf" / "index.html": build_lebenslauf(data),
        ROOT / "unterricht" / "index.html": build_unterricht(data),
        ROOT / "hoerbeispiele" / "index.html": build_hoerbeispiele(data),
        ROOT / "links" / "index.html": build_links(data),
        ROOT / "sitemap.xml": build_sitemap(),
    }

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Built {path.relative_to(ROOT)}")


if __name__ == "__main__":
    build_all()
