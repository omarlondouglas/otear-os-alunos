# Google Maps Scapping - IP Blocking Reference

## Problem: Google Blocks Datacenter IPs

Google Maps aggressively blocks access from datacenter IPs (VPS, cloud providers). When detected, it redirects to `consent.google.com` and **never accepts the consent button click** — regardless of method.

## What Was Tried (All Failed on Datacenter IP)

| Method | Result |
|--------|--------|
| `browser_navigate` to Google Maps | Redirects to consent.google.com |
| `browser_click` on "Accept" button | Click doesn't advance page |
| `browser_console` JS click | Button doesn't respond |
| `browser_console` cookie injection (`document.cookie`) | Ignored by Google |
| Playwright with `locale: pt-BR, timezone: America/Sao_Paulo` | Still redirects to consent |
| Playwright with `context.add_cookies()` (21 real cookies) | Still redirects to consent |
| Page reload after consent attempt | Stays on consent page |
| DuckDuckGo HTML version | Results in iframe, can't extract |
| Google Search (`/search?q=...&tbm=lcl`) | CAPTCHA block |

## Root Cause

Google determines datacenter IP by:
- IP range reputation (known cloud/VPS ranges)
- Missing residential ISP signals
- TLS fingerprinting
- Behavioral patterns

**Cookies alone cannot bypass this.** The consent page is IP-based, not cookie-based.

## Working Alternatives

1. **Run script on residential IP** — The `scripts/scraper.py` Playwright script works perfectly on home internet connections
2. **Google Places API** — Paid but reliable, works from any IP with valid API key
3. **Residential proxy** — Services like Bright Data, Oxylabs (complex, paid)
4. **Manual search** — User searches Google Maps manually and shares results

## Detection Script

To check if an IP is blocked:

```bash
curl -s -o /dev/null -w "%{http_code}" "https://www.google.com/maps/search/test"
# 200 = OK, 302 = redirect to consent (blocked)
```

## Session Details (2026-06-19)

- **Server IP:** 49.13.218.249 (German datacenter)
- **Target:** `empresas de energia solar em Rio das Ostras`
- **Cookies provided:** 21 real Google cookies (SID, HSID, SSID, NID, etc.)
- **Result:** All approaches failed — Google forced consent page regardless
- **Conclusion:** Must use residential IP or Google Places API
