# magda-schwerzmann.ch

Statische Website mit integriertem visuellen Editor (`/admin/`) für **Magda Schwerzmann**.
Komplett unabhängig von Wix (CHF 0.– Hosting-Kosten auf GitHub Pages, Cloudflare Pages oder Raspberry Pi).

## Lokal starten & bearbeiten

```bash
python3 server.py 8080
```

- **Website:** http://localhost:8080/
- **Visueller Editor (CMS):** http://localhost:8080/admin/

Alle Inhalte sind in [`data/content.json`](data/content.json) gespeichert. Beim Klick auf **«💾 Änderungen speichern»** im Editor wird `data/content.json` aktualisiert und [`build.py`](build.py) generiert sofort alle 7 HTML-Seiten neu.

## Kostenloses Hosting auf GitHub Pages

1. Dieses Verzeichnis als GitHub-Repository pushen (Branch `main`).
2. In den Repository-Einstellungen unter **Settings → Pages → Build and deployment** als Source **GitHub Actions** auswählen.
3. Die enthaltene Workflow-Datei [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) baut und veröffentlicht die Seite bei jeder Änderung automatisch.
4. Damit deine Gotte direkt im Browser unter `https://www.magda-schwerzmann.ch/admin/` bearbeiten kann:
   - Auf GitHub unter **Settings → Developer settings → Personal access tokens → Fine-grained tokens** ein Token erstellen, das **nur auf dieses eine Repository** Zugriff hat (`Contents: Read and write`).
   - Einmalig auf Ihrem Computer/Tablet unter `/admin/` im Reiter **«☁️ GitHub / Cloud»** das Repository (`dein-name/magda-website`) und das Token eintragen. Danach kann sie jederzeit mit einem Klick Konzerte und Texte speichern.

## DNS-Umzug von Wix (ohne E-Mail-Unterbruch)

Die E-Mail (`info@magda-schwerzmann.ch`) läuft bereits über **Zoho Mail EU** (`mx.zoho.eu`), nicht über Wix. Beim Umzug der Domain weg von den Wix-Nameservern (`ns12.wixdns.net`) müssen beim Domain-Registrar (oder Cloudflare DNS) lediglich folgende Einträge übernommen werden:

- **Web (`A` / `CNAME`):** auf GitHub Pages oder Cloudflare Pages zeigen lassen.
- **E-Mail (`MX`):**
  - `10 mx.zoho.eu.`
  - `20 mx2.zoho.eu.`
  - `50 mx3.zoho.eu.`
- **SPF (`TXT`):** bestehenden `v=spf1 include:zoho.eu ~all` Eintrag übernehmen.
