import os
import sys
from enum import Enum
from typing import Optional, Tuple, List
from copy import deepcopy

class Player(Enum):
    HUMAN = 1
    AI = -1
    EMPTY = 0

class GameMode(Enum):
    HUMAN_VS_AI = 1
    HUMAN_VS_HUMAN = 2
    AI_VS_AI = 3

class TicTacToe:
    def __init__(self, board_size: int = 3, win_count: int = 3):
        self.board_size = board_size
        self.win_count = win_count
        self.board = [[Player.EMPTY for _ in range(board_size)] for _ in range(board_size)]
        self.ai_depth = 5
        self.history = []
    
    def display_board(self):
        """Display the current game board"""
        print("\n")
        for i, row in enumerate(self.board):
            print(f" {i} | ", end="")
            for j, cell in enumerate(row):
                if cell == Player.HUMAN:
                    print("X", end=" ")
                elif cell == Player.AI:
                    print("O", end=" ")
                else:
                    print(".", end=" ")
            print()
        print("    " + "-" * (self.board_size * 2 - 1))
        print("    ", end="")
        for j in range(self.board_size):
            print(j, end=" ")
        print("\n")
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid"""
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self.board[row][col] == Player.EMPTY
        return False
    
    def make_move(self, row: int, col: int, player: Player) -> bool:
        """Make a move on the board"""
        if self.is_valid_move(row, col):
            self.board[row][col] = player
            self.history.append((row, col, player))
            return True
        return False
    
    def check_winner(self) -> Optional[Player]:
        """Check if there's a winner"""
        # Check rows
        for row in self.board:
            if all(cell == row[0] and cell != Player.EMPTY for cell in row):
                return row[0]
        
        # Check columns
        for col in range(self.board_size):
            column = [self.board[row][col] for row in range(self.board_size)]
            if all(cell == column[0] and cell != Player.EMPTY for cell in column):
                return column[0]
        
        # Check diagonals
        diag1 = [self.board[i][i] for i in range(self.board_size)]
        if all(cell == diag1[0] and cell != Player.EMPTY for cell in diag1):
            return diag1[0]
        
        diag2 = [self.board[i][self.board_size - 1 - i] for i in range(self.board_size)]
        if all(cell == diag2[0] and cell != Player.EMPTY for cell in diag2):
            return diag2[0]
        
        return None
    
    def is_board_full(self) -> bool:
        """Check if board is full"""
        return all(cell != Player.EMPTY for row in self.board for cell in row)
    
    def evaluate(self) -> int:
        """Evaluation function for game state"""
        winner = self.check_winner()
        if winner == Player.AI:
            return 100
        elif winner == Player.HUMAN:
            return -100
        return 0
    
    def get_available_moves(self) -> List[Tuple[int, int]]:
        """Get all available moves"""
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == Player.EMPTY:
                    moves.append((i, j))
        return moves
    
    def minimax(self, depth: int, is_ai_turn: bool, alpha: int = -float('inf'), beta: int = float('inf')) -> Tuple[int, Optional[Tuple[int, int]]]:
        """Minimax algorithm with alpha-beta pruning"""
        winner = self.check_winner()
        if winner == Player.AI:
            return 100 + depth, None
        elif winner == Player.HUMAN:
            return -100 - depth, None
        elif self.is_board_full():
            return 0, None
        elif depth == 0:
            return self.evaluate(), None
        
        available_moves = self.get_available_moves()
        best_move = None
        
        if is_ai_turn:
            max_eval = -float('inf')
            for move in available_moves:
                self.board[move[0]][move[1]] = Player.AI
                eval_score, _ = self.minimax(depth - 1, False, alpha, beta)
                self.board[move[0]][move[1]] = Player.EMPTY
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in available_moves:
                self.board[move[0]][move[1]] = Player.HUMAN
                eval_score, _ = self.minimax(depth - 1, True, alpha, beta)
                self.board[move[0]][move[1]] = Player.EMPTY
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
    
    def get_best_ai_move(self) -> Optional[Tuple[int, int]]:
        """Get the best move for AI"""
        _, best_move = self.minimax(self.ai_depth, True)
        return best_move
    
    def show_winning_sequence(self, ai_wins: bool):
        """Display ideal winning sequence"""
        board_copy = deepcopy(self.board)
        sequence = []
        current_player = Player.AI if ai_wins else Player.HUMAN
        opponent = Player.HUMAN if ai_wins else Player.AI
        
        self.board = board_copy
        while not self.check_winner() and not self.is_board_full():
            if current_player == Player.AI:
                _, move = self.minimax(self.ai_depth, True)
            else:
                _, move = self.minimax(self.ai_depth, False)
            
            if move is None:
                break
            
            self.board[move[0]][move[1]] = current_player
            sequence.append((move, current_player))
            current_player, opponent = opponent, current_player
        
        self.board = board_copy
        return sequence
    
    def set_difficulty(self, depth: int):
        """Set AI difficulty level"""
        self.ai_depth = max(1, min(depth, 9))
        print(f"Difficulty set to depth: {self.ai_depth}")
    
    def reset_game(self):
        """Reset the game board"""
        self.board = [[Player.EMPTY for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.history = []

import time

def play_game(mode: GameMode, game: TicTacToe):
    """Main game loop"""
    print(f"\n=== Game Started: {mode.name} ===")
    game.reset_game()
    
    while True:
        game.display_board()
        
        # 1. Check for Terminal State
        winner = game.check_winner()
        if winner:
            print(f"{'AI' if winner == Player.AI else 'Player'} wins!")
            break
        
        if game.is_board_full():
            print("It's a draw!")
            break
        
        # 2. Handle Game Modes
        if mode == GameMode.HUMAN_VS_AI:
            # Human Turn (X)
            print("Your turn (X):")
            while True:
                try:
                    row, col = map(int, input("Enter row and column (0-2): ").split())
                    if game.make_move(row, col, Player.HUMAN):
                        break
                except:
                    print("Invalid input!")
            
            # AI Turn (O) - Only if game isn't over
            if not game.check_winner() and not game.is_board_full():
                move = game.get_best_ai_move()
                if move:
                    game.make_move(move[0], move[1], Player.AI)
                    print(f"AI plays at ({move[0]}, {move[1]})")

        elif mode == GameMode.HUMAN_VS_HUMAN:
            player = Player.HUMAN if len(game.history) % 2 == 0 else Player.AI
            symbol = "X" if player == Player.HUMAN else "O"
            print(f"Player {symbol} turn:")
            while True:
                try:
                    row, col = map(int, input("Enter row and column (0-2): ").split())
                    if game.make_move(row, col, player):
                        break
                except:
                    print("Invalid input!")

        elif mode == GameMode.AI_VS_AI:
            # Determine which AI is moving based on history length
            # Even turns = AI 1 (acting as HUMAN/X), Odd turns = AI 2 (acting as AI/O)
            is_first_ai_turn = (len(game.history) % 2 == 0)
            current_player = Player.HUMAN if is_first_ai_turn else Player.AI
            
            print(f"AI ({'X' if is_first_ai_turn else 'O'}) is thinking...")
            time.sleep(1) # Slows down the spam so you can watch
            
            # We call minimax. For X, we want to minimize score; for O, we maximize.
            _, move = game.minimax(game.ai_depth, not is_first_ai_turn)
            
            if move:
                game.make_move(move[0], move[1], current_player)

def main():
    """Main program"""
    game = TicTacToe()
    
    while True:
        print("\n=== Tic Tac Terminal ===\nLearn to play Tic Tac Toe with an unbeatable AI opponent!")
        print("1. Human vs AI")
        print("2. Human vs Human")
        print("3. AI vs AI")
        print("4. Set Difficulty")
        print("5. Exit")
        
        choice = input("Select option: ")
        
        if choice == "1":
            play_game(GameMode.HUMAN_VS_AI, game)
        elif choice == "2":
            play_game(GameMode.HUMAN_VS_HUMAN, game)
        elif choice == "3":
            play_game(GameMode.AI_VS_AI, game)
        elif choice == "4":
            depth = int(input("Enter depth (1-9): "))
            game.set_difficulty(depth)
        elif choice == "5":
            break

if __name__ == "__main__":
    main()