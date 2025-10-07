const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Navigate to the local server
  await page.goto('http://127.0.0.1:8080/', { waitUntil: 'networkidle0' });

  // Get spacing information for Tools button
  const spacing = await page.evaluate(() => {
    const toolsButton = document.querySelector('.nav-link');
    const mainElement = document.querySelector('main');

    if (!toolsButton || !mainElement) {
      return { error: 'Elements not found' };
    }

    const buttonRect = toolsButton.getBoundingClientRect();
    const mainRect = mainElement.getBoundingClientRect();

    // Get computed styles
    const navElement = document.querySelector('.section-top nav');
    const navStyles = window.getComputedStyle(navElement);

    return {
      toolsButtonTop: buttonRect.top,
      mainTop: mainRect.top,
      spaceFromMainTop: buttonRect.top - mainRect.top,
      navMarginTop: navStyles.marginTop,
      navPaddingTop: navStyles.paddingTop,
      buttonMarginTop: window.getComputedStyle(toolsButton).marginTop,
    };
  });

  console.log('Spacing Analysis:');
  console.log('=================');
  console.log(`Space from main top to Tools button: ${spacing.spaceFromMainTop}px`);
  console.log(`Nav margin-top: ${spacing.navMarginTop}`);
  console.log(`Nav padding-top: ${spacing.navPaddingTop}`);
  console.log(`Button margin-top: ${spacing.buttonMarginTop}`);

  await browser.close();
})();
