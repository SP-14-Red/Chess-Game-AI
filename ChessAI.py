#AI file: in charge of implenting algorithms for AI gameplay
import random

pieceWeight = {'K': 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0

# random move set for initial testing
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

# implementing algorithns such as minimax/greedy
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = - CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkmate:
                score = - turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

# Scoring for the board
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceWeight[square[1]]
            elif square[0] == 'b':
                score -= pieceWeight[square[1]]
    return score