const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.goto('http://127.0.0.1:8080/', { waitUntil: 'networkidle0' });

  const spacing = await page.evaluate(() => {
    const navButton = document.querySelector('.nav-link');
    const mainElement = document.querySelector('main');
    const sectionTop = document.querySelector('.section-top');
    const nav = document.querySelector('.section-top nav');

    const mainStyles = window.getComputedStyle(mainElement);
    const sectionTopStyles = window.getComputedStyle(sectionTop);
    const navStyles = window.getComputedStyle(nav);
    const buttonStyles = window.getComputedStyle(navButton);

    return {
      main: {
        paddingTop: mainStyles.paddingTop,
        paddingBottom: mainStyles.paddingBottom,
        paddingLeft: mainStyles.paddingLeft,
        paddingRight: mainStyles.paddingRight,
        borderTop: mainStyles.borderTop,
      },
      sectionTop: {
        marginTop: sectionTopStyles.marginTop,
        paddingTop: sectionTopStyles.paddingTop,
      },
      nav: {
        marginTop: navStyles.marginTop,
        paddingTop: navStyles.paddingTop,
      },
      button: {
        marginTop: buttonStyles.marginTop,
        paddingTop: buttonStyles.paddingTop,
      }
    };
  });

  console.log('Pensanta Detailed Spacing:');
  console.log('==========================');
  console.log('Main:', spacing.main);
  console.log('Section-top:', spacing.sectionTop);
  console.log('Nav:', spacing.nav);
  console.log('Button:', spacing.button);

  await browser.close();
})();
