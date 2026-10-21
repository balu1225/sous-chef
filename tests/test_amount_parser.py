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
