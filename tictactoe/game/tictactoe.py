import numpy as np
from typing import List, Tuple, Optional
from enum import Enum

class Player(Enum):
    EMPTY = 0
    X = 1
    O = -1

class GameResult(Enum):
    ONGOING = 0
    X_WINS = 1
    O_WINS = -1
    DRAW = 2

class TicTacToe:
    """Core Tic-Tac-Toe game logic"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the game board"""
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = Player.X
        self.game_over = False
        self.winner = None
        self.move_count = 0
    
    def get_board_state(self) -> np.ndarray:
        """Get current board state as numpy array"""
        return self.board.copy()
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get list of valid moves (empty positions)"""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0]
    
    def make_move(self, row: int, col: int) -> bool:
        """Make a move at the specified position"""
        if self.game_over or self.board[row, col] != 0:
            return False
        
        self.board[row, col] = self.current_player.value
        self.move_count += 1
        
        # Check for win or draw
        self._check_game_end()
        
        # Switch player
        if not self.game_over:
            self.current_player = Player.O if self.current_player == Player.X else Player.X
        
        return True
    
    def _check_game_end(self):
        """Check if the game has ended"""
        # Check rows
        for row in self.board:
            if abs(sum(row)) == 3:
                self.game_over = True
                self.winner = Player.X if sum(row) == 3 else Player.O
                return
        
        # Check columns
        for col in range(3):
            col_sum = sum(self.board[:, col])
            if abs(col_sum) == 3:
                self.game_over = True
                self.winner = Player.X if col_sum == 3 else Player.O
                return
        
        # Check diagonals
        diag1_sum = sum([self.board[i, i] for i in range(3)])
        diag2_sum = sum([self.board[i, 2-i] for i in range(3)])
        
        for diag_sum in [diag1_sum, diag2_sum]:
            if abs(diag_sum) == 3:
                self.game_over = True
                self.winner = Player.X if diag_sum == 3 else Player.O
                return
        
        # Check for draw
        if self.move_count == 9:
            self.game_over = True
            self.winner = None  # Draw
    
    def get_result(self) -> GameResult:
        """Get the current game result"""
        if not self.game_over:
            return GameResult.ONGOING
        elif self.winner is None:
            return GameResult.DRAW
        elif self.winner == Player.X:
            return GameResult.X_WINS
        else:
            return GameResult.O_WINS
    
    def board_to_vector(self) -> np.ndarray:
        """Convert board to 1D vector for neural network input"""
        return self.board.flatten()
    
    def vector_to_board(self, vector: np.ndarray) -> np.ndarray:
        """Convert 1D vector back to 3x3 board"""
        return vector.reshape(3, 3)
    
    def print_board(self):
        """Print the current board state"""
        symbols = {0: ' ', 1: 'X', -1: 'O'}
        print("\n  0   1   2")
        for i in range(3):
            print(f"{i} {symbols[self.board[i,0]]} | {symbols[self.board[i,1]]} | {symbols[self.board[i,2]]}")
            if i < 2:
                print("  --|---|--")
        print()
    
    def clone(self):
        """Create a copy of the current game state"""
        new_game = TicTacToe()
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.move_count = self.move_count
        return new_game 