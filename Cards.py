import random


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = rank

        if rank == 1:  # Ace
            self.value = -1
        elif rank in [11, 12]:  # Jack or Queen
            self.value = 10
        elif rank == 13:  # King
            self.value = 0
        elif rank >= 14:  # Joker
            self.value = -2

    def description(self) -> str:
        value_str = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King", 14: "Joker"}.get(
            self.rank, str(self.rank)
        )
        return f"{value_str} of {self.suit}"

    def __str__(self) -> str:
        symbol = {
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣",
            "Spades": "♠",
            "Joker": "$"
        }
        _rank = {1: "A", 11: "J", 12: "Q", 13: "K", 14: "$"}.get(self.rank, str(self.rank))
        return f"{_rank}{symbol[self.suit]}"


class Deck:
    def __init__(self):
        self.cards: list[Card] = []

    def shuffle(self) -> Deck:
        random.shuffle(self.cards)
        return self


class DrawPile(Deck):
    def __init__(self):
        super().__init__()
        self.__build()
        self.shuffle()

    def draw(self) -> Card:
        return self.cards.pop()

    def __build(self) -> None:
        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            for rank in range(1, 14):
                self.cards.append(Card(suit, rank))
        self.cards.append(Card("Joker", 14))
        self.cards.append(Card("Joker", 14))


class DiscardPile(Deck):
    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def top_card(self) -> Card | None:
        if self.cards:
            return self.cards[-1]
        return None


######################=- HAND CLASSES -=######################


class RawHand:
    def __init__(self, deck: DrawPile):
        self.cards: list[Card] = [deck.draw() for _ in range(9)]

    def raw_get_cards(self) -> list[Card]:
        return self.cards

    def raw_get_total(self) -> int:
        total = 0
        for card in self.cards:
            if card is not None:
                total += card.value
        return total

    def raw_get(self, row: int, col: int) -> Card:
        return self.cards[self._index_of(row, col)]

    @staticmethod
    def _index_of(row: int, col: int) -> int:
        index = row * 3 + col
        if 0 <= index < 9:
            return index
        raise IndexError("Card index out of range")

    @staticmethod
    def _to_row_col(index: int) -> tuple[int, int]:
        if 0 <= index < 9:
            return divmod(index, 3)
        raise IndexError("Card index out of range")


class Hand(RawHand):
    def __init__(self, deck: DrawPile):
        super().__init__(deck)
        self.revealed: list[bool] = [False] * 9

    def reveal(self, row: int, col: int) -> None:
        self.revealed[self._index_of(row, col)] = True

    def get_cards(self) -> list[Card | None]:
        return [self.get(*self._to_row_col(i)) for i in range(9)]

    def get_total(self) -> int:
        total = 0
        for i in range(9):
            if self.revealed[i]:
                card = self.get(*self._to_row_col(i))
                if card is not None:
                    total += card.value
        return total

    def get(self, row: int, col: int) -> Card | None:
        if not self.revealed[self._index_of(row, col)]:
            return None
        return super().raw_get(row, col)

    def place(self, row: int, col: int, card: Card) -> Card:
        current_card = self.cards[self._index_of(row, col)]
        self.cards[self._index_of(row, col)] = card
        self.revealed[self._index_of(row, col)] = True
        return current_card

    def __str__(self) -> str:
        result = ""
        for row in range(3):
            for col in range(3):
                card = self.get(row, col)
                if card:
                    result += str(card) + " "
                else:
                    result += "XX "
            result += "\n"
        return result.strip()


class NullHand(Hand):
    def __init__(self):
        self.cards = []

    def reveal(self, row: int, col: int) -> None:
        raise NotImplementedError("NullHand does not support revealing cards.")

    def get_cards(self) -> list[Card | None]:
        raise NotImplementedError("NullHand does not support getting cards.")

    def get_total(self) -> int:
        raise NotImplementedError("NullHand does not support getting total.")

    def get(self, row: int, col: int) -> Card | None:
        raise NotImplementedError("NullHand does not support getting cards.")

    def place(self, row: int, col: int, card: Card) -> Card:
        raise NotImplementedError("NullHand does not support placing cards.")

if __name__ == "__main__":
    import main
    main.main()