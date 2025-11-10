const puppeteer = require('puppeteer');

const sites = [
  'https://fabricademochilas.com.ar',
  'https://mochilasbaratas.com.ar',
  'https://mochilasconlogo.com.ar',
  'https://mochilaseconomicas.com.ar',
  'https://tallerdemochilas.com.ar',
  'https://cartucherasconlogo.com.ar',
  'https://cartucheraspormayor.com.ar',
  'https://kitescolaresconcartuchera.com.ar',
  'https://kitescolaresconmochila.com.ar',
  'https://fabricamosmochilas.com.ar',
  'https://officesite.com.ar'
];

(async () => {
  const browser = await puppeteer.launch({headless: 'new'});
  
  for (const url of sites) {
    try {
      const slug = url.replace('https://', '').replace('www.', '').split('/')[0].replace(/\./g, '-');
      console.log(`📸 Capturing: ${url}`);
      
      const page = await browser.newPage();
      await page.setViewport({width: 800, height: 500});
      await page.goto(url, {waitUntil: 'networkidle2', timeout: 30000});
      await page.screenshot({path: `img/portfolio/${slug}-800x500.png`});
      await page.close();
      
      console.log(`   ✓ Saved: ${slug}-800x500.png`);
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
    }
  }
  
  await browser.close();
  console.log('\n✅ All screenshots captured!');
})();
