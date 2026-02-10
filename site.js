(function () {
  const navToggle = document.querySelector('.nav-toggle')
  const navLinks = document.querySelector('.nav-links')
  const navBackdrop = document.querySelector('.nav-backdrop')

  if (navToggle && navLinks && navBackdrop) {
    const openLabel = navToggle.getAttribute('aria-label') || 'Open menu'
    const closeLabel = navBackdrop.getAttribute('aria-label') || 'Close menu'

    const setMenuOpen = isOpen => {
      navLinks.classList.toggle('open', isOpen)
      navBackdrop.classList.toggle('show', isOpen)
      navToggle.setAttribute('aria-expanded', String(isOpen))
      navToggle.setAttribute('aria-label', isOpen ? closeLabel : openLabel)
      document.body.style.overflow = isOpen ? 'hidden' : ''
    }

    navToggle.addEventListener('click', () => {
      setMenuOpen(!navLinks.classList.contains('open'))
    })

    navBackdrop.addEventListener('click', () => setMenuOpen(false))

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => setMenuOpen(false))
    })
  }

  document.querySelectorAll('[data-track-whatsapp]').forEach(link => {
    link.addEventListener('click', () => {
      if (typeof window.trackWhatsAppConversion === 'function') {
        window.trackWhatsAppConversion()
      }
    })
  })

  document.querySelectorAll('[data-portfolio-name]').forEach(link => {
    link.addEventListener('click', () => {
      if (typeof window.trackPortfolioClick === 'function') {
        window.trackPortfolioClick(link.dataset.portfolioName)
      }
    })
  })

  document.querySelectorAll('[data-track-tool]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (typeof window.trackToolUsage === 'function') {
        window.trackToolUsage(btn.dataset.trackTool)
      }
    })
  })

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReducedMotion) {
    document.querySelectorAll('video').forEach(video => {
      video.autoplay = false
      video.loop = false
      video.pause()
      video.removeAttribute('autoplay')
      video.removeAttribute('loop')
    })
  }
})()
