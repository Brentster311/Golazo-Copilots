import pytest
from game.models.card import Card

class TestCard:
    def test_card_creation(self):
        card = Card(suit='hearts', rank='A')
        assert card.suit == 'hearts'
        assert card.rank == 'A'

    def test_rank_value(self):
        assert Card(suit='hearts', rank='A').rank_value() == 14
        assert Card(suit='hearts', rank='K').rank_value() == 13
        assert Card(suit='hearts', rank='2').rank_value() == 2

    def test_card_equality(self):
        c1 = Card(suit='hearts', rank='A')
        c2 = Card(suit='hearts', rank='A')
        assert c1 == c2

    def test_card_inequality(self):
        c1 = Card(suit='hearts', rank='A')
        c2 = Card(suit='spades', rank='A')
        assert c1 != c2
