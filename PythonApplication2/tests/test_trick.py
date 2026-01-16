"""Tests for Trick model and trick-taking gameplay - CALJACK-003.

These tests are written BEFORE the Trick class and game methods exist (TDD).
All tests should FAIL initially until Developer implements the functionality.
"""

import pytest


class TestTrickCreation:
    """Tests for Trick instantiation."""

    def test_trick_can_be_created(self):
        """Trick should be creatable."""
        from game.models.trick import Trick
        
        trick = Trick()
        assert trick is not None

    def test_trick_starts_empty(self):
        """New trick should have no cards."""
        from game.models.trick import Trick
        
        trick = Trick()
        assert trick.lead_card is None
        assert trick.follow_card is None

    def test_trick_tracks_lead_player(self):
        """Trick should track which player led."""
        from game.models.trick import Trick
        
        trick = Trick(lead_player=1)
        assert trick.lead_player == 1


class TestTrickCompletion:
    """Tests for Trick.is_complete() method."""

    def test_empty_trick_not_complete(self):
        """Trick with no cards is not complete."""
        from game.models.trick import Trick
        
        trick = Trick()
        assert trick.is_complete() is False

    def test_trick_with_lead_only_not_complete(self):
        """Trick with only lead card is not complete."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick()
        trick.lead_card = Card(suit='hearts', rank='A')
        assert trick.is_complete() is False

    def test_trick_with_both_cards_complete(self):
        """Trick with both cards is complete."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick()
        trick.lead_card = Card(suit='hearts', rank='A')
        trick.follow_card = Card(suit='hearts', rank='K')
        assert trick.is_complete() is True


class TestTrickWinner:
    """Tests for Trick.winner() method - AC #3."""

    def test_higher_same_suit_wins(self):
        """Higher card of same suit wins."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick(lead_player=1)
        trick.lead_card = Card(suit='hearts', rank='K')
        trick.follow_card = Card(suit='hearts', rank='A')
        
        assert trick.winner(trump_suit='spades') == 2

    def test_lead_wins_if_higher(self):
        """Lead card wins if higher than follow of same suit."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick(lead_player=1)
        trick.lead_card = Card(suit='hearts', rank='A')
        trick.follow_card = Card(suit='hearts', rank='K')
        
        assert trick.winner(trump_suit='spades') == 1

    def test_trump_beats_non_trump(self):
        """Trump card beats non-trump regardless of rank."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick(lead_player=1)
        trick.lead_card = Card(suit='hearts', rank='A')
        trick.follow_card = Card(suit='spades', rank='2')
        
        assert trick.winner(trump_suit='spades') == 2

    def test_higher_trump_wins(self):
        """Higher trump beats lower trump."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick(lead_player=1)
        trick.lead_card = Card(suit='spades', rank='K')
        trick.follow_card = Card(suit='spades', rank='A')
        
        assert trick.winner(trump_suit='spades') == 2

    def test_lead_wins_if_follow_different_suit_no_trump(self):
        """Lead wins if follow plays different non-trump suit."""
        from game.models.trick import Trick
        from game.models.card import Card
        
        trick = Trick(lead_player=1)
        trick.lead_card = Card(suit='hearts', rank='2')
        trick.follow_card = Card(suit='diamonds', rank='A')
        
        assert trick.winner(trump_suit='spades') == 1


class TestFollowSuitValidation:
    """Tests for can_play_card() - follow suit rules - AC #2."""

    def test_lead_player_can_play_any_card(self):
        """Lead player can play any card from hand."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        for card in game.player1_hand:
            assert game.can_play_card(player=1, card=card) is True

    def test_must_follow_suit_if_able(self):
        """Second player must follow suit if they have that suit."""
        from game.models.california_jack import CaliforniaJackGame
        from game.models.card import Card
        from game.models.trick import Trick
        
        game = CaliforniaJackGame.new_game(seed=42)
        game.trump_suit = 'spades'
        game.current_trick = Trick(lead_player=1)
        game.current_trick.lead_card = Card(suit='hearts', rank='A')
        game.current_player = 2
        game.player2_hand = [
            Card(suit='hearts', rank='K'),
            Card(suit='diamonds', rank='Q')
        ]
        
        assert game.can_play_card(player=2, card=Card(suit='hearts', rank='K')) is True
        assert game.can_play_card(player=2, card=Card(suit='diamonds', rank='Q')) is False

    def test_must_trump_if_cannot_follow_suit(self):
        """If cannot follow suit, must trump if able."""
        from game.models.california_jack import CaliforniaJackGame
        from game.models.card import Card
        from game.models.trick import Trick
        
        game = CaliforniaJackGame.new_game(seed=42)
        game.trump_suit = 'spades'
        game.current_trick = Trick(lead_player=1)
        game.current_trick.lead_card = Card(suit='hearts', rank='A')
        game.current_player = 2
        game.player2_hand = [
            Card(suit='spades', rank='2'),
            Card(suit='diamonds', rank='Q')
        ]
        
        assert game.can_play_card(player=2, card=Card(suit='spades', rank='2')) is True
        assert game.can_play_card(player=2, card=Card(suit='diamonds', rank='Q')) is False

    def test_can_play_any_if_cannot_follow_or_trump(self):
        """If cannot follow suit AND cannot trump, can play any card."""
        from game.models.california_jack import CaliforniaJackGame
        from game.models.card import Card
        from game.models.trick import Trick
        
        game = CaliforniaJackGame.new_game(seed=42)
        game.trump_suit = 'spades'
        game.current_trick = Trick(lead_player=1)
        game.current_trick.lead_card = Card(suit='hearts', rank='A')
        game.current_player = 2
        game.player2_hand = [
            Card(suit='diamonds', rank='Q'),
            Card(suit='clubs', rank='K')
        ]
        
        assert game.can_play_card(player=2, card=Card(suit='diamonds', rank='Q')) is True
        assert game.can_play_card(player=2, card=Card(suit='clubs', rank='K')) is True


class TestPlayCard:
    """Tests for play_card() method."""

    def test_play_card_removes_from_hand(self):
        """Playing a card removes it from player hand."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        card = game.player1_hand[0]
        initial_hand_size = len(game.player1_hand)
        
        game.play_card(player=1, card=card)
        
        assert len(game.player1_hand) == initial_hand_size - 1
        assert card not in game.player1_hand

    def test_play_card_adds_to_trick(self):
        """Playing a card adds it to current trick."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        card = game.player1_hand[0]
        
        game.play_card(player=1, card=card)
        
        assert game.current_trick is not None
        assert game.current_trick.lead_card == card

    def test_play_card_switches_current_player(self):
        """Playing a card switches to other player."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        assert game.current_player == 1
        
        card = game.player1_hand[0]
        game.play_card(player=1, card=card)
        
        assert game.current_player == 2


class TestDrawCards:
    """Tests for draw_cards() method - AC #4."""

    def test_winner_draws_first(self):
        """Trick winner draws the top card from stock."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        top_card = game.stock.top_card()
        initial_p1_hand = len(game.player1_hand)
        
        game.draw_cards(winner=1)
        
        assert top_card in game.player1_hand
        assert len(game.player1_hand) == initial_p1_hand + 1

    def test_loser_draws_second(self):
        """Trick loser draws the second card from stock."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        initial_stock = len(game.stock)
        initial_p1_hand = len(game.player1_hand)
        initial_p2_hand = len(game.player2_hand)
        
        game.draw_cards(winner=1)
        
        assert len(game.player1_hand) == initial_p1_hand + 1
        assert len(game.player2_hand) == initial_p2_hand + 1
        assert len(game.stock) == initial_stock - 2

    def test_no_draw_when_stock_empty(self):
        """No cards drawn when stock is empty."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        while len(game.stock) > 0:
            game.stock.draw()
        
        initial_p1_hand = len(game.player1_hand)
        game.draw_cards(winner=1)
        
        assert len(game.player1_hand) == initial_p1_hand


class TestResolveTrick:
    """Tests for resolve_trick() method - AC #5."""

    def test_resolve_returns_winner(self):
        """resolve_trick returns the winner."""
        from game.models.california_jack import CaliforniaJackGame
        from game.models.card import Card
        from game.models.trick import Trick
        
        game = CaliforniaJackGame.new_game(seed=42)
        game.trump_suit = 'clubs'
        game.current_trick = Trick(lead_player=1)
        game.current_trick.lead_card = Card(suit='hearts', rank='K')
        game.current_trick.follow_card = Card(suit='hearts', rank='A')
        
        winner = game.resolve_trick()
        assert winner == 2

    def test_winner_leads_next_trick(self):
        """Winner of trick becomes current player."""
        from game.models.california_jack import CaliforniaJackGame
        from game.models.card import Card
        from game.models.trick import Trick
        
        game = CaliforniaJackGame.new_game(seed=42)
        game.trump_suit = 'clubs'
        game.current_trick = Trick(lead_player=1)
        game.current_trick.lead_card = Card(suit='hearts', rank='K')
        game.current_trick.follow_card = Card(suit='hearts', rank='A')
        
        game.resolve_trick()
        assert game.current_player == 2


class TestGameOver:
    """Tests for game over detection - AC #6."""

    def test_game_not_over_with_cards_remaining(self):
        """Game is not over while cards remain."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        assert game.is_game_over() is False

    def test_game_over_when_all_cards_played(self):
        """Game is over when stock and hands are empty."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        while len(game.stock) > 0:
            game.stock.draw()
        game.player1_hand = []
        game.player2_hand = []
        
        assert game.is_game_over() is True

    def test_game_not_over_with_empty_stock_but_cards_in_hand(self):
        """Game continues with empty stock if hands have cards."""
        from game.models.california_jack import CaliforniaJackGame
        
        game = CaliforniaJackGame.new_game(seed=42)
        while len(game.stock) > 0:
            game.stock.draw()
        
        assert len(game.player1_hand) > 0
        assert game.is_game_over() is False
