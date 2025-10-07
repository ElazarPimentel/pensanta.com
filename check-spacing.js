const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  await page.goto('http://127.0.0.1:8080/index-eng.html');

  // Get spacing info for section-top and nav
  const spacing = await page.evaluate(() => {
    const elements = {
      'section-top': document.querySelector('.section-top'),
      'section-top nav': document.querySelector('.section-top nav'),
      'nav-link (Tools button)': document.querySelector('.nav-link')
    };

    const results = {};

    for (const [name, el] of Object.entries(elements)) {
      if (!el) continue;
      const styles = window.getComputedStyle(el);
      results[name] = {
        marginTop: styles.marginTop,
        marginBottom: styles.marginBottom,
        paddingTop: styles.paddingTop,
        paddingBottom: styles.paddingBottom,
        display: styles.display,
        justifyContent: styles.justifyContent
      };
    }

    return results;
  });

  console.log('Section Top Spacing Analysis:\n');
  for (const [element, values] of Object.entries(spacing)) {
    console.log(`${element}:`);
    console.log(`  Margin: ${values.marginTop} (top) / ${values.marginBottom} (bottom)`);
    console.log(`  Padding: ${values.paddingTop} (top) / ${values.paddingBottom} (bottom)`);
    console.log(`  Display: ${values.display}`);
    if (values.justifyContent) console.log(`  Justify: ${values.justifyContent}`);
    console.log('');
  }

  await browser.close();
})();
