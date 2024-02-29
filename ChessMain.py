#Driver file: in charge of user input and current game state

import pygame as p
import ChessEngine

p.init()
WIDTH = HEIGHT = 800
DIMENSION = 8 # Chess boards are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

# For loading images
def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.smoothscale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    

# Main driver that will handle user input and update graphics
def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('SP-14-RED | Chess AI')
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = () #none selected initially
    playerClicks = [] #tracks player clicks

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #mouse 
            elif e.type == p.MOUSEBUTTONDOWN: #click functions
                location = p.mouse.get_pos() #takes x and y position of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = () #unselects click
                else:
                    sqSelected = (row, col) #select click
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2: #action on second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            #key presses
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z key is pressed
                    gs.undoMove()       
                    moveMade = True 
                    animate = False
        if moveMade:
            if animate:
                if len(gs.moveLog) != 0:
                    animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

# Responsable for all the graphics 
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on the board

# highglights valid moves
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.fill(p.Color('#6495ED'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))

# Draw squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color("#eeeed2"), p.Color("#769656")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw pieces on the board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # If empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# piece animation movement
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # piece capture animate
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw movement
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    main()