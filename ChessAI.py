#AI file: in charge of implenting algorithms for AI gameplay
import random

pieceWeight = {'K': 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

# random move set for initial testing and if no best moves are found
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

# implementing algorithns such as minimax/greedy
def findBestMoveGreedy(gs, validMoves):
    turnMultiplier = 1 if gs.whiteMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = - CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
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

def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findNegaMax(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteMove else -1)
    return nextMove

def findMinMaxRecursive(gs, validMoves, depth, whiteMove): #more effective but slower past depth 2
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxRecursive (gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxRecursive (gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
    
def findNegaMax(gs, validMoves, depth, alpha, beta, turnMultiplier): #implemented alpha/beta pruning. improved run time
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMax(gs, nextMoves, depth - 1,  -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: #alpha/beta pruning steps
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
    
def scoreBoard(gs):    #positve score is white advanatage and negative score is black advantage
    if gs.checkmate:
        if gs.whiteMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceWeight[square[1]]
            elif square[0] == 'b':
                score -= pieceWeight[square[1]]
    return score

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