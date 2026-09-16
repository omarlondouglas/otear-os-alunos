const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const USERNAME = 'brandsdecoded__';
const MAX_POSTS = 10;
const RUN_ID = '2026-03-14-092007';
const OUTPUT_BASE = path.join(__dirname, 'output', RUN_ID, USERNAME);
const PROFILE_DIR = path.join(__dirname, '..', '..', '_opensquad', '_browser_profile');

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function dismissPopups(page) {
  // Close "Log in" / "Ver mais conteudo" modals
  const closeSelectors = [
    'svg[aria-label="Close"], svg[aria-label="Fechar"]',
    'button:has(svg[aria-label="Close"]), button:has(svg[aria-label="Fechar"])',
    'div[role="dialog"] button:first-child',
    'div[role="dialog"] [role="button"]'
  ];
  for (const sel of closeSelectors) {
    try {
      const btn = await page.$(sel);
      if (btn) {
        await btn.click();
        await sleep(1000);
        return true;
      }
    } catch(e) {}
  }
  // Try pressing Escape
  try {
    await page.keyboard.press('Escape');
    await sleep(1000);
  } catch(e) {}
  return false;
}

(async () => {
  console.log('📸 Scraper iniciando...');
  console.log(`Perfil: @${USERNAME} | Posts: ${MAX_POSTS}\n`);

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: true,
    channel: 'chrome',
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
  });

  const page = context.pages()[0] || await context.newPage();

  try {
    // Phase 1: Navigate to profile
    console.log('🔍 Acessando perfil...');
    await page.goto(`https://www.instagram.com/${USERNAME}/`, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(4000);

    // Dismiss login popup
    await dismissPopups(page);
    await sleep(1000);
    await dismissPopups(page);
    await sleep(1000);

    // Scroll to load posts
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() => window.scrollBy(0, 600));
      await sleep(1500);
      await dismissPopups(page);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await sleep(1500);

    // Phase 2: Collect post links
    console.log('🔍 Coletando links dos posts...');
    const postLinks = await page.$$eval('a[href*="/p/"]', (links) => {
      const seen = new Set();
      return links
        .map(a => a.getAttribute('href'))
        .filter(href => {
          if (!href || seen.has(href)) return false;
          seen.add(href);
          return href.match(/^\/[A-Za-z0-9_.-]+\/p\/[A-Za-z0-9_-]+\//) || href.match(/^\/p\/[A-Za-z0-9_-]+\//);
        });
    });

    console.log(`📋 Encontrados ${postLinks.length} posts`);
    const postsToScrape = postLinks.slice(0, MAX_POSTS);
    console.log(`📋 Coletando ${postsToScrape.length} posts...\n`);

    const report = [];
    let totalSlides = 0;

    // Phase 3: Open each post and capture slides
    for (let i = 0; i < postsToScrape.length; i++) {
      const postHref = postsToScrape[i];
      const shortcode = postHref.match(/\/p\/([A-Za-z0-9_-]+)\//)?.[1] || `unknown-${i+1}`;
      const postDir = path.join(OUTPUT_BASE, `post-${String(i+1).padStart(2,'0')}`);
      fs.mkdirSync(postDir, { recursive: true });

      console.log(`📸 Post ${i+1}/${postsToScrape.length}: ${shortcode}`);

      // Navigate to individual post
      await page.goto(`https://www.instagram.com/p/${shortcode}/`, { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(3000);
      await dismissPopups(page);
      await sleep(1000);

      let slideCount = 0;

      // Capture slide function
      const captureSlide = async (slideNum) => {
        // Find main post image - try multiple selectors
        const imgSelectors = [
          'article div[role="presentation"] img',
          'article img[sizes]',
          'article ul img[src*="scontent"]',
          'article img[src*="scontent"]',
          'img[src*="scontent"][style*="object-fit"]',
          'div[role="presentation"] img',
          'img[sizes][src*="scontent"]'
        ];

        for (const sel of imgSelectors) {
          const imgs = await page.$$(sel);
          // Get the last visible one (carousel shows current slide last)
          const img = imgs.length > 0 ? imgs[imgs.length - 1] : null;
          if (img) {
            const src = await img.getAttribute('src');
            if (src && src.includes('scontent')) {
              const slidePath = path.join(postDir, `slide-${String(slideNum).padStart(2,'0')}.jpg`);

              // Try direct download first
              try {
                const response = await page.request.get(src);
                const buffer = await response.body();
                if (buffer.length > 5000) { // Valid image (not a tiny placeholder)
                  fs.writeFileSync(slidePath, buffer);
                  console.log(`  ✓ slide-${String(slideNum).padStart(2,'0')}.jpg (${Math.round(buffer.length/1024)}KB)`);
                  return true;
                }
              } catch(e) {}

              // Fallback: element screenshot
              try {
                await img.screenshot({ path: slidePath, quality: 95, type: 'jpeg' });
                const stat = fs.statSync(slidePath);
                if (stat.size > 5000) {
                  console.log(`  ✓ slide-${String(slideNum).padStart(2,'0')}.jpg (screenshot ${Math.round(stat.size/1024)}KB)`);
                  return true;
                }
              } catch(e) {}
            }
          }
        }

        // Last resort: screenshot the whole article
        const article = await page.$('article');
        if (article) {
          const slidePath = path.join(postDir, `slide-${String(slideNum).padStart(2,'0')}.jpg`);
          await article.screenshot({ path: slidePath, quality: 90, type: 'jpeg' });
          console.log(`  ✓ slide-${String(slideNum).padStart(2,'0')}.jpg (full article)`);
          return true;
        }
        return false;
      };

      // Capture first slide
      if (await captureSlide(1)) {
        slideCount = 1;
      }

      // Navigate carousel slides
      let attempts = 0;
      while (attempts < 15) {
        const nextBtn = await page.$('button[aria-label="Next"], button[aria-label="Avançar"], button[aria-label="Próximo"], button[aria-label="Go Forward"]');
        if (!nextBtn) break;

        try {
          const isVisible = await nextBtn.isVisible();
          if (!isVisible) break;
          await nextBtn.click();
          await sleep(1500);
          slideCount++;
          await captureSlide(slideCount);
          attempts++;
        } catch(e) {
          break;
        }
      }

      totalSlides += slideCount;
      report.push({ shortcode, slides: slideCount });
      console.log(`  → ${slideCount} slide(s)\n`);

      // Wait between posts (natural behavior)
      if (i < postsToScrape.length - 1) {
        const wait = 3000 + Math.floor(Math.random() * 3000);
        await sleep(wait);
      }
    }

    // Phase 4: Report
    const reportMd = `# Scraping Report — @${USERNAME}

## Resumo
- **Perfil:** @${USERNAME}
- **Posts coletados:** ${report.length}
- **Total de slides:** ${totalSlides}
- **Data:** ${new Date().toISOString().split('T')[0]}

## Posts

${report.map((r, i) => `${i+1}. \`/${r.shortcode}/\` — ${r.slides} slide(s)`).join('\n')}

## Arquivos

Salvos em: \`squads/instagram-scraper/output/${RUN_ID}/${USERNAME}/\`
`;

    fs.writeFileSync(path.join(OUTPUT_BASE, '..', 'report.md'), reportMd);

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('SCRAPING COMPLETO');
    console.log(`Perfil:     @${USERNAME}`);
    console.log(`Posts:      ${report.length} coletados`);
    console.log(`Imagens:    ${totalSlides} slides baixados`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  } catch(err) {
    console.error('❌ Erro:', err.message);
  } finally {
    await context.close();
  }
})();
