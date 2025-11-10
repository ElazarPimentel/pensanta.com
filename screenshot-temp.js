const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: 'new'});
  const page = await browser.newPage();
  await page.setViewport({width: 800, height: 500});
  await page.goto('https://lodevictor.com/', {waitUntil: 'networkidle2', timeout: 30000});
  await page.screenshot({path: 'img/portfolio/lodevictor-800x500.png'});
  console.log('✓ Saved: img/portfolio/lodevictor-800x500.png');
  await browser.close();
})();
