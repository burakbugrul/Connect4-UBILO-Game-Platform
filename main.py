import os
import sys
from game import Game


if __name__ == "__main__":
    game = Game()
    game.get_players()
    game.play()