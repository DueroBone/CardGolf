import random
from typing import TYPE_CHECKING
from Cards import Hand, NullHand, Card

if TYPE_CHECKING:
    from GameHolder import Game


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: Hand = NullHand()

    # PRE-GAME
    def _set_hand(self, hand: Hand) -> None:
        self.hand = hand

    def get_revealed_cards(self) -> list[Card | None]:
        return self.hand.get_cards()

    def get_hand_total(self) -> int:
        return self.hand.get_total()

    def _reveal_card(self, row: int, col: int) -> None:
        """Used x3 for begenning of game"""
        self.hand.reveal(row, col)

    # PRIMARY METHODS
    def play_turn(self, game: Game) -> None:
        raise NotImplementedError()

    def _check_top_discarded_card(self, game: Game) -> Card | None:
        return game.check_discarded_card()

    def _draw(self, game: Game) -> Card:
        return game.draw_card()

    def _get_top_discarded_card(self, game: Game) -> Card | None:
        return game.get_discard_card()

    def _place_card(self, row: int, col: int, card: Card, game: Game) -> None:
        discarded = self.hand.place(row, col, card)
        # TODO: check for replacing with same
        game.discard_card(discarded)
        self.__triple_check()

    def __triple_check(self) -> None:
        self.hand.check_three_in_a_row()

    def on_endgame(self) -> None:
        self.hand.reveal_all()

    def get_cards_remaining(self) -> int:
        return self.hand.get_card_count()


class HumanPlayer(Player):
    def play_turn(self, game: Game) -> None:
        # Check the top discarded card
        draw_from_discard = False
        print(f"Current hand:\n{self.hand}\n")
        top_discarded_card = self._check_top_discarded_card(game)
        if top_discarded_card:
            print(f"Top discarded card: {top_discarded_card}")
            draw_from_discard = (
                input("Do you want to draw from the discard pile? (y/n): ")
                .strip()
                .lower()
                == "y"
            )
        else:
            print("No cards in the discard pile.")

        # Draw a card from the draw pile or discard pile
        if draw_from_discard:
            drawn_card = top_discarded_card
            print(f"Drew from discard pile: {drawn_card}")
        else:
            drawn_card = self._draw(game)
            print(f"Drew from draw pile: {drawn_card}")
            if drawn_card is None:
                raise ValueError("Draw pile is empty. Cannot draw a card.")

        # Place the drawn card
        row = input("Enter the row (0-2) to place the card: ")
        if row == "":
            # Discard
            game.discard_card(drawn_card)  # type: ignore
        else:
            row = int(row)
            col = int(input("Enter the column (0-2) to place the card: "))
            print(f"Placing drawn card at ({row}, {col})")
            self._place_card((int(row)), col, drawn_card, game)  # type: ignore
        print(f"New hand:\n{self.hand}\n")


class DebugPlayer(Player):
    def play_turn(self, game: Game) -> None:
        # Draw a card from the draw pile
        drawn_card = self._draw(game)

        # Place the drawn card in a random position
        row = random.randint(0, 2)
        col = random.randint(0, 2)
        print(f"Placing {drawn_card} at ({row}, {col})")
        self._place_card(row, col, drawn_card, game)
        print(f"New hand:\n{self.hand}\n")

    def __str__(self) -> str:
        return f"DebugPlayer(name={self.name}, hand={self.hand})"


if __name__ == "__main__":
    import main

    main.main()
