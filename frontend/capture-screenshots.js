const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOTS_DIR = path.join(__dirname, '..', 'docs', 'screenshots');
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

async function captureScreenshots() {
  const screenshots = [];
  let browser;

  try {
    // Ensure screenshots directory exists
    if (!fs.existsSync(SCREENSHOTS_DIR)) {
      fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    }

    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    console.log(`Navigating to ${BASE_URL}...`);

    // Navigate to the app
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000); // Wait for any animations

    // Hero screenshot - main view
    const heroPath = path.join(SCREENSHOTS_DIR, 'hero.png');
    await page.screenshot({ path: heroPath, fullPage: false });
    screenshots.push({
      filename: 'hero.png',
      path: 'docs/screenshots/hero.png',
      type: 'hero',
      description: 'Main application view - YouTube Transcript Downloader'
    });
    console.log('✓ Captured hero.png');

    // Feature 1: Single Download Tab (should be default)
    const singleTabPath = path.join(SCREENSHOTS_DIR, 'feature-01-single-download.png');
    await page.screenshot({ path: singleTabPath, fullPage: false });
    screenshots.push({
      filename: 'feature-01-single-download.png',
      path: 'docs/screenshots/feature-01-single-download.png',
      type: 'feature',
      description: 'Single video transcript download interface'
    });
    console.log('✓ Captured feature-01-single-download.png');

    // Try to click Bulk tab if it exists
    try {
      const bulkTab = await page.$('text=Bulk');
      if (bulkTab) {
        await bulkTab.click();
        await page.waitForTimeout(500);

        const bulkPath = path.join(SCREENSHOTS_DIR, 'feature-02-bulk-download.png');
        await page.screenshot({ path: bulkPath, fullPage: false });
        screenshots.push({
          filename: 'feature-02-bulk-download.png',
          path: 'docs/screenshots/feature-02-bulk-download.png',
          type: 'feature',
          description: 'Bulk playlist/channel download interface'
        });
        console.log('✓ Captured feature-02-bulk-download.png');
      }
    } catch (e) {
      console.log('Note: Bulk tab not found, skipping');
    }

    // Full page screenshot
    const fullPagePath = path.join(SCREENSHOTS_DIR, 'full-page.png');
    await page.screenshot({ path: fullPagePath, fullPage: true });
    screenshots.push({
      filename: 'full-page.png',
      path: 'docs/screenshots/full-page.png',
      type: 'feature',
      description: 'Full page view of the application'
    });
    console.log('✓ Captured full-page.png');

    // Mobile viewport screenshot
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    const mobilePath = path.join(SCREENSHOTS_DIR, 'feature-03-mobile.png');
    await page.screenshot({ path: mobilePath, fullPage: false });
    screenshots.push({
      filename: 'feature-03-mobile.png',
      path: 'docs/screenshots/feature-03-mobile.png',
      type: 'feature',
      description: 'Mobile responsive view'
    });
    console.log('✓ Captured feature-03-mobile.png');

    await browser.close();

    // Write manifest
    const manifest = {
      generated: new Date().toISOString(),
      baseURL: BASE_URL,
      projectType: 'web-app',
      screenshots: screenshots,
      total: screenshots.length,
      failed: 0
    };

    fs.writeFileSync(
      path.join(SCREENSHOTS_DIR, 'manifest.json'),
      JSON.stringify(manifest, null, 2)
    );

    console.log(`\n✅ Screenshot capture complete!`);
    console.log(`Total: ${screenshots.length} screenshots`);
    console.log(`Location: ${SCREENSHOTS_DIR}`);

  } catch (error) {
    console.error('Screenshot capture failed:', error.message);
    if (browser) await browser.close();
    process.exit(1);
  }
}

captureScreenshots();
