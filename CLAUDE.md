# Pensanta Website Enhancement Project

## Project Overview
Professional project management consultancy website with bilingual support (Spanish/English), focusing on minimal design, accessibility, and performance.

## Design System

### Core Philosophy
- **Mobile-first**: Design for mobile, enhance for larger screens
- **Semantic-first**: HTML5 elements over divs/spans
- **Minimal CSS**: Only essential styles, no bloat
- **Dark-theme default**: Modern, professional appearance
- **Accessibility-first**: WCAG 2.1 AA compliance minimum
- **Performance-focused**: Fast loading, minimal resources

### Color Palette
```css
:root {
  /* Primary Colors */
  --color-background: #000000;
  --color-surface: #111111;
  --color-surface-elevated: #222222;
  
  /* Text Colors */
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-muted: #a0a0a0;
  
  /* Accent Colors */
  --color-accent: #4a9eff;
  --color-accent-hover: #2980ff;
  --color-success: #00d084;
  --color-warning: #ffb800;
  --color-error: #ff5722;
  
  /* Border Colors */
  --color-border-primary: #404040;
  --color-border-secondary: #606060;
}
```

### Spacing System (rem-based)
```css
:root {
  --space-xs: 0.25rem;    /* 4px */
  --space-sm: 0.5rem;     /* 8px */
  --space-md: 1rem;       /* 16px */
  --space-lg: 1.5rem;     /* 24px */
  --space-xl: 2rem;       /* 32px */
  --space-2xl: 3rem;      /* 48px */
  --space-3xl: 4rem;      /* 64px */
}
```

### Typography Scale
```css
:root {
  --font-family-primary: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", sans-serif;
  --font-family-mono: "SF Mono", "Monaco", "Inconsolata", "Fira Code", "Droid Sans Mono", monospace;
  
  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-lg: 1.125rem;  /* 18px */
  --font-size-xl: 1.25rem;   /* 20px */
  --font-size-2xl: 1.5rem;   /* 24px */
  --font-size-3xl: 2rem;     /* 32px */
  --font-size-4xl: 2.5rem;   /* 40px */
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Border Radius System
```css
:root {
  --radius-sm: 0.25rem;    /* 4px */
  --radius-md: 0.5rem;     /* 8px */
  --radius-lg: 1rem;       /* 16px */
  --radius-xl: 1.5rem;     /* 24px */
  --radius-full: 9999px;   /* Full rounded */
}
```

## Semantic HTML Guidelines

### Required Elements
- `<header>` with proper `role="banner"`
- `<nav>` with `role="navigation"` and `aria-label`
- `<main>` with `role="main"` and `id="main-content"`
- `<section>` for distinct content areas with headings
- `<footer>` with `role="contentinfo"`

### Accessibility Requirements
- Skip navigation links
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels for interactive elements
- Focus management and keyboard navigation
- Color contrast ratio 4.5:1 minimum
- Alternative text for images
- Form labels and descriptions

## Performance Standards

### Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

### Optimization Strategies
- Minimize CSS and eliminate unused styles
- Optimize images (WebP format, proper sizing)
- Use system fonts to avoid font loading delays
- Implement critical CSS inlining
- Minimize JavaScript usage

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

## File Organization
```
/
├── index.html (Spanish)
├── index-eng.html (English)
├── css/
│   ├── styles.css (main stylesheet)
│   └── critical.css (above-the-fold styles)
├── img/
│   ├── *.webp (optimized images)
│   └── *.svg (icons and graphics)
└── js/ (if needed)
    └── main.js (progressive enhancement only)
```

## Enhancement Priorities

### Phase 1: Foundation (High Impact)
1. Standardize semantic HTML across both language versions
2. Implement consistent accessibility features
3. Modernize CSS organization with custom properties
4. Optimize responsive design for mobile-first approach

### Phase 2: Polish (Medium Impact)
1. Enhance visual design with micro-interactions
2. Implement performance optimizations
3. Add progressive enhancement features
4. Improve SEO and metadata consistency

### Phase 3: Advanced (Low Impact)
1. Advanced animations and transitions
2. Service worker for offline functionality
3. Advanced analytics and tracking
4. A/B testing capabilities

## Code Quality Standards

### CSS
- Use CSS custom properties for all design tokens
- Follow BEM methodology for class naming
- Group related styles logically
- Use progressive enhancement approach
- Minimize specificity conflicts

### HTML
- Validate against HTML5 standards
- Ensure semantic meaning over visual appearance
- Use appropriate ARIA attributes
- Maintain consistent indentation (2 spaces)
- Include proper meta tags and structured data

### General
- Mobile-first responsive design
- Progressive enhancement over graceful degradation
- Performance budget: < 100KB initial page load
- Accessibility testing with screen readers
- Cross-browser testing on target browsers

## Testing Checklist

### Accessibility
- [ ] Screen reader compatibility (NVDA, JAWS, VoiceOver)
- [ ] Keyboard navigation functionality
- [ ] Color contrast validation
- [ ] Focus indicator visibility
- [ ] ARIA attributes correctness

### Performance
- [ ] Lighthouse score > 90 for all metrics
- [ ] WebPageTest analysis
- [ ] Mobile performance testing
- [ ] Image optimization validation
- [ ] CSS and JS minification

### Compatibility
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Print stylesheet functionality
- [ ] High contrast mode support
- [ ] Reduced motion preferences

## Deployment Considerations
- Use semantic versioning for releases
- Implement proper caching strategies
- Ensure HTTPS certificate validity
- Monitor Core Web Vitals in production
- Regular accessibility audits

---
*This document serves as the source of truth for all design and development decisions on the Pensanta website project.*