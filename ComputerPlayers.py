import random
from typing import TYPE_CHECKING
from Cards import Hand, NullHand, Card
from MyErrors import IllegalMoveError
from Players import Player
import torch

if TYPE_CHECKING:
    from GameHolder import Game


class RandomPlayer(Player):
    def __init__(
        self,
        name: str,
        printable: bool = False,
        discard_acceptance_probability: float = 0.5,
    ):
        super().__init__(name)
        self.discard_acceptance_probability = discard_acceptance_probability
        self.printable = printable

    def play_turn(self, game: Game) -> None:
        # Draw a card from the draw pile
        if (
            random.random() < self.discard_acceptance_probability
            and self._check_top_discarded_card(game)
        ):
            drawn_card = self._get_top_discarded_card(game)
        else:
            try:
                drawn_card = self._draw(game)
            except IndexError:
                return

        # Place the drawn card in a random position
        row = random.randint(0, 2)
        col = random.randint(0, 2)
        print(f"Placing {drawn_card} at ({row}, {col})") if self.printable else None
        self._place_card(row, col, drawn_card, game)  # type: ignore
        print(f"New hand:\n{self.hand}\n") if self.printable else None


class NeuralNetworkPlayer(Player):
    """
    Input format: [hand_card_0, hand_card_1, hand_card_2,
    hand_card_3, hand_card_4, hand_card_5,
    hand_card_6, hand_card_7, hand_card_8,
    top_discarded_card, drawn_card, hand_total,
    hand_cards_placed, min_opponent_cards_remaining,
    opponent_hand_total]

    Output format: [draw_from_discard, draw_from_draw_pile,
    row_0_col_0, row_0_col_1, row_0_col_2, row_1_col_0,
    row_1_col_1, row_1_col_2, row_2_col_0, row_2_col_1,
    row_2_col_2, discard_drawn_card]

    Total input size: 15
    Total output size: 12
    """

    def __init__(self, name: str, model: torch.nn.Module, printable: bool = False):
        super().__init__(name)
        self.model: torch.nn.Module = model
        self.model.eval()
        self.printable = printable

    def play_turn(self, game: Game) -> None:
        # Decide whether to draw from the discard pile or the draw pile
        if self._check_top_discarded_card(game):
            # Only if there is a card in the discard pile
            draw_from_discard, _, __ = self.get_output(game, None)
        else:
            draw_from_discard = False

        if draw_from_discard:
            drawn_card = self._get_top_discarded_card(game)
            print(f"Drew from discard pile: {drawn_card}") if self.printable else None
            if drawn_card is None:
                raise IllegalMoveError("Discard pile is empty. Cannot draw a card.")
        else:
            drawn_card = self._draw(game)
            print(f"Drew from draw pile: {drawn_card}") if self.printable else None
            if drawn_card is None:
                raise IllegalMoveError("Draw pile is empty. Cannot draw a card.")

        # Place the drawn card based on the neural network's prediction
        ___, row, col = self.get_output(game, drawn_card)

        if row == -1 and col == -1:
            game.discard_card(drawn_card)
            print(f"Discarded {drawn_card}") if self.printable else None
            return

        print(f"Placing {drawn_card} at ({row}, {col})") if self.printable else None
        self._place_card(row, col, drawn_card, game)
        print(f"New hand:\n{self.hand}\n") if self.printable else None

    def _prepare_input(self, game: Game, drawn_card: Card | None) -> torch.Tensor:
        _top_discarded_card = game.check_discarded_card()

        # -1 for unrevealed cards, rank for revealed cards
        hand_state = [card.rank if card else -1 for card in self.hand.get_cards()]
        hand_total = self.hand.get_total()
        hand_cards_placed = self.hand.get_card_count()
        top_discarded_card_state = (
            _top_discarded_card.rank if _top_discarded_card else -1
        )
        drawn_card_state = drawn_card.rank if drawn_card else -1
        best_opponent = min(
            game.get_opponents(self),
            key=lambda opponent: opponent.hand.get_card_count(),
        )
        min_opponent_cards_remaining = best_opponent.hand.get_card_count()
        opponent_hand_total = best_opponent.hand.get_total()

        input_vector = [
            *hand_state,
            top_discarded_card_state,
            drawn_card_state,
            hand_total,
            hand_cards_placed,
            min_opponent_cards_remaining,
            opponent_hand_total,
        ]

        device = next(self.model.parameters()).device

        return torch.tensor(
            input_vector,
            dtype=torch.float32,
            device=device,
        ).unsqueeze(0)

    def get_output(
        self,
        game: Game,
        drawn_card: Card | None
    ) -> tuple[bool, int, int]:

        input_tensor = self._prepare_input(game, drawn_card)

        with torch.no_grad():
            output = self.model(input_tensor)

        draw_from_discard = torch.argmax(output[:, :2]).item() == 1

        highest_index = 0
        highest_value = float("-inf")

        for i in range(2, 12):
            if output[0, i] > highest_value:
                highest_value = output[0, i]
                highest_index = i

        if highest_index == 11:
            row, col = -1, -1
        else:
            row = (highest_index - 2) // 3
            col = (highest_index - 2) % 3

        return draw_from_discard, row, col


if __name__ == "__main__":
    import main

    main.main()
