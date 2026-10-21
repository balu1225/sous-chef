# PRODUCT DEVELOPMENT DOCUMENT
# "Sous-Chef": Voice-First Kitchen Inventory, Meal Planning & Nutrition Agent

Version 2.0 (full product) · Owner: Visweswarachary · Status: Approved for build
Launch vehicle: Amazon Developer Hackathon, Alexa+ track → closed beta → public launch

---

## 0. Instructions for the AI assistant reading this document

You are the lead engineer and product partner on this project. Use this document as the single source of truth.

1. **Reliability is the #1 priority**, ahead of features and speed. When there's a trade-off, choose reliability and explain why.
2. **Never invent APIs, SDK functions, config fields, prices or limits.** If you're not sure something exists (MCP SDK, Alexa+, Google, Apple, AWS, Neon, USDA), say so and tell me where to verify it.
3. Build in the **phase order in Section 18**. Don't jump ahead; each phase has exit criteria.
4. For every step give: goal, complete files (not fragments), how to run, how to test, and what could go wrong.
5. Existing code to **reuse, not rewrite**: `ledger.py`, `schema.sql`, `test_ledger.py` (tested Postgres event-sourced ledger). Extend them.
6. Prefer **free tiers** until Phase 3. Flag any step that would cost money before doing it.
7. Keep a running **friction log** and **decision log** (Section 20) as we work.
8. Ask me before changing anything in Sections 5, 9 or 10 (requirements, tool contracts, reliability rules).

---

## 1. Executive summary

Households buy fresh food with good intentions, lose track of it, and throw a lot of it away, while facing "what's for dinner?" stress every evening. Existing apps fail because typing inventory into a screen is tedious, so people stop within days.

**Sous-Chef** is a voice-first kitchen assistant. You talk naturally ("I just bought 2 gallons of milk, 6 eggs and a bunch of spinach"); it keeps an accurate inventory, warns before food expires, suggests meals from what you actually have (prioritizing food about to spoil), deducts ingredients when you cook, and estimates calories and protein.

**What makes it different:**
- **Zero typing:** ambient voice on Alexa+, with more channels later.
- **Trustworthy:** an inventory that can't silently drift or be corrupted, and an AI that is never allowed to invent food you don't have.
- **Fast and cheap:** plain code does the thinking; the LLM only does the talking.
- **Open:** built on MCP, so any AI assistant or device can plug in.

---

## 2. Problem, users and user stories

### 2.1 Target users
| Persona | Situation | Main pain |
|---|---|---|
| **Busy parent** | Cooks for a family, shops weekly | No time to plan; food spoils at the back of the fridge |
| **Young professional** | Cooks a few nights a week | Buys ingredients for one recipe, the rest goes to waste |
| **Health-focused cook** | Tracks protein / calories | Logging meals in apps is tedious |
| **Recipe keeper** | Has family recipes | Recipes live in their head or on paper, not in any tool |

### 2.2 User stories
| # | As a… | I want to… | So that… |
|---|---|---|---|
| US-1 | shopper returning home | say all my groceries in one sentence | inventory updates without typing |
| US-2 | cook | say "I used half the chicken" or "the rest of the milk" | partial use is tracked |
| US-3 | user | say "undo that" or "no, 2 eggs not 12" | mistakes are fixed instantly |
| US-4 | home cook | be warned 48 hours before food expires | I use it before it spoils |
| US-5 | tired person at 6 PM | ask "what's for dinner?" | I get one good idea from what I have |
| US-6 | cook | say "I made it, 2 servings" | ingredients are deducted and the meal is logged |
| US-7 | recipe keeper | dictate "Grandma's Chili" by voice | my own recipes get suggested too |
| US-8 | health-focused cook | ask "how much protein today?" | I track nutrition without typing |
| US-9 | user | be asked occasionally "still have the spinach?" | inventory stays accurate |
| US-10 | household | log leftovers | leftovers get eaten, not forgotten |
| US-11 | user | ask "what do I need for Grandma's Chili?" | I get a shopping list |
| US-12 | user | set "never suggest peanuts" | suggestions respect our household |
| US-13 | user | use my phone or another assistant | I'm not locked to one device |

---

## 3. Scope

### 3.1 Release plan
| Release | Contents |
|---|---|
| **R1 – Hackathon MVP** | Alexa+ via MCP; add/use/undo; expiry warnings; custom recipes; dinner suggestions; cook & deduct; calories/protein; ~30 seed recipes |
| **R2 – Closed beta** | Corrections, confidence scores & check-ins, leftovers, shopping list, never-suggest list, web companion app, account linking, observability |
| **R3 – Public launch** | Multiple channels (other assistants, mobile), model gateway with fallbacks, paid Postgres with high availability, pricing, larger recipe catalog |
| **R4 – Later** | Grocery delivery integration, receipt/photo scanning, multi-person profiles & permissions, calendar meal planning, smart-fridge integrations |

### 3.2 Out of scope (all releases unless re-approved)
- Medical or clinical nutrition advice, diagnosis, or allergy guarantees.
- Selling user data or advertising.
- Payments inside the voice experience.

---

## 4. Conversation design

### 4.1 Channels
| Channel | Release | Role |
|---|---|---|
| Alexa+ (Echo devices) | R1 | Primary, hands-free kitchen use |
| Web companion app | R2 | Review inventory, edit recipes, see nutrition charts, settings |
| Other MCP-capable assistants (e.g., Claude, ChatGPT) | R3 | Same tools, no extra backend work |
| Mobile app / other voice assistants | R3+ | Verify each platform's integration options before committing |

### 4.2 Persona and voice rules
- **Persona:** "Resourceful Sous-Chef": warm, practical, brief, encouraging.
- **Never judgmental** about waste, eating or weight.
- Voice replies **under 25 words** where possible; **one main suggestion + one backup** at most.
- Numbers for nutrition are always "about".
- Confirmations are short and specific: "Added milk, eggs and spinach."

### 4.3 Key flows

**Flow A – Add groceries**
User: "I just bought 2 gallons of milk, 6 eggs and a bunch of spinach."
→ parse → one atomic batch → "Added milk, eggs and spinach. The spinach is good for about 5 days."

**Flow B – Dinner**
User: "What's for dinner?"
→ read precomputed suggestions → "Your spinach expires tomorrow. Try a chicken spinach rice bowl, about 540 calories and 42 grams of protein. Or Grandma's Chili."
User: "The bowl. I made it, 2 servings." → deduct + log meal → "Done. Enjoy!"

**Flow C – Save recipe**
User: "Save a recipe called Grandma's Chili with ground beef, beans, tomatoes and chili powder, serves 4."
→ classify ingredients core/optional/staple → save → "Saved Grandma's Chili. You have everything except beans."

**Flow D – Correction / undo**
User: "Undo that." → reverts the whole last utterance → "Undone: milk, eggs and spinach removed."
User: "No, 2 eggs not 12." → item-level correction → "Fixed: 2 eggs."

**Flow E – Check-in (R2)**
At a natural moment (e.g., right after a dinner request): "Quick check, do you still have the cilantro?" → yes / gone / a little.

**Flow F – Nutrition**
"How much protein have I had today?" → "About 85 grams of protein and 1,700 calories so far today."

### 4.4 Failure flows
| Situation | Behavior |
|---|---|
| Silence | Gentle prompt after ~5 s: "Checking stock or looking for dinner ideas?" |
| Unknown ingredient | Ask: "I don't know kohlrabi yet. Is it a vegetable or a pantry item?" |
| Vague amount ("some cheese") | One question: "Roughly how much: a little, half, or most of it?" |
| Big/destructive change | Read back first: "Just to confirm, 50 eggs?" |
| Not enough stock | "You have 2 eggs, not 4. Use both?" |
| Backend error | Plain message, data kept safe: "I saved your groceries, but can't get suggestions right now." |
| Off-topic | Short, friendly redirect back to the kitchen |

### 4.5 Proactive behavior
- Expiry warnings and check-ins are delivered when the user is already interacting, plus a daily summary where the platform supports notifications (verify Alexa+ proactive notification capabilities and limits).
- Max 2 check-in questions per day; each item at most once every 3 days; users can turn check-ins off.

---

## 5. Functional requirements

### Inventory
- **FR-1** Extract multiple items, quantities, units and storage zones from one utterance.
- **FR-2** Assign storage zone and estimated expiry from the ingredient table's shelf-life data.
- **FR-3** Append-only event log; each utterance is one atomic batch with an idempotency key; current stock is a projection updated in the same transaction.
- **FR-4** Undo the last utterance (whole batch) and correct a single item from the last change.
- **FR-5** Rule-based parsing of fractional/approximate amounts ("half", "the rest", "a couple", "1 and a half cups"); vague amounts trigger one clarifying question.
- **FR-6** Per-item confidence score (time since confirmed, approximate amount, expiry).
- **FR-7** Check-ins: max 2/day, least-certain perishables first, can be disabled.
- **FR-8** Leftovers logged as new items with short shelf life.

### Recipes
- **FR-9** Save custom recipes by voice (name, servings, ingredients with roles, optional steps).
- **FR-10** Canonical ingredient names with synonyms, families and substitutions (lookup table).
- **FR-11** Ingredients tagged core / optional / staple, set once at save time.
- **FR-12** Deterministic scoring: filter (≤1 missing core, enough quantity, never-suggest list), then rank by coverage, expiry urgency, confidence, preference, variety, and optional goal (high protein, quick).
- **FR-13** Suggestions precomputed on every inventory change and nightly; stored per household.
- **FR-14** Voice output limited to 1 main + 1 backup suggestion.
- **FR-15** Any LLM-generated recipe is validated against stock before being spoken.
- **FR-16** Shopping list for a chosen recipe (missing items).
- **FR-17** Household "never suggest" ingredient list.

### Cooking and nutrition
- **FR-18** "I made it, N servings" deducts ingredients atomically and logs the meal.
- **FR-19** Calories and protein per 100 g per canonical ingredient (from USDA FoodData Central), average weights for countable items.
- **FR-20** Recipe nutrition per serving computed at save time.
- **FR-21** Daily/weekly nutrition summaries by voice and in the web app; opt-in.

### Platform
- **FR-22** All capabilities exposed as MCP tools over Streamable HTTP (spec 2025-11-25 or later).
- **FR-23** Account linking / OAuth per household (verify Alexa+ account-linking requirements for MCP servers).
- **FR-24** Web companion app (R2) using the same backend.

---

## 6. Non-functional requirements

| Area | Requirement |
|---|---|
| **Data integrity** | Zero lost or double-applied changes; projection always equals event-log replay (`verify()` = no problems) |
| **Latency (server)** | MCP tool calls p95 < 300 ms; DB reads ~10 ms; writes < 50 ms |
| **Latency (end to end)** | Measure in beta (Alexa+ speech/LLM/voice time is outside our control); target user-perceived < 2.5 s p95 |
| **Availability** | R1/R2: best effort on free tiers. R3: 99.9% with paid Postgres (HA + point-in-time recovery) and ≥2 server instances |
| **Scale** | Stateless servers scale horizontally; per-household advisory locks; evening peak 5–7 PM load tested at 10× expected beta traffic |
| **Cost** | No LLM call for matching, confirmations or math; LLM cost per dinner request reduced ≥90% vs. LLM-only design (measure) |
| **Privacy** | Only inventory, recipes, meals and settings stored; no voice audio stored by us |
| **Accessibility** | Fully usable by voice alone; web app meets WCAG 2.1 AA |

---

## 7. Architecture

### 7.1 Components
```
                ┌───────────── Channels ─────────────┐
 Alexa+ (R1)    Web app (R2)    Other MCP assistants (R3)
        │             │                  │
        └──── MCP over Streamable HTTPS + OAuth ────┘
                          │
                ┌─────────▼──────────┐
                │   MCP Server       │  stateless, Python (official MCP SDK / FastMCP)
                │  - tool handlers   │
                │  - amount parser   │  rule-based, no LLM
                │  - validators      │
                └───┬───────┬────────┘
                    │       │
          ┌─────────▼─┐  ┌──▼────────────────┐
          │ Postgres  │  │ Model gateway (R3) │  small model for fallback parsing &
          │ ledger,   │  │ Bedrock / others   │  phrasing; fallback chain
          │ recipes,  │  └────────────────────┘
          │ meals     │
          └─────▲─────┘
                │
       ┌────────┴─────────┐
       │ Background worker │  recompute suggestions on change + nightly;
       │ + scheduler       │  expiry warnings; check-in selection
       └───────────────────┘
```

### 7.2 Key design choices
| Decision | Choice | Reason |
|---|---|---|
| Integration standard | MCP, Streamable HTTP | Required for Alexa+; works with any MCP client |
| Database | Postgres (Neon free for R1–R2; paid HA in R3) | Transactions, row-level security, standard and portable |
| Source of truth | Append-only event log + projection | Audit, undo, corrections, drift detection |
| Matching | Plain code + precompute | Fast, cheap, consistent, can't hallucinate |
| LLM role | Language only (parsing fallback, phrasing) | Reliability and cost |
| Nutrition data | USDA FoodData Central, preloaded | Free, public, no live calls in conversations |
| Hosting | Container platform with HTTPS (choose a free option for R1; verify limits) | Simple, scalable |

### 7.3 Model gateway (R3)
- One internal interface for all LLM calls, with a fallback chain (e.g., primary → secondary provider → tiny local model → fixed template).
- Per-task routing: smallest model that passes the evals for that task.
- Every model must pass the golden test set (Section 16) before being enabled.

---

## 8. Data model

All tables keyed by `household_id`, protected by Postgres row-level security. Existing: `households`, `batches`, `events`, `inventory` (see `schema.sql`).

| Table | Key columns |
|---|---|
| `inventory` (extend) | + `estimated` (bool), `last_confirmed_at`, `canonical_id` |
| `events` (extend) | + `confirm` event type, `estimated`, `source` (voice / app / correction / checkin) |
| `ingredients` | canonical_id, name, synonyms[], family_of, unit_family, avg_weight_g, shelf_life_days {fridge, freezer, pantry, opened}, kcal_per_100g, protein_g_per_100g, source |
| `substitutions` | ingredient_id, substitute_id, ratio, note |
| `recipes` | recipe_id, household_id (null = shared seed), name, servings, steps, kcal_per_serving, protein_per_serving, prep_minutes, created_by |
| `recipe_ingredients` | recipe_id, canonical_id, qty_base, unit_family, role (core/optional/staple) |
| `suggestions` | household_id, recipe_id, score, missing[], uses_expiring[], computed_at |
| `meals` | meal_id, household_id, recipe_id, servings, kcal, protein_g, eaten_at, idempotency_key |
| `checkins` | household_id, item, asked_at, answered_at, answer |
| `household_settings` | never_suggest[], checkins_enabled, nutrition_enabled, units (metric/US), timezone |

---

## 9. MCP tool contracts

All tools return structured JSON. All write tools require `idempotency_key` (one per user utterance). Descriptions stay short (they're sent on every request).

| Tool | Input | Output |
|---|---|---|
| `manage_inventory` | ops[]: `{type: add/consume/discard/set, item, qty?, unit?, fraction?, zone?, expires_at?, approx?}`, idempotency_key | per-item before/after; all-or-nothing; clear error |
| `query_inventory` | item?, expiring_within_hours?, low_confidence_only? | items with qty, unit, zone, expiry, confidence |
| `undo_last_change` | batch_id?, idempotency_key | reverted items |
| `correct_item` | item, qty, unit, idempotency_key | corrected before/after |
| `save_custom_recipe` | name, servings, ingredients[{item, qty, unit, role}], steps?, idempotency_key | saved recipe, nutrition/serving, stock match |
| `suggest_recipes` | goal?: use_expiring / high_protein / quick | top 1 + backup with missing items, expiring items used, nutrition/serving |
| `cook_recipe` | recipe_id, servings_eaten, idempotency_key | deducted ingredients, meal logged |
| `log_leftovers` | recipe_id, servings_left, idempotency_key | leftover item created |
| `shopping_list` | recipe_id | missing items with quantities |
| `nutrition_summary` | period: today / week | kcal, protein (estimates) |
| `answer_checkin` | item, answer: yes / gone / little, idempotency_key | updated item |
| `update_settings` | never_suggest?, checkins_enabled?, nutrition_enabled? | settings |

---

## 10. Reliability engineering (main focus)

### 10.1 Data correctness
- Append-only event log; database trigger blocks updates.
- One utterance = one atomic batch; any failure rolls back everything.
- Idempotency key per write; concurrent duplicates apply once.
- Per-household transaction-scoped advisory lock.
- Exact decimals (NUMERIC).
- Validation: known units, positive finite quantities, no negative stock, no unit-family mixing, sane maximums.
- Undo and corrections are new events, never deletions.
- Nightly `verify()` per household; alert on any mismatch.

### 10.2 AI grounding
- The model may only state stock, recipes and nutrition **returned by tools** (server instructions + tool descriptions).
- Matching, scoring, nutrition math and quantity math are plain code.
- LLM-generated recipes are validated against stock; failures are rejected, not spoken.
- Prompt-injection protection: tools only act within the caller's household; no tool executes free-text commands; inputs are schema-validated.

### 10.3 Never guess
- Unknown items, vague amounts and big/destructive changes trigger a clarifying question or read-back.

### 10.4 Graceful failure
- Timeouts on every DB and external call; reads retried once; writes only retried with the same idempotency key.
- Partial degradation: inventory writes succeed even if suggestions fail.
- Speakable error messages; never stack traces.
- Health checks; circuit breaker around the model gateway; fixed-template fallback when all models fail.

### 10.5 Drift control
- Confidence scores, check-ins, item-level corrections and leftovers (Section 5) keep the inventory close to reality.
- Metric: inventory accuracy after 14 days ≥ 85% (beta fridge audits).

### 10.6 Backups and recovery
- R1–R2: provider backups (verify Neon free-tier retention).
- R3: point-in-time recovery, documented restore drill, RPO ≤ 5 min, RTO ≤ 1 h.

---

## 11. Recipe matching algorithm

1. **Normalize** inventory and recipe ingredients to canonical IDs (synonyms, families, substitutions).
2. **Filter out** recipes with >1 missing core ingredient, insufficient quantity, or a never-suggest ingredient.
3. **Score** remaining recipes:

| Factor | Weight |
|---|---|
| Coverage of core + optional ingredients | 45% |
| Uses items expiring within 48 h | 30% |
| Confidence in required items | 10% |
| User preference (own recipes, favorites) | 10% |
| Variety (not cooked recently) | 5% |
| Goal boost (high protein / quick) | +bonus when requested |

4. **Precompute** top 10 per household on every inventory change (only recipes touching changed items, via an ingredient → recipe index) and nightly.
5. **Tune** weights using beta data on accepted suggestions.

---

## 12. Nutrition

- Data: USDA FoodData Central (free, public); preload kcal and protein per 100 g for each canonical ingredient. Verify licensing and API-key terms on the official site.
- Countable items have average weights (1 egg ≈ 50 g).
- Recipe nutrition per serving computed at save time; meals logged at cook time.
- Opt-in; always "about"; no judgment, no extreme goals, no medical advice.
- Later: carbs, fat, fiber; per-person tracking when multi-person profiles exist.

---

## 13. AI / LLM strategy

| Task | Approach |
|---|---|
| Understanding user intent and choosing tools | Alexa+ built-in model (R1); other assistants' models (R3) |
| Amount parsing | Rule-based parser first; small LLM fallback (Bedrock) for leftovers |
| Ingredient role tagging when saving recipes | Small LLM once per recipe, then stored |
| Confirmations | Fixed templates |
| Phrasing suggestions | Template or small LLM |
| "Invent something with what I have" | Larger LLM with in-stock list only, validated before speaking |

Evaluation: every model/prompt change runs the golden set; ship only if accuracy doesn't drop.

---

## 14. Security, privacy and compliance

- TLS everywhere; data encrypted at rest (provider default; verify).
- OAuth / account linking per household; tokens never logged.
- Row-level security + household_id on every query.
- Data minimization: no audio, no payment data, no government IDs stored by us.
- User controls: export data, delete household (cascades all rows).
- Privacy policy and terms before beta; follow Amazon's policies for Alexa+ integrations (verify current requirements).
- Secrets in environment variables / secret manager, never in the repo.

---

## 15. Observability and operations

- Structured logs with request ID, household ID (hashed), tool, duration, result.
- Metrics: tool latency p50/p95/p99, error rate per tool, DB latency, LLM calls and cost, verify() mismatches, clarification rate, correction rate, undo rate.
- Alerts: error rate spike, latency over budget, any verify() mismatch, DB connection exhaustion.
- Dashboards in R2 (free tooling first).
- Runbooks: DB restore, model outage fallback, bad deploy rollback.

---

## 16. Testing and success criteria

### 16.1 Tests
- Unit: ledger, parser, matching, nutrition math, validators.
- Concurrency: parallel writes, duplicate retries, multiple server instances.
- Golden set: 50 phrases (R1) → 300+ real recorded phrases (R2) covering bulk lists, accents, slang, vague amounts, unknown items, corrections, undo, nutrition questions.
- Contract tests for each MCP tool.
- Load test: evening peak at 10× expected traffic.
- Chaos: DB unavailable, model unavailable, slow responses.

### 16.2 Success metrics
| Metric | Target |
|---|---|
| Correct item extraction on first try | ≥ 95% (R1), ≥ 98% (R3) |
| Lost or double-applied changes | 0 |
| Hallucinated ingredients reaching users | 0 (enforced by validation) |
| Server tool latency p95 | < 300 ms |
| Inventory accuracy after 14 days | ≥ 85% |
| Suggestion acceptance rate | track; improve each release |
| Food saved (expiring items used via suggestions) | track per household |
| Week-4 retention (beta) | track; target set after R2 baseline |

---

## 17. Business

- **Value:** less food waste (money saved), less decision stress, effortless nutrition tracking.
- **Pricing (hypothesis to test in beta):** free tier (inventory + basic suggestions) and premium (nutrition history, unlimited custom recipes, meal planning, extra channels). Validate willingness to pay before R3.
- **Go-to-market:** hackathon visibility → beta via cooking and parenting communities → launch on Alexa+ and the web.
- **Cost control:** plain-code matching, precompute, smallest viable models, free tiers until revenue.

---

## 18. Roadmap and exit criteria

| Phase | Build | Exit criteria |
|---|---|---|
| **P0 Foundation** (done) | Postgres ledger, schema, tests | 12/12 tests pass |
| **P1 Hackathon MVP** | MCP server (Streamable HTTP, 2025-11-25); Alexa+ connection; manage/query/undo; parser; ingredients + USDA nutrition; custom recipes; matching + suggest/cook/nutrition tools; 50-phrase golden set; demo video; submission | One voice command works end to end on Alexa+; all R1 tools pass tests; submission complete |
| **P2 Beta** | Corrections, confidence, check-ins, leftovers, shopping list, settings, web app, OAuth, observability, 300-phrase golden set | 20+ beta households for 4 weeks; accuracy ≥ 85%; zero data-integrity incidents |
| **P3 Launch** | Paid HA Postgres + PITR, multi-instance hosting, model gateway, extra channels, pricing, privacy/legal | 99.9% over 30 days in staging; load test passed; restore drill passed |
| **P4 Growth** | Grocery delivery, receipt scanning, multi-person profiles, meal-plan calendar | Driven by beta/launch data |

---

## 19. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Alexa+ MCP integration details differ from assumptions | Connect one tool end to end first (P1 step 2); simulated web fallback allowed for the hackathon |
| Inventory drift destroys trust | Event log, corrections, confidence, check-ins, leftovers |
| LLM hallucination | Tool-only facts, plain-code matching, validation |
| Logging fatigue | Multi-item voice, cook-to-deduct, minimal check-ins |
| Free-tier limits (sleep, storage, no SLA) | Fine for P1–P2; upgrade in P3; cold-start measured |
| Platform lock-in | MCP + web app + model gateway |
| Nutrition misread as medical advice | Opt-in, estimates only, clear disclaimer, no goals beyond general wellness |
| Privacy concerns | Minimal data, export/delete, RLS, encryption |

---

## 20. Hackathon submission (P1 deliverables)

Track: **Alexa+**. Mini challenges: **AWS Builder**, **Open Source**.

Checklist:
- [ ] Self-hosted MCP server, spec 2025-11-25+, Streamable HTTP, actually imported and run in the repo.
- [ ] Demo of the MCP server working with Alexa+ (or the simulated web path, with source in the repo).
- [ ] Repo: public + LICENSE, or private and shared with testing@devpost.com and chris-trag, knmeiss, giolaq, anishamalde, mosesroth, emersonsklar (invites expire after 7 days; add at submission time).
- [ ] Text description.
- [ ] Demo video < 3 min, public, English, no copyrighted music.
- [ ] Product feedback on every tool/SDK used (incl. AWS services and how).
- [ ] Explanation of what existed before vs. built during the window.
- [ ] AWS Builder: documented Bedrock (and/or Kiro) integration.
- [ ] Open Source: separate MIT repo with the ingredient + nutrition table; contribution URL, repo URL, GitHub username, short description.
- [ ] Optional: feature requests.
- [ ] Optional: friction log (up to 10% bonus): task, steps, expected vs. actual, severity, workaround, suggestion.

Demo script (< 3 min): problem (0:00–0:20) → bulk add by voice with live DB (0:20–0:50) → save Grandma's Chili (0:50–1:20) → "what's for dinner?" with expiring spinach + nutrition, then "I made it" (1:20–2:00) → protein today + undo (2:00–2:30) → architecture + measured latency + Bedrock + open source (2:30–3:00).

---

## 21. Open questions to verify (do not assume)

1. Exact steps and requirements to connect a self-hosted MCP server to Alexa+ (auth, account linking, endpoint rules).
2. Which MCP Python SDK version supports protocol 2025-11-25 and Streamable HTTP; how to confirm the negotiated version.
3. Alexa+ proactive notification capabilities and limits.
4. Free hosting options with public HTTPS and their sleep/limit behavior.
5. Neon free-tier backup retention and cold-start time.
6. USDA FoodData Central API key and data-use terms.
7. Bedrock model availability/pricing for the smallest suitable model, and any free credits.

---

## 22. Glossary

- **MCP (Model Context Protocol):** open standard that lets AI assistants call external tools; how Alexa+ talks to our server.
- **Streamable HTTP:** the MCP transport required by the hackathon.
- **Event log / projection:** every change is stored as a permanent record; current stock is calculated from those records.
- **Idempotency key:** a unique ID per request so a retry never applies twice.
- **Row-level security (RLS):** database rule that hides other households' rows.
- **Golden set:** fixed list of test phrases with expected results, run on every change.
- **p95:** 95% of requests are faster than this.
