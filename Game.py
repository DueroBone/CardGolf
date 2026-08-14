from Cards import DiscardPile, DrawPile, Hand, NullHand, Card
import random


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: Hand = NullHand()

    def _set_hand(self, hand: Hand) -> None:
        self.hand = hand

    def get_revealed_cards(self) -> list[Card | None]:
        return self.hand.get_cards()

    def get_total(self) -> int:
        return self.hand.get_total()

    def discard(self, card: Card, discard_pile: DiscardPile) -> None:
        discard_pile.add_card(card)

    def place_card(self, row: int, col: int, card: Card, game: Game) -> None:
        discarded = self.hand.place(row, col, card)
        self.discard(discarded, game.discard_pile)

    def reveal_card(self, row: int, col: int) -> None:
        self.hand.reveal(row, col)


class Game:
    def __init__(self, players: list[Player]):
        self.draw_pile = DrawPile()
        self.discard_pile: DiscardPile = DiscardPile()
        self.players: list[Player] = players
        for player in self.players:
            _hand = Hand(self.draw_pile)
            player._set_hand(_hand)

    def get_players(self) -> list[Player]:
        return self.players

    def draw_card(self) -> Card:
        return self.draw_pile.draw()

    def discard_card(self, card: Card) -> None:
        self.discard_pile.add_card(card)

    def get_discarded_pile(self) -> Card | None:
        return self.discard_pile.top_card()


def sample_game():
    player1 = Player("Alice")
    player2 = Player("Bob")
    # random.seed(42)  # For reproducibility

    game = Game([player1, player2])

    for player in game.get_players():
        print(f"{player.name}'s hand:")
        player.place_card(random.randint(0, 2), random.randint(0, 2), game.draw_pile.draw(), game)
        print(player.hand)

        print(f"Total value: {player.get_total()}\n")


if __name__ == "__main__":
    import main

    main.main()
