"""Sous-Chef Culinary Rescue & Kitchen Mishap Remedies.

Provides witty, humorous empathy and practical culinary chemistry remedies
when cooking goes wrong (oversalted, burned, too spicy, dry, curdled, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class KitchenMishap:
    category: str
    quips: list[str]
    remedy_steps: list[str]
    pro_tip: str


MISHAP_DATABASE: dict[str, KitchenMishap] = {
    "burned": KitchenMishap(
        category="Burned or Charred Food",
        quips=[
            "Don't panic! We're not calling the fire department just yet, and we can call it 'artisanally blackened' if anyone asks!",
            "Ah, a surprise smoky barbecue edition! Breathe in, breathe out—we can salvage this.",
            "Step away from the smoke alarm! Every great chef has cremated something at least once."
        ],
        remedy_steps=[
            "Rule #1: DO NOT scrape the bottom of the pan! That's where the bitter carbon lives.",
            "Gently spoon or pour the unburned top food into a clean pot or skillet.",
            "Stir in a dollop of plain yogurt, sour cream, or a half-spoon of peanut butter to neutralize residual acrid smokiness.",
            "If it's meat with a charred crust, slice off the burnt outer layer, shred the rest, and toss in barbecue or pan sauce."
        ],
        pro_tip="A tiny splash of sweet maple syrup or brown sugar helps mask bitter burned undertones."
    ),

    "too_salty": KitchenMishap(
        category="Over-Salted Dish",
        quips=[
            "Whoops! Did the salt shaker top pop off, or are we secretly cooking for sea captains?",
            "It's giving 'ocean water aesthetic'! Don't toss it out, culinary chemistry is on our side.",
            "Salt happens to the best of us! Let's dial down the salinity dial."
        ],
        remedy_steps=[
            "Dilute with liquid: add a splash of water, unsalted stock, or heavy cream.",
            "Fight salt with acid: a squeeze of fresh lemon juice or cider vinegar tricks your tastebuds into perceiving less saltiness.",
            "Add sweet or starch: stir in diced tomatoes, cooked rice, unsalted beans, or a spoonful of brown sugar.",
            "The classic grandma trick: drop in thick slices of peeled raw potato and simmer for 10 minutes; they absorb excess sodium like sponges (then discard the potato)."
        ],
        pro_tip="Never add salt while standing over steam; the steam clogs the shaker or dumps a tsunami of salt all at once!"
    ),

    "too_spicy": KitchenMishap(
        category="Too Spicy / Hot",
        quips=[
            "Sound the dragon alarm! Your taste buds are currently sending an SOS signal.",
            "Is it hot in here, or did a whole family of ghost peppers move into your skillet?",
            "Water won't help you now, my fiery friend! But dairy is about to be your superhero."
        ],
        remedy_steps=[
            "Capsaicin is fat-soluble: swirl in sour cream, whole milk, Greek yogurt, or coconut milk.",
            "Add sweetness: a teaspoon of honey, sugar, or maple syrup neutralizes fiery heat.",
            "Balance with acid: a squeeze of fresh lime juice cuts through pepper oils.",
            "Bulk it up: double the non-spicy ingredients (more rice, beans, or shredded cheese)."
        ],
        pro_tip="Never drink plain water for spicy heat—it just spreads the capsaicin oil around. Drink milk or eat bread!"
    ),

    "too_dry": KitchenMishap(
        category="Overcooked / Dry Meat",
        quips=[
            "Ah, the classic accidental beef jerky! Don't worry, your teeth will forgive us.",
            "Turned your chicken into a hockey puck? Let's give it a luxury spa rehydration.",
            "Dry meat isn't dead—it's just thirsty! Time for culinary resuscitation."
        ],
        remedy_steps=[
            "Slice or shred it thin against the grain: thinner fibers absorb liquids 5x faster.",
            "Bathe it in warm liquid: toss shredded meat in hot broth, melted butter, olive oil, or pan juices.",
            "Transform into tacos, quesadillas, or a chicken salad with mayo and avocado.",
            "Top with a rich sauce like chimichurri, guacamole, or gravy."
        ],
        pro_tip="Always let cooked chicken rest for 5 minutes before cutting; slicing too early lets all the juice leak onto the board!"
    ),

    "too_watery": KitchenMishap(
        category="Watery / Runny Sauce or Soup",
        quips=[
            "Looks like your sauce went for an unauthorized swim in the deep end!",
            "A little runny? We can turn this broth puddle into velvety liquid gold in two minutes.",
            "No one likes a soup that's masquerading as tea! Let's thicken it up."
        ],
        remedy_steps=[
            "Take the lid off and let it bubble over medium-high heat to reduce and evaporate water.",
            "Quick Slurry: Whisk 1 teaspoon cornstarch or flour in 2 tablespoons cold water until smooth, then stir into the simmering sauce for 60 seconds.",
            "Mash some of the cooked beans, potatoes, or veggies directly against the pot wall to create natural body.",
            "Swirl in a cold tablespoon of butter off the heat (monter au beurre) for a rich, glossy finish."
        ],
        pro_tip="Never add dry flour directly to hot liquid, or you'll get stubborn flour dumplings instead of a smooth sauce!"
    ),

    "too_sour": KitchenMishap(
        category="Too Sour / Overly Acidic",
        quips=[
            "If your face is stuck in a permanent lemon pucker, we went a little too wild on the citrus!",
            "Pucker up! That vinegar had big ambitions today. Let's tame the tang.",
            "Acid attack in progress! Time to bring out the baking chemistry."
        ],
        remedy_steps=[
            "Add a tiny pinch of baking soda (1/8 tsp): watch it fizz! It chemically neutralizes excess acid without changing the volume.",
            "Balance with sweet: stir in 1/2 teaspoon sugar, honey, or caramelized onions.",
            "Mellow with fat: stir in heavy cream, grated cheese, or a knob of butter."
        ],
        pro_tip="Taste after 30 seconds of adding baking soda; the fizzing is carbonic acid escaping!"
    ),

    "too_sweet": KitchenMishap(
        category="Too Sweet",
        quips=[
            "Dinner is trying to moonlight as dessert! Let's pull it back to the savory side.",
            "Did the sugar fairy break into your kitchen? We can fix this before anyone thinks it's cake.",
            "A little sweet talk is fine, but this sauce is overdoing it!"
        ],
        remedy_steps=[
            "Add acid: a squeeze of lemon juice or apple cider vinegar cuts through cloying sweetness.",
            "Add heat: a pinch of cayenne, chili flakes, or black pepper balances high sugar.",
            "Add salt and savory depth: stir in a dash of soy sauce, Worcestershire sauce, or a pinch of salt."
        ],
        pro_tip="Bitter greens like spinach or kale soak up and counter sweet glazes beautifully."
    ),

    "sauce_curdled": KitchenMishap(
        category="Curdled / Broken Sauce",
        quips=[
            "Your sauce is having an emotional breakdown and trying to separate into cottage cheese!",
            "Don't cry over split sauce! Emulsions break, but we can whip them back into shape.",
            "The sauce broke, but your kitchen confidence doesn't have to!"
        ],
        remedy_steps=[
            "Take the pan completely off the burner right now.",
            "Whisk in 1 tablespoon of ice-cold water or heavy cream vigorously with a fork or whisk.",
            "If that doesn't fix it, put an egg yolk in a clean bowl and slowly whisk the broken sauce into it droplet by droplet."
        ],
        pro_tip="Curdling happens when heat is too high. Always warm dairy gently and never boil heavy sour cream."
    ),

    "stuck_to_pan": KitchenMishap(
        category="Food Stuck to the Pan",
        quips=[
            "Looks like your food developed an intense emotional attachment to the skillet floor!",
            "It's clinging for dear life! Let's perform a gentle pan divorce.",
            "Don't scrape! A gouged skillet is forever, but stuck food can be persuaded."
        ],
        remedy_steps=[
            "Turn off the heat completely and cover the pan tightly with a lid or plate for 2 minutes.",
            "The trapped steam will soften the bottom crust and release the food naturally.",
            "Or splash 2 tablespoons of water or broth around the edges: the sizzle will deglaze the bottom instantly!"
        ],
        pro_tip="Food usually sticks when the pan wasn't preheated enough before adding oil, or when you tried to flip it too early before the crust formed!"
    ),

    "bland": KitchenMishap(
        category="Bland / Lacks Flavor",
        quips=[
            "It's giving 'hospital food aesthetic' or 'spa water in bowl form'. Let's wake those flavors up!",
            "Tastes like nothing? 90% of the time, bland food isn't missing exotic spices—it's missing acid and salt!",
            "Let's turn the volume knob on your tastebuds from a 2 to a 10!"
        ],
        remedy_steps=[
            "Add salt first: salt doesn't make food taste salty; it pulls out the natural flavors.",
            "Add acid: a squeeze of fresh lemon juice or splash of vinegar acts like a high-definition filter for taste.",
            "Add umami: a splash of soy sauce, Worcestershire, or a sprinkle of parmesan adds savory depth.",
            "Finish with fresh cracked black pepper or a drizzle of good olive oil."
        ],
        pro_tip="Always taste your dish at the end before serving; food tastes less intense as it cools down."
    ),

    "general": KitchenMishap(
        category="General Kitchen Mishap",
        quips=[
            "Even Julia Child famously dropped food on the floor and laughed it off! Tell me what went wrong.",
            "Take a deep breath! There are no kitchen mistakes, only unexpected new recipes.",
            "I've got your back! Tell me what's happening: is it burned, too salty, too spicy, too dry, or too watery?"
        ],
        remedy_steps=[
            "Don't throw anything away yet—almost every kitchen mistake has a culinary antidote!",
            "Tell me: say 'I burned it', 'it's too salty', 'it's too spicy', 'it's dry', or 'it's too watery' and I'll rescue it!"
        ],
        pro_tip="A calm cook makes the best food. Step back, lower the flame, and take a sip of water."
    )
}


def get_remedy_for_mishap(category: str) -> dict:
    """Returns a witty quip, step-by-step remedy, and spoken message."""
    mishap = MISHAP_DATABASE.get(category, MISHAP_DATABASE["general"])
    quip = random.choice(mishap.quips)
    spoken = (
        f"{quip} "
        f"Here's the rescue plan: {mishap.remedy_steps[0]} "
        f"Also, {mishap.remedy_steps[1]} "
        f"Pro tip: {mishap.pro_tip}"
    )

    return {
        "category": mishap.category,
        "type": category,
        "quip": quip,
        "remedy_steps": mishap.remedy_steps,
        "pro_tip": mishap.pro_tip,
        "spoken_message": spoken
    }
