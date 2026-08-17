from evotorch.neuroevolution import NEProblem
import torch
from torch import nn
from ComputerPlayers import NeuralNetworkPlayer, RandomPlayer
from GameHolder import Game, Player
from MyErrors import IllegalMoveError
from evotorch.algorithms import GeneticAlgorithm
from evotorch.operators import GaussianMutation
from multiprocessing import Pool


class Network(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(15, 25),
            nn.Tanh(),
            nn.Linear(25, 20),
            nn.Sigmoid(),
            nn.Linear(20, 12),
        )
        # Randomly initialize the weights and biases
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)

    def forward(self, x):
        return self.network(x)


def play_game_with_network(network: nn.Module) -> tuple[Game, float]:
    players = [
        NeuralNetworkPlayer("Neural Player", network),
        RandomPlayer("Random Player"),
    ]
    game = Game(*players, print_errors=True)
    try:
        game.play_game()
    except IllegalMoveError as e:
        print(f"Illegal move during game: {e}")
        return game, float(500)
    except Exception as e:
        print(f"Error during game: {e.with_traceback(e.__traceback__)}")
        return game, float("inf")
    return (
        game,
        game.get_Players()[0].get_raw_hand_total() + game.illegal_move_count * 100,
    )  # Penalty for illegal moves


def play_games(network: nn.Module, num_rounds=100) -> float:
    scores = []
    games = []

    for _ in range(num_rounds):
        game, score = play_game_with_network(network)
        games.append(game)
        scores.append(score)

    if sum(scores) <= 0 or not scores:
        pass

    return sum(scores) / len(scores) if scores else float("inf")


def EvolveNetwork(num_generations=100, population_size=20, num_rounds=20) -> nn.Module:
    problem = NEProblem(
        objective_sense="min",
        network=Network(),
        network_eval_func=lambda net: play_games(net, num_rounds=num_rounds),
        num_actors=20,
    )

    searcher = GeneticAlgorithm(
        problem,
        popsize=population_size,
        operators=[
            GaussianMutation(
                problem,
                stdev=0.1,
            ),
        ],
    )

    for generation in range(num_generations):
        searcher.step()
        print(
            "Generation:",
            generation,
            "Best fitness:",
            searcher.status["best_eval"],
        )

    return searcher.status["pop_best"]


def main():
    best_network = EvolveNetwork(num_generations=50, population_size=10, num_rounds=50)
    torch.save(best_network.state_dict(), "best_network.pth")
    print("Best network saved to best_network.pth")


if __name__ == "__main__":
    print("Test the network before evolving:")
    play_games(Network(), num_rounds=10)  # Test the network before evolving
    print("Passed!\nEvolving the network...")
    main()
