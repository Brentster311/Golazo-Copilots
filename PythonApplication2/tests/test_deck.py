import pytest
from game.models.deck import Deck

class TestDeck:
    def test_deck_has_52_cards(self):
        deck = Deck()
        assert len(deck) == 52

    def test_shuffle_changes_order(self):
        d1 = Deck()
        d2 = Deck()
        d2.shuffle(seed=42)
        assert d1._cards[0] != d2._cards[0]

    def test_deal_removes_cards(self):
        deck = Deck()
        cards = deck.deal(6)
        assert len(cards) == 6
        assert len(deck) == 46

    def test_draw_returns_top_card(self):
        deck = Deck()
        top = deck.top_card()
        drawn = deck.draw()
        assert top == drawn
        assert len(deck) == 51

    def test_top_card_does_not_remove(self):
        deck = Deck()
        deck.top_card()
        assert len(deck) == 52
