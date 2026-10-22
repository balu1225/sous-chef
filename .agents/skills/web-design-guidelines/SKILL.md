---
name: web-design-guidelines
description: Standards for accessibility, responsive typography, keyboard navigation, smooth 60fps view transitions, and PWA installability.
---

# Web Design Guidelines (Vercel Agent Skills)

## 1. Ergonomics & Progressive Disclosure
- **Do Not Clutter the Primary Viewport:**
  - When the user is cooking hands-free via Alexa or an Echo Dot, the screen should be a calm, ambient display.
  - No giant blinking microphone orbs if voice is already active on the device.
  - Floating action buttons and drawers keep the workspace serene.
- **Keyboard Shortcuts (Instant Productivity):**
  - `Space`: Pause / Resume active step timer.
  - `Right Arrow` or `N`: Advance to next cooking step.
  - `Left Arrow` or `P`: Go back to previous step.
  - `/` or `C`: Open subtle voice/chat slide drawer.
  - `Escape`: Close modals and drawers.

## 2. Ultra-Smooth 60fps Motion
- Avoid animating expensive CSS properties like `width`, `height`, `top`, `left`, `margin`.
- Only animate GPU-accelerated composited properties: `transform` and `opacity`.
- Use Apple's signature spring easing: `cubic-bezier(0.16, 1, 0.3, 1)`.

## 3. PWA (Progressive Web App) Standards
- Full support for `manifest.json`.
- `apple-mobile-web-app-capable`: `yes`.
- `apple-mobile-web-app-status-bar-style`: `black-translucent`.
- Responsive viewport meta: `viewport-fit=cover`.
