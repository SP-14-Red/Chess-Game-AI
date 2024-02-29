#Driver file: in charge of user input and current game state

import pygame as p
import ChessEngine

p.init()
WIDTH = HEIGHT = 800
DIMENSION = 8 # Chess boards are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
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
    #screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

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
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            #key presses
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z key is pressed
                    gs.undoMove()       
                    moveMade = True 

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
        

# Responsable for all the graphics 
def drawGameState(screen, gs):
    drawBoard(screen) # Draw squares on the board
    drawPieces(screen, gs.board) # Draw pieces on the board

# Draw squares on the board
def drawBoard(screen):
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


if __name__ == "__main__":
    main()