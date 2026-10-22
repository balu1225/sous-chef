---
name: composition-patterns
description: Guidelines from Vercel Agent Skills for building resilient, composable, and cleanly separated frontend components without monolithic prop explosion.
---

# Composition Patterns (Vercel Agent Skills)

This skill guides structuring UI components into composable, focused, and maintainable units.

## Core Principles

1. **Inversion of Control over Megamorphic Components**:
   - Avoid creating massive monolithic components with 20+ boolean flags (`hasSearch`, `showSidebar`, `isModal`, etc.).
   - Use composition: break screens into independent sub-views (Hero Column, Lyrics Stream, Storage Grid, Slide Drawer).

2. **Progressive Disclosure**:
   - The primary viewport must display ONLY the essential context needed right now (e.g., active recipe cover, active step lyric, transport scrubber).
   - Ancillary tools (Chat transcript, Nutrition rings, Recipe cookbook) belong in slide-over drawers or bottom-dock floating sheets that appear on demand.

3. **Compound Component State Synchronization**:
   - Single source of truth for cooking session state (`/api/cooking`).
   - Sibling components (Scrubber, Lyric active line, Audio chime, Transport buttons) react to a single state transition cleanly without circular event loops.

4. **Slot and Projection Pattern**:
   - Separate container layout geometry from item view templates.
   - For example, `renderLyrics(steps, activeIdx)` produces clean standalone lyric items that can be styled independently.
