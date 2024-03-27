#Driver file: in charge of user input and current game state

import pygame as p
import os
import ChessEngine, ChessAI

p.init()
WIDTH = HEIGHT = 600
DIMENSION = 8 # Chess boards are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
move_sound = p.mixer.Sound("sounds/move.wav")

# For loading images
def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        chessPieces = p.image.load("images/" + piece + ".png")
        IMAGES[piece] = p.transform.smoothscale(chessPieces, (SQ_SIZE - 10, SQ_SIZE - 10))
    
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
    gameOver = False
    playerOne = True # Determines if white is player(T) or AI(F)
    playerTwo = False # Deterermines if black is player(T) or AI(F)

    while running:
        humanTurn = (gs.whiteMove and playerOne) or (not gs.whiteMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse 
            elif e.type == p.MOUSEBUTTONDOWN: #click functions
                if not gameOver and humanTurn:
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
                                p.mixer.Sound.play(move_sound)
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
                    gameOver = False
                    gs.checkmate = False
                    gs.stalemate = False
                    gs.undoMove()       
                    moveMade = True 
                    animate = False
                elif e.key == p.K_r: #reset board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                elif e.key == p.K_w: #Switches white pieces to AI or player when left ctrl is pressed
                    if playerOne == True:
                        playerOne = False
                    else:
                        playerTwo = True
                elif e.key == p.K_b: #Switches Black pieces to AI or player when left ctrl is pressed
                    if playerTwo == True:
                        playerTwo = False
                    else:
                        playerTwo = True
        #AI Move
        if not gameOver and not humanTurn:
            AI_Move = ChessAI.findBestMove(gs, validMoves)
            if AI_Move is None:
                AI_Move = ChessAI.findRandomMove(validMoves)
            p.mixer.Sound.play(move_sound)
            gs.makeMove(AI_Move)
            moveMade = True
            animate = True
        if moveMade:
            if animate:
                if len(gs.moveLog) != 0:
                    animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkmate:
            gameOver = True
            if gs.whiteMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate, Game is over')

        clock.tick(MAX_FPS)
        p.display.flip()

# Responsable for all the graphics 
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on the board
    drawSquareLabels(screen)

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

@staticmethod
def get_alphacol(col):
    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    return ALPHACOLS[col]

# Draw squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color("#eeeed2"), p.Color("#769656")] #light, dark
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawSquareLabels(screen):
    font = p.font.SysFont('monospace', 18, bold = True)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            #row position text
            if c == 0:
                color = "#769656" if r % 2 == 0 else "#eeeed2"
                label = font.render(str(DIMENSION - r), 1, color)
                label_pos = (5, 5 + r * SQ_SIZE)
                screen.blit(label, label_pos)
            #columns position text
            if r == 7:
                color = "#769656" if (r + c) % 2 == 0 else "#eeeed2"
                label = font.render(get_alphacol(c), 1, color)
                label_pos = (c * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 20)
                screen.blit(label, label_pos)

# Draw pieces on the board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # If empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE + 4, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

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
        drawSquareLabels(screen)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # piece capture animate
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw movement
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE + 4, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Calibri", 48, True, False)
    textObject = font.render(text, 1, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 1, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()