---
name: frontend-design
description: Creating distinctive, production-grade interfaces, cinematic layouts, typography, and focused visual hierarchy rather than generic cluttered AI designs.
---

# Frontend Design Engineering Standard

## 1. Core Principles (Apple & Vercel Aesthetic)
- **Cinematic Simplicity:** Avoid the "kitchen sink" anti-pattern where every button, orb, metric, and log is dumped onto the screen simultaneously. Focus the user's attention on what they care about *right now*.
- **The "Now Playing" Paradigm:** Like Apple Music Fullscreen or Apple Fitness:
  - Left pane: The Hero Card (Current Dish, Album Art, or Storage Focus) with high visual polish.
  - Right pane: Active synchronized focus (Current Cooking Step in large, high-contrast typography; upcoming/past steps softly dimmed like real-time lyrics).
- **Progressive Disclosure:** Secondary utilities (manual text chat input, developer diagnostics, raw JSON) should be tucked away into an elegant, discreet slide-over drawer (`[💬]`) or triggered via keyboard shortcuts (`/`).
- **Ambient Lighting:** Instead of flat grey boxes, use rich radial ambient lighting that gently breathes behind content, matching the palette of the active dish or kitchen theme.

## 2. Typography & Hierarchy
- **Fluid Headline Typography:**
  ```css
  font-size: clamp(1.75rem, 3.5vw, 2.75rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.15;
  ```
- **High-Contrast Active State:**
  - Active Step / Lyric: `#ffffff` (opacity 1.0, bold, slight glow).
  - Inactive / Upcoming Steps: `rgba(255, 255, 255, 0.3)` (softly blurred, readable on hover/focus).

## 3. PWA & Standalone Installability
- Web applications must be installable as standalone PWAs on mobile, iPad, and desktop with zero browser chrome (`display: standalone`).
- Include `manifest.json`, theme colors, app icons, and touch event support.
