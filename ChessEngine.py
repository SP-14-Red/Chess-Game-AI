# Engine file: in charge of game rules and move related data

class GameState():
    def __init__(self):
        #8x8 chessboard set up in the traditional poisitons
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
            ]
        
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteMove = True
        self.moveLog = [] #Log moves for review or replay after
        self.wK_Location = (7, 4)
        self.bK_Location = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () 
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wKs, self.currentCastlingRight.wQs, self.currentCastlingRight.bQs, self.currentCastlingRight.bKs)]


    #takes move changes and initializes the move
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved  
        self.moveLog.append(move) #log for future use
        self.whiteMove = not self.whiteMove #swap player
        #update king location
        if move.pieceMoved == 'wK':
            self.wK_Location = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.bK_Location = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            #promotedPiece = input("Promote to Q, R, B, or N")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capture
        #update enpassant
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()
        
        #castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #king side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #moves rook
                self.board[move.endRow][move.endCol + 1] = '--' #update space
            else: #queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] #moves rook
                self.board[move.endRow][move.endCol - 2] = '--' #update space

        self.updateCastelRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wKs, self.currentCastlingRight.wQs, self.currentCastlingRight.bQs, self.currentCastlingRight.bKs))


    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteMove = not self.whiteMove
            
            #update king pos
            if move.pieceMoved == 'wK':
                self.wK_Location = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.bK_Location = (move.startRow, move.startCol)
            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            #undo for castling
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wKs, newRights.wQs, newRights.bKs, newRights.bQs,) 
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] #moves rook
                    self.board[move.endRow][move.endCol - 1] = '--' #update space
                else: #queen side
                    self.board[move.endRow][move.endCol + 2] = self.board[move.endRow][move.endCol + 1] #moves rook
                    self.board[move.endRow][move.endCol + 1] = '--' #update space  
    
    #can castle
    def updateCastelRights(self, move):
        #king movement
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wKs = False
            self.currentCastlingRight.wQs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bKs = False
            self.currentCastlingRight.bQs = False
        #rook movements
        elif move.pieceMoved == 'wR': #white rooks
            if move.startRow == 7:
                if move.startCol == 0 : #left side rook
                    self.currentCastlingRight.wQs = False
                elif move.startCol == 7 : #right side rook
                    self.currentCastlingRight.wKs = False
        elif move.pieceMoved == 'bR': #black rooks
            if move.startRow == 0:
                if move.startCol == 0 : #left side rook
                    self.currentCastlingRight.bQs = False
                elif move.startCol == 7 : #right side rook
                    self.currentCastlingRight.bKs = False    
        #if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wKs = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bKs = False        

    def getValidMoves(self):
        tempEnpassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wKs, self.currentCastlingRight.wQs, self.currentCastlingRight.bKs, self.currentCastlingRight.bQs, )
        moves = self.allPossibleMoves()
        for i in range(len(moves) -1, -1, -1):
            self.makeMove(moves[i])
            self.whiteMove = not self.whiteMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        if self.whiteMove:
            self.getCastleMoves(self.wK_Location[0], self.wK_Location[1], moves)
        else:
            self.getCastleMoves(self.bK_Location[0], self.bK_Location[1], moves)
        self.enPassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        if self.whiteMove:
            return self.sqUnderAttack(self.wK_Location[0], self.wK_Location[1])
        else:
            return self.sqUnderAttack(self.bK_Location[0], self.bK_Location[1])

    def sqUnderAttack(self, r, c):
        self.whiteMove = not self.whiteMove #change turns
        oppMoves = self.allPossibleMoves()
        self.whiteMove = not self.whiteMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def allPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range (len(self.board[r])):
                       turn = self.board[r][c][0]
                       if (turn == 'w' and self.whiteMove) or (turn == 'b' and not self.whiteMove):
                            piece = self.board[r][c][1]
                            self.moveFunctions[piece](r, c, moves) #calls move functions
        return moves                        

    def getPawnMoves(self, r, c, moves):
        if self.whiteMove: #white pawns
            if self.board[r - 1][c] == "--": 
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove = True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove = True))

        else:
            if self.board[r + 1][c] == "--": 
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove = True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove = True))
            
        

    def getRookMoves(self, r, c, moves):
        directions = ( (-1, 0), (1, 0), (0, 1), (0, -1) )        
        enemyColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8: #in bounds
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move( (r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move( (r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        directions = ((-2, 1), (-2, -1), (2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))   
        allyColor = "w" if self.whiteMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #in bounds
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ( (-1,  1), (-1, -1), (1 , -1), (1, 1) )  
        enemyColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8: #in bounds
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1))    
        allyColor = "w" if self.whiteMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #in bounds
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))     

    def getCastleMoves(self, r, c, moves):
        if self.sqUnderAttack(r, c):
            return #cannot castle while in check
        if (self.whiteMove and self.currentCastlingRight.wKs) or (not self.whiteMove and self.currentCastlingRight.bKs):
            self.getKingSideCastleMoves(r,c, moves)
        if (self.whiteMove and self.currentCastlingRight.wQs) or (not self.whiteMove and self.currentCastlingRight.bQs):
            self.getQueenSideCastleMoves(r,c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.sqUnderAttack(r, c + 1) and not self.sqUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, r, c, moves):  
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.sqUnderAttack(r, c - 1) and not self.sqUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))  



class CastleRights():
    def __init__(self, wKs, bKs, wQs, bQs):
        self.wKs = wKs
        self.bKs = bKs
        self.wQs = wQs
        self.bQs = bQs

class Move():
    #maps keys to values
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
     
    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]    
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol 
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.isCastleMove = isCastleMove
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
                  

    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + ", " + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]




        