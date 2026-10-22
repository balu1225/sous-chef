---
name: apple-design-system
description: Apple Human Interface Guidelines (HIG), Cupertino glassmorphism, fluid responsive layouts (Echo Show, iPad, Desktop, Mobile), kinetic macro rings, and ultra-low latency UI state management for Sous-Chef.
---

# Apple Design System & Human Interface Guidelines (HIG)

## 1. Cupertino Visual Tokens & Glassmorphism
- **Color Palette (Dark Mode Elegance):**
  - Canvas / Background: `#080b11` to `#0d131f` deep space gradient.
  - Glass Layer 1 (Base Panel): `rgba(255, 255, 255, 0.04)` with `backdrop-filter: blur(24px) saturate(180%)`.
  - Glass Layer 2 (Cards / Widgets): `rgba(255, 255, 255, 0.07)` with `border: 1px solid rgba(255, 255, 255, 0.1)`.
  - Glass Layer 3 (Active / Hover): `rgba(255, 255, 255, 0.12)` with `box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37)`.
- **System Accents:**
  - Alexa Cyan / Dynamic Glow: `#00d2ff` -> `#3a7bd5`
  - Apple Fitness Calorie Pink/Red: `#fa114f` (glow: `rgba(250, 17, 79, 0.4)`)
  - Apple Fitness Protein Neon Green: `#00f59b` (glow: `rgba(0, 245, 155, 0.4)`)
  - Warm Amber Warning: `#ff9500` (glow: `rgba(255, 149, 0, 0.3)`)
  - Emergency Alert Red: `#ff3b30`
- **Typography:**
  - Font Stack: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Outfit", system-ui, sans-serif`.
  - Metrics Font: `"SF Pro Display", "JetBrains Mono", tabular-nums`.

## 2. Responsive Breakpoint Rules (Echo Show to Desktop)
- **Echo Show 8 & 10 (1280px × 800px & 1024px × 600px):**
  - Landscape touch optimization.
  - Min touch target: 48px × 48px.
  - Large readable typography (headers at least 24px, body 16px).
- **iPad / Tablet (768px – 1024px):**
  - Dual-pane layout (Voice Assistant Orb left, Storage & Cooking Station right).
  - Collapsible drawer for dense lists.
- **Mobile Handheld (375px – 767px):**
  - Single column fluid flow with bottom navigation tabs.
- **Desktop Ultrawide (1200px+):**
  - 1440px max content width container, centered with soft glow ambient background.

## 3. Kinetic Animation & Micro-Interactions
- **Apple Spring Physics:**
  ```css
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  ```
- **Haptic-Style Visual Feedback:**
  - On button tap: `transform: scale(0.97);` with instant release to `scale(1.0)`.
  - On card hover: subtle lift `-2px` with luminous border glow increase.

## 4. Low-Latency State Architecture
- **Optimistic UI Updates:** UI updates immediately on user input before network confirmation (<16ms 60fps).
- **Selective DOM Reconciliation:** Check state string parity before mutating DOM tree to avoid reflows and flicker.
- **Audio Web Synth Integration:** Micro audio chimes using HTML5 Web Audio API for timer bells and haptic confirmation without loading external MP3 assets.
