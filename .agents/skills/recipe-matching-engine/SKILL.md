---
name: recipe-matching-engine
description: Deterministic recipe scoring algorithm, exclusion filters, expiry prioritization, and atomic cooking deduction rules.
---

# Recipe Matching Engine Engineering Standard

## 1. Principles
- **No Hallucinated Ingredients:** AI never suggests recipes requiring ingredients the user does not have (unless missing at most 1 core item with explicit disclosure).
- **Expiry Prioritization:** Food expiring within 48 hours is heavily boosted to prevent waste.
- **Deterministic Math:** Pure scoring algorithm in code, not subjective LLM hallucination.

## 2. Hard Exclusion Filters
Before scoring, a candidate recipe is **disqualified** if:
1. **Missing Core Ingredients > 1:** Missing 2 or more core ingredients. (Missing 1 core is allowed only if marked as "need to pick up X").
2. **Insufficient Quantity:** Available stock of a core ingredient is less than 50% of the required amount.
3. **Never-Suggest Match:** Contains any ingredient listed in the household's `never_suggest` settings.

## 3. Deterministic Scoring Formula
For recipes passing hard filters, calculate:
$$\text{Score} = (0.45 \times C) + (0.30 \times E_{48\text{h}}) + (0.10 \times \text{Conf}) + (0.10 \times P) + (0.05 \times V) + \text{GoalBoost}$$

Where:
- **$C$ (Coverage %):** Ratio of available ingredients to total required ingredients ($0.0 \text{ to } 1.0$).
- **$E_{48\text{h}}$ (Expiring Boost):**
  - $1.0$ if the recipe uses at least one ingredient expiring within 48 hours.
  - $0.5$ if uses ingredient expiring within 3–5 days.
  - $0.0$ otherwise.
- **$\text{Conf}$ (Confidence):** Current inventory confidence (stubbed as $1.0$ in R1 per D8).
- **$P$ (User Preference):** Favorite cuisine or rating ($0.5 \text{ default}$).
- **$V$ (Variety):** $1.0$ if not cooked in the last 7 days; $0.0$ if cooked yesterday.
- **$\text{GoalBoost}$:** $+0.10$ if user has a high-protein goal and recipe provides $\ge 30\text{g}$ protein/serving.

## 4. Cook & Deduct Pattern (`cook_recipe`)
When the user says "I made it, 2 servings":
1. Acquire household advisory lock.
2. Scale ingredient amounts by: `scale_factor = target_servings / recipe_base_servings`.
3. Deduct core and available optional ingredients from `inventory_events` in an atomic batch.
4. Record meal in `logged_meals` with calculated calories and protein.
5. Return spoken response:
   ```json
   {
     "ok": true,
     "meal_logged": {
       "recipe_name": "Grandma's Chili",
       "servings": 2,
       "total_kcal": 780.0,
       "total_protein_g": 52.0,
       "deducted_items": ["1 lb ground beef", "1 can black beans", "1 can crushed tomatoes"],
       "spoken_message": "Logged 2 servings of Grandma's Chili. Deducted ground beef and tomatoes. That adds 780 calories and 52 grams of protein."
     }
   }
   ```

## 5. Seed Recipes (~10 R1 Recipes)
1. Grandma's Quick Chili (Ground Beef, Black Beans, Crushed Tomatoes, Olive Oil)
2. Spinach & Cheddar Scramble (Eggs, Spinach, Cheddar, Butter)
3. Simple Chicken Rice Bowl (Chicken Breast, White Rice, Olive Oil)
4. Classic Omelet (Eggs, Cheddar, Butter)
5. Cheesy Rice & Beans (White Rice, Black Beans, Cheddar)
6. Garlic Herb Chicken (Chicken Breast, Olive Oil, Salt, Black Pepper)
7. Creamy Spinach Eggs (Eggs, Spinach, Milk, Butter)
8. Quick Beef & Rice Skillet (Ground Beef, White Rice, Crushed Tomatoes)
9. Black Bean Soup (Black Beans, Crushed Tomatoes, Olive Oil)
10. Protein Scramble (Eggs, Chicken Breast, Spinach)

## 6. Implementation Checklist
- [ ] Hard filters reject $>1$ missing core ingredient.
- [ ] Expiry boost of 30% strictly prioritized.
- [ ] Atomic batch deduction in ledger with idempotency key.
- [ ] Macro calculation matches USDA values.
