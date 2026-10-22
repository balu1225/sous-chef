import pytest
from sous_chef.parser.amount_parser import parse_kitchen_utterance

def test_missing_quantity_triggers_clarification():
    # User says "add milk and eggs" without any amount
    res = parse_kitchen_utterance("add milk and eggs")
    assert res.needs_clarification is True
    assert "How much" in res.clarifying_question
    assert "milk" in res.clarifying_question or "eggs" in res.clarifying_question

def test_single_missing_item_triggers_targeted_question():
    res = parse_kitchen_utterance("I bought chicken")
    assert res.needs_clarification is True
    assert res.clarifying_question == "How much chicken did you add?"

def test_explicit_quantities_parsed_accurately():
    res = parse_kitchen_utterance("I bought 2 gallons of milk and a dozen eggs")
    assert res.needs_clarification is False
    assert len(res.items) == 2
    
    milk = next(i for i in res.items if i.item == "milk")
    assert milk.qty == 2.0
    assert milk.unit == "gallons"
    
    eggs = next(i for i in res.items if i.item == "eggs")
    assert eggs.qty == 12.0
    assert eggs.unit in ("count", "dozen")

def test_consume_action_detected():
    res = parse_kitchen_utterance("I used half a cup of milk")
    assert res.action == "consume"
    assert res.needs_clarification is False
    assert len(res.items) == 1
    assert res.items[0].unit == "cup"

def test_spoiled_food_discard_needs_no_quantity():
    # User says "the milk is spoiled" -> atomic discard without asking for amounts
    res = parse_kitchen_utterance("the milk is spoiled")
    assert res.action == "discard"
    assert res.needs_clarification is False
    assert len(res.items) == 1
    assert res.items[0].item == "milk"

def test_recipe_suggestion_with_15_minutes_quick_filter():
    res = parse_kitchen_utterance("what can I make in 15 minutes or less?")
    assert res.action == "suggest_recipes"
    assert res.context.get("max_minutes") == 15
    assert res.context.get("goal") == "quick"

def test_music_control_intents():
    res_play = parse_kitchen_utterance("play cooking music")
    assert res_play.action == "music_control"
    assert res_play.context.get("state") == "play"

    res_stop = parse_kitchen_utterance("stop music")
    assert res_stop.action == "music_control"
    assert res_stop.context.get("state") == "stop"

def test_timer_control_intents():
    res_start = parse_kitchen_utterance("start timer")
    assert res_start.action == "timer_control"
    assert res_start.context.get("state") == "start"

    res_pause = parse_kitchen_utterance("pause timer")
    assert res_pause.action == "timer_control"
    assert res_pause.context.get("state") == "stop"

def test_confirm_action_intents():
    for phrase in ["i stopped the stove", "stove is off", "mixed it", "checked it", "done"]:
        res = parse_kitchen_utterance(phrase)
        assert res.action == "confirm_action", f"Failed for phrase: {phrase}"
        assert res.context.get("confirmed") is True

def test_prep_item_check_intent():
    res = parse_kitchen_utterance("I got the eggs")
    assert res.action == "check_prep_item"
    assert "eggs" in res.context.get("checked_item")

def test_kitchen_mishap_intents():
    mishaps = [
        ("I burned the chicken", "burned"),
        ("The soup is too salty", "too_salty"),
        ("My mouth is on fire, it's too spicy", "too_spicy"),
        ("The meat is dry like rubber", "too_dry"),
        ("The sauce is too watery and thin", "too_watery"),
        ("Too much lemon it's too sour", "too_sour"),
        ("The food is stuck to the pan", "stuck_to_pan"),
        ("Help I messed up my cooking", "general"),
    ]
    for utterance, expected_type in mishaps:
        res = parse_kitchen_utterance(utterance)
        assert res.action == "kitchen_mishap", f"Failed action for '{utterance}'"
        assert res.context.get("mishap_type") == expected_type, f"Failed type for '{utterance}'"


def test_save_recipe_intents():
    # Contextual saving during or after cooking
    res1 = parse_kitchen_utterance("save this recipe as spicy scramble")
    assert res1.action == "save_recipe"
    assert res1.context.get("recipe_name") == "spicy scramble"
    assert len(res1.items) == 0

    res2 = parse_kitchen_utterance("save what i cooked as quick lunch")
    assert res2.action == "save_recipe"
    assert res2.context.get("recipe_name") == "quick lunch"
    assert len(res2.items) == 0

    res3 = parse_kitchen_utterance("save this as mom's omelet")
    assert res3.action == "save_recipe"
    assert "mom" in res3.context.get("recipe_name")
    assert len(res3.items) == 0

    # Explicit ingredient specification
    res4 = parse_kitchen_utterance("save recipe spicy eggs with 3 eggs 1 cup spinach and 2 oz cheddar")
    assert res4.action == "save_recipe"
    assert res4.context.get("recipe_name") == "spicy eggs"
    item_names = {i.item for i in res4.items}
    assert "eggs" in item_names
    assert "spinach" in item_names
    assert "cheddar" in item_names



