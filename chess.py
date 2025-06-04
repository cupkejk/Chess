import time

def inBounds(x, y):
    if(x > 7 or x < 0): return False
    if(y > 7 or y < 0): return False
    return True

class Board:
    def __init__(self):
        self.board = [[Blank() for _ in range(8)] for _ in range(8)]
        for i in range(8):
            self.board[1][i] = Pawn(-1)
            self.board[6][i] = Pawn(1)
        self.board[0][0] = Rook(-1)
        self.board[0][7] = Rook(-1)
        self.board[7][0] = Rook(1)
        self.board[7][7] = Rook(1)
        self.board[0][1] = Knight(-1)
        self.board[0][6] = Knight(-1)
        self.board[7][1] = Knight(1)
        self.board[7][6] = Knight(1)
        self.board[0][2] = Bishop(-1)
        self.board[0][5] = Bishop(-1)
        self.board[7][2] = Bishop(1)
        self.board[7][5] = Bishop(1)
        self.board[0][3] = Queen(-1)
        self.board[0][4] = King(-1)
        self.board[7][3] = Queen(1)
        self.board[7][4] = King(1)
        self.MAX_STAMINA = 10
        self.staminas = [self.MAX_STAMINA, self.MAX_STAMINA]
        self.lastTime = time.time()
        self.time = self.lastTime
        self.staminaDeductionPerSec = 0.5
        self.lastMove = [time.time(), time.time()]
        self.moveCooldown = 1
    
    def isOccupied(self, x, y):
        if isinstance(self.board[y][x], Blank):
            return 0
        else: return self.board[y][x].color
    
    def getPiece(self, x, y):
        return self.board[y][x]
    
    def deltaLastMove(self, color):
        now = time.time()
        if color == 1:
            return now - self.lastMove[1]
        else: return now - self.lastMove[0]
    
    def revert_move(self, move, piece):
        self.board[move.toy][move.tox].moved = False
        self.board[move.fromy][move.fromx] = self.board[move.toy][move.tox]
        self.board[move.toy][move.tox] = piece
    
    def setLastMove(self, color):
        now = time.time()
        if color == 1:
            self.lastMove[1] = now
        else: self.lastMove[0] = now

    def printMask(self, mask):
        for i in range(len(mask)):
            for j in range(len(mask[i])):
                if mask[i][j]:
                    print(1, end = '')
                else:
                    print(0, end = '')
            print()
    
    def is_valid(self, move):
        color = self.isOccupied(move.fromx, move.fromy)

        if not inBounds(move.fromx, move.fromy) or not inBounds(move.tox, move.toy): return False
        if self.stamina_from_move(move, before = True) > self.getStamina(color): return False
        if self.deltaLastMove(color) < self.moveCooldown: return False

        mask = self.board[move.fromy][move.fromx].createMask(move.fromx, move.fromy, self)
        self.printMask(mask)
        return mask[move.toy][move.tox]
    
    def move_piece(self, move):
        if not self.is_valid(move): return False
        print(move.fromx, move.fromy, move.tox, move.toy) #to delete

        color = self.isOccupied(move.fromx, move.fromy)
        self.setLastMove(color)

        self.board[move.toy][move.tox] = self.board[move.fromy][move.fromx]
        self.board[move.toy][move.tox].moved = True
        self.board[move.fromy][move.fromx] = Blank()
        return True
    
    def move_test(self, move):
        self.board[move.toy][move.tox] = self.board[move.fromy][move.fromx]
        self.board[move.toy][move.tox].moved = True
        self.board[move.fromy][move.fromx] = Blank()

    def checkWin(self):
        blackwin = True
        whitewin = True
        for row in self.board:
            for piece in row:
                if(str(piece) == "wK"): blackwin = False
                if(str(piece) == "bK"): whitewin = False
        if(whitewin): return 1
        if(blackwin): return -1
        return 0
    
    def stamina_from_move(self, move, before):
        try:
            if before:piece_moved = self.getPiece(move.fromx, move.fromy)
            else: piece_moved = self.getPiece(move.tox, move.toy)
        except IndexError:
            print(f"Error: Move coordinates ({move.fromx},{move.fromy}) out of bounds for stamina check.")
            return 0.0

        piece_char_representation = str(piece_moved).strip()

        if len(piece_char_representation) < 2:
            return 0.0

        piece_type_char = piece_char_representation[1]

        stamina_costs = {
            'P': 1.0,
            'N': 2.5,
            'B': 2.5,
            'R': 3.0,
            'Q': 4.0,
            'K': 0.5
        }

        cost = stamina_costs.get(piece_type_char)

        if cost is None:
            print(f"Warning: Piece type '{piece_type_char}' from '{piece_char_representation}' has no defined stamina cost. Defaulting to 0.")
            return 0.0
    
        return cost
    
    def getStamina(self, color):
        if color == 1:
            return self.staminas[1]
        else: return self.staminas[0]
    
    def setStamina(self, color, val):
        if color == 1:
            self.staminas[1] = val
        else: self.staminas[0] = val
    
    def updateStamina(self):
        self.time = time.time()
        dt = self.time - self.lastTime
        self.lastTime = self.time
        adding = self.staminaDeductionPerSec * dt
        for i in range(2):
            self.staminas[i] += adding
            if self.staminas[i] > self.MAX_STAMINA: self.staminas[i] = 10
    
    def deductStamina(self, move):
        deduction = self.stamina_from_move(move, before = False)
        col = self.isOccupied(move.tox, move.toy)
        stamina = self.getStamina(col) - deduction
        self.setStamina(col, stamina)



    

class Move:
    def __init__(self, fromx, fromy, tox, toy):
        self.fromx = fromx
        self.fromy = fromy
        self.tox = tox
        self.toy = toy

class ChessPiece:
    def __init__(self, points = 0, color = 0):
        self.points = points
        self.color = color
        self.moved = False
    
    def createMask(self, x, y, board):
        return self.emptyMask()

    def cast(self, x, y, xdir, ydir, board, mask, limit):
        for i in range(1, limit):
            newx = x+xdir*i
            newy = y+ydir*i
            if inBounds(newx, newy):
                newcol = board.isOccupied(newx, newy)
                if newcol == self.color: break
                elif newcol == -self.color:
                    mask[newy][newx] = True
                    break
                mask[newy][newx] = True

    
    def emptyMask(self):
        return [[False for _ in range(8)] for _ in range(8)]


class Blank(ChessPiece):
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return "  "

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(1, color)
    
    def __str__(self):
        if(self.color == 1): return "wP"
        else: return "bP"

    def createMask(self, x, y, board):
        mask = self.emptyMask()
        sign = 0
        if(self.color == 1):
            sign = -1
        else:
            sign = 1
        
        if inBounds(x, y+sign) and not board.isOccupied(x, y+sign):
            mask[y+sign][x] = True
            if not self.moved:
                if inBounds(x, y+sign*2) and not board.isOccupied(x, y+sign*2): mask[y+sign*2][x] = True
        if inBounds(x+1, y+sign) and board.isOccupied(x+1, y+sign) == -self.color: mask[y+sign][x+1] = True
        if inBounds(x-1, y+sign) and board.isOccupied(x-1, y+sign) == -self.color: mask[y+sign][x-1] = True
        return mask

class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(3, color)
    
    def __str__(self):
        if(self.color == 1): return "wN"
        else: return "bN"
    
    def createMask(self, x, y, board):
        mask = self.emptyMask()
        moves = [[1, 2], [2, 1], [-1, 2], [2, -1], [1, -2], [-2, 1], [-1, -2], [-2, -1]]
        for move in moves:
            newx = x + move[0]
            newy = y + move[1]
            if inBounds(newx, newy) and board.isOccupied(newx, newy) != self.color: mask[newy][newx] = True
        return mask

class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(5, color)
    
    def __str__(self):
        if(self.color == 1): return "wR"
        else: return "bR"
    
    def createMask(self, x, y, board):
        mask = self.emptyMask()
        self.cast(x, y, -1, 0, board, mask, 8)
        self.cast(x, y, 0, 1, board, mask, 8)
        self.cast(x, y, 1, 0, board, mask, 8)
        self.cast(x, y, 0, -1, board, mask, 8)
        return mask

class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(3, color)
    
    def __str__(self):
        if(self.color == 1): return "wB"
        else: return "bB"
    
    def createMask(self, x, y, board):
        mask = self.emptyMask()
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                self.cast(x, y, j, i, board, mask, 8)
        return mask

class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(9, color)
    
    def __str__(self):
        if(self.color == 1): return "wQ"
        else: return "bQ"
    
    def createMask(self, x, y, board):
        mask = self.emptyMask()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if(j == 0 and i == 0): continue
                self.cast(x, y, j, i, board, mask, 8)
        return mask

class King(ChessPiece):
    def __init__(self, color):
        super().__init__(1000, color)
    
    def __str__(self):
        if(self.color == 1): return "wK"
        else: return "bK"
    
    def createMask(self, x, y, board):
        mask = self.emptyMask()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if(j == 0 and i == 0): continue
                self.cast(x, y, j, i, board, mask, 2)
        return mask

def pam(piece, x, y):
    board = Board()
    board.board[y][x] = piece
    mask = board.board[y][x].createMask(x, y, board)
    for row in mask:
        for bul in row:
            if bul:
                print(1, end = '')
            else:
                print(0, end='')
        print()

def consolePlay():
    board = Board()
    while True:
        print(board.toStr(1))
        move = input().split(' ')
        print(move)
        numbers = [eval(i) for i in move]
        move = Move(numbers[0], numbers[1], numbers[2], numbers[3])
        board.move_piece(move)