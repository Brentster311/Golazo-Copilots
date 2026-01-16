import pytest
from game.models.california_jack import CaliforniaJackGame

class TestCaliforniaJackGame:
    def test_new_game_deals_6_cards_each(self):
        game = CaliforniaJackGame.new_game(seed=42)
        assert len(game.player1_hand) == 6
        assert len(game.player2_hand) == 6

    def test_new_game_has_40_cards_in_stock(self):
        game = CaliforniaJackGame.new_game(seed=42)
        assert len(game.stock) == 40

    def test_trump_suit_matches_top_card(self):
        game = CaliforniaJackGame.new_game(seed=42)
        top_card = game.stock.top_card()
        assert game.trump_suit == top_card.suit

    def test_player1_starts(self):
        game = CaliforniaJackGame.new_game(seed=42)
        assert game.current_player == 1
