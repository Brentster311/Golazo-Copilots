import random
from typing import List, Optional
from game.models.card import Card

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self):
        self._cards: List[Card] = []
        self._build()

    def _build(self) -> None:
        self._cards = [Card(suit=s, rank=r) for s in SUITS for r in RANKS]

    def shuffle(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            random.seed(seed)
        random.shuffle(self._cards)

    def deal(self, count: int) -> List[Card]:
        dealt = self._cards[:count]
        self._cards = self._cards[count:]
        return dealt

    def draw(self) -> Optional[Card]:
        return self._cards.pop(0) if self._cards else None

    def top_card(self) -> Optional[Card]:
        return self._cards[0] if self._cards else None

    def __len__(self) -> int:
        return len(self._cards)
