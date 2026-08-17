from Cards import DiscardPile, DrawPile, Hand, Card
from MyErrors import IllegalMoveError
from Players import Player, DebugPlayer, HumanPlayer


class Game:
    def __init__(self, *Players: Player, print_errors: bool = True):
        self.illegal_move_count = 0
        self.draw_pile = DrawPile()
        self.discard_pile: DiscardPile = DiscardPile()
        self.Player: list[Player] = list(Players)
        self.print_errors = print_errors
        for player in self.Player:
            _hand = Hand(self.draw_pile)
            player._set_hand(_hand)

    def get_Players(self) -> list[Player]:
        return self.Player

    def draw_card(self) -> Card:
        return self.draw_pile.draw()

    def discard_card(self, card: Card) -> None:
        self.discard_pile.add_card(card)

    def check_discarded_card(self) -> Card | None:
        return self.discard_pile.top_card()

    def get_discard_card(self) -> Card | None:
        return self.discard_pile.draw()

    def is_game_over(self) -> bool:
        # Check if the draw pile is empty
        if not self.draw_pile.cards:
            return True

        # Check if any player has no un-revelead cards left
        for player in self.Player:
            hand_cards = player.get_revealed_cards()
            return all(card is not None for card in hand_cards)
        return False

    def get_opponents(self, current_player: Player) -> list[Player]:
        return [player for player in self.Player if player != current_player]

    def play_round(self) -> None:
        for player in self.Player:
            try:
                player(self)
            except IllegalMoveError as e:
                print(f"Illegal move by {player.name}: {e}") if self.print_errors else None
                self.illegal_move_count += 1
                continue

    def play_game(self) -> None:
        while not self.is_game_over():
            self.play_round()

    @staticmethod
    def sample_game():
        game = Game(HumanPlayer("Player 1"), DebugPlayer("Player 2"))

        print("Starting game...\n")

        while not game.is_game_over():
            for player in game.get_Players():
                print(f"{player.name}'s turn:")
                player(game)
                print()

        min_score = game.get_Players()[0].get_hand_total()
        winner = game.get_Players()[0]

        for player in game.get_Players():
            player.on_endgame()
            score = player.get_hand_total()
            print(f"Player {player.name}'s hand:\n{player.hand}\nTotal: {score}")
            if score < min_score:
                min_score = score
                winner = player
            print()

        print(f"\n{winner.name} wins with a total of {min_score}!")


if __name__ == "__main__":
    import main

    main.main()
