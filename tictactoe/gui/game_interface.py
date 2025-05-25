import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import threading
import time
from typing import Optional
import os

from game.tictactoe import TicTacToe, Player, GameResult
from models.neural_network import TicTacToeAgent, RandomAgent, HeuristicAgent
from training.trainer import TicTacToeTrainer

class TicTacToeGUI:
    """Graphical User Interface for Tic-Tac-Toe game"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Neural Network Tic-Tac-Toe")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Game state
        self.game = TicTacToe()
        self.agent = TicTacToeAgent()  # For Hard difficulty
        self.medium_agent = TicTacToeAgent()  # For Medium difficulty
        self.trainer = TicTacToeTrainer(self.agent)
        
        # Load different models for different difficulties
        self.models_loaded = {"medium": False, "hard": False}
        
        # Try to load Medium model (basic trained model)
        if os.path.exists("models/trained_model.pth"):
            try:
                self.medium_agent.load_model("models/trained_model.pth")
                self.models_loaded["medium"] = True
                print("✅ Loaded MEDIUM model: models/trained_model.pth")
            except Exception as e:
                print(f"⚠️ Failed to load medium model: {e}")
        
        # Try to load Hard model (ultra-trained model)
        if os.path.exists("models/ultra_trained_model.pth"):
            try:
                self.agent.load_model("models/ultra_trained_model.pth")
                self.models_loaded["hard"] = True
                print("✅ Loaded HARD model: models/ultra_trained_model.pth (93.6% win rate)")
            except Exception as e:
                print(f"⚠️ Failed to load hard model: {e}")
        
        # Print status
        if self.models_loaded["medium"] and self.models_loaded["hard"]:
            print("🎯 All AI models loaded successfully!")
            default_difficulty = "Hard"
        elif self.models_loaded["hard"]:
            print("🎯 Ultra AI loaded - try Hard difficulty!")
            default_difficulty = "Hard"
        elif self.models_loaded["medium"]:
            print("🎯 Basic AI loaded - try Medium difficulty!")
            default_difficulty = "Medium"
        else:
            print("ℹ️ No trained models found - only Easy (random) available")
            default_difficulty = "Easy"
        
        # Game settings
        self.difficulty = tk.StringVar(value=default_difficulty)
        self.human_is_x = tk.BooleanVar(value=True)
        self.game_mode = tk.StringVar(value="Human vs AI")
        
        # UI elements
        self.buttons = []
        self.status_label = None
        self.score_label = None
        
        # Game statistics
        self.stats = {"wins": 0, "losses": 0, "draws": 0}
        
        self.setup_ui()
        self.new_game()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title
        title_label = tk.Label(self.root, text="Neural Network Tic-Tac-Toe", 
                              font=("Arial", 20, "bold"), fg="blue")
        title_label.pack(pady=10)
        
        # Control panel
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Difficulty selection
        diff_frame = tk.Frame(control_frame)
        diff_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(diff_frame, text="Difficulty:", font=("Arial", 12)).pack()
        difficulty_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty,
                                       values=["Easy", "Medium", "Hard"], state="readonly")
        difficulty_combo.pack()
        difficulty_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)
        
        # Add difficulty info labels
        easy_info = tk.Label(diff_frame, text="Easy: Random AI", font=("Arial", 8), fg="gray")
        easy_info.pack()
        
        medium_status = "✅ Neural Network" if self.models_loaded["medium"] else "❌ No Model"
        medium_color = "green" if self.models_loaded["medium"] else "red"
        medium_info = tk.Label(diff_frame, text=f"Medium: {medium_status}", 
                              font=("Arial", 8), fg=medium_color)
        medium_info.pack()
        
        hard_status = "✅ Ultra AI (93.6%)" if self.models_loaded["hard"] else "❌ No Model"
        hard_color = "green" if self.models_loaded["hard"] else "red"
        hard_info = tk.Label(diff_frame, text=f"Hard: {hard_status}", 
                            font=("Arial", 8), fg=hard_color)
        hard_info.pack()
        
        # Game mode selection
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(mode_frame, text="Game Mode:", font=("Arial", 12)).pack()
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.game_mode,
                                 values=["Human vs AI", "AI vs AI"], state="readonly")
        mode_combo.pack()
        mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # Player selection
        player_frame = tk.Frame(control_frame)
        player_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(player_frame, text="You are:", font=("Arial", 12)).pack()
        player_combo = ttk.Combobox(player_frame, textvariable=self.human_is_x,
                                   values=[True, False], state="readonly")
        player_combo.pack()
        
        # Game board
        board_frame = tk.Frame(self.root, bg="black")
        board_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(board_frame, text="", font=("Arial", 24, "bold"),
                               width=4, height=2, bg="lightgray",
                               command=lambda r=i, c=j: self.on_button_click(r, c))
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.buttons.append(row)
        
        # Status and controls
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Your turn!", 
                                    font=("Arial", 14), fg="green")
        self.status_label.pack()
        
        # Score display
        self.score_label = tk.Label(status_frame, text="Wins: 0 | Losses: 0 | Draws: 0",
                                   font=("Arial", 12))
        self.score_label.pack(pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="New Game", command=self.new_game,
                 font=("Arial", 12), bg="lightblue").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Train AI", command=self.open_training_window,
                 font=("Arial", 12), bg="lightgreen").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Save Model", command=self.save_model,
                 font=("Arial", 12), bg="lightyellow").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Load Model", command=self.load_model,
                 font=("Arial", 12), bg="lightcoral").pack(side=tk.LEFT, padx=5)
    
    def on_button_click(self, row: int, col: int):
        """Handle button click on game board"""
        if self.game.game_over or self.game.board[row, col] != 0:
            return
        
        if self.game_mode.get() == "Human vs AI":
            # Human move
            if (self.game.current_player == Player.X and self.human_is_x.get()) or \
               (self.game.current_player == Player.O and not self.human_is_x.get()):
                self.make_move(row, col)
                
                # AI move after human move
                if not self.game.game_over:
                    self.root.after(500, self.ai_move)
    
    def make_move(self, row: int, col: int):
        """Make a move on the board"""
        if self.game.make_move(row, col):
            self.update_board()
            self.check_game_end()
    
    def ai_move(self):
        """Make AI move"""
        if self.game.game_over:
            return
        
        current_state = self.game.get_board_state()
        valid_moves = self.game.get_valid_moves()
        
        # Get AI opponent based on difficulty
        if self.difficulty.get() == "Easy":
            opponent = RandomAgent()
            move = opponent.get_move(current_state, valid_moves)
        elif self.difficulty.get() == "Medium":
            if self.models_loaded["medium"]:
                # Use trained neural network
                move = self.medium_agent.get_move(current_state, valid_moves, temperature=0.1)
            else:
                # Fallback to heuristic agent
                opponent = HeuristicAgent()
                move = opponent.get_move(current_state, valid_moves)
        else:  # Hard
            if self.models_loaded["hard"]:
                # Use ultra-trained neural network
                move = self.agent.get_move(current_state, valid_moves, temperature=0.0)
            else:
                # Fallback to heuristic agent (better than random)
                opponent = HeuristicAgent()
                move = opponent.get_move(current_state, valid_moves)
        
        self.make_move(move[0], move[1])
    
    def update_board(self):
        """Update the visual board"""
        symbols = {0: "", 1: "X", -1: "O"}
        colors = {0: "lightgray", 1: "lightblue", -1: "lightcoral"}
        
        for i in range(3):
            for j in range(3):
                value = self.game.board[i, j]
                self.buttons[i][j].config(text=symbols[value], bg=colors[value])
        
        # Update status
        if not self.game.game_over:
            if self.game_mode.get() == "Human vs AI":
                if (self.game.current_player == Player.X and self.human_is_x.get()) or \
                   (self.game.current_player == Player.O and not self.human_is_x.get()):
                    self.status_label.config(text="Your turn!", fg="green")
                else:
                    self.status_label.config(text="AI thinking...", fg="orange")
            else:
                player_name = "X" if self.game.current_player == Player.X else "O"
                self.status_label.config(text=f"AI {player_name} thinking...", fg="blue")
    
    def check_game_end(self):
        """Check if game has ended and update statistics"""
        if self.game.game_over:
            result = self.game.get_result()
            
            if result == GameResult.DRAW:
                self.status_label.config(text="It's a draw!", fg="blue")
                self.stats["draws"] += 1
            elif self.game_mode.get() == "Human vs AI":
                if (result == GameResult.X_WINS and self.human_is_x.get()) or \
                   (result == GameResult.O_WINS and not self.human_is_x.get()):
                    self.status_label.config(text="You win!", fg="green")
                    self.stats["wins"] += 1
                else:
                    self.status_label.config(text="AI wins!", fg="red")
                    self.stats["losses"] += 1
            else:  # AI vs AI
                winner = "X" if result == GameResult.X_WINS else "O"
                self.status_label.config(text=f"AI {winner} wins!", fg="purple")
            
            self.update_score_display()
    
    def update_score_display(self):
        """Update the score display"""
        self.score_label.config(
            text=f"Wins: {self.stats['wins']} | Losses: {self.stats['losses']} | Draws: {self.stats['draws']}"
        )
    
    def new_game(self):
        """Start a new game"""
        self.game.reset()
        self.update_board()
        
        if self.game_mode.get() == "AI vs AI":
            self.status_label.config(text="AI vs AI - Click to start", fg="blue")
            self.root.after(1000, self.ai_vs_ai_game)
        else:
            if self.human_is_x.get():
                self.status_label.config(text="Your turn! (You are X)", fg="green")
            else:
                self.status_label.config(text="AI starts! (You are O)", fg="orange")
                self.root.after(1000, self.ai_move)
    
    def ai_vs_ai_game(self):
        """Run AI vs AI game"""
        if self.game.game_over:
            return
        
        current_state = self.game.get_board_state()
        valid_moves = self.game.get_valid_moves()
        
        # Both players use the trained agent with different temperatures
        if self.game.current_player == Player.X:
            move = self.agent.get_move(current_state, valid_moves, temperature=0.1)
        else:
            move = self.agent.get_move(current_state, valid_moves, temperature=0.3)
        
        self.make_move(move[0], move[1])
        
        if not self.game.game_over:
            self.root.after(1000, self.ai_vs_ai_game)
    
    def on_difficulty_change(self, event=None):
        """Handle difficulty change"""
        self.new_game()
    
    def on_mode_change(self, event=None):
        """Handle game mode change"""
        self.new_game()
    
    def open_training_window(self):
        """Open training configuration window"""
        training_window = TrainingWindow(self.root, self.agent, self.trainer)
    
    def save_model(self):
        """Save the trained model"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pth",
            filetypes=[("PyTorch files", "*.pth"), ("All files", "*.*")]
        )
        if filename:
            self.agent.save_model(filename)
            messagebox.showinfo("Success", f"Model saved to {filename}")
    
    def load_model(self):
        """Load a trained model"""
        filename = filedialog.askopenfilename(
            filetypes=[("PyTorch files", "*.pth"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.agent.load_model(filename)
                messagebox.showinfo("Success", f"Model loaded from {filename}")
                self.new_game()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

class TrainingWindow:
    """Training configuration window"""
    
    def __init__(self, parent, agent: TicTacToeAgent, trainer: TicTacToeTrainer):
        self.agent = agent
        self.trainer = trainer
        
        self.window = tk.Toplevel(parent)
        self.window.title("Train Neural Network")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        self.setup_training_ui()
    
    def setup_training_ui(self):
        """Setup training UI"""
        
        # Title
        tk.Label(self.window, text="Neural Network Training", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Training options
        options_frame = tk.Frame(self.window)
        options_frame.pack(pady=10)
        
        # Episodes
        tk.Label(options_frame, text="Episodes:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.episodes_var = tk.IntVar(value=500)
        episodes_spin = tk.Spinbox(options_frame, from_=100, to=5000, increment=100,
                                  textvariable=self.episodes_var, width=10)
        episodes_spin.grid(row=0, column=1, padx=10)
        
        # Batch size
        tk.Label(options_frame, text="Batch Size:", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
        self.batch_var = tk.IntVar(value=32)
        batch_spin = tk.Spinbox(options_frame, from_=16, to=128, increment=16,
                               textvariable=self.batch_var, width=10)
        batch_spin.grid(row=1, column=1, padx=10)
        
        # Training buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Train vs Random", 
                 command=self.train_random, bg="lightblue",
                 font=("Arial", 12)).pack(pady=5, fill=tk.X)
        
        tk.Button(button_frame, text="Train vs Heuristic", 
                 command=self.train_heuristic, bg="lightgreen",
                 font=("Arial", 12)).pack(pady=5, fill=tk.X)
        
        tk.Button(button_frame, text="Train Self-Play", 
                 command=self.train_self_play, bg="lightyellow",
                 font=("Arial", 12)).pack(pady=5, fill=tk.X)
        
        tk.Button(button_frame, text="Evaluate Agent", 
                 command=self.evaluate_agent, bg="lightcoral",
                 font=("Arial", 12)).pack(pady=5, fill=tk.X)
        
        tk.Button(button_frame, text="Show Training Progress", 
                 command=self.show_progress, bg="lightpink",
                 font=("Arial", 12)).pack(pady=5, fill=tk.X)
        
        # Progress display
        self.progress_text = tk.Text(self.window, height=10, width=50)
        self.progress_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Scrollbar for text
        scrollbar = tk.Scrollbar(self.progress_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.progress_text.yview)
    
    def log_message(self, message: str):
        """Add message to progress text"""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.window.update()
    
    def train_random(self):
        """Train against random opponent"""
        self.log_message("Starting training against random opponent...")
        
        def train_thread():
            episodes = self.episodes_var.get()
            batch_size = self.batch_var.get()
            
            # Redirect print to GUI
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                results = self.trainer.train_against_random(episodes, batch_size)
                output = sys.stdout.getvalue()
                
                self.window.after(0, lambda: self.log_message(output))
                self.window.after(0, lambda: self.log_message(f"Training complete! Win rate: {results['win_rate']:.3f}"))
                
            finally:
                sys.stdout = old_stdout
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def train_heuristic(self):
        """Train against heuristic opponent"""
        self.log_message("Starting training against heuristic opponent...")
        
        def train_thread():
            episodes = self.episodes_var.get()
            batch_size = self.batch_var.get()
            
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                results = self.trainer.train_against_heuristic(episodes, batch_size)
                output = sys.stdout.getvalue()
                
                self.window.after(0, lambda: self.log_message(output))
                self.window.after(0, lambda: self.log_message(f"Training complete! Win rate: {results['win_rate']:.3f}"))
                
            finally:
                sys.stdout = old_stdout
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def train_self_play(self):
        """Train with self-play"""
        self.log_message("Starting self-play training...")
        
        def train_thread():
            episodes = self.episodes_var.get()
            batch_size = self.batch_var.get()
            
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                results = self.trainer.train_self_play(episodes, batch_size)
                output = sys.stdout.getvalue()
                
                self.window.after(0, lambda: self.log_message(output))
                self.window.after(0, lambda: self.log_message(f"Training complete! Win rate: {results['win_rate']:.3f}"))
                
            finally:
                sys.stdout = old_stdout
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def evaluate_agent(self):
        """Evaluate the trained agent"""
        self.log_message("Evaluating agent...")
        
        def eval_thread():
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                # Evaluate against both opponents
                random_results = self.trainer.evaluate_agent("random", 100)
                heuristic_results = self.trainer.evaluate_agent("heuristic", 100)
                
                output = sys.stdout.getvalue()
                self.window.after(0, lambda: self.log_message(output))
                
            finally:
                sys.stdout = old_stdout
        
        threading.Thread(target=eval_thread, daemon=True).start()
    
    def show_progress(self):
        """Show training progress plots"""
        try:
            self.trainer.plot_training_progress()
        except Exception as e:
            self.log_message(f"Error showing progress: {str(e)}")

if __name__ == "__main__":
    app = TicTacToeGUI()
    app.run() 