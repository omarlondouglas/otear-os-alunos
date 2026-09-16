const { chromium } = require('playwright');
const path = require('path');

const PROFILE_DIR = path.join(__dirname, '..', '..', '_opensquad', '_browser_profile');

(async () => {
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: true,
    channel: 'chrome',
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
  });

  const page = context.pages()[0] || await context.newPage();

  try {
    await page.goto('https://www.instagram.com/brandsdecoded__/', { waitUntil: 'networkidle', timeout: 30000 });
    await new Promise(r => setTimeout(r, 5000));

    // Take screenshot
    await page.screenshot({ path: path.join(__dirname, 'output', '2026-03-14-092007', '_debug-page.jpg'), quality: 80, type: 'jpeg', fullPage: false });
    console.log('Screenshot salvo');

    // Check page title and URL
    console.log('URL:', page.url());
    console.log('Title:', await page.title());

    // Check for login form
    const hasLoginForm = await page.$('input[name="username"]');
    console.log('Login form present:', !!hasLoginForm);

    // Check for login required page
    const bodyText = await page.textContent('body');
    if (bodyText.includes('Log in') || bodyText.includes('Entrar')) {
      console.log('STATUS: Precisa de login!');
    }

    // Try to find any links
    const allLinks = await page.$$eval('a', links => links.map(a => a.href).filter(h => h.includes('/p/')));
    console.log('Post links found:', allLinks.length);
    if (allLinks.length > 0) {
      console.log('First 3:', allLinks.slice(0, 3));
    }

    // Try different selectors for posts
    const selectors = [
      'article a[href*="/p/"]',
      'main a[href*="/p/"]',
      'a[href*="/p/"]',
      'div._ac7v a',
      'div[style] a[href*="/p/"]'
    ];
    for (const sel of selectors) {
      const count = await page.$$eval(sel, els => els.length).catch(() => 0);
      console.log(`Selector "${sel}": ${count} elements`);
    }

  } catch(err) {
    console.error('Error:', err.message);
  } finally {
    await context.close();
  }
})();
