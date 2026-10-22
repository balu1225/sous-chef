# Sous-Chef: Master Project Context & Living Log

*Last updated: 2026-10-19 11:41 PDT · Owner: Visweswarachary (Viswa)*  
*Standing Rule: This file must be updated whenever any change, decision, plan, or milestone is executed.*

---

## 1. Operating Principles & Standing Directives

1. **Phase Discipline:** Strictly follow the PDD phase order. Currently in **PLANNING PHASE**. Produce plans, designs, decisions, and checklists. Do not write implementation code unless explicitly instructed by the user.
2. **Reliability #1:** Reliability takes precedence over features and speed. When a trade-off exists, choose reliability and document the rationale in the Decision Log.
3. **No Inventions:** Never invent APIs, SDK functions, configuration fields, prices, or limits (MCP SDK, Alexa+, AWS/Bedrock, Neon, USDA). If unsure, verify against verified documentation.
4. **Free Tier Strictness:** Only free tiers until Phase P3. Flag any cost implication before suggesting.
5. **Single Source of Truth:** PDD v2.0. Seek explicit approval before altering Sections 5 (requirements), 9 (tool contracts), or 10 (reliability rules).
6. **Continuous Context Recording (Standing Command):** Maintain and update this file (`PROJECT_CONTEXT.md`) with every change so progress, decisions, friction, and context are persistently tracked.

---

## 2. Product Overview

- **Product Name:** Sous-Chef
- **Concept:** Voice-first kitchen assistant for inventory management, meal planning, and nutrition.
- **Key Capabilities:**
  - Conversational inventory intake ("I bought 2 gallons of milk, 6 eggs, spinach").
  - Proactive expiry warnings and dinner suggestions prioritizing items spoiling within 48h.
  - "I made it, 2 servings" automatically deducts ingredients and logs calories/protein.
  - Save custom family recipes by voice.
- **Core Differentiators:**
  - Zero typing needed (voice-first on Alexa+).
  - Trustworthy append-only inventory ledger that cannot silently drift.
  - LLM strictly handles natural language parsing; plain code does math, scoring, and inventory validation. AI is never allowed to invent ingredients.
  - Standard Model Context Protocol (MCP) foundation for multi-client portability.
- **Hackathon Track:** *Build, Ship, Shape: Amazon Developer Hackathon* (Alexa+ Track; Mini-challenges: AWS Builder, Open Source).
- **Hard Deadline:** **Friday, October 23, 2026, at 12:00 PM PDT** (~4 working days remaining).

---

## 3. Architecture & Tech Stack

- **Client Channels:** Alexa+ (R1) → Web Companion App (R2) → Multi-client MCP & Mobile (R3).
- **MCP Server:** Stateless Python using official MCP SDK (FastMCP pinned to `1.30.0`), Streamable HTTP transport on `/mcp/<secret-path>`, Protocol `2025-11-25`.
- **Database:** Postgres ledger with append-only event log, DB trigger blocking updates/deletes, per-household advisory locks, exact `NUMERIC` math, and base units (count, g, ml).
  - *Hackathon Environment (D10):* Local Postgres + `cloudflared` named/stable tunnel (ensures <50 ms DB latency, eliminates cold-starts).
- **Nutrition Source:** USDA FoodData Central preloaded canonical ingredients (kcal and protein per 100g).
- **Matching Engine:** Deterministic scoring algorithm:
  - Coverage: 45%
  - Expiring within 48h: 30%
  - Confidence: 10%
  - User Preference: 10%
  - Variety: 5% + Goal Boost.
- **LLM Layer:** Amazon Bedrock (small model) used solely for recipe tagging (core/optional/staple) in R1.

---

## 4. Current Phase & Progress Status

| Phase | Description | Status | Details |
|---|---|---|---|
| **P0** | Foundation: Postgres Ledger | **DONE** | `ledger.py`, `schema.sql`, `test_ledger.py`. 12/12 tests passing. Timezone fix applied (F1). |
| **P1** | Hackathon MVP | **PLANNING** | Scope selected: Option A (Demo-critical). Step 2 (Connect to Alexa+) planned. |
| **P2** | Beta | Not Started | Web companion app, OAuth 2.1 + PKCE (Cognito), confidence scores, check-ins, leftovers. |
| **P3** | Public Launch | Not Started | Paid HA Postgres, model gateway with fallback chain. |
| **P4** | Growth | Not Started | Multi-household scale, advanced nutrition goals. |

---

## 5. Scope Selection: Option A (Demo-Critical)

Due to the hard deadline of **October 23, 2026, 12:00 PM PDT**, Option A is selected to guarantee reliability-first quality.

### In Scope for Option A:
- End-to-end Alexa+ connection (with web simulator fallback).
- Write tools: `manage_inventory` (add/use), `undo_last_change`.
- Read tool: `query_inventory` (with expiry filter).
- Rule-based amount parser for spoken units.
- 50-ingredient canonical table with USDA kcal/protein values.
- Recipe storage: `save_custom_recipe` (voice intake).
- Matching: `suggest_recipes` (prioritizing food expiring within 48h).
- Consumption: `cook_recipe` ("I made it") + ingredient deduction.
- Nutrition: `nutrition_summary` (calories and protein today).
- ~10 seed recipes + 1 custom family recipe ("Grandma's Chili").
- 25-phrase golden test set.
- Bedrock recipe tagging integration (AWS Builder challenge).
- Separate MIT open-source repo for ingredient/nutrition data (Open Source challenge).
- 3-minute video demo + submission writeup and mandatory Amazon product feedback.

### 4-Day Execution Schedule:
- **Mon Oct 19:** Finalize planning decisions; Access check & cloudflared tunnel setup (Steps 1–2).
- **Tue Oct 20:** MCP server integration (Steps 3–8); `manage_inventory` & `undo_last_change`.
- **Wed Oct 21:** Amount parser; ingredient table; recipes; `suggest_recipes`, `cook_recipe`, `nutrition_summary`.
- **Thu Oct 22:** Golden set testing; Bedrock recipe tagging; open-source repo; record demo video.
- **Fri Oct 23:** Submission text, product feedback document, final review; submit by 10:00 AM PDT (2h buffer before 12:00 PM PDT cutoff).

---

## 6. P1 Step 2: Connect to Alexa+ (Detailed Plan)

### Goal
Prove the riskiest link in the system: `Alexa+ (or Simulator) → cloudflared tunnel → FastMCP Server → Postgres → Spoken Response` using `query_inventory` before building write tools.

### Key Amazon Verified Specifications:
- **Transport:** Streamable HTTP required; HTTP+SSE deprecated.
- **Protocol:** `2025-11-25` (official).
- **Latency Target:** Round-trip query response under 500 ms (server latency under 50 ms).
- **Auth:** Account linking is optional. For hackathon dev stage: No account linking, single demo household, endpoint placed behind an unguessable path (`/mcp/<secret-token>`).

### Execution Steps:
1. **Access Check (30–60 min):** Verify Amazon Developer Console has Alexa+ Add-ons and Web Simulator access. Install `alexa-ai` CLI and run `alexa-ai configure`. (*Go / No-Go decision on native Alexa+ path*).
2. **Tunnel Setup (30 min):** Set up `cloudflared` named tunnel for stable public HTTPS URL.
3. **Server Configuration (30 min):** Configure MCP server on `/mcp/<secret-path>`, disable token check, bind to fixed demo household, expose `query_inventory`.
4. **Inspector Pass (30 min):** Validate `tools/list` and `query_inventory` via MCP Inspector through the tunnel.
5. **Scaffold & Metadata (1 hr):** `alexa-ai new mcp` (No account linking), configure `addon.json` (HTTPS endpoint, name, description, 3–4 example phrases, placeholder icons, 600x900 carousel image).
6. **Deploy to Dev Stage (15 min):** `alexa-ai deploy` to push add-on to developer console.
7. **Simulator Testing (1 hr):** Test in Web Simulator (Isolation mode, then Global mode). Verify Response Detail and server logs.
8. **Logging (15 min):** Record latency, negotiated protocol, and any friction points in this document.

### Fallback Path (Trigger by end of Tue Oct 20):
If Alexa+ console access is unavailable or CLI deploy fails, switch immediately to the permitted web simulator path: a lightweight web companion where a Bedrock model calls the exact same MCP Streamable HTTP server.

---

## 7. Decision Log

| # | Decision | Status | Rationale |
|---|---|---|---|
| **D1** | Pin MCP Python SDK to `1.30.0` (FastMCP) | **Confirmed** | Officially targets protocol `2025-11-25`. Avoids 2.x breaking renames (`MCPServer`) and protocol churn (`2026-07-28`). |
| **D2** | Stateless Streamable HTTP with JSON responses | **Confirmed** | Required by Alexa+; horizontally scalable; no sticky sessions. |
| **D3** | Uniform response envelope: `{ok: true, ...}` or `{ok: false, error: {code, message, retryable}}` | **Confirmed** | Spoken-safe messages. No raw SQL or stack traces ever reach user TTS. |
| **D4** | Worker thread execution with hard 4.0s timeout | **Confirmed** | FastMCP 1.x sync handlers block event loop. Thread pool prevents starvation; 4.0s timeout beats conversational voice cutoff. |
| **D5** | UTC session pinning, connection checkout verification | **Confirmed** | Resolves F1 timezone drift; survives idle connection dropouts. |
| **D6** | Migrations run as a separate deployment step | **Confirmed** | Avoids concurrent DDL lock races across instances. |
| **D7** | No account linking for R1; unguessable endpoint path (`/mcp/<secret-path>`) | **Confirmed** | Alexa+ requires full OAuth 2.1 + PKCE if auth is enabled. Dev-stage add-on is restricted to developer account; unguessable path protects the demo endpoint. |
| **D7b**| Full OAuth 2.1 + PKCE deferred to P2 | **Planned (P2)**| Candidate: Amazon Cognito. Required for multi-household beta. |
| **D8** | Stub `confidence` as null; keep `low_confidence_only` in contract | **Confirmed** | Adheres to PDD Section 9 contract without premature complexity. |
| **D9** | Server starts independently of DB; readiness probe reports health | **Confirmed** | Prevents boot crash loops when DB is momentarily unavailable. |
| **D10**| Local Postgres + `cloudflared` named tunnel for Hackathon Demo | **Confirmed** | Solves 500 ms round-trip latency requirement. Free-tier cloud hosts (sleeping compute / cold DB) introduce 2–4s latency spikes. |
| **D11**| Modular folder structure (`src/`, `db/`, `alexa/`, `tests/`) | **Confirmed** | Separates Alexa CLI metadata/manifest from Python MCP server, ledger, and tests. Prevents root clutter and simplifies packaging. |
| **D12**| Standard Hackathon Path: Self-hosted MCP Server + Web Simulator | **Confirmed** | Official Alexa+ console/CodeArtifact is gated to preview partners. Devpost rules explicitly validate self-hosted MCP servers demoed via a web companion. Unlocks AWS Builder mini-challenge. |
| **D13**| Repository Agent Skills in `.agents/skills/` | **Confirmed** | Provide tailored skills for FastMCP 1.30.0, Postgres Ledger, and Bedrock Boto3 directly in the workspace rather than relying on disparate external downloads. |

---

## 8. Friction Log

| # | Issue Encountered | Severity | Resolution / Status |
|---|---|---|---|
| **F1** | `expires_at` returned in server local timezone (11/12 tests passed) | Medium | Pin Postgres session to UTC in `Store` (`SET TIME ZONE 'UTC'`). 12/12 tests now pass. |
| **F2** | MCP SDK 1.x vs 2.x breaking architectural split | Low | Pin to `mcp>=1.30.0,<2.0.0` (D1). |
| **F3** | FastMCP sync tools block the event loop | Medium | Wrap execution in `ThreadPoolExecutor` with 4.0s timeout (D4). |
| **F4** | DB outage retry can exceed 8s voice turn timeout | Low | 2.5s acquire timeout + 1.5s query timeout ensures error envelope returns in <4.0s. |
| **F5** | `@alexa-ai/cli` not on public npmjs (HTTP 404) | High | Amazon hosts `@alexa-ai/*` on private AWS CodeArtifact (`alexa-ai-372468808636.d.codeartifact.us-west-2.amazonaws.com`). Requires whitelisted AWS IAM account. Evaluated in Step 1 Go/No-Go. Resolved by adopting D12. |

---

## 9. Change & Activity History

- **2026-10-16:** P0 ledger validated (12/12 tests pass). Prototype server skeleton archived in `Kitchen_Agent_P1_step1.zip`.
- **2026-10-19 11:28:** Verified hackathon hard deadline: Friday, Oct 23, 2026, 12:00 PM PDT.
- **2026-10-19 11:41:** Formalized P1 Step 2 plan; selected Scope Option A (Demo-Critical); confirmed D7 (no-linking secret path) and D10 (local Postgres + cloudflared tunnel); created `PROJECT_CONTEXT.md` as master living log under standing instruction.
- **2026-10-20 11:28:** Confirmed Decision D11 (Modular folder structure).
- **2026-10-20 11:30:** Scaffolded modular directories (`db/`, `src/sous_chef/`, `alexa/`, `tests/`, `web_simulator/`). Verified local runtime environment: Python 3.13.7, Node v26.8.2, npm 11.19.1, Homebrew 7.0.6, Postgres 17. Initiating Step 1 (Alexa+ access check).
- **2026-10-20 12:26:** Installed `cloudflared` (2026.10.2). Encountered F5: `@alexa-ai/cli` is restricted to private AWS CodeArtifact registry; initiating Go/No-Go check with user on preview access vs. permitted web simulator fallback.
- **2026-10-20 13:20:** Confirmed Decision D12: Adopted the standard hackathon practice (Self-hosted MCP Server + Web Simulator front-end via Bedrock) to avoid gated console bottlenecks and guarantee deadline delivery.
- **2026-10-20 13:22:** Defined Decision D13 (Repository Agent Skills) for `.agents/skills/`.
- **2026-10-20 15:00:** Generated and verified all 8 comprehensive Agent Skills in `.agents/skills/` (`fastmcp-server`, `postgres-ledger`, `amount-parser`, `web-voice-companion`, `bedrock-converse`, `usda-nutrition`, `recipe-matching-engine`, `reliability-testing`). Full engineering blueprints and standards are now permanently active.
- **2026-10-20 20:05:** Initialized local isolated PostgreSQL 17 cluster on port 5433 with trust authentication and applied `db/schema.sql`. Placed modular backend (`src/sous_chef/`) and contract tests (`tests/`). Executed full automated suite: **40/40 tests passing**.
- **2026-10-20 20:21:** Implemented write tools (`manage_inventory`, `undo_last_change`) in `src/sous_chef/server.py`. Built and mounted the Web Voice Companion Simulator (`web_simulator/index.html`, `style.css`, `app.js`).
- **2026-10-20 20:46:** Implemented rule-based amount parser (`src/sous_chef/parser/amount_parser.py`) and strict ambiguity resolution. Saying "add milk and eggs" triggers clarification ("How much of the milk and eggs did you add?") rather than guessing quantities. Added spoken unit formatting. All **46/46 automated tests passing in 10.0s**.
- **2026-10-21 10:47:** Installed and verified the `archify` interactive diagramming & explainer skill in `.agents/skills/archify/` (version 3.2.0). All runtime checks (`doctor`) passed. Ready to generate interactive system maps and hackathon explainer artifacts.
- **2026-10-21 11:10:** Installed and configured `graphify` knowledge graph skill (`.agents/skills/graphify/`, `.agents/rules/graphify.md`, `.agents/workflows/graphify.md`, and PyPI `graphifyy`). Ran AST extraction across all codebase symbols: mapped 2,740 nodes, 8,399 edges, and 80 communities. Generated interactive standalone visualization at `graphify-out/graph.html`.
- **2026-10-21 12:10:** Initialized isolated Git repository with `.gitignore` and `README.md`. Created public GitHub repository and pushed entire codebase to [github.com/balu1225/sous-chef](https://github.com/balu1225/sous-chef). All 46/46 tests pass.
- **2026-10-21 19:30:** Implemented Guided Cooking Mode, Web Audio Lo-Fi Ambience Engine, and Smart Step Timer Alerts with Action Confirmation:
  - **Lo-Fi Kitchen Ambience Engine (`CookingMusicEngine`):** Zero-dependency Web Audio API procedural chords (Fmaj7 - Em7 - Dm7 - Cmaj7), volume slider, visualizer animation, and voice ducking.
  - **Smart Step Timer & Audio Ducking:** Automatically silences background music on timer completion, sounds 3-tone chime, transforms voice orb to pulsing amber alert state (`timer-alert`), and pops up Action Alert Modal.
  - **Proactive Spoken Instructions (Female Persona):** Speaks actionable instructions ("Ding! Timer's up! Turn off the stove, give it a good mix, and check your food.").
  - **Interactive Action Acknowledgement:** Saying "Stove is off", "Mixed it", or "Done" (or clicking confirm) acknowledges the action, returns to the cooking flow, and resumes the music.
  - **Spoiled Food Removal:** Saying "The milk is spoiled" discards available inventory atomically without prompting for quantity.
  - **Expanded Automated Test Suite:** Added unit & integration tests in `test_amount_parser.py` and `test_server.py`. Full test suite: **54/54 tests passing in 10.5s**.
