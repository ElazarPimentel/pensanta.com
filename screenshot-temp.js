const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: 'new'});
  const page = await browser.newPage();
  await page.setViewport({width: 800, height: 500});
  await page.goto('https://draandreaesparza.com/', {waitUntil: 'networkidle2', timeout: 30000});
  await page.screenshot({path: 'img/portfolio/draandreaesparza-800x500.png'});
  console.log('✓ Saved screenshot');
  await browser.close();
})();
