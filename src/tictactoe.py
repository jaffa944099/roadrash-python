import tkinter as tk
from tkinter import messagebox, ttk

class TicTacToe(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tic-Tac-Toe")
        self.geometry("300x350")
        self.resizable(False, False)
        
        # Try to use clam theme if available
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header label
        self.header = ttk.Label(self, text=f"Player {self.current_player}'s turn", font=('Helvetica', 14, 'bold'))
        self.header.pack(pady=10)
        
        # Game board frame
        self.board_frame = ttk.Frame(self)
        self.board_frame.pack()
        
        # Create 3x3 grid of buttons
        for i in range(9):
            btn = tk.Button(self.board_frame, text="", font=('Helvetica', 20, 'bold'), width=5, height=2,
                            command=lambda i=i: self.make_move(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)
            
        # Reset button
        self.reset_btn = ttk.Button(self, text="Restart Game", command=self.reset_game)
        self.reset_btn.pack(pady=20)
        
    def make_move(self, index):
        if self.board[index] == "" and not self.check_winner():
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            
            if self.check_winner():
                self.header.config(text=f"Player {self.current_player} Wins!")
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!", parent=self)
            elif "" not in self.board:
                self.header.config(text="It's a Tie!")
                messagebox.showinfo("Game Over", "It's a tie!", parent=self)
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.header.config(text=f"Player {self.current_player}'s turn")
                
    def check_winner(self):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)              # Diagonals
        ]
        
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != "":
                return True
        return False
        
    def reset_game(self):
        self.current_player = "X"
        self.board = [""] * 9
        self.header.config(text=f"Player {self.current_player}'s turn")
        for btn in self.buttons:
            btn.config(text="")
