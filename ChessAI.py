#AI file: in charge of implenting algorithms for AI gameplay
import random


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove():
    return