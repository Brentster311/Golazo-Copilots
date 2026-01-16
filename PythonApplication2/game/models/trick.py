"""Trick model for California Jack game."""

from dataclasses import dataclass
from typing import Optional

from game.models.card import Card


@dataclass
class Trick:
    """
    Represents a single trick in California Jack.
    
    A trick consists of two cards - one led by the first player,
    and one followed by the second player.
    
    Attributes:
        lead_card: The card played by the lead player
        follow_card: The card played by the following player
        lead_player: Which player led (1 or 2)
    """
    
    lead_card: Optional[Card] = None
    follow_card: Optional[Card] = None
    lead_player: int = 1
    
    def is_complete(self) -> bool:
        """
        Check if the trick is complete (both cards played).
        
        Returns:
            True if both cards have been played, False otherwise
        """
        return self.lead_card is not None and self.follow_card is not None
    
    def winner(self, trump_suit: str) -> int:
        """
        Determine the winner of this trick.
        
        California Jack rules:
        - Higher card of lead suit wins, unless
        - A trump card is played, then highest trump wins
        
        Args:
            trump_suit: The trump suit for this hand
            
        Returns:
            Player number (1 or 2) who won the trick
        """
        if not self.is_complete():
            raise ValueError("Cannot determine winner of incomplete trick")
        
        lead = self.lead_card
        follow = self.follow_card
        follow_player = 2 if self.lead_player == 1 else 1
        
        lead_is_trump = lead.suit == trump_suit
        follow_is_trump = follow.suit == trump_suit
        
        # Case 1: Follow played trump, lead did not
        if follow_is_trump and not lead_is_trump:
            return follow_player
        
        # Case 2: Lead played trump, follow did not
        if lead_is_trump and not follow_is_trump:
            return self.lead_player
        
        # Case 3: Both trump - higher trump wins
        if lead_is_trump and follow_is_trump:
            if follow.rank_value() > lead.rank_value():
                return follow_player
            return self.lead_player
        
        # Case 4: Neither trump
        # Follow must match lead suit to win, otherwise lead wins
        if follow.suit == lead.suit:
            if follow.rank_value() > lead.rank_value():
                return follow_player
            return self.lead_player
        
        # Follow played different non-trump suit - lead wins
        return self.lead_player
